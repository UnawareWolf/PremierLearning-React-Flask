from datetime import datetime, timedelta
from abc import ABC


class RawMatch(ABC):

    def __init__(self):
        self.player_id = None
        self.minutes = None
        self.points = None
        self.gameweek = None
        self.opponent = None

    def format_as_db_insert(self):
        return (
            self.player_id,
            float(self.minutes),
            float(self.points),
            self.gameweek,
            self.opponent
        )


class Match(RawMatch):

    def __init__(self, player, match_json, teams):
        super().__init__()

        self.player = player
        self.player_id = self.player.id
        self.gameweek = match_json['round']

        self.is_gkp = int(player.position == 1)
        self.is_def = int(player.position == 2)
        self.is_mid = int(player.position == 3)
        self.is_att = int(player.position == 4)

        self.minutes = match_json['minutes']

        self.home = match_json['was_home']
        self.points = int(match_json['total_points'])
        self.fixture_id = int(match_json['fixture'])
        self.ict = float(match_json['ict_index'])

        self.opponent_team = teams[int(match_json['opponent_team'])]
        try:
            self.opponent_team_match = self.opponent_team.team_match_dict[self.fixture_id]
        except:
            self.opponent_team_match = self.opponent_team.future_team_match_dict[self.fixture_id]
        if self.home:
            team_id = int(self.opponent_team_match.fixture_json['team_h'])
        else:
            team_id = int(self.opponent_team_match.fixture_json['team_a'])
        self.team = teams[team_id]
        try:
            self.team_match = self.team.team_match_dict[self.fixture_id]
        except:
            self.team_match = self.team.future_team_match_dict[self.fixture_id]

        self.opponent = self.opponent_team.name

        self.average_points_in_previous_matches = 0
        self.average_points_last_5 = 0
        self.average_points_last_3 = 0
        self.points_last = 0

        self.average_ict_in_previous_matches = 0
        self.matches_played = 0
        self.valid_for_learning = False

        self.ict_point_regression_deviation = 0
        self.player_point_deviation_per_game = 0

        self.minutes_last = 0
        self.average_minutes_last_3 = 0
        self.average_minutes_last_5 = 0
        self.average_minutes = 0
        self.matches_available = 0

    def __str__(self):
        return '%i - %i %s (%i)' % (self.opponent_team_match.conceded, self.opponent_team_match.scored,
                                    self.opponent_team.name, self.points)


class FutureMatch(RawMatch):

    def __init__(self, player, future_match_json, teams):
        super().__init__()

        self.player = player
        self.player_id = self.player.id
        self.gameweek = future_match_json['event']

        self.is_gkp = int(player.position == 1)
        self.is_def = int(player.position == 2)
        self.is_mid = int(player.position == 3)
        self.is_att = int(player.position == 4)

        self.home = future_match_json['is_home']
        self.fixture_id = future_match_json['id']
        self.points = 0

        self.opponent_team = teams[self.get_opponent_id(future_match_json)]
        try:
            self.opponent_team_match = self.opponent_team.future_team_match_dict[self.fixture_id]
        except:
            self.opponent_team_match = self.opponent_team.team_match_dict[self.fixture_id]

        self.team = player.team
        try:
            self.team_match = self.team.future_team_match_dict[self.fixture_id]
        except:
            self.team_match = self.team.team_match_dict[self.fixture_id]

        self.opponent = self.opponent_team.name

        self.chance_of_playing = player.element_dict['chance_of_playing_next_round']


        self.average_points_in_previous_matches = player.average_points_so_far
        self.average_points_last_5 = 0
        self.average_points_last_3 = 0
        self.points_last = 0

        self.ict_point_regression_deviation = player.ict_deviation
        self.matches_played = player.matches_played
        self.player_point_deviation_per_game = player.point_deviation_per_game

        self.fixture_date = self.get_fixture_date(future_match_json['kickoff_time'])

        # print(self.fixture_date)
        self.average_minutes_when_played = 0

        self.minutes_last = 0
        self.average_minutes_last_3 = 0
        self.average_minutes_last_5 = 0
        self.average_minutes = 0
        self.matches_available = 0
        self.minutes = 0

    def update_points_based_on_expected_minutes(self):
        if self.minutes <= 40 or self.average_minutes_last_3 < 40 or self.matches_played < 3:
            self.points = 0
        if self.chance_of_playing is not None:
            self.points = self.chance_of_playing * self.points / 100
        # expected_points_per_min = self.points / 90
        # self.points = expected_points_per_min * self.expected_minutes

    def get_opponent_id(self, future_match_json):
        if self.home:
            return future_match_json['team_a']
        return future_match_json['team_h']

    @staticmethod
    def get_fixture_date(kickoff_time):
        try:
            date_segments = kickoff_time.split('T')[0].split('-')
            return datetime(int(date_segments[0]), int(date_segments[1]), int(date_segments[2]))
        except:
            return None

    def within_n_gameweeks(self, current_gameweek, n):
        if self.gameweek is None:
            return False
        return self.gameweek - current_gameweek <= n

    # def within_n_weeks(self, n):
    #     today = datetime.today()
    #     offset = (today.weekday() - 2) % 7
    #     last_wednesday = today - timedelta(days=offset)
    #
    #     try:
    #         days_delta = self.fixture_date - last_wednesday
    #
    #         return days_delta.days < n * 7
    #     except:
    #         return False

    def __str__(self):
        return 'gameweek: %i points: %.2f vs: %s' % (self.gameweek, self.points, self.opponent_team.name)
