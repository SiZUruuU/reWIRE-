import pygame

from ...utils import EntityType
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
        self.belt_movement()

    def load_animations(self):
        return super().load_animations()
