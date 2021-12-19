import sqlite3

from flask import g

from premierlearning import RawMatch
from premierlearning import RawPlayer

DATABASE = '../database/fantasy.db'
DROP = '../database/drop_tables.sql'
SCHEMA = '../database/schema.sql'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class DB_Handler:

    def __init__(self):
        self.connection = get_db()
        self.cursor = self.connection.cursor()
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def run_sql_script(self, path):
        with open(path) as f:
            self.cursor.executescript(f.read())

    def init_db(self):
        self.run_sql_script(DROP)
        self.run_sql_script(SCHEMA)
    
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
    
    def add_match_to_dict(self, matches_dict, match, player_id):
        if match['gameweek'] is None:
            match['gameweek'] = 0
        if player_id not in matches_dict:
            matches_dict[player_id] = {match['gameweek']: [match]}
        else:
            if match['gameweek'] not in matches_dict[player_id]:
                matches_dict[player_id][match['gameweek']] = [match]
            else:
                matches_dict[player_id][match['gameweek']].append(match)

    def get_future_match_jsons(self):
        future_matches = {}
        for db_future_match in self.cursor.execute('select player_id, minutes, points, gameweek from future_matches').fetchall():
            player_id = db_future_match[0]
            future_match = {
                'minutes': db_future_match[1],
                'points': db_future_match[2],
                'gameweek': db_future_match[3]
            }
            self.add_match_to_dict(future_matches, future_match, player_id)
        return future_matches

    @staticmethod
    def convert_match_from_json(player_id, match_json):
        match = RawMatch()
        match.player_id = player_id
        match.minutes = match_json['minutes']
        match.points = match_json['points']
        match.gameweek = match_json['gameweek']
        return match
    
    def get_match_jsons(self):
        matches = {}
        for db_match in self.cursor.execute('select player_id, minutes, points, gameweek from matches').fetchall():
            player_id = db_match[0]
            match = {
                'minutes': db_match[1],
                'points': db_match[2],
                'gameweek': db_match[3]
            }
            self.add_match_to_dict(matches, match, player_id)
        return matches

    def get_player_jsons(self):
        players = {}
        matches = self.get_match_jsons()
        future_matches = self.get_future_match_jsons()
        for db_player in self.cursor.execute('select id, first_name, surname, team_id, current_cost, position from players').fetchall():
            player_id = db_player[0]
            player_matches = {}
            if player_id in matches:
                player_matches = matches[player_id]
            player = {
                'id': player_id,
                'first_name': db_player[1],
                'last_name': db_player[2],
                'team_id': db_player[3],
                'current_cost': db_player[4],
                'position': db_player[5],
                'matches': player_matches,
                'future_matches': future_matches[player_id]
            }
            players[player_id] = player
        return players

    def get_player_objects(self):
        players = {}
        player_jsons = self.get_player_jsons()
        for player_id, player_json in player_jsons.items():
            player = RawPlayer()
            player.id = player_id
            player.first_name = player_json['first_name']
            player.last_name = player_json['last_name']
            player.team_id = player_json['team_id']
            player.current_cost = player_json['current_cost']
            player.position = player_json['position']
            matches = []

            for gameweek, match_jsons in player_json['matches'].items():
                for match_json in match_jsons:
                    matches.append(self.convert_match_from_json(player_id, match_json))
            player.matches = matches
            future_matches = []

            for gameweek, future_match_jsons in player_json['future_matches'].items():
                for future_match_json in future_match_jsons:
                    future_matches.append(self.convert_match_from_json(player_id, future_match_json))
            player.future_matches = future_matches
            players[player_id] = player
        return players
