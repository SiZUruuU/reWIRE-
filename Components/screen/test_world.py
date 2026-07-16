from .states import State as Base
import pygame

# TESTING FOR FEATURES
class TestWorld(Base):
    def __init__(self, game):
        # intialize using the parent __init__
        Base.__init__(self, game)
    
    def update(self, delta_time, actions):
        self.game.reset_keys()

    def render(self, display):
        display.fill((50, 60, 90))
        self.test_platform(display)

    # creates a checker platform at the middle of the game world
    def test_platform(self, display):
        dark = (90, 100, 130)
        light = (115, 130, 170)
        color = ()
        # loops through x and y
        for i in range(1,9): # y-axis
            for j in range(1,19): # x-axis
                # check to assign tile color to achieve checker pattern
                if i % 2 == 0:
                    if j % 2 == 0:
                        color = dark
                    else:
                        color = light
                else:
                    if j % 2 == 0:
                        color = light
                    else:
                        color = dark
                # draw rect based on i and j as offset
                pygame.draw.rect(display, color, (j*self.game.TILE_WIDTH, i*self.game.TILE_HEIGHT, self.game.TILE_WIDTH, self.game.TILE_HEIGHT))