import pygame
from .states import State as Base
from ..map.test_map import TestMap
from ..camera import Camera, Follow
from ..entity import Player, Belt
from ..utils import get_world_mousePos

# Direction enums
# class Direction:
#     #Changed enum value to ints
#     #W/ the idea to increment when rotating 
#     NORTH = 1
#     SOUTH = 3
#     EAST = 2
#     WEST = 4

# TESTING FOR FEATURES
class TestWorld(Base):
    def __init__(self, game):
        # intialize using the parent __init__
        super().__init__(game)
        # create sprite group
        self.all_sprites = pygame.sprite.Group()
        # initalize the map
        self.game = game
        self.map = TestMap(game, self.all_sprites)
        # initalize the player and camera (with camera type)
        self.player = Player(game.GAME_WIDTH/2, game.GAME_HEIGHT/2, self.all_sprites)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))
        self.direction = 2

    def update(self, delta_time, actions):        
        # convert mouse coords to world coords:
        mouse = get_world_mousePos(self.game, self.camera)
        if actions["r_key"]:
                print("R key response")
                if self.direction < 4:
                    self.direction += 1
                elif self.direction == 4:
                    self.direction = 1
                print(f"New dir: {self.direction}")
                self.game.reset_keys("r_key")

        # handle object placement
        if actions["LMB"]:
            if self.map.is_tile_free(mouse['tile_x'], mouse['tile_y']):
                entity = Belt(mouse['world_x'], mouse['world_y'], self.direction, self.all_sprites)
                self.map.add_entity(entity, mouse['tile_x'], mouse['tile_y'])
                self.game.reset_keys("LMB")
                # print(f"Tile free, placed entity at x:{mouse['world_x']} y:{mouse['world_y']}")
            else:
                pass
                # print("Tile obstructed")

        # update all sprites in this world:
        self.all_sprites.update(self.game.global_time, delta_time, actions)
        self.camera.scroll(delta_time)        

    def render(self, display):
        display.fill((50, 60, 90))
        # render the map:
        self.map.draw(display, self.camera)
        # render all sprites in this world:
        for sprite in self.all_sprites:
            display.blit(sprite.image, (sprite.rect.x - self.camera.offset.x, sprite.rect.y - self.camera.offset.y))
