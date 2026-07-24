from ...utils import EntityType, Animation, Direction, ResourceType
from .generator import Generator
from pygame import Vector2

FUEL_VALUES = {
    ResourceType.WOOD: 1,
    ResourceType.CHARCOAL: 4
}

# this class is highly similar to furnace but instead of processing it produces
# I should make better classes soon with a better strategy pattern
class StoneGenerator(Generator):
    FOOTPRINT = (2, 2)
    PORT_MAP = {
        (1, 0): {"port": "fuel", "input_direction": (-1, 0)} # top right
    }

    def __init__(self, position, direction, world, generator_type):
        super().__init__(position, direction, world, generator_type)
        self.port_map = self.PORT_MAP
        self.input_buffer = {p["port"]: None for p in self.port_map.values()}
        self.fuel_left = 0
        self.apply_direction(direction)

    def get_port(self, tile_x, tile_y, from_direction=None):        
        if tile_x is None or tile_y is None:
            return next(iter(self.port_map.values()))["port"]

        self_tile_x, self_tile_y = self.world.map.world_to_tile(self.position.x, self.position.y)
        raw_offset = (tile_x - self_tile_x, tile_y - self_tile_y)

        for local_offset, port_data in self.port_map.items():
            rotated_local = self.rotate_footprint_offset(local_offset)
            expected_dir = self.rotate_offset(port_data["input_direction"])
            if rotated_local != raw_offset:
                continue
            if from_direction is not None and tuple(from_direction) != expected_dir:
                continue
            return port_data["port"]
        return None

    def can_accept(self, resource, port):
        if port is None:
            return False
        if self.input_buffer.get(port) is not None:
            return False
        return port == "fuel" and resource.resource_type in FUEL_VALUES

    def accept(self, resource, tile_x=None, tile_y=None, from_direction=None):
        port = self.get_port(tile_x, tile_y, from_direction)
        if not self.can_accept(resource, port):
            return False
        self.input_buffer[port] = resource
        resource.take_resource(self)
        self.fuel_left = FUEL_VALUES[resource.resource_type]
        return True

    def is_full(self, port="fuel"):
        return self.input_buffer.get(port) is not None

    def update(self, global_time, delta_time, actions):
        if self.output_buffer is None and self.input_buffer.get("fuel") is not None:
            self.timer += delta_time
            if self.timer >= self.cooldown:
                self.timer = 0.0
                self.generate()
        self.try_release()
        self.animate(global_time)

    def generate(self):
        had_output_before = self.output_buffer
        super().generate()
        if had_output_before is None and self.output_buffer is not None:
            self.consume_fuel()

    def consume_fuel(self):
        self.fuel_left -= 1
        if self.fuel_left <= 0:
            fuel = self.input_buffer.get("fuel")
            self.input_buffer["fuel"] = None
            if fuel is not None:
                self.world.all_sprites.remove(fuel)

    def apply_direction(self, direction):
        self.direction = direction
        self.output_position = self.get_output_position()
        dir_key = Direction((int(direction.x), int(direction.y)))
        self.rotated_inactive = self.world.game.assets[self.entity_type][Animation.STRAIGHT][dir_key]
        self.rotated_active = self.world.game.assets[self.entity_type][Animation.ACTIVE][dir_key]
        self.image = self.rotated_inactive[0]

    def animate(self, global_time):
        frames = self.rotated_active if self.input_buffer.get("fuel") is not None else self.rotated_inactive
        total = len(frames)
        frame_index = int(global_time * self.animation_speed) % total
        self.image = frames[frame_index]

        if not self.world.is_prep_stage and self.output_buffer is None and self.input_buffer.get("fuel") is not None:
            self.apply_shake(self.position, self.timer, self.cooldown, max_intensity=1.0)
        else:
            self.rect.topleft = (int(self.position.x), int(self.position.y))