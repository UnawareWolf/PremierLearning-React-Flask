from .user_squad import UserSquad
from persistence import DB_Handler

import json

class OptimiseRunner:

    def __init__(self, user_json):
        self.nope = None
        self.squad = None
        self.transfers = None
        self.csrftoken = None
        self.user_json = user_json
    
    def get_ids(self):
        return self.squad.get_player_ids()

    def populate_squad(self):
        with open('data/element_types.json') as f_in:
            elements_dict = json.load(f_in)

        db_handler = DB_Handler()
        players = db_handler.get_player_objects()
        db_handler.close_connection()

        self.squad = UserSquad(self.user_json, players, elements_dict)
        
    def run(self):
        
        self.populate_squad()
        self.transfers = self.squad.make_sensible_transfers()
    
    def get_transfers(self):
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

    def get_transfers_json(self):
        transfers = {}
        temp_gameweek = self.squad.next_gameweek
        transfer_index = 0
        for scheme_entry in self.transfers['scheme']:
            transfers_this_week = []
            for _ in range(scheme_entry):
                transfers_this_week.append(self.transfers['transfer_tuple'][transfer_index].format_as_json())
                transfer_index += 1
            transfers[temp_gameweek] = transfers_this_week
            temp_gameweek += 1
        return transfers
