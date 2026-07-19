from ..base import BaseEntity
from ...utils import EntityType
import pygame

class ResourceEntity(BaseEntity):
    def __init__(self, position, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        self.direction = pygame.Vector2(0,0)
        self.velocity = pygame.Vector2(0,0)
        self.current_machine = None
    
    def update(self):
        pass