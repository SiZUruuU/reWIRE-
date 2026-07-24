from .map import BaseMap
from pygame import draw, Surface, SRCALPHA

class FactoryMap(BaseMap):
    def __init__(self, world):
        self.rows = 9
        self.cols = 19
        super().__init__(self.cols, self.rows, world)
        self.dark = (90, 100, 130, 32)
        self.light = (115, 130, 170, 32)
        self.tile_size = self.world.game.TILE_SIZE
        self.grid_width = self.cols * self.tile_size
        self.grid_height = self.rows * self.tile_size
        
        self.origin_x = (self.world.game.GAME_WIDTH - self.grid_width) // 2
        self.origin_y = (self.world.game.GAME_HEIGHT - self.grid_height) // 2

        self.surface = None
        self.pre_render()

    def pre_render(self):
        self.surface = Surface((self.grid_width, self.grid_height), SRCALPHA)
        for i in range(self.rows):
            for j in range(self.cols):
                color = self.dark if (i + j) % 2 == 0 else self.light
                local_x = j * self.tile_size
                local_y = i * self.tile_size
                draw.rect(self.surface, color, (local_x, local_y, self.tile_size, self.tile_size))

    def draw(self, display, camera):
        screen_x = self.origin_x - camera.offset.x
        screen_y = self.origin_y - camera.offset.y
        if self.surface:
            display.blit(self.surface, (screen_x, screen_y))
    
    def world_to_tile(self, world_x, world_y):
        local_x = world_x - self.origin_x
        local_y = world_y - self.origin_y
        return int(local_x // self.tile_size), int(local_y // self.tile_size)
    
    def tile_to_world(self, tile_x, tile_y):
        return (
            self.origin_x + tile_x * self.tile_size,
            self.origin_y + tile_y * self.tile_size
        )