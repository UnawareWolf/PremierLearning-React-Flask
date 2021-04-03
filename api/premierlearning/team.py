from .team_match import TeamMatch


class Team:

    def __init__(self, team_dict, fixtures_json, last_season_team_standings):
        self.team_dict = team_dict
        self.id = team_dict['id']
        self.name = team_dict['short_name']

        self.last_season_finish = self.find_last_season_finish(last_season_team_standings)

        self.average_points_so_far = 0
        self.average_scored_so_far = 0
        self.average_conceded_so_far = 0

        self.team_match_dict = {}
        self.future_team_match_dict = {}
        self.populate_fixtures(fixtures_json)

        self.strength = {}

        for position in ['attack', 'defence']:
            for location in ['home', 'away']:
                strength_key = 'strength_%s_%s' % (position, location)
                self.strength[strength_key] = team_dict[strength_key]

    def find_last_season_finish(self, last_season_team_standings):
        try:
            place = last_season_team_standings[self.name]
        except:
            place = 21
        return place

    def populate_fixtures(self, fixtures_json):
        for fixture_json in fixtures_json:
            played_home = int(fixture_json['team_h']) == self.id
            if played_home or int(fixture_json['team_a']) == self.id:
                if fixture_json['finished']:
                    self.team_match_dict[int(fixture_json['id'])] = TeamMatch(fixture_json, played_home)
                else:
                    self.future_team_match_dict[int(fixture_json['id'])] = TeamMatch(fixture_json, played_home)

        self.build_snapshot_stats()
        for team_match in self.future_team_match_dict.values():
            team_match.average_scored_in_previous_matches = self.average_scored_so_far
            team_match.average_conceded_in_previous_matches = self.average_conceded_so_far
            team_match.average_points_in_previous_matches = self.average_points_so_far

    def build_snapshot_stats(self):
        match_count = 0
        point_sum_so_far = 0

        scored_so_far = 0
        conceded_so_far = 0
        for match in self.team_match_dict.values():
            match.average_points_in_previous_matches = self.average_points_so_far
            match.average_scored_in_previous_matches = self.average_scored_so_far
            match.average_conceded_in_previous_matches = self.average_conceded_so_far

            match_count += 1
            point_sum_so_far += match.points
            self.average_points_so_far = point_sum_so_far / match_count
            scored_so_far += match.scored
            conceded_so_far += match.conceded
            self.average_scored_so_far = scored_so_far / match_count
            self.average_conceded_so_far = conceded_so_far / match_count

    def __str__(self):
        return self.name
