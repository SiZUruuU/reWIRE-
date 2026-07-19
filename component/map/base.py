from abc import ABC, abstractmethod
from ..utils import EntityType
from ..entity import *
from pygame import Vector2

# ABSTRACT CLASS FOR MAPS:
class BaseMap(ABC):
    ENTITY = {
        EntityType.CONVEYOR : Conveyor
    }

    def __init__(self, width, height, world):
        self.world = world
        # sprite groups for this world:
        self.all_sprites = world.all_sprites
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

    def place_entity(self, grid: Vector2, direction: Vector2, entity_type: EntityType):
        # check if grid is free:
        x, y = int(grid.x), int(grid.y)
        if self.is_tile_free(x, y):
            self.grid[x][y] = self.ENTITY[entity_type](
                grid * self.world.game.TILE_SIZE, # revert index back to world coordinates
                direction,
                self.world,
                entity_type
            )
            # tile was placed:
            return True
        # something's blocking the waaaay:
        return False

    @abstractmethod
    def draw(self, display, camera):
        pass
