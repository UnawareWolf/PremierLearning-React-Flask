import numpy

from abc import ABC

from premierlearning.clean_match import BUILT_KEYS, STAT_KEYS, PastStats, StatWindow, get_default_past_stats
from .match import PastMatch, FutureMatch


class RawPlayer(ABC):

    def __init__(self):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.team_id = None
        self.team_name = None
        self.current_cost = None
        self.position = None
        self.matches = None
        self.future_matches = None,
        self.code = None
    
    def __repr__(self):
        points = 0
        if len(self.future_matches) > 0:
            points = self.future_matches[0].points
        return '%s %s: %.1f (£%.1fm)' % (self.first_name, self.last_name, points, self.current_cost)
    
    def format_as_db_insert(self):
        return (
            self.id,
            self.first_name,
            self.last_name,
            self.team_id,
            self.team_name,
            self.current_cost,
            self.position,
            self.code
        )
    

    def get_points_between_gameweeks(self, gameweek_from, gameweek_to, bench_multiplier, bench_boost_gw, free_hit_gw):
        return sum(self.get_points_in_gameweek_n(n, bench_multiplier, bench_boost_gw, free_hit_gw) for n in range(gameweek_from, gameweek_to + 1))


    def get_points_in_gameweek_n(self, n, bench_multiplier, bench_boost_gw, free_hit_gw):
        # bench_multiplier = 1
        if n == bench_boost_gw:
            bench_multiplier = 1
        if n == free_hit_gw:
            bench_multiplier = 0
        return sum(fixture.points for fixture in (self.future_matches + self.matches) if fixture.gameweek == n) * bench_multiplier


