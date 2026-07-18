import pygame
from ..base_entity import BaseEntity

XAXIS = 0
YAXIS = 1

class Belt(BaseEntity):
    def __init__(self, x, y, direction, groups):
        super().__init__(groups)
        self.x, self.y = x, y
        self.width, self.height = 32, 32
        self.direction = direction
            
        self.axis = XAXIS if (direction % 2 == 0) else YAXIS #2 == east && 4 == west

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x,y))

        self.sprite_sheet = "asset/sprites/belt_spritesheet.png"
        self.animations = {}
       
        self.current_frame = 0
        self.animation_speed = .25

        self.load_animations()

        if self.axis == XAXIS:
            if self.direction == 2:
                self.animations[XAXIS] = [pygame.transform.flip(f, True, False) for f in self.animations[XAXIS]]
            else:
                pass

        elif self.axis == YAXIS:
            if self.direction == 3:
                self.animations[YAXIS] = [pygame.transform.flip(f, False, True) for f in self.animations[YAXIS]]
            else:
                pass

    def load_animations(self):
        self.animations[XAXIS] = self.load_frames(self.sprite_sheet, 0, 0, 32, 32, 5)
        self.animations[YAXIS] = self.load_frames(self.sprite_sheet, 0, 64, 32, 32, 5)

    def update(self, global_time, delta_time, actions):
        # update animation
        self.image = self.play_animation(self.axis, global_time)


