class Transfer:

    def __init__(self, player_out, player_in):
        self.player_out = player_out.player
        self.player_in = player_in.player
        self.purchase_price = int(player_in.purchase_price)
        self.selling_price = int(player_out.selling_price)

    def get_net_value(self):
        return self.selling_price - self.purchase_price

    def get_net_points(self):
        return self.player_in.points_over_next_5_gameweeks - self.player_out.points_over_next_5_gameweeks

    def is_possible(self, current_squad, bank):
        return self.does_not_violate_team_constraints(current_squad) and self.is_within_budget(bank)

    def does_not_violate_team_constraints(self, current_squad):
        return True

    def is_within_budget(self, bank):
        return self.get_net_value() + bank >= 0

    def __str__(self):
        return str(self.player_out) + " -> " + str(self.player_in)

    def format_as_request(self):
        return {
            'element_in': self.player_in.id,
            'element_out': self.player_out.id,
            'purchase_price': self.purchase_price,
            'selling_price': self.selling_price
        }
