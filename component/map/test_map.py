from .base_map import BaseMap
import pygame

class TestMap(BaseMap):
    def __init__(self, world):
        super().__init__(19, 9, world)
        self.dark = (90, 100, 130)
        self.light = (115, 130, 170)
        self.rows = 9
        self.cols = 19
    
    # creates a checker platform at the middle of the game world
    def draw(self, display, camera):
        # loops through x and y axis to place tiles
        for i in range(0, self.rows): # y-axis
            for j in range(0, self.cols): # x-axis
                # sets tile color (odd or even) for checkered pattern
                color = self.dark if (i+j) % 2 == 0 else self.light
                # world and screen offset calculation:
                # caclulate offset of each tile
                world_x = j*self.world.game.TILE_SIZE
                world_y = i*self.world.game.TILE_SIZE
                # calculate offset of each tile with respect to the camera
                screen_x = world_x - camera.offset.x
                screen_y = world_y - camera.offset.y
                # draw the tile
                pygame.draw.rect(
                    display, color, 
                    (screen_x, screen_y, self.world.game.TILE_SIZE, self.world.game.TILE_SIZE)
                )
