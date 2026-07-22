from ...utils import EntityType, ResourceType
from .machine import MachineEntity
from ..resources.resource_data import RESOURCE_DATA

# This class should not be treated as a machine despite being a child class of
# MachineEntity, placed only by us devs to the world/level's designated selling area

class SellBox(MachineEntity):
    # sell box simply does one thing, accepts resources and convert
    # it into cash value based on the RESOURCE_DATA
    def __init__(self, position, direction, world, entity_type):
        super().__init__(position, direction, world, entity_type)        
        self.recipes = None # recipe must be None

    def can_accept(self, resource, port="material"):
        if self.input_buffer.get(port) is not None:
            return False
        return True # should accept anything

    def accept(self, resource, tile_x=None, tile_y=None):
        port = self.get_port(tile_x, tile_y)
        if not self.can_accept(resource, port):
            return False

        # if there's a resource, get it's value and turn it to cash
        value = RESOURCE_DATA.get(resource.resource_type, {}).get("value", 0)
        self.world.cash += value

        # as any machine entities, we must detach it from where it came
        resource.take_resource(self)
        self.world.all_sprites.remove(resource) # item destroyed
        return True

    def update(self, global_time, delta_time, actions):
        self.animate(global_time)
