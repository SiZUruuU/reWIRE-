from .map import BaseMap
import pygame

class TestMap(BaseMap):
    def __init__(self, game):
        super().__init__(game)
        self.dark = (90, 100, 130)
        self.light = (115, 130, 170)
        self.rows = 9
        self.cols = 19
    
    # creates a checker platform at the middle of the game world
    def draw(self, display, camera):
        # loops through x and y axis to place tiles
        for i in range(1, self.rows): # y-axis
            for j in range(1, self.cols): # x-axis
                # sets tile color (odd or even) for checkered pattern
                color = self.dark if (i+j) % 2 == 0 else self.light
                # world and screen offset calculation:
                # caclulate offset of each tile
                world_x = j*self.game.TILE_WIDTH
                world_y = i*self.game.TILE_HEIGHT
                # calculate offset of each tile with respect to the camera
                screen_x = world_x - camera.offset.x
                screen_y = world_y - camera.offset.y
                # draw the tile
                pygame.draw.rect(display, color, (screen_x, screen_y, self.game.TILE_WIDTH, self.game.TILE_HEIGHT))
