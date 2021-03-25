import sqlite3


class DB_Handler:

    def __init__(self):
        self.connection = sqlite3.connect('database/fantasy.db')
        self.cursor = self.connection.cursor()
    
    def close_connection(self):
        self.connection.close()

    def run_sql_script(self, path):
        with open(path) as f:
            self.cursor.executescript(f.read())

    def initialise_db(self):
        self.run_sql_script('database/drop_tables.sql')
        self.run_sql_script('database/schema.sql')
    
    def persist_player(self, player):
        self.cursor.execute('insert into players values (?, ?, ?)', (player['id'], player['name'], player['team_id']))

    def get_players(self):
        players = []
        for player in self.cursor.execute('select id, name, team_id from players').fetchall():
            players.append({'id': player[0], 'name': player[1], 'team_id': player[2]})
        return players
