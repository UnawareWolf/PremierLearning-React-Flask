from datetime import datetime
from abc import ABC, abstractmethod
from premierlearning.clean_match import STAT_KEYS, CleanMatch, GameStats, PastStats, get_default_game_stats, get_default_past_stats, get_default_stat_window


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


def string_to_bool(true_or_false):
        if true_or_false == 'True':
            return True
        if true_or_false == 'False':
            return False
        return true_or_false


class AbstractMatch(RawMatch):
    
    def __init__(self, player, match_json: dict, teams: dict):
        super().__init__()

        self.player = player
        self.player_id = self.player.id
        self.gameweek = self.get_gw(match_json)

        self.is_gkp = int(player.position == 1)
        self.is_def = int(player.position == 2)
        self.is_mid = int(player.position == 3)
        self.is_att = int(player.position == 4)

        self.minutes = 0
        self.home = self.get_home(match_json)
        self.points = 0
        self.fixture_id = self.get_fixture_id(match_json)
        self.opponent_team = teams[self.get_opponent_id(match_json)]
        self.opponent_team_match = self.get_opponent_team_match()
        self.team = self.get_team(teams)
        self.team_match = self.get_team_match()
        self.opponent = self.opponent_team.name

        self.ict_point_regression_deviation = 0
        self.matches_played = 0
        self.matches_available = 0
        self.valid_for_learning = False

        self.past_stats: PastStats = get_default_past_stats()
        self.game_stats: GameStats = get_default_game_stats()

    
    @abstractmethod
    def get_gw(self, match_json: dict):
        pass

    @abstractmethod
    def get_home(self, match_json: dict):
        pass

    @abstractmethod
    def get_fixture_id(self, match_json: dict):
        pass

    @abstractmethod
    def get_opponent_id(self, match_json: dict):
        pass

    @abstractmethod
    def get_opponent_team_match(self):
        pass

    @abstractmethod
    def get_team(self, teams):
        pass

    @abstractmethod
    def get_team_match(self):
        pass
    
    def to_clean_match(self) -> CleanMatch:
        clean_match: CleanMatch = {
            'is_valid': self.valid_for_learning,
            'matches_played': self.matches_played,
            # 'points': self.stat_windows['points'],
            # 'goals_scored': self.stat_windows['goals_scored'],
            # 'assists': self.stat_windows['assists'],
            'past_stats': self.past_stats,
            'ict_point_deviation': self.ict_point_regression_deviation,
            'is_gkp': self.is_gkp,
            'is_def': self.is_def,
            'is_mid': self.is_mid,
            'is_att': self.is_att,
            'is_home': int(string_to_bool(self.home)),
            'team_average_points': self.team_match.average_points_in_previous_matches,
            'team_average_scored': self.team_match.average_scored_in_previous_matches,
            'team_average_conceded': self.team_match.average_conceded_in_previous_matches,
            'opponent_average_points': self.opponent_team_match.average_points_in_previous_matches,
            'opponent_average_scored': self.opponent_team_match.average_scored_in_previous_matches,
            'opponent_average_conceded': self.opponent_team_match.average_conceded_in_previous_matches,
            'team_last_season_finish': self.team.last_season_finish,
            'opponent_last_season_finish': self.opponent_team.last_season_finish,
            'played_last_season': int(self.player.played_last_season),
            'last_season_points_per_min': self.player.points_per_min_last_season,
            'game_stats': self.game_stats
            # 'points_out': self.points
            # 'goals_out': self.goals_scored,
            # 'assists_out': self.assists
        }
        return clean_match


