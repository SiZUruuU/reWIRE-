from ...utils import EntityType, ResourceType
from .machine import MachineEntity
from ..resources.resource_data import RESOURCE_DATA
from pygame import Vector2
from component.utils.enums import AudioType, OST, SFX

# This class should not be treated as a machine despite being a child class of
# MachineEntity, placed only by us devs to the world/level's designated selling area

class SellBox(MachineEntity):
    # sell box simply does one thing, accepts resources and convert
    # it into cash value based on the RESOURCE_DATA
    def __init__(self, position, direction, world, entity_type):
        super().__init__(position, direction, world, entity_type)        
        self.recipes = None # recipe must be None
        self.sfx = self.world.game.audio_handler

    def can_accept(self, resource, port="material"):
        if self.input_buffer.get(port) is not None:
            return False
        return True # should accept anything

    def accept(self, resource, tile_x=None, tile_y=None, from_direction=None):
        port = self.get_port(tile_x, tile_y)
        if not self.can_accept(resource, port):
            return False

        self.sfx.play_sfx(AudioType.SFX, SFX.SELL, 1.0)

        value = RESOURCE_DATA.get(resource.resource_type, {}).get("value", 0)
        self.world.earned_cash_today = round(self.world.earned_cash_today + value, 5)

        self.world.particles.emit_burst(
            self.position + Vector2(16, 16),
            color=(80, 220, 100),
            count=14,
            size_range=(2, 5),
            speed_range=(30, 200),
            lifetime_range=(0.25, 1),
        )

        resource.take_resource(self)
        self.world.all_sprites.remove(resource)
        return True

    def update(self, global_time, delta_time, actions):
        self.animate(global_time)
