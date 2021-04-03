class FormattedMatchData:

    def __init__(self, match):
        self.matches_played = match.matches_played

        self.player_average_points = match.average_points_in_previous_matches
        self.player_points_last_5 = match.average_points_last_5
        self.player_points_last_3 = match.average_points_last_3
        self.player_points_last = match.points_last

        self.player_point_deviation = match.player_point_deviation_per_game
        self.ict_point_deviation = match.ict_point_regression_deviation
        self.is_gkp = match.is_gkp
        self.is_def = match.is_def
        self.is_mid = match.is_mid
        self.is_att = match.is_att

        self.is_home = int(self.string_to_bool(match.home))

        self.team_average_points = match.team_match.average_points_in_previous_matches
        self.team_average_scored = match.team_match.average_scored_in_previous_matches
        self.team_average_conceded = match.team_match.average_conceded_in_previous_matches
        self.opponent_average_points = match.opponent_team_match.average_points_in_previous_matches
        self.opponent_average_scored = match.opponent_team_match.average_scored_in_previous_matches
        self.opponent_average_conceded = match.opponent_team_match.average_conceded_in_previous_matches

        self.played_last_season = int(match.player.played_last_season)
        self.last_season_points_per_min = match.player.points_per_min_last_season
        self.team_last_season_finish = match.team.last_season_finish
        self.opponent_last_season_finish = match.opponent_team.last_season_finish

        self.player_points = match.points

        self.input = [self.matches_played, self.player_average_points, self.player_point_deviation,
                      self.player_points_last_5, self.player_points_last_3, self.player_points_last,
                      self.ict_point_deviation, self.is_gkp, self.is_def, self.is_mid, self.is_att,
                      self.is_home, self.team_average_points, self.team_average_scored, self.team_average_conceded,
                      self.opponent_average_points, self.opponent_average_scored, self.opponent_average_conceded,
                      self.team_last_season_finish, self.opponent_last_season_finish, self.played_last_season,
                      self.last_season_points_per_min]

        self.output = [self.player_points]

    @staticmethod
    def string_to_bool(true_or_false):
        if true_or_false == 'True':
            return True
        elif true_or_false == 'False':
            return False
        return true_or_false
