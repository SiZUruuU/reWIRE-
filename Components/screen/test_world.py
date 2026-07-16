from .states import State as Base
import pygame

# TESTING FOR FEATURES
class TestWorld(Base):
    def __init__(self, game):
        # intialize using the parent __init__
        super().__init__(game)
    
    def update(self, delta_time, actions):
        self.game.reset_keys()

    def render(self, display):
        display.fill((50, 60, 90))