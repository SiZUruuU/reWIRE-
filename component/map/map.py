from abc import ABC, abstractmethod

from ..utils import EntityType, Animation, Direction
from ..entity import *
from pygame import Vector2

# Dict for corner coords to animation sprite:
CORNER_MAP = {
    # north
    ((0, -1), (-1, 0)): Animation.BOTLEFT,    # Coming from East, turning North
    ((0, -1), (1, 0)):  Animation.BOTRIGHT_F, # Coming from West, turning North
    # south
    ((0, 1), (1, 0)):   Animation.TOPRIGHT,   # Coming from West, turning South
    ((0, 1), (-1, 0)):  Animation.TOPLEFT_F,  # Coming from East, turning South
    # east
    ((1, 0), (0, -1)):  Animation.TOPLEFT,    # Coming from South, turning East
    ((1, 0), (0, 1)):   Animation.BOTLEFT_F,  # Coming from North, turning East
    # west
    ((-1, 0), (0, 1)):  Animation.BOTRIGHT,   # Coming from North, turning West
    ((-1, 0), (0, -1)): Animation.TOPRIGHT_F, # Coming from South, turning West
}
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
    
    def is_tile_valid(self, tile_x, tile_y):
        return 0 <= tile_x < len(self.grid) and 0 <= tile_y < len(self.grid[0])

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

            # conveyor belt realignment of sprite
            if entity_type == EntityType.CONVEYOR:
                # recalculate the layout of the belt we just placed:
                self.belt_neighbor_recalculation(x, y)
                
                # check the tile directly in front of this new belt:
                downstream_x = x + int(direction.x)
                downstream_y = y + int(direction.y)
                self.belt_neighbor_recalculation(downstream_x, downstream_y)

            # tile was placed:
            return True
        # something's blocking the waaaay
        return False

    # change belt based on current neighbor
    def belt_neighbor_recalculation(self, x, y):
        # null check:
        if not self.is_tile_valid(x, y):
            return
        
        # grab the current belt:
        tile = self.grid[x][y]
        if not isinstance(tile, Conveyor):            
            return
        
        # grab its direction:
        tile_dir = (int(tile.direction.x), int(tile.direction.y))
        
        # upstream tile is the neighboring tile
        upstream_tile = None
        # check all neighbors, west, east, north, south:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            # next neighbor to check:
            nx, ny = x + dx, y + dy
            # check if neighbor is a belt"
            if self.is_tile_valid(nx, ny):
                neighbor = self.grid[nx][ny]
                # if it's a belt grab its direction to know where its moving from:
                if isinstance(neighbor, Conveyor):
                    n_dir = (int(neighbor.direction.x), int(neighbor.direction.y))
                    
                    # if the direction it is moving towards is the current belt:
                    if nx + n_dir[0] == x and ny + n_dir[1] == y:
                        # check if the neighbor belt and the current belt is going the same direction:
                        if n_dir == tile_dir:
                            # if it is, it's straight:
                            upstream_tile = neighbor
                            break
                        elif n_dir[0] * tile_dir[0] + n_dir[1] * tile_dir[1] == 0:
                            upstream_tile = neighbor

        # if there's not upstream tile, it's straight:
        if not upstream_tile:
            tile.set_layout(Animation.STRAIGHT, Direction(tile_dir))
            return
        
        up_dir = (int(upstream_tile.direction.x), int(upstream_tile.direction.y))
        dot = tile.direction.dot(upstream_tile.direction)

        if dot == 1:
            tile.set_layout(Animation.STRAIGHT, Direction(tile_dir))
        elif dot == 0:
            corner = CORNER_MAP.get((tile_dir, up_dir))
            if corner:
                tile.set_layout(Animation.CORNER, corner)
            else:
                tile.set_layout(Animation.STRAIGHT, Direction(tile_dir))

    @abstractmethod
    def draw(self, display, camera):
        pass