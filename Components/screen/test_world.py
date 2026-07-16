from .states import State as Base
from Components.map.test_map import TestMap
from Components.entity.camera import *
from Components.entity.player.player import Player

# TESTING FOR FEATURES
class TestWorld(Base):
    def __init__(self, game):
        # intialize using the parent __init__
        super().__init__(game)
        # initalize the map
        self.map = TestMap(game)
        self.player = Player(game.GAME_WIDTH/2, game.GAME_HEIGHT/2, game.all_sprites)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))

    def update(self, delta_time, actions):
        self.game.all_sprites.update(delta_time, actions)
        self.camera.scroll()
        self.game.reset_keys()

    def render(self, display):
        display.fill((50, 60, 90))
        self.map.draw(display, self.camera)
        for sprite in self.game.all_sprites:
            display.blit(sprite.image, (sprite.rect.x - self.camera.offset.x, sprite.rect.y - self.camera.offset.y))