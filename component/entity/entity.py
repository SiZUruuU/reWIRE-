from abc import ABC, abstractmethod
from ..utils import EntityType
import pygame

# ABSTRACT CLASS FOR ENTITIES
class BaseEntity(ABC, pygame.sprite.Sprite):
    def __init__(self, position: pygame.Vector2, world, entity_type: EntityType):
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

    def get_frame_animation(self, state, global_time):
        # checks if there's only one animation type:
        if state is None:
            total = len(self.animations)
            frame = int(global_time * self.animation_speed) % total
            return self.animations[frame]
        else:
            frames = self.animations[state]
            total = len(frames)
            frame = int(global_time * self.animation_speed) % total
            return frames[frame]


    def set_layout(self, animation_type, key):
        self.animations = self.world.game.assets[self.entity_type][animation_type][key]
        self.image = self.animations[0]