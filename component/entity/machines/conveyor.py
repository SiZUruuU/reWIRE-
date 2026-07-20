from ...utils import EntityType, Animation, Direction
from .machine import MachineEntity
from pygame import Vector2

class Conveyor(MachineEntity):
    def __init__(self, position: Vector2, direction: Vector2, world, entity_type: EntityType):
        super().__init__(position, direction, world, entity_type)
        self.width, self.height = 32, 32
        self.direction = direction
        self.speed = 20

        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animations = world.game.assets[EntityType.CONVEYOR][Animation.STRAIGHT][dir_key]

        self.image = self.animations[0]
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
       
        self.animation_speed = 7.5 # in seconds

    def update(self, global_time, delta_time, actions):
        # update animation
        self.image = self.get_frame_animation(None, global_time)