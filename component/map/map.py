from abc import ABC, abstractmethod

class BaseMap(ABC):
    def __init__(self, game, group, width, height):
        self.game = game
        # sprite groups for this world:
        self.all_sprites = group
        # create base empty world map:
        # this is used for tracking which tile is occupied 
        self.grid = [[None for _ in range(height)] for _ in range(width)]

    def is_tile_free(self, tile_x, tile_y):
        # boundary check:
        if 0 <= tile_x < len(self.grid) and 0 <= tile_y < len(self.grid[0]):
            # if tile[x][y] is None then return True
            # if tile[x][y] has value it would return False
            return self.grid[tile_x][tile_y] is None
        # boundary check fail:
        return False

    def add_entity(self, entity, x, y):
        # check if grid is free:
        if self.is_tile_free(x, y):
            self.grid[x][y] = entity
            # tile was placed:
            return True
        # something's blocking the waaaay:
        return False

    @abstractmethod
    def draw(self, display, camera):
        pass
