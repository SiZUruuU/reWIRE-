from ...utils import ResourceType
from .machine import MachineEntity

# this machine breaks down stone to make sand
# input:stone = output:sand
class Crusher(MachineEntity):
    def __init__(self, position, direction, world, entity_type):
        super().__init__(position, direction, world, entity_type)
        self.width, self.height = 32, 32            
        self.animation_speed = 10 # in seconds
        self.recipes = {
            ResourceType.STONE: {
                "output": ResourceType.SAND, "duration": 3.75
            },
        }
    
    def update(self, global_time, delta_time, actions):
        super().update(global_time, delta_time, actions)