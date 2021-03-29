import requests
import itertools
import math

from pulp import LpMaximize, LpProblem, lpSum, LpVariable, PULP_CBC_CMD

from premierlearning import Transfer
from premierlearning import RawPlayer
from .logged_in_action_performer import pick_team, get_player_ids, make_transfers

MANAGER_API = 'https://fantasy.premierleague.com/api/entry/%i/'
MANAGER_PICKS_API = 'https://fantasy.premierleague.com/api/entry/%i/event/%i/picks/'
MANAGER_TRANSFERS_API = 'https://fantasy.premierleague.com/api/entry/%i/transfers/'
MANAGER_GAMEWEEK_API = 'https://fantasy.premierleague.com/api/entry/%i/history/'
BUDGET = 1000
MAX_PLAYERS_PER_TEAM = 3


class Squad:

    def __init__(self, players, element_types, next_gameweek):
        self.squad = []
        self.starters = []
        self.bench = []
        self.next_gameweek = next_gameweek
        self.next_week_projected_points = 0
        self.captain = None
        self.vice_captain = None
        self.element_types = element_types
        self.player_dict = {}
        self.wrapped_player_dict = {}
        self.budget = BUDGET
        self.spent = 0
        self.free_transfers = 0
        self.transfers_done = []
        self.future_starting_teams = {}
        self.bank = 0
        self.manager_id = 0

        self.bench_boost_gw = 0
        self.free_hit_gw = 0

        self.populate_player_dict(players)
        self.populate_wrapped_player_dict(players)
        self.username = None
        self.password = None

    def populate_by_log_in(self, manager_id, username, password):
        self.username = username
        self.password = password
        self.manager_id = manager_id
        manager_json = requests.get(MANAGER_API % manager_id).json()

        manager_picks_json = get_player_ids(self.manager_id, self.username, self.password).json()

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

    def populate_from_manager_id(self, manager_id):
        self.manager_id = manager_id
        manager_json = requests.get(MANAGER_API % manager_id).json()
        last_gameweek = manager_json['current_event']

        manager_picks_json = requests.get(MANAGER_PICKS_API % (manager_id, last_gameweek)).json()

        manager_transfers = requests.get(MANAGER_TRANSFERS_API % manager_id).json()
        manager_gameweeks = requests.get(MANAGER_GAMEWEEK_API % manager_id).json()

        try:
            self.budget = manager_json['last_deadline_value'] + manager_json['last_deadline_bank']
            self.bank = manager_json['last_deadline_bank']
        except:
            pass

        self.free_transfers = self.get_manager_free_transfers(manager_gameweeks)

        self.squad.clear()
        squad_ids = []
        for element in manager_picks_json['picks']:
            squad_ids.append(element['element'])

        self.populate_squad(squad_ids)

        self.budget = self.bank

        for player in self.squad:
            purchase_price = self.get_purchase_price(player, manager_transfers, manager_json['started_event'])
            wrapped_player = WrappedPlayer(player, purchase_price)
            self.wrapped_player_dict[player.id] = wrapped_player
            self.budget += wrapped_player.selling_price

    @staticmethod
    def get_purchase_price(player, manager_transfers, first_gw):
        purchase_price = None
        for transfer in manager_transfers:
            if transfer['element_in'] == player.id:
                purchase_price = transfer['element_in_cost']

        if purchase_price is not None:
            return purchase_price
        return player.get_price_at_gw(first_gw)

    @staticmethod
    def get_manager_free_transfers(manager_gameweeks):
        free_transfers = 0
        for gameweek in manager_gameweeks['current']:
            free_transfers = Squad.get_free_transfers_next_week(free_transfers, gameweek['event_transfers'])
        return free_transfers

    @staticmethod
    def get_free_transfers_next_week(current_free_transfers, transfers_made):
        if transfers_made == 0:
            current_free_transfers += 1
        elif transfers_made >= 2:
            current_free_transfers = 1
        if current_free_transfers >= 2:
            current_free_transfers = 2
        return current_free_transfers

    def build_from_scratch(self):
        squad_ids = self.get_optimised_squad_ids(self.next_gameweek, self.next_gameweek + 5, 15)

        self.populate_squad(squad_ids)

    def populate_player_dict(self, players):
        for player in players:
            self.player_dict[player.id] = player

    def populate_wrapped_player_dict(self, players):
        for player in players:
            self.wrapped_player_dict[player.id] = WrappedPlayer(player, player.current_cost)

    def get_optimised_squad_ids(self, gameweek_from, gameweek_to, allowed_transfers):
        squad_keys = set(player.id for player in self.squad)

        starters_model = LpProblem(name="optimise-squad", sense=LpMaximize)

        valid_player_ids = list(i for i in self.wrapped_player_dict.keys())

        x = {i: LpVariable(name=f"x_{i}", cat="Binary") for i in valid_player_ids}
        y1 = {i: LpVariable(name=f"y1_{i}", cat="Binary") for i in valid_player_ids}
        y2 = {i: LpVariable(name=f"y2_{i}", cat="Binary") for i in valid_player_ids}
        y3 = {i: LpVariable(name=f"y3_{i}", cat="Binary") for i in valid_player_ids}
        z = {i: LpVariable(name=f"z_{i}", cat="Binary") for i in valid_player_ids}

        # Constraint for budget
        starters_model += (lpSum(x[i] * self.wrapped_player_dict[i].selling_price +
                                 y1[i] * self.wrapped_player_dict[i].selling_price +
                                 y2[i] * self.wrapped_player_dict[i].selling_price +
                                 y3[i] * self.wrapped_player_dict[i].selling_price +
                                 z[i] * self.wrapped_player_dict[i].selling_price
                                 for i in valid_player_ids) <= self.budget, "starters_budget")

        # Constraint for squad size
        starters_model += (lpSum(x.values()) == 11, "starters_size")
        starters_model += (lpSum(y1.values()) == 1, "bench_size_1")
        starters_model += (lpSum(y2.values()) == 1, "bench_size_2")
        starters_model += (lpSum(y3.values()) == 1, "bench_size_3")
        starters_model += (lpSum(z.values()) == 1, "bench_keeper_size")

        # Constraint for no duplicate players
        for i in valid_player_ids:
            starters_model += lpSum(x[i] + y1[i] + y2[i] + y3[i] + z[i]) <= 1

        # Constraints for number of players per team
        for team_no in range(1, 21):
            starters_model += lpSum(x[i] * int(self.wrapped_player_dict[i].player.team_id == team_no) +
                                    y1[i] * int(self.wrapped_player_dict[i].player.team_id == team_no) +
                                    y2[i] * int(self.wrapped_player_dict[i].player.team_id == team_no) +
                                    y3[i] * int(self.wrapped_player_dict[i].player.team_id == team_no) +
                                    z[i] * int(self.wrapped_player_dict[i].player.team_id == team_no)
                                    for i in valid_player_ids) <= MAX_PLAYERS_PER_TEAM

        # Constraints for number of players per position
        for element_type in self.element_types:
            starters_model += lpSum(x[i] * int(self.wrapped_player_dict[i].player.position == element_type['id']) +
                                    y1[i] * int(self.wrapped_player_dict[i].player.position == element_type['id']) +
                                    y2[i] * int(self.wrapped_player_dict[i].player.position == element_type['id']) +
                                    y3[i] * int(self.wrapped_player_dict[i].player.position == element_type['id']) +
                                    z[i] * int(self.wrapped_player_dict[i].player.position == element_type['id'])
                                    for i in valid_player_ids) <= element_type['squad_select']

        starters_model += lpSum(y1[i] * int(self.wrapped_player_dict[i].player.position == 1) +
                                y2[i] * int(self.wrapped_player_dict[i].player.position == 1) +
                                y3[i] * int(self.wrapped_player_dict[i].player.position == 1)
                                for i in valid_player_ids) == 0
        starters_model += lpSum(z[i] * int(self.wrapped_player_dict[i].player.position == 1)
                                for i in valid_player_ids) == 1

        # Constrain transfer cap
        starters_model += (lpSum(x[i] * int(i in squad_keys) +
                                 y1[i] * int(i in squad_keys) +
                                 y2[i] * int(i in squad_keys) +
                                 y3[i] * int(i in squad_keys) +
                                 z[i] * int(i in squad_keys)
                                 for i in valid_player_ids) >= 15 - allowed_transfers, "number_of_transfers")

        # Objective function
        starters_model += lpSum(
            x[i] * self.wrapped_player_dict[i].player
            .get_points_between_gameweeks(gameweek_from, gameweek_to, 1, self.bench_boost_gw, self.free_hit_gw)
            + y1[i] * self.wrapped_player_dict[i].player
            .get_points_between_gameweeks(gameweek_from, gameweek_to, 0.4, self.bench_boost_gw, self.free_hit_gw)
            + y2[i] * self.wrapped_player_dict[i].player
            .get_points_between_gameweeks(gameweek_from, gameweek_to, 0.14, self.bench_boost_gw, self.free_hit_gw)
            + y3[i] * self.wrapped_player_dict[i].player
            .get_points_between_gameweeks(gameweek_from, gameweek_to, 0.05, self.bench_boost_gw, self.free_hit_gw)
            + z[i] * self.wrapped_player_dict[i].player
            .get_points_between_gameweeks(gameweek_from, gameweek_to, 0.05, self.bench_boost_gw, self.free_hit_gw)
            for i in valid_player_ids)

        starters_model.solve(PULP_CBC_CMD(msg=0))
        return self.get_player_ids_from_solved_model(starters_model)

    @staticmethod
    def get_player_ids_from_solved_model(model):
        ids = []
        for var in model.variables():
            if var.value() == 1:
                ids.append(int(var.name.split('_')[1]))
                # ids.append(int(var.name[1:]))
        return ids

    def populate_squad(self, player_ids):
        self.squad.clear()
        self.starters.clear()
        self.bench.clear()
        self.spent = 0

        for player_id in player_ids:
            player = self.player_dict[player_id]
            self.squad.append(player)
            self.spent += player.current_cost

        self.squad.sort(key=lambda footballer: footballer.position)

        self.populate_future_starting_teams(5)

    @staticmethod
    def get_bench_ids(player_ids, starter_ids):
        # return list(player.id for player in self.squad if player.id not in starter_ids)
        return list(i for i in player_ids if i not in starter_ids)

    def populate_future_starting_teams(self, weeks_ahead):
        for i in range(weeks_ahead):
            gameweek = self.next_gameweek + i
            player_ids = self.get_player_ids()
            starter_ids = self.pick_starting_team(player_ids, gameweek)

            self.future_starting_teams[gameweek] = StartingSquad(self.player_dict, starter_ids,
                                                                 self.get_bench_ids(player_ids, starter_ids), gameweek)

    def get_starting_squad(self, player_ids, gameweek):
        starter_ids = self.pick_starting_team(player_ids, gameweek)
        return StartingSquad(self.player_dict, starter_ids, self.get_bench_ids(player_ids, starter_ids), gameweek)

    def predict_points_in_gameweek(self, gameweek):
        player_ids = self.get_player_ids()
        starter_ids = self.pick_starting_team(player_ids, gameweek)
        starting_squad = StartingSquad(self.player_dict, starter_ids, self.get_bench_ids(player_ids, starter_ids),
                                       gameweek)
        return starting_squad.points

    def pick_starting_team(self, squad_ids, gameweek):
        pick_starting_lineup_model = LpProblem(name="optimise-squad", sense=LpMaximize)

        # squad_ids = set()
        # for player in self.squad:
        #     squad_ids.add(player.id)

        x = {i: LpVariable(name=f"x_{i}", cat="Binary") for i in squad_ids}

        # Constraint for starting team size
        pick_starting_lineup_model += (lpSum(x.values()) == 11, "squad_size")

        # Constraints for number of players per position
        for element_type in self.element_types:
            pick_starting_lineup_model += lpSum(x[i] * int(self.player_dict[i].position == element_type['id'])
                                                for i in squad_ids) >= element_type['squad_min_play']
            pick_starting_lineup_model += lpSum(x[i] * int(self.player_dict[i].position == element_type['id'])
                                                for i in squad_ids) <= element_type['squad_max_play']

        # Objective function
        pick_starting_lineup_model += lpSum(x[i] * self.player_dict[i].get_points_in_gameweek_n(gameweek, 1, 0, 0)
                                            # * int(self.player_dict[i].get_recent_game_minutes() > 150)
                                            for i in squad_ids)

        pick_starting_lineup_model.solve(PULP_CBC_CMD(msg=0))

        self.next_week_projected_points = 0

        return self.get_player_ids_from_solved_model(pick_starting_lineup_model)

    def get_suggested_transfers(self, max_transfers):
        new_ids = self.get_optimised_squad_ids(self.next_gameweek, self.next_gameweek + 5, max_transfers)

        squad_keys = self.get_player_ids()

        players_in = list(self.wrapped_player_dict[i] for i in new_ids if i not in squad_keys)
        players_in.sort(key=lambda player_: (player_.player.position, player_.purchase_price))
        players_out = list(self.wrapped_player_dict[i] for i in squad_keys if i not in new_ids)
        players_out.sort(key=lambda player_: (player_.player.position, player_.selling_price))
        assert len(players_in) == len(players_out)

        suggested_transfers = []
        for i in range(len(players_in)):
            suggested_transfers.append(Transfer(players_out[i], players_in[i]))

        return suggested_transfers

    # def make_transfers(self, transfer_count):
    #     new_ids = self.get_optimised_squad_ids(self.next_gameweek, self.next_gameweek + 5, transfer_count)
    #
    #     squad_keys = set()
    #     for player in self.squad:
    #         squad_keys.add(player.id)
    #
    #     players_in = list(self.player_dict[i] for i in new_ids if i not in squad_keys)
    #     players_in.sort(key=lambda player_: player_.position)
    #     players_out = list(self.player_dict[i] for i in squad_keys if i not in new_ids)
    #     players_out.sort(key=lambda player_: player_.position)
    #
    #     assert len(players_in) == len(players_out)
    #
    #     for i in range(len(players_in)):
    #         self.transfers_done.append(Transfer(players_out[i], players_in[i]))
    #
    #     self.populate_squad(new_ids)

    def make_sensible_transfers(self):
        best_five_transfers = self.get_suggested_transfers(5)
        strategy = None
        if len(best_five_transfers) > 0:
            no_hit_strategy = self.get_transfer_strategy(self.free_transfers, best_five_transfers)
            one_hit_strategy = self.get_transfer_strategy(self.free_transfers + 1, best_five_transfers)
            two_hit_strategy = self.get_transfer_strategy(self.free_transfers + 2, best_five_transfers)

            # a = self.get_accurate_points_for_strategy(no_hit_strategy)
            # b = self.get_accurate_points_for_strategy(one_hit_strategy)
            # c = self.get_accurate_points_for_strategy(two_hit_strategy)

            # print()

            strategy = no_hit_strategy
            # suggested_transfers = self.get_transfer_strategy(2, best_five_transfers)
            #
            # for transfer in suggested_transfers:
            #     self.make_transfer(transfer)
        return strategy

    def get_accurate_points_for_strategy(self, transfer_strategy):
        gameweek = self.next_gameweek
        player_ids = self.get_player_ids()
        transfer_list = list(transfer_strategy['transfer_tuple'])
        starting_teams = []
        for transfer_count in transfer_strategy['scheme']:
            transfers_this_week = transfer_list[:transfer_count]
            del transfer_list[:transfer_count]
            for transfer in transfers_this_week:
                player_ids.remove(transfer.player_out.id)
                player_ids.append(transfer.player_in.id)
            starting_teams.append(self.get_starting_squad(player_ids, gameweek))
            gameweek += 1
        return sum(starting_team.points for starting_team in starting_teams)

    def get_transfer_strategy(self, free_transfers, suggested_transfers):
        transfer_schemes = {}
        temp_free_transfers = free_transfers
        scheme_id = 0
        for combination in itertools.product(*list([0, 1, 2, 3] for _ in range(4))):
            valid_scheme = True
            for transfer_count in combination:
                if transfer_count > temp_free_transfers:
                    valid_scheme = False
                    break
                temp_free_transfers = self.get_free_transfers_next_week(temp_free_transfers, transfer_count)

            temp_free_transfers = free_transfers
            if valid_scheme:
                total_transfers = sum(combination)
                transfer_tuple_id_dict = {}
                transfer_tuple_id = 0
                for transfer_tuple in itertools.permutations(suggested_transfers, r=total_transfers):
                    transfer_tuple_id_dict[transfer_tuple_id] = {'transfer_tuple': transfer_tuple, 'points': 0}
                    transfer_tuple_id += 1
                transfer_schemes[scheme_id] = {'scheme': combination, 'transfers': transfer_tuple_id_dict}
                scheme_id += 1

        transfer_dict_list = []
        for scheme in transfer_schemes.values():
            transfers_list = scheme['transfers']
            for transfer_dict in transfers_list.values():
                transfer_dict['points'] = self.get_points_from_players_and_transfer_strategy(
                    list(self.squad), scheme['scheme'], transfer_dict['transfer_tuple'])
                transfer_dict['scheme'] = scheme['scheme']
                transfer_dict_list.append(transfer_dict)
        transfer_dict_list.sort(key=lambda transfer_plan: transfer_plan['points'], reverse=True)
        return transfer_dict_list[0]
        # print()

    @staticmethod
    def static_do_transfers(squad, transfers):
        for transfer in transfers:
            squad.remove(transfer.player_out)
            squad.append(transfer.player_in)
        return squad

    @staticmethod
    def team_numbers_are_valid(players):
        team_counts = {}
        for player in players:
            if player.team_id not in team_counts.keys():
                team_counts[player.team_id] = 1
            else:
                team_counts[player.team_id] += 1

        for i in team_counts.values():
            if i > 3:
                return False
        return True

    @staticmethod
    def transfers_within_budget(transfers, budget):
        net_cost = budget
        for transfer in transfers:
            net_cost += transfer.get_net_value()
        return net_cost >= 0

    @staticmethod
    def squad_is_valid(players):
        return Squad.team_numbers_are_valid(players)

    def get_points_from_players_and_transfer_strategy(self, players, transfer_scheme, transfer_tuple):
        gameweek = self.next_gameweek
        points = 0
        current_squad = players
        transfer_list = list(transfer_tuple)
        temp_budget = self.bank
        for transfer_count in transfer_scheme:
            transfers_this_week = transfer_list[:transfer_count]
            del transfer_list[:transfer_count]
            if not self.transfers_within_budget(transfers_this_week, temp_budget):
                points = 0
                break
            current_squad = self.static_do_transfers(current_squad, transfers_this_week)
            for transfer in transfers_this_week:
                temp_budget += transfer.get_net_value()
            if not self.squad_is_valid(current_squad):
                points = 0
                break
            for player in current_squad:
                points += player.get_points_in_gameweek_n(gameweek, 1, self.bench_boost_gw, self.free_hit_gw)
            gameweek += 1
        return points

    def make_transfers(self, max_transfers):
        suggested_transfers = self.get_suggested_transfers(max_transfers)
        for transfer in suggested_transfers:
            self.make_transfer(transfer)

    def make_transfer(self, transfer):
        squad_keys = self.get_player_ids()
        squad_keys.remove(transfer.player_out.id)
        squad_keys.append(transfer.player_in.id)
        self.transfers_done.append(transfer)
        self.populate_squad(squad_keys)

    def get_player_ids(self):
        return list(player.id for player in self.squad)

    @staticmethod
    def transfers_made(old_squad_ids, new_squad_ids):
        return sum(list(1 for _ in new_squad_ids if _ not in old_squad_ids))

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

    def log_in_and_pick_team(self):
        request_payload = self.pick_team_request_format()
        pick_team(self.manager_id, request_payload, self.username, self.password)

    def format_transfer_requests(self):
        request_payload = {
            'chips': None,
            'entry': self.manager_id,
            'event': self.next_gameweek,
            'transfers': []
        }
        for transfer in self.transfers_done:
            request_payload['transfers'].append(transfer.format_as_request())

        return request_payload

    def log_in_and_make_transfers(self):
        request_payload = self.format_transfer_requests()
        make_transfers(request_payload, self.username, self.password)
        self.transfers_done.clear()


