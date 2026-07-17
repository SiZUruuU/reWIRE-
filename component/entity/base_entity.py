from abc import ABC, abstractmethod
import pygame

# ABSTRACT CLASS FOR ENTITIES
class BaseEntity(ABC, pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.direction = 0
        self.animations = {}
        self.current_frame = 0
        self.frame_duration = 100
        
    @abstractmethod
    def update(self, global_time, delta_time, actions):
        pass

    @abstractmethod
    def load_animations(self):
        pass

    # helper methods
    def load_frames(self, filename, x, y, width, height, amount):
        sprite_sheet = pygame.image.load(filename)
        frames = []
        for i in range(amount):
            frame = sprite_sheet.subsurface(pygame.Rect(x+i*width, y, width, height))
            frames.append(frame)
        return frames

    def play_animation(self, state, time):
        total_frames = len(self.animations[state])
               
        self.current_frame = (time // self.frame_duration) % total_frames
        return self.animations[state][int(self.current_frame)]
