class Economy:
    def __init__(self, starting_cash=0):
        self.cash = starting_cash
        # resources is basically the things you'd need to build the machines
        self.resources = {}

    def add_cash(self, amount):
        self.cash += amount

    def spend_cash(self, amount):
        if self.cash < amount:
            return False
        self.cash -= amount
        return True

    def add_resource(self, resource_type, amount=1):
        self.resources[resource_type] = self.resources.get(resource_type, 0) + amount

    def get_resource_count(self, resource_type):
        return self.resources.get(resource_type, 0)

    def can_afford(self, recipe):
        # recipe: {resource_type: amount_required}
        return all(self.get_resource_count(rt) >= amt for rt, amt in recipe.items())

    def spend_resources(self, recipe):
        if not self.can_afford(recipe):
            return False
        for rt, amt in recipe.items():
            self.resources[rt] -= amt
        return True