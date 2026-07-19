import pygame
from ..base_entity import BaseEntity
from ...utils import EntityType, Animation, Direction

class Conveyor(BaseEntity):
    def __init__(self, x, y, direction, world):
        super().__init__(world)
        self.x, self.y = x, y
        self.width, self.height = 32, 32
        self.direction = direction
        self.speed = 20

        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animations = world.game.assets[EntityType.CONVEYOR][Animation.STRAIGHT][dir_key]

        self.image = self.animations[0]
        self.rect = self.image.get_rect(topleft=(x,y))
       
        self.animation_speed = 7.5

    def update(self, global_time, delta_time, actions):
        # update animation
        self.play_animation(global_time)


