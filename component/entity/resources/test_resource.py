import pygame

from ...utils.coordinates import check_tile_at

from ..base_entity import BaseEntity

class TestResource(BaseEntity):
    def __init__(self, x, y, world):
        super().__init__(world)
        self.x = x
        self.y = y

        self.direction = pygame.Vector2(0,0)
        self.velocity = pygame.Vector2(0,0)

        self.image = pygame.Surface((16, 16))
        self.image.fill((100, 255, 100))

        self.rect = self.image.get_rect(topleft=(x,y))

    def update(self, global_time, delta_time, actions):
        # check tile on grid:
        centerx = self.x + (self.rect.width/2)
        centery = self.y + (self.rect.height/2)
        tile = check_tile_at(centerx, centery, self.world.game, self.world.map.grid)

        # if tile has machine move resource:
        if not tile is None:
            # if there's a new direction snap it to align
            if tile.direction != self.direction:
                tile_x = self.x//self.world.game.TILE_SIZE * self.world.game.TILE_SIZE 
                tile_y = self.y//self.world.game.TILE_SIZE * self.world.game.TILE_SIZE

                if tile.direction.x != 0:
                    self.y = tile_y + self.world.game.TILE_SIZE/2 - self.rect.height/2
                if tile.direction.y != 0:
                    self.x = tile_x + self.world.game.TILE_SIZE/2 - self.rect.width/2
            self.direction = tile.direction
            self.velocity = self.direction * tile.speed
        else:
            self.velocity.x -= self.velocity.x * 2 * delta_time
            self.velocity.y -= self.velocity.y * 2 * delta_time
        
        self.x += self.velocity.x * delta_time
        self.y += self.velocity.y * delta_time

        self.rect.topleft = (round(self.x), round(self.y))

    def load_animations(self):
        return super().load_animations()