class WrappedPlayer:

    def __init__(self, player: RawPlayer, purchase_price):
        self.player = player
        self.purchase_price = purchase_price
        self.selling_price = self.get_selling_price()

    def get_selling_price(self):
        price_change = self.player.current_cost - self.purchase_price
        if price_change <= 0:
            return self.player.current_cost

        return self.purchase_price + math.floor(price_change / 2)


class StartingSquad:

    def __init__(self, player_dict, starter_ids, bench_ids, gameweek):
        self.gameweek = gameweek
        self.players = list(player_dict[i] for i in starter_ids)
        self.players.sort(key=lambda player_: player_.get_points_in_gameweek_n(gameweek, 1, 0, 0), reverse=True)

        self.points = 0
        self.captain = self.players[0]
        self.vice_captain = self.players[1]

        self.players.sort(key=lambda player_: player_.position)
        for player in self.players:
            player_points = player.get_points_in_gameweek_n(gameweek, 1, 0, 0)
            self.points += player_points

        self.points += self.captain.get_points_in_gameweek_n(gameweek, 1, 0, 0)

        self.bench = list(player_dict[i] for i in bench_ids if player_dict[i].position != 1)
        bench_keeper = next(player_dict[i] for i in bench_ids if player_dict[i].position == 1)
        self.bench.sort(key=lambda player_: player_.get_points_in_gameweek_n(gameweek, 1, 0, 0), reverse=True)
        self.bench.insert(0, bench_keeper)

    def __str__(self):
        return 'gameweek: %i points: %.2f' % (self.gameweek, self.points)
