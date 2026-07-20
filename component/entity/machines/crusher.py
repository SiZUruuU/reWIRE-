from ...utils import EntityType, Animation, Direction
from .machine import MachineEntity
from pygame import Vector2

# this machine breaks down stone to make sand
# input:stone = output:sand
class Crusher(MachineEntity):
    def __init__(self, position, direction, world, entity_type):
        super().__init__(position, direction, world, entity_type)
    
    def update(self):
        pass