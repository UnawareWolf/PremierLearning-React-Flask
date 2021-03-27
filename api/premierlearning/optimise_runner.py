from .squad import Squad
from .db_handler import DB_Handler

import json

class OptimiseRunner:

    def __init__(self):
        self.nope = None
        
    def run(self):
        
        with open('element_types.json') as f_in:
            elements_dict =  json.load(f_in)

        db_handler = DB_Handler('../database')
        # db_handler.init_db()
        players = db_handler.get_players()
        db_handler.close_connection()

        squad = Squad(players, elements_dict, 30)
        squad.populate_by_log_in(7414114)
        squad.make_sensible_transfers()

        print()
