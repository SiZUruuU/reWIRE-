import pygame

from .states import State
from ..map.test_map import TestMap
from ..camera import Camera, Follow
from ..entity import Player, TestResource
from ..utils import get_world_mousePos, EntityType

# TESTING FOR FEATURES
class TestWorld(State):
    def __init__(self, game):
        super().__init__(game)

        self.all_sprites = pygame.sprite.Group()        
        self.game = game
        self.map = TestMap(self)

        # initalize the player and camera (with camera type):
        self.player = Player(game.GAME_WIDTH/2, game.GAME_HEIGHT/2, self)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))

        # entity data:
        self.directions = [
                pygame.Vector2(-1, 0),
                pygame.Vector2(0, -1),
                pygame.Vector2(1, 0),
                pygame.Vector2(0, 1)
                           ]
        
        self.dir_index = 0
        self.direction = self.directions[0]

        # entity tracking:        
        self.selected_entity = EntityType.NONE
        # hotbar use keys 1-9
        self.hotbar = [
            EntityType.CONVEYOR,
            EntityType.NONE,
        ]

    def update(self, delta_time, actions):        
        # World related actions:
        self.handle_inputs(actions)        

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
        
        # preview selected item:
        if self.selected_entity != EntityType.NONE:
            mouse = get_world_mousePos(self.game, self.camera)

            preview_x = (mouse['tile_x'] * self.game.TILE_SIZE)

    def handle_inputs(self, actions):                
        mouse = get_world_mousePos(self.game, self.camera)

        # hotbar selection:
        for k in range(len(self.hotbar)):
            key_string = f"key_{k+1}"
            if actions[key_string]:
                self.selected_entity = self.hotbar[k]
                self.game.reset_key(key_string)
                print(f"selected: {self.hotbar[k]}")
            
        # clear selection:
        if actions["key_q"]:
            self.selected_entity = EntityType.NONE
            self.game.reset_key("key_q")
            print("Cleared selection")

        # handle rotation data:
        if actions["key_r"]:
                self.dir_index += 1
                self.dir_index = self.dir_index % 4
                self.direction = self.directions[self.dir_index]
                self.game.reset_key("key_r")

        # handle object placement:
        if actions["LMB"] and self.selected_entity != EntityType.NONE:
            self.map.place_entity(self.selected_entity, mouse['tile_x'], mouse['tile_y'])
            self.game.reset_key("LMB")

        # resource placement test:
        if actions["RMB"]:
            TestResource(mouse['world_x'], mouse['world_y'], self)            
            self.game.reset_key("RMB")