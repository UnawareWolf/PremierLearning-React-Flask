import requests
import numpy
import os.path

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from keras.models import Sequential
from keras.layers import Dense
from sklearn import linear_model
from .season import *
from .formatted_match_data import FormattedMatchData
from persistence import DB_Handler

FANTASY_JSON_FILE_LOCATION = 'data/season_20_21/fantasy.json'
FIXTURES_JSON_FILE_LOCATION = 'data/season_20_21/fixtures.json'
PLAYER_JSON_FILE_LOCATION = 'data/season_20_21/players/player_%i.json'
FANTASY_API = 'https://fantasy.premierleague.com/api/bootstrap-static/'
FIXTURES_API = 'https://fantasy.premierleague.com/api/fixtures/'
PLAYER_API = 'https://fantasy.premierleague.com/api/element-summary/%i/'
QUICK_RUN = True
ALWAYS_UPDATE = False


class Runner:
    def __init__(self):
        self.points_learner_input = []
        self.points_learner_output = []
        self.minutes_learner_input = []
        self.minutes_learner_output = []
        self.squad = None
        self.current_season = None
        self.past_seasons = []
        self.epochs = 8
        self.batch_size = 32
        self.model_repetitions = 4
        if QUICK_RUN:
            self.epochs = 2
            self.batch_size = 32
            self.model_repetitions = 2

    def run(self):
        self.update_persisted_data_if_outdated()

        print('Setting up players and teams...')
        self.current_season = CurrentSeason()
        self.populate_past_seasons()

        self.calculate_player_ict_and_points_regression()

        print('Preparing data for learning...')
        self.populate_formatted_match_data()

        self.learn()
        self.current_season.calculate_player_points_over_next_5_gameweeks()

        self.persist_players()

        # self.populate_squad()

        # print()

    def update_persisted_data_if_outdated(self):
        fantasy_json_from_api = self.get_request_json(FANTASY_API)

        update_all = self.should_update_data(fantasy_json_from_api)

        if update_all:
            print('Getting latest data...')
            self.persist_json(FANTASY_JSON_FILE_LOCATION, fantasy_json_from_api)

        if update_all or not os.path.isfile(FIXTURES_JSON_FILE_LOCATION):
            fixtures_json = self.get_request_json(FIXTURES_API)
            if fixtures_json is not None:
                self.persist_json(FIXTURES_JSON_FILE_LOCATION, fixtures_json)

        if fantasy_json_from_api is not None:
            for element in fantasy_json_from_api['elements']:
                player_id = element['id']
                player_file_path = PLAYER_JSON_FILE_LOCATION % player_id

                if update_all or not os.path.isfile(player_file_path):
                    player_json = self.get_request_json(PLAYER_API % player_id)
                    if player_json is not None:
                        self.persist_json(player_file_path, player_json)

    @staticmethod
    def get_request_json(uri):
        try:
            return requests.get(uri).json()
        except:
            return None

    def should_update_data(self, fantasy_json_from_api):
        if ALWAYS_UPDATE:
            return True
        if fantasy_json_from_api is None:
            return False

        fantasy_json_file = None
        if os.path.isfile(FANTASY_JSON_FILE_LOCATION):
            fantasy_json_file = self.read_json(FANTASY_JSON_FILE_LOCATION)

        if fantasy_json_file is None:
            return True

        last_api_match_id = self.get_last_event_checked_id(fantasy_json_from_api)
        last_file_match_id = self.get_last_event_checked_id(fantasy_json_file)
        return last_api_match_id != last_file_match_id

    def populate_past_seasons(self):
        self.past_seasons.append(PastSeason(19))
        self.past_seasons.append(PastSeason(18))

        all_seasons = []
        for season in self.past_seasons:
            all_seasons.append(season)
        all_seasons.append(self.current_season)

        for player in self.current_season.players:
            for season in all_seasons:
                if player.code in season.player_code_dict:
                    player_last_season = season.player_code_dict[player.code]
                    if season.years[0] - 1 in player.history_past:
                        player_last_season.points_per_min_last_season = player.history_past[season.years[0] - 1]
                        player_last_season.played_last_season = True

        print()

    def populate_formatted_match_data(self):
        self.populate_learning_inputs_for_season(self.current_season)
        for season in self.past_seasons:
            self.populate_learning_inputs_for_season(season)

    def populate_learning_inputs_for_season(self, season):
        for player in season.players:
            for match in player.matches:
                self.minutes_learner_input.append([match.minutes_last, match.average_minutes_last_3,
                                                   match.average_minutes_last_5, match.average_minutes,
                                                   match.matches_available, match.average_points_in_previous_matches])
                self.minutes_learner_output.append([match.minutes])
                if match.valid_for_learning:
                    formatted_match_data = FormattedMatchData(match)
                    self.points_learner_input.append(formatted_match_data.input)
                    self.points_learner_output.append(formatted_match_data.output)

    def calculate_player_ict_and_points_regression(self):
        ict_values = []
        points = []

        for player in self.current_season.players:
            for match in player.matches:
                if match.valid_for_learning:  # and match.is_training_data (if not then its testing data)
                    ict_values.append([match.average_ict_in_previous_matches])
                    points.append([match.average_points_in_previous_matches])

        ict_reg = linear_model.LinearRegression()
        ict_reg.fit(ict_values, points)

        predicted_points = ict_reg.predict(ict_values)

        for player in self.current_season.players:
            for match in player.matches:
                if match.valid_for_learning:  # also fit testing data here using the regression fitted on training data
                    points_predicted_by_ict = ict_reg.predict([[match.average_ict_in_previous_matches]])[0][0]
                    match.ict_point_regression_deviation = points_predicted_by_ict - match.average_points_in_previous_matches

            player_predicted_points_from_ict = ict_reg.predict([[player.average_ict_so_far]])[0][0]
            player.ict_deviation = player_predicted_points_from_ict - player.average_points_so_far

        # pyplot.scatter(ict_values, points)
        # pyplot.plot(ict_values, predicted_points, color='blue', linewidth=3)
        #
        # pyplot.show()

    @staticmethod
    def loss_season_one(y_true, y_pred):
        y_true = float(y_true)
        y_pred = float(y_pred)

        return abs(y_true - y_pred) ** 2

    # def get_predicted_minutes_input(self):
    #     model_input = []
    #     model_output = []
    #
    #     for player in self.current_season.players:
    #         # player.build_snapshot_minutes()
    #
    #         for match in player.matches:
    #             model_input.append([match.minutes_last, match.minutes_last_3, match.minutes_last_5,
    #                                 match.average_minutes, match.matches_available])
    #             model_output = [match.minutes]
    #
    #     return model_input

    def predict_minutes(self, future_matches):

        model = Sequential()
        model.add(Dense(6, input_dim=6, activation='relu'))
        model.add(Dense(3, activation='relu'))
        model.add(Dense(1))

        model.compile(loss=self.loss_season_one, optimizer='adam')

        self.minutes_learner_input = numpy.array(self.minutes_learner_input)
        self.minutes_learner_output = numpy.array(self.minutes_learner_output)

        train_length = int(len(self.minutes_learner_output) * 4 / 5)

        input_train = self.minutes_learner_input[:train_length, :]
        output_train = self.minutes_learner_output[:train_length, :]
        input_test = self.minutes_learner_input[train_length:, :]
        output_test = self.minutes_learner_output[train_length:, :]

        model.fit(input_train, output_train, epochs=self.epochs, batch_size=self.batch_size, verbose=0)

        model.evaluate(input_test, output_test)

        input_data = []

        for match in future_matches:
            input_data.append([match.minutes_last, match.average_minutes_last_3,
                               match.average_minutes_last_5, match.average_minutes,
                               match.matches_available, match.average_points_in_previous_matches])

        numpy_input_data = numpy.array(input_data)
        future_predictions = model.predict(numpy_input_data)
        return future_predictions

    def learn(self):
        future_matches = []

        for player in self.current_season.players:
            for future_match in player.future_matches:
                future_matches.append(future_match)

        model_predictions = []
        minute_predictions = []

        for i in range(self.model_repetitions):
            model_predictions.append(self.get_single_model_predictions(future_matches))
            minute_predictions.append(self.predict_minutes(future_matches))

        averaged_predictions = []
        for i in range(len(model_predictions[0])):
            single_match_predictions = []
            for prediction_array in model_predictions:
                single_match_predictions.append(prediction_array[i])
            averaged_predictions.append(sum(single_match_predictions)/len(single_match_predictions))

        averaged_minute_predictions = []
        for i in range(len(minute_predictions[0])):
            single_match_minute_predictions = []
            for prediction_array in minute_predictions:
                single_match_minute_predictions.append(prediction_array[i])
            averaged_minute_predictions.append(sum(single_match_minute_predictions)/len(single_match_minute_predictions))

        for i in range(len(future_matches)):
            future_matches[i].points = averaged_predictions[i][0]
            future_matches[i].minutes = averaged_minute_predictions[i][0]
            future_matches[i].update_points_based_on_expected_minutes()

    def get_single_model_predictions(self, future_matches):
        model = Sequential()
        model.add(Dense(22, input_dim=22, activation='relu'))
        model.add(Dense(10, activation='relu'))
        model.add(Dense(1))

        model.compile(loss=self.loss_season_one, optimizer='adam')

        self.points_learner_input = numpy.array(self.points_learner_input)
        self.points_learner_output = numpy.array(self.points_learner_output)

        train_length = int(len(self.points_learner_input) * 4 / 5)

        input_train = self.points_learner_input[:train_length, :]
        output_train = self.points_learner_output[:train_length, :]
        input_test = self.points_learner_input[train_length:, :]
        output_test = self.points_learner_output[train_length:, :]

        # model.fit(input_train, output_train, epochs=8, batch_size=16)
        model.fit(input_train, output_train, epochs=self.epochs, batch_size=self.batch_size, verbose=0)

        model.evaluate(input_test, output_test)

        # predictions = model.predict(input_test)
        #
        # model.summary()

        # matches = []
        input_data = []

        for future_match in future_matches:
            input_data.append(FormattedMatchData(future_match).input)

        # for player in self.current_season.players:
        #     for future_match in player.future_matches:
        #         matches.append(future_match)
        #         input_data.append(FormattedMatchData(future_match).input)
                # future_match.points = model.predict(numpy.array([FormattedMatchData(future_match).input]))[0][0]

        numpy_input_data = numpy.array(input_data)
        future_predictions = model.predict(numpy_input_data)
        return future_predictions
    
    def persist_players(self):
        db_handler = DB_Handler()
        db_handler.init_db()
        db_handler.persist_players(self.current_season.players)
        db_handler.connection.commit()
        db_handler.close_connection()

    def dump_element_types(self):
        with open('element_types.json', 'w') as f:
            json.dump(self.current_season.element_type_dict, f)

    @staticmethod
    def get_last_event_checked_id(fantasy_json):
        last_api_match_id = None
        for event in fantasy_json['events']:
            if event['data_checked']:
                last_api_match_id = event['id']
            else:
                break
        return last_api_match_id

    @staticmethod
    def read_json(file_path):
        with open(file_path) as file:
            return json.load(file)

    @staticmethod
    def persist_json(file_path, json_data):
        with open(file_path, 'w') as file:
            json.dump(json_data, file)
