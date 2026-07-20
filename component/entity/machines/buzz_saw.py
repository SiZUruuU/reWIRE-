from ...utils import EntityType, Animation, Direction
from .machine import MachineEntity
from pygame import Vector2

# this machine receives basic wood or stone
# wood = planks
# stone = stone blocks
class Buzzsaw(MachineEntity):
    def __init__(self, position, direction, world, entity_type):
        super().__init__(position, direction, world, entity_type)
        # create input and output setups
    
    def update(self):
        pass