class PastMatch(AbstractMatch):

    def __init__(self, player, match_json, teams):
        super().__init__(player, match_json, teams)

        self.minutes = match_json['minutes']

        self.points = int(match_json['total_points'])
        # self.ict = float(match_json['ict_index'])
        
        # self.average_ict_in_previous_matches = 0
        for key in STAT_KEYS:
            self.game_stats[key] = float(match_json[key])
        
        if self.game_stats['goals_conceded'] >= 2:
            self.game_stats['conceded_2_plus'] = 1
            if self.game_stats['goals_conceded'] >= 4:
                self.game_stats['conceded_4_plus'] = 1
            else:
                self.game_stats['conceded_4_plus'] = 0
        else:
            self.game_stats['conceded_4_plus'] = 0
        
        if self.game_stats['minutes'] >= 60:
            self.game_stats['minutes_60_plus'] = 1
        else:
            self.game_stats['minutes_60_plus'] = 0
        
        if self.game_stats['minutes'] > 0:
            self.game_stats['chance_to_play'] = 1
        else:
            self.game_stats['chance_to_play'] = 0
        

        # self.goals_scored = match_json['goals_scored']
        # self.assists = match_json['assists']
    
    def get_gw(self, match_json: dict):
        return match_json['round']
    
    def get_home(self, match_json: dict):
        return match_json['was_home']
    
    def get_fixture_id(self, match_json: dict):
        return int(match_json['fixture'])
    
    def get_opponent_id(self, match_json: dict):
        return int(match_json['opponent_team'])
    
    def get_team(self, teams):
        # Cannot do player.team because player may play for new team
        if self.home:
            team_id = int(self.opponent_team_match.fixture_json['team_h'])
        else:
            team_id = int(self.opponent_team_match.fixture_json['team_a'])
        return teams[team_id]

    def get_team_match(self):
        if self.fixture_id in self.team.team_match_dict:
            return self.team.team_match_dict[self.fixture_id]
        return self.team.future_team_match_dict[self.fixture_id]
    
    def get_opponent_team_match(self):
        if self.fixture_id in self.opponent_team.team_match_dict:
            return self.opponent_team.team_match_dict[self.fixture_id]
        return self.opponent_team.future_team_match_dict[self.fixture_id]

    def __str__(self):
        return '%i - %i %s (%i)' % (self.opponent_team_match.conceded, self.opponent_team_match.scored,
                                    self.opponent_team.name, self.points)


class FutureMatch(AbstractMatch):

    def __init__(self, player, future_match_json, teams):
        super().__init__(player, future_match_json, teams)

        self.chance_of_playing = player.element_dict['chance_of_playing_next_round']

        # self.average_points_in_previous_matches = player.average_points_so_far

        self.ict_point_regression_deviation = player.ict_deviation
        self.matches_played = player.matches_played
        # self.player_point_deviation_per_game = player.point_deviation_per_game

        self.fixture_date = self.get_fixture_date(future_match_json['kickoff_time'])
    
    def get_gw(self, match_json: dict):
        return match_json['event']
    
    def get_home(self, match_json: dict):
        return match_json['is_home']
    
    def get_fixture_id(self, match_json: dict):
        return match_json['id']
    
    def get_opponent_team_match(self):
        if self.fixture_id in self.opponent_team.future_team_match_dict:
            return self.opponent_team.future_team_match_dict[self.fixture_id]
        return self.opponent_team.team_match_dict[self.fixture_id]
    
    def get_team(self, teams):
        return self.player.team
    
    def get_team_match(self):
        if self.fixture_id in self.team.future_team_match_dict:
            return self.team.future_team_match_dict[self.fixture_id]
        return self.team.team_match_dict[self.fixture_id]

    def update_points_based_on_expected_minutes(self):
        if self.game_stats['minutes'] <= 40 or self.past_stats['chance_to_play']['last_3_avg'] < 0.44 or self.matches_played < 3:
            self.points = 0
        if self.chance_of_playing is not None:
            self.points = self.chance_of_playing * self.points / 100

    def get_opponent_id(self, match_json):
        if self.home:
            return match_json['team_a']
        return match_json['team_h']

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
    
    def calc_points_from_stats(self):
        self.points = 1 # for assuming they play
        if self.is_gkp:
            self.points += sum([
                self.game_stats['goals_scored'] * 6,
                self.game_stats['saves'] / 3,
                self.game_stats['clean_sheets'] * 4,
                self.game_stats['conceded_2_plus'] * -1,
                self.game_stats['conceded_4_plus'] * -1
            ])
        elif self.is_def:
            self.points += sum([
                self.game_stats['goals_scored'] * 6,
                self.game_stats['clean_sheets'] * 4,
                self.game_stats['conceded_2_plus'] * -1,
                self.game_stats['conceded_4_plus'] * -1
            ])
        elif self.is_mid:
            self.points += sum([
                self.game_stats['goals_scored'] * 5,
                self.game_stats['clean_sheets']
            ])
        else:
            self.points += self.game_stats['goals_scored'] * 4
        
        self.points += sum([
            self.game_stats['assists'] * 3,
            self.game_stats['bonus'],
            self.game_stats['yellow_cards'] * -1,
            self.game_stats['minutes_60_plus']
        ])
    
    def set_minutes_from_stats(self):
        self.minutes = self.game_stats['minutes']

    def __str__(self):
        return 'gameweek: %i points: %.2f vs: %s' % (self.gameweek, self.points, self.opponent_team.name)
