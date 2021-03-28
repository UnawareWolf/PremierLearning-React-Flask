from .squad import Squad
from persistence import DB_Handler

import json

class OptimiseRunner:

    def __init__(self):
        self.nope = None
        self.squad = None
        
    def run(self):
        
        with open('element_types.json') as f_in:
            elements_dict =  json.load(f_in)

        db_handler = DB_Handler('../database')
        players = db_handler.get_players()
        db_handler.close_connection()

        self.squad = Squad(players, elements_dict, 30)
        self.squad.populate_by_log_in(7414114)
        self.squad.make_sensible_transfers()
    
    def get_a_player(self):
        return str(self.squad.squad[0])
