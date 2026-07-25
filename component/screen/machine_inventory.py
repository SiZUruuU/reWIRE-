class MachineInventory:
    def __init__(self, counts=None):
        # counts: {EntityType: int}
        self.counts = counts if counts is not None else {}

    def add(self, entity_type, amount=1):
        self.counts[entity_type] = self.counts.get(entity_type, 0) + amount

    def remove(self, entity_type, amount=1):
        current = self.counts.get(entity_type, 0)
        if current < amount:
            return False
        self.counts[entity_type] = current - amount
        return True

    def get_count(self, entity_type):
        return self.counts.get(entity_type, 0)

    def has(self, entity_type):
        return self.get_count(entity_type) > 0

    def reset(self):
        self.counts = {et: 0 for et in self.counts}