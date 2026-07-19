from abc import ABC, abstractmethod
import pygame

# ABSTRACT CLASS FOR ENTITIES
class BaseEntity(ABC, pygame.sprite.Sprite):
    def __init__(self, world):
        super().__init__(world.all_sprites)
        self.world = world
        self.direction = 0
        self.animations = {}
        self.current_frame = 0
        self.animation_speed = .25
        
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