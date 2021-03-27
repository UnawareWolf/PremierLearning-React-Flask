import sqlite3
from premierlearning import RawMatch
from premierlearning import RawPlayer


class DB_Handler:

    def __init__(self, database_directory):
        self.db_dir = database_directory
        self.connection = sqlite3.connect(self.db_dir + '/fantasy.db')
        self.cursor = self.connection.cursor()
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def run_sql_script(self, path):
        with open(path) as f:
            self.cursor.executescript(f.read())

    def init_db(self):
        self.run_sql_script(self.db_dir + '/drop_tables.sql')
        self.run_sql_script(self.db_dir + '/schema.sql')
    
    def persist_players(self, players):
        for player in players:
            self.persist_player(player)

    def persist_player(self, player):
        self.cursor.execute('''insert into players (id, first_name, surname, team_id, current_cost, position)
            values (?, ?, ?, ?, ?, ?)''', player.format_as_db_insert())
        for match in player.matches:
            self.persist_match(match)
        for future_match in player.future_matches:
            self.persist_future_match(future_match)
    
    def persist_future_match(self, match):
        self.cursor.execute('''insert into future_matches (player_id, minutes, points, gameweek)
            values (?, ?, ?, ?)''', match.format_as_db_insert())
    
    def persist_match(self, match):
        self.cursor.execute('''insert into matches (player_id, minutes, points, gameweek)
            values (?, ?, ?, ?)''', match.format_as_db_insert())

    def get_future_matches(self):
        future_matches = {}
        for db_future_match in self.cursor.execute('select player_id, minutes, points, gameweek from future_matches').fetchall():
            future_match = self.convert_match_from_db(db_future_match)
            if future_match.player_id in future_matches:
                future_matches[future_match.player_id].append(future_match)
            else:
                future_matches[future_match.player_id] = [future_match]
        return future_matches
    
    @staticmethod
    def convert_match_from_db(db_match):
        match = RawMatch()
        match.player_id = db_match[0]
        match.minutes = db_match[1]
        match.points = db_match[2]
        match.gameweek = db_match[3]
        return match

    def get_matches(self):
        matches = {}
        for db_match in self.cursor.execute('select player_id, minutes, points, gameweek from matches').fetchall():
            match = self.convert_match_from_db(db_match)
            if match.player_id in matches:
                matches[match.player_id].append(match)
            else:
                matches[match.player_id] = [match]
        return matches

    def get_players(self):
        players = []
        matches_dict = self.get_matches()
        future_matches_dict = self.get_future_matches()
        for db_player in self.cursor.execute('select id, first_name, surname, team_id, current_cost, position from players').fetchall():
            player = RawPlayer()
            player.id = db_player[0]
            player.first_name = db_player[1]
            player.last_name = db_player[2]
            player.team_id = db_player[3]
            player.current_cost = db_player[4]
            player.position = db_player[5]
            player.matches = matches_dict[player.id]
            player.future_matches = future_matches_dict[player.id]
            players.append(player)
        
        return players
