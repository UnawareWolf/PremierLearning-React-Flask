import sys
import requests
import os.path
from premierlearning.clean_match import BUILT_KEYS, CHANCE_TO_PLAY, STAT_KEYS, get_input_keys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from premierlearning.learning import *

from sklearn import linear_model
from .season import *
from persistence import DB_Handler

FANTASY_API = 'https://fantasy.premierleague.com/api/bootstrap-static/'
FIXTURES_API = 'https://fantasy.premierleague.com/api/fixtures/'
PLAYER_API = 'https://fantasy.premierleague.com/api/element-summary/%i/'


class Runner:
    def __init__(self):
        self.squad = None
        self.current_season = None
        self.past_seasons = []

    def run(self):
        self.update_persisted_data_if_outdated()

        print('Setting up players and teams...')
        self.current_season = CurrentSeason()
        self.populate_past_seasons()
        self.process_player_matches()

        self.calculate_player_ict_and_points_regression()

        print('Preparing data for learning...')

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
            self.persist_json(FANTASY_JSON_FILE_LOCATION % (SEASON_YR, SEASON_YR + 1), fantasy_json_from_api)

        if update_all or not os.path.isfile(FIXTURES_JSON_FILE_LOCATION % (SEASON_YR, SEASON_YR + 1)):
            fixtures_json = self.get_request_json(FIXTURES_API)
            if fixtures_json is not None:
                self.persist_json(FIXTURES_JSON_FILE_LOCATION % (SEASON_YR, SEASON_YR + 1), fixtures_json)

        if fantasy_json_from_api is not None:
            for element in fantasy_json_from_api['elements']:
                player_id = element['id']
                player_file_path = PLAYER_JSON_FILE_LOCATION % (SEASON_YR, SEASON_YR + 1) + str(player_id) + '.json'

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
        if '--update' in sys.argv:
        # if ALWAYS_UPDATE:
            return True
        if fantasy_json_from_api is None:
            return False

        fantasy_json_file = None
        if os.path.isfile(FANTASY_JSON_FILE_LOCATION % (SEASON_YR, SEASON_YR + 1)):
            fantasy_json_file = self.read_json(FANTASY_JSON_FILE_LOCATION % (SEASON_YR, SEASON_YR + 1))

        if fantasy_json_file is None:
            return True

        last_api_match_id = self.get_last_event_checked_id(fantasy_json_from_api)
        last_file_match_id = self.get_last_event_checked_id(fantasy_json_file)
        return last_api_match_id != last_file_match_id

    def populate_past_seasons(self):
        for i in reversed(range(18, SEASON_YR)):
            self.past_seasons.append(PastSeason(i))

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
    
    def process_player_matches(self):
        # last_szn = next(szn for szn in self.past_seasons if szn.years[0] == self.current_season.years[0] - 1)
        # if self.current_season.next_gameweek < 12:
        #     for player in self.current_season.players:
        #         if player.code in last_szn.player_code_dict:
        #             player.attach_last_szn_matches(last_szn.player_code_dict[player.code])
        
        for player in self.current_season.players:
            player.process_matches()
        for season in self.past_seasons:
            for player in season.players:
                player.process_matches()


    def populate_formatted_match_data(self):
        learner_input = self.get_learning_inputs_for_season(self.current_season)
        for season in self.past_seasons:
            learner_input.extend(self.get_learning_inputs_for_season(season))
        return learner_input

    def get_learning_inputs_for_season(self, season) -> list:
        learner_input = []
        for player in season.players:
            for match in player.matches:
                learner_input.append(match.to_clean_match())
        return learner_input

    def calculate_player_ict_and_points_regression(self):
        ict_values = []
        points = []

        # for season in list(self.past_seasons + [self.current_season]):
        for player in self.current_season.players:
            # for player in season.players:
            for match in player.matches:
                if match.valid_for_learning:  # and match.is_training_data (if not then its testing data)
                    ict_values.append([match.past_stats['ict_index']['avg']])
                    points.append([match.game_stats['total_points']])

        # for player in self.past_seasons[0].players:
        #     for match in player.matches:
        #         if match.valid_for_learning:  # and match.is_training_data (if not then its testing data)
        #             ict_values.append([match.average_ict_in_previous_matches])
        #             points.append([match.average_points_in_previous_matches])

        ict_reg = linear_model.LinearRegression()
        ict_reg.fit(ict_values, points)

        # predicted_points = ict_reg.predict(ict_values)

        for player in self.current_season.players:
            for match in player.matches:
                if match.valid_for_learning:  # also fit testing data here using the regression fitted on training data
                    points_predicted_by_ict = ict_reg.predict([[match.past_stats['ict_index']['avg']]])[0][0]
                    match.ict_point_regression_deviation = points_predicted_by_ict - match.past_stats['total_points']['avg']

            player_predicted_points_from_ict = ict_reg.predict([[player.past_stats['ict_index']['avg']]])[0][0]
            player.ict_deviation = player_predicted_points_from_ict - player.past_stats['total_points']['avg']

        # pyplot.scatter(ict_values, points)
        # pyplot.plot(ict_values, predicted_points, color='blue', linewidth=3)
        #
        # pyplot.show()


    def learn(self):
        clean_matches = self.populate_formatted_match_data()

        valid_clean_matches = [match for match in clean_matches if match['is_valid']]

        future_matches = []
        future_clean_matches = []
        for player in self.current_season.players:
            for future_match in player.future_matches:
                future_matches.append(future_match)
                future_clean_matches.append(future_match.to_clean_match())
        
        learnt_stats = {}
        for key in STAT_KEYS + BUILT_KEYS:
            learnt_stats[key] = get_avg_predictions(valid_clean_matches, future_clean_matches, get_input_keys(key), key, True)
        
        learnt_stats[CHANCE_TO_PLAY] = get_avg_predictions(clean_matches, future_clean_matches, get_input_keys(CHANCE_TO_PLAY), CHANCE_TO_PLAY, False)

        def set_zero_if_neg(val):
            if val < 0:
                return 0
            return val

        for i in range(len(future_matches)):
            for key in STAT_KEYS + BUILT_KEYS + [CHANCE_TO_PLAY]:
                future_matches[i].game_stats[key] = set_zero_if_neg(learnt_stats[key][i][0])
            future_matches[i].calc_points_from_stats()
            future_matches[i].set_minutes_from_stats()
            future_matches[i].update_points_based_on_expected_minutes()

    
    def persist_players(self):
        print('Connecting to database')
        db_handler = DB_Handler()
        db_handler.init_db()
        print('Persisting players')
        db_handler.persist_players(self.current_season.players)
        db_handler.connection.commit()
        db_handler.close_connection()
        print('Run finished')

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
