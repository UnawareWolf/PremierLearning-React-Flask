class TeamMatch:

    def __init__(self, fixture_json, home):
        self.fixture_json = fixture_json
        self.id = self.fixture_json['id']
        self.home = home
        home_away_code = self.HomeAwayChar(home)
        try:
            self.scored = int(self.get_goals_scored(home_away_code.code))
            self.conceded = int(self.get_goals_scored(home_away_code.opponent))
            self.won = self.scored > self.conceded
            self.lost = self.conceded > self.scored
            self.drew = self.scored == self.conceded
            self.points = self.get_points()
        except:
            self.scored = 0
            self.conceded = 0
            self.won = False
            self.lost = False
            self.drew = False
            self.points = 0

        self.average_scored_in_previous_matches = 0
        self.average_conceded_in_previous_matches = 0
        self.average_points_in_previous_matches = 0

    def get_goals_scored(self, h_or_a):
        return self.fixture_json['team_%s_score' % h_or_a]

    def get_points(self):
        points = 0
        if self.drew:
            points = 1
        elif self.won:
            points = 3
        return points

    class HomeAwayChar:
        def __init__(self, home):
            if home:
                self.code = 'h'
                self.opponent = 'a'
            else:
                self.code = 'a'
                self.opponent = 'h'
