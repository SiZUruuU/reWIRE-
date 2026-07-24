from ...utils import EntityType, Animation, Direction, check_tile_at
from ..resources.resource import ResourceEntity
from ..entity import BaseEntity
from .generator_data import GENERATOR_DATA
from pygame import Vector2

# Since generators are all the same, difference are same data name with different values,
# We will make a single class to create all the kinds of generators
# Note: unique generators with fuel ports must be created seperately
# this generator class is only for basic generators that produces resources in a
# constant rate
class Generator(BaseEntity):
    def __init__(self, position, direction, world, generator_type):
        super().__init__(position, world, EntityType.GENERATOR)
        self.direction = direction
        self.entity_type = generator_type

        data = GENERATOR_DATA[generator_type]
        self.resource_type = data["resource_type"]
        self.cooldown = data["cooldown"]
        self.footprint = data["footprint"]
        self.output_offset = data.get("output_offset", (0, 0))
        self.output_position = self.get_output_position()

        self.timer = 0.0
        self.output_buffer = None

        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animation_speed = 10.0
        self.animations = world.game.assets[generator_type][Animation.STRAIGHT][dir_key]
        self.image = self.animations[0]
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, global_time, delta_time, actions):
        if self.world.is_prep_stage:
            self.animate(global_time)
            return
        if self.output_buffer is None:
            self.timer += delta_time
            if self.timer >= self.cooldown:
                self.timer = 0.0
                self.generate()
        self.try_release()
        self.animate(global_time)  

    def generate(self):
        output_position = self.output_position
        infront = check_tile_at(output_position.x, output_position.y, self.world.game, self.world.map)
        if infront is None:
            return

        tile_x, tile_y = self.world.map.world_to_tile(output_position.x, output_position.y)

        if hasattr(infront, "get_port"):
            port = infront.get_port(tile_x, tile_y, self.direction)
            if port is None or infront.is_full(port):
                return
        else:
            if infront.is_full():
                return

        self.output_buffer = ResourceEntity(self.position.copy(), self.world, self.resource_type)

    def try_release(self):
        if self.output_buffer is None:
            return
        output_position = self.output_position
        infront = check_tile_at(output_position.x, output_position.y, self.world.game, self.world.map)
        if infront is None:
            return
        tile_x, tile_y = self.world.map.world_to_tile(output_position.x, output_position.y)
        if infront.accept(self.output_buffer, tile_x, tile_y, self.direction):
            self.output_buffer = None

    def animate(self, global_time):
        if not self.world.is_prep_stage and self.output_buffer is None:
            elapsed = self.timer
            self.apply_shake(self.position, elapsed, self.cooldown, max_intensity=0.5)
        else:
            self.rect.topleft = (int(self.position.x), int(self.position.y))

        self.image = self.get_frame_animation(None, global_time)

    def apply_direction(self, direction):
        self.direction = direction
        self.output_position = self.get_output_position()

    def is_full(self, port=None):
        return self.output_buffer is not None

    def accept(self, resource, tile_x=None, tile_y=None, from_direction=None):
        return False    

def get_generator_class(generator_type):
    data = GENERATOR_DATA[generator_type]

    class _Generator(Generator):

        FOOTPRINT = data["footprint"]

        def __init__(self, position, direction, world, generator_type):
            super().__init__(position, direction, world, generator_type)

    _Generator.__name__ = f"Generator_{generator_type}"
    return _Generator