from ...utils import ResourceType
from .machine import MachineEntity

# this machine receives basic wood or stone
# wood = planks
# stone = stone blocks
class Buzzsaw(MachineEntity):
    def __init__(self, position, direction, world, entity_type):
        super().__init__(position, direction, world, entity_type)
        self.width, self.height = 32, 32
        self.animation_speed = 7.5 # in seconds
        self.recipes = {
            ResourceType.WOOD: {
                "output": ResourceType.BOARDS, "duration": 2.5
            },
            ResourceType.STONE: {
                "output": ResourceType.STONE_BLOCKS, "duration": 4
            }
        }
    
    def update(self, global_time, delta_time, actions):
        super().update(global_time, delta_time, actions)