from abc import ABC, abstractmethod
from ..utils import EntityType
import pygame

# ABSTRACT CLASS FOR ENTITIES
class BaseEntity(ABC, pygame.sprite.Sprite):
    def __init__(self, position, world, entity_type: EntityType):
        # weird bug I found, so to fix layering we need to set the ._layer first
        # before doing super().__init__()
        self._layer = entity_type.layer
        super().__init__(world.all_sprites)
        self.entity_type = entity_type
        self.position = position
        self.world = world

        # Default values, override if you want to
        self.image = pygame.Surface((world.game.TILE_SIZE, world.game.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
        
        self.animations = {}
        self.current_frame = 0
        self.animation_speed = 0
        
    @abstractmethod
    def update(self, global_time, delta_time, actions):
        pass

    def play_animation(self, global_time):
        total = len(self.animations)
        frame = int(global_time * self.animation_speed) % total
        self.image = self.animations[frame]
    
    def get_frame_animation(self, state, global_time):
        list = self.animations[state]
        total = len(list)
        frame = int(global_time * self.animation_speed) % total        
        return list[frame]