import requests

from .squad import AbstractSquad, MANAGER_API
from .logged_in_action_performer import get_manager_id, get_player_ids, make_transfers

class UserSquad(AbstractSquad):

    def __init__(self, email, password, players, element_types):
        super().__init__(players, element_types)
        self.email = email
        self.password = password
        self.manager_id = get_manager_id(self.email, self.password)
        self.populate_by_log_in()

    def populate_by_log_in(self):
        manager_json = requests.get(MANAGER_API % self.manager_id).json()

        manager_picks_json = get_player_ids(self.email, self.password).json()

        try:
            self.budget = manager_json['last_deadline_value'] + manager_json['last_deadline_bank']
            self.bank = manager_json['last_deadline_bank']
        except:
            pass

        self.free_transfers = manager_picks_json['transfers']['limit']
        if self.free_transfers is None:
            self.free_transfers = 15

        self.squad.clear()
        squad_ids = []
        for element in manager_picks_json['picks']:
            squad_ids.append(element['element'])

        self.populate_squad(squad_ids)

        self.bank = manager_picks_json['transfers']['bank']
        self.budget = self.bank

        for element in manager_picks_json['picks']:
            player_id = element['element']
            wrapped_player = self.wrapped_player_dict[player_id]
            wrapped_player.purchase_price = element['purchase_price']
            wrapped_player.selling_price = element['selling_price']
            self.budget += wrapped_player.selling_price

    def pick_team_request_format(self):
        starting_team = self.future_starting_teams[self.next_gameweek]
        captain = starting_team.captain
        vice_captain = starting_team.vice_captain

        picks = {}
        placement = 1
        for player in starting_team.players:
            if player.id not in picks:
                picks[player.id] = player.format_as_request_pick(placement, False, False)
            placement += 1

        picks[captain.id]['is_captain'] = True
        picks[vice_captain.id]['is_vice_captain'] = True

        for player in starting_team.bench:
            picks[player.id] = player.format_as_request_pick(placement, False, False)
            placement += 1

        return {'chip': None, 'picks': list(picks.values())}

    def format_transfer_requests(self):
        request_payload = {
            'chips': None,
            'entry': self.manager_id,
            'event': self.next_gameweek,
            'transfers': []
        }
        for transfer in self.staged_transfers:
            request_payload['transfers'].append(transfer.format_as_request())

        return request_payload

    def log_in_and_make_transfers(self):
        request_payload = self.format_transfer_requests()
        make_transfers(request_payload, self.email, self.password)
        self.staged_transfers.clear()
