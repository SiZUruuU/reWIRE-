from ...utils import EntityType, Animation, Direction
from .machine import MachineEntity
from pygame import Vector2

# this machine needs two inputs a fuel source and the processable source
# input1:fuel input2:material = output:metals,glass,charcoal
class Furnace(MachineEntity):
    def __init__(self, position, direction, world, entity_type):
        super().__init__(position, direction, world, entity_type)

    def update(self):
        pass