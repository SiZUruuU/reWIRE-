import pygame

from ...utils import check_tile_at, EntityType
from .resource import ResourceEntity

class TestResource(ResourceEntity):
    def __init__(self, position, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        offset = world.game.TILE_SIZE/2
        self.position += pygame.Vector2(offset, offset)

        self.image = pygame.Surface((16, 16))
        self.image.fill((100, 255, 100))
        self.rect = self.image.get_rect(center=(position.x, position.y))

    def update(self, global_time, delta_time, actions):
        # check tile on grid:
        tile = check_tile_at(self.position.x, self.position.y, self.world.game, self.world.map.grid)

        # if tile has machine move resource:
        if not tile is None:
            # if there's a new direction snap it to align
            if tile.direction != self.direction:
                #tile_x = self.position.x//self.world.game.TILE_SIZE * self.world.game.TILE_SIZE
                #tile_y = self.position.y//self.world.game.TILE_SIZE * self.world.game.TILE_SIZE

                if tile.direction.x != 0:
                    self.position.y = tile.position.y + tile.width/2
                if tile.direction.y != 0:
                    self.position.x = tile.position.x + tile.height/2
            self.direction = tile.direction
            self.velocity = self.direction * tile.speed
        else:
            # dampen speed to 0 instead of stopping immediately
            self.velocity.x -= self.velocity.x * 2 * delta_time
            self.velocity.y -= self.velocity.y * 2 * delta_time
        # update positon:
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time
        # update bounding box pos:
        self.rect.center = (round(self.position.x), round(self.position.y))

    def load_animations(self):
        return super().load_animations()