class Player(RawPlayer):

    def __init__(self, fantasy_json, element_dict, player_json, teams, current_gameweek):
        super().__init__()
        
        self.played_last_season = False
        self.points_per_min_last_season = 0
        self.current_gameweek = current_gameweek

        # self.average_points_so_far = 0
        # self.average_ict_so_far = 0
        self.ict_deviation = 0
        self.matches_played = 0
        # self.point_deviation_per_game = 0

        self.points_over_next_5_gameweeks = 0

        # self.points_so_far = []
        self.past_stats: PastStats = get_default_past_stats()
        self.minutes_so_far = []

        self.element_dict = element_dict
        # self.player_dict = requests.get(PLAYER_API % element_dict['id']).json()
        self.player_json = player_json
        self.id = int(self.element_dict['id'])
        self.code = int(self.element_dict['code'])
        self.history_past = {}
        self.populate_history_past()

        self.position = self.element_dict['element_type']

        self.first_name = self.element_dict['first_name']
        self.last_name = self.element_dict['second_name']

        self.points_per_game = float(self.element_dict['points_per_game'])

        self.current_cost = float(self.element_dict['now_cost'])

        self.last_szn_matches = []
        self.last_szn_avg_mins = 0
        self.last_szn_avg_points = 0

        self.matches = []
        self.future_matches = []
        
        self.teams = teams
        self.team = teams[int(self.element_dict['team'])]
        self.team_name = self.team.name
        self.team_id = self.team.id

        self.populate_matches(teams)

        self.last_opponent_strength = self.get_last_opponent_strength(teams)

        self.last_points = float(self.get_last_points())

        # self.attach_last_szn_matches()

        # self.build_snapshot_stats()

        # self.populate_future_matches(teams)

    def __str__(self):
        points = 0
        if len(self.future_matches) > 0:
            points = self.future_matches[0].points
        return '%s %s (%s): %.1f (%s)' % (self.first_name, self.last_name, self.team.name, points, self.current_cost)

    def get_last_points(self):
        if self.last_opponent_strength is not None:
            return self.player_json['history'][-2]['total_points']
        return 0

    def populate_history_past(self):
        if 'history_past' in self.player_json:
            for past_season in self.player_json['history_past']:
                years = past_season['season_name']
                start_year = int(years.split('/')[0][2:])
                total_points = float(past_season['total_points'])
                minutes_played = float(past_season['minutes'])
                if minutes_played > 200:
                    self.history_past[start_year] = total_points / minutes_played
                else:
                    self.history_past[start_year] = 0

    def get_last_opponent_strength(self, teams):
        history = self.player_json['history']
        if len(history) > 1:
            last_match = history[-1]

            last_opponent = teams[int(last_match['opponent_team'])]
            strength_key = 'strength_attack'
            if last_match['was_home']:
                strength_key += '_home'
            else:
                strength_key += '_away'

            return last_opponent.strength[strength_key]
        return None

    def populate_matches(self, teams):
        for match_json in self.player_json['history']:
            if match_json['team_h_score'] is not None:
                self.matches.append(PastMatch(self, match_json, teams))
    

    def attach_last_szn_matches(self, past_szn_player):
        self.last_szn_matches = past_szn_player.matches
        # match_count = len(self.last_szn_matches)
        # if match_count > 0:
        #     self.last_szn_avg_mins = sum(list(match.minutes for match in self.last_szn_matches)) / match_count
        # match_count_gt_zero = len(list(match for match in self.last_szn_matches if match.minutes > 0))
        # if match_count_gt_zero > 0:
        #     self.last_szn_avg_points = sum(list(match.points for match in self.last_szn_matches if match.minutes > 0)) / match_count_gt_zero
        len_matches = len(self.matches)
        len_past_matches = len(past_szn_player.matches)
        len_matches_to_insert = 7 - len_matches
        if len_past_matches >= len_matches_to_insert:
            matches_to_insert = past_szn_player.matches[- len_matches_to_insert:]
        else:
            matches_to_insert = past_szn_player.matches
        if self.matches:
            matches_to_insert.extend(self.matches)
            self.matches = matches_to_insert
        else:
            self.matches = matches_to_insert


    def process_matches(self):
        self.build_snapshot_stats()
        self.populate_future_matches()


    def populate_future_matches(self):
        for future_match_json in self.player_json['fixtures']:
            self.future_matches.append(FutureMatch(self, future_match_json, self.teams))

        # minutes_greater_than_0 = list(mins for mins in self.minutes_so_far if mins > 0)
        # average_minutes_when_played = 0
        # if len(minutes_greater_than_0) > 0:
        #     average_minutes_when_played = sum(minutes_greater_than_0) / len(minutes_greater_than_0)

        for match in self.future_matches:
            # if len(self.minutes_so_far) > 0:
            #     # if len is up to 6, include some proportion of stats from last szn :)
            #     match.minutes_last = self.minutes_so_far[-1]
            #     match.average_minutes_last_3 = sum(self.minutes_so_far[-3:]) / len(self.minutes_so_far[-3:])
            #     match.average_minutes_last_5 = sum(self.minutes_so_far[-5:]) / len(self.minutes_so_far[-5:])
            #     match.average_minutes = sum(self.minutes_so_far) / len(self.minutes_so_far)
            #     match.matches_available = len(self.minutes_so_far)
            #     match.average_minutes_when_played = average_minutes_when_played

            # elif len(self.last_szn_matches) > 0:
            #     match.minutes_last = self.last_szn_avg_mins
            #     match.average_minutes_last_3 = self.last_szn_avg_mins
            #     match.average_minutes_last_5 = self.last_szn_avg_mins
            #     match.average_minutes = self.last_szn_avg_mins
            #     match.matches_available = 0
            #     match.average_minutes_when_played = self.last_szn_avg_mins # this is not right, should calculate

            # match.points_last = self.final_stats['points']['last']
            # match.average_points_last_3 = self.final_stats['points']['last_3_avg']
            # match.average_points_last_5 = self.final_stats['points']['last_5_avg']
            match.past_stats = self.past_stats

            # if len(self.points_so_far) > 0:
            #     match.points_last = self.points_so_far[-1]
            #     match.average_points_last_3 = sum(self.points_so_far[-3:]) / len(self.points_so_far[-3:])
            #     match.average_points_last_5 = sum(self.points_so_far[-5:]) / len(self.points_so_far[-5:])
            # # elif len(self.last_szn_matches) > 0:
            # #     match.points_last = self.last_szn_avg_points
            # #     match.average_points_last_3 = self.last_szn_avg_points
            # #     match.average_points_last_5 = self.last_szn_avg_points

    def build_snapshot_stats(self):
        # ict_sum_so_far = 0

        # stats_so_far = {
        #     'points': [],
        #     'goals_scored': []
        # }
        stats_so_far = {}
        for key in STAT_KEYS + BUILT_KEYS:
            stats_so_far[key] = []
        
        chance_to_play_list = []

        for match in self.matches:
            if match.game_stats['minutes'] == 0:
                if len(chance_to_play_list) > 0:
                    match.past_stats['chance_to_play'] = self.get_stat_window(chance_to_play_list)
                chance_to_play_list.append(0)
                continue
            # if match.minutes == 0:
            #     continue
            chance_to_play_list.append(1)

            # match.average_points_in_previous_matches = self.average_points_so_far
            if self.matches_played >= 1:
                for key, stats_list in stats_so_far.items():
                    match.past_stats[key] = self.get_stat_window(stats_list)

            # match.average_ict_in_previous_matches = self.average_ict_so_far

            match.matches_played = self.matches_played
            # match.player_point_deviation_per_game = self.point_deviation_per_game

            if self.matches_played >= 3:
                match.valid_for_learning = True

            self.matches_played += 1

            # ict_sum_so_far += match.ict
            # self.average_ict_so_far = ict_sum_so_far / self.matches_played

            for key, stats_list in stats_so_far.items():
                # if key == 'points':
                #     stats_list.append(float(match.points))
                # else:
                stats_list.append(match.game_stats[key])


                # stats_list.append(float(getattr(match, key)))
            # stats_so_far['points'].append(match.points)
            # self.point_deviation_per_game = numpy.std(numpy.array(stats_so_far['points']))

        # self.build_snapshot_minutes()

        if self.matches_played >= 1:
            for key, stats_list in stats_so_far.items():
                self.past_stats[key] = self.get_stat_window(stats_list)
            self.past_stats['chance_to_play'] = self.get_stat_window(chance_to_play_list)
    
    def get_stat_window(self, stats_list) -> StatWindow:
        return {
            'last': stats_list[-1],
            'last_3_avg': sum(stats_list[-3:]) / len(stats_list[-3:]),
            'last_5_avg': sum(stats_list[-5:]) / len(stats_list[-5:]),
            'avg': sum(stats_list) / len(stats_list),
            'deviation': numpy.std(numpy.array(stats_list))
        }
    
    # def get_final_stats_initial_values(self):
    #     stats = {}
    #     for key in LEARNING_KEYS:
    #         stats[key] = get_default_stat_window()
    #     return stats
    #     # return {
    #     #     'points': get_default_stat_window(),
    #     #     'goals_scored': get_default_stat_window()
    #     # }

    # def build_snapshot_minutes(self):
    #     minutes_so_far = []
    #     for match in self.matches:
    #         if len(minutes_so_far) > 0:
    #             match.minutes_last = minutes_so_far[-1]
    #             match.average_minutes_last_3 = sum(minutes_so_far[-3:]) / len(minutes_so_far[-3:])
    #             match.average_minutes_last_5 = sum(minutes_so_far[-5:]) / len(minutes_so_far[-5:])
    #             match.average_minutes = sum(minutes_so_far) / len(minutes_so_far)
    #             match.matches_available = len(minutes_so_far)

    #         minutes_so_far.append(int(match.minutes))
    #     self.minutes_so_far = minutes_so_far

    def calculate_points_over_next_5_gameweeks(self):
        self.points_over_next_5_gameweeks = self.get_points_within_n_gameweeks(5)

    def get_points_within_n_gameweeks(self, n):
        return sum(fixture.points for fixture in self.future_matches
                   if fixture.within_n_gameweeks(self.current_gameweek, n))

    # def get_recent_game_minutes(self):
    #     minutes = 0
    #     n = len(self.matches)
    #     if n > 3:
    #         n = 3
    #     for match in self.matches[-n:]:
    #         minutes += match.minutes
    #     return minutes

    def get_price_at_gw(self, gw):
        for past_gw in self.player_json['history']:
            if past_gw['round'] == gw:
                return past_gw['value']

        return self.player_json['history'][0]['value']

    def format_as_request_pick(self, placement, is_captain, is_vice_captain):
        return {
            'element': self.id,
            'position': placement,
            'is_captain': is_captain,
            'is_vice_captain': is_vice_captain
        }
