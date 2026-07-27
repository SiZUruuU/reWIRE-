import random

class BreakdownComponent:
    def __init__(self, wear_per_cycle=6, break_chance_base=0.0015, break_chance_per_wear=0.00015, full_break_chance=0.00030):
        self.wear = 0.0
        self.is_broken = False
        self.severity = None

        self.wear_per_cycle = wear_per_cycle
        self.break_chance_base = break_chance_base
        self.break_chance_per_wear = break_chance_per_wear
        self.full_break_chance = full_break_chance
        

    def register_cycle(self):
        if self.is_broken:
            return
        self.wear = min(self.wear + self.wear_per_cycle, 100)
        chance = self.break_chance_base + (self.wear * self.break_chance_per_wear)
        if random.random() < chance:
            self.trigger_breakdown()

    def trigger_breakdown(self):
        self.is_broken = True
        self.severity = "full" if random.random() < self.full_break_chance else "inefficient"

    def repair(self):
        self.is_broken = False
        self.severity = None
        self.wear = 0.0

    @property
    def slowdown_multiplier(self):
        if self.is_broken and self.severity == "inefficient":
            return 2.5
        return 1.0

    @property
    def is_fully_stopped(self):
        return self.is_broken and self.severity == "full"