from ..entity import BaseEntity
from ...utils import EntityType
import pygame

class ResourceEntity(BaseEntity):
    def __init__(self, position: pygame.Vector2, world, entity_type: EntityType, resource_type):
        super().__init__(position, world, entity_type)
        self.resource_type = resource_type
        self.direction = pygame.Vector2(0,0)
        self.current_machine = None

        # realign position to match the center of the tile
        offset = world.game.TILE_SIZE/2
        self.position += pygame.Vector2(offset, offset)        
        self.image = world.game.assets[entity_type][resource_type].copy()    
        self.rect = self.image.get_rect(center=(self.position.x, self.position.y))
    
    def update(self, global_time, delta_time, actions):
        pass

    # Methods called by machine:
    def take_resource(self, machine):
        self.current_machine = machine