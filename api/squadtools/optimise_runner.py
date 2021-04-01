from .user_squad import UserSquad
from persistence import DB_Handler

import json

class OptimiseRunner:

    def __init__(self, email, password):
        self.nope = None
        self.squad = None
        self.transfers = None
        self.email = email
        self.password = password
        
    def run(self):
        
        with open('data/element_types.json') as f_in:
            elements_dict =  json.load(f_in)

        db_handler = DB_Handler()
        players = db_handler.get_players()
        db_handler.close_connection()

        self.squad = UserSquad(self.email, self.password, players, elements_dict)
        self.transfers = self.squad.make_sensible_transfers()
    
    def get_transfers(self):
        # transfer_list = []
        # for transfer in self.transfers['transfer_tuple']:
        #     transfer_list.append(str(transfer))
        # return transfer_list
        temp_gameweek = self.squad.next_gameweek
        transfer_index = 0
        transfers_list = []
        for scheme_entry in self.transfers['scheme']:
            transfer_gw_dict = {'gameweek': temp_gameweek, 'transfers': [] }
            for _ in range(scheme_entry):
                transfer_gw_dict['transfers'].append(str(self.transfers['transfer_tuple'][transfer_index]))
                transfer_index += 1
            transfers_list.append(transfer_gw_dict)
            temp_gameweek += 1
        return transfers_list
