from .squad import Squad
from persistence import DB_Handler

import json

class OptimiseRunner:

    def __init__(self, manager_id, username, password):
        self.nope = None
        self.squad = None
        self.transfers = None
        self.manager_id = manager_id
        self.username = username
        self.password = password
        
    def run(self):
        
        with open('data/element_types.json') as f_in:
            elements_dict =  json.load(f_in)

        db_handler = DB_Handler()
        players = db_handler.get_players()
        db_handler.close_connection()

        self.squad = Squad(players, elements_dict, 30)
        self.squad.populate_by_log_in(self.manager_id, self.username, self.password)
        self.transfers = self.squad.make_sensible_transfers()
    
    def get_transfers(self):
        # transfers_string = ''
        temp_gameweek = self.squad.next_gameweek
        transfer_index = 0
        transfers_dict = {}
        for scheme_entry in self.transfers['scheme']:
            
            # transfers_string += 'gameweek %i transfers:\n' % temp_gameweek
            for _ in range(scheme_entry):
                if temp_gameweek not in transfers_dict:
                    transfers_dict[temp_gameweek] = [str(self.transfers['transfer_tuple'][transfer_index])]
                else:
                    transfers_dict[temp_gameweek].append(str(self.transfers['transfer_tuple'][transfer_index]))
                # transfers_string += '%s\n' % self.transfers['transfer_tuple'][transfer_index]
                transfer_index += 1
            temp_gameweek += 1
            # transfers_string += '\n'
        # return transfers_string
        return transfers_dict
