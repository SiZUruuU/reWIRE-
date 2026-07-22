from ...utils import EntityType, Animation, Direction, check_tile_at
from ..resources.resource import ResourceEntity
from ..entity import BaseEntity
from .generator_data import GENERATOR_DATA
from pygame import Vector2

# Since generators are all the same, difference are same data name with different values,
# We will make a single class to create all the kinds of generators
class Generator(BaseEntity):
    def __init__(self, position, direction, world, generator_type):
        super().__init__(position, world, EntityType.GENERATOR)
        self.direction = direction
        self.generator_type = generator_type

        data = GENERATOR_DATA[generator_type]
        self.resource_type = data["resource_type"]
        self.cooldown = data["cooldown"]
        self.footprint = data["footprint"]

        self.timer = 0.0
        self.output_buffer = None

        dir_key = Direction(direction.x, direction.y)
        self.animation_speed = 10.0
        self.animations = world.game.assets[generator_type][Animation.STRAIGHT][dir_key]
        self.image = self.animations[0]
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        print(f"WIDTH:{self.width}, HEIGHT:{self.height}")

    def update(self, global_time, delta_time, actions):
        if self.output_buffer is None:
            self.timer += delta_time
            if self.timer >= self.cooldown:
                self.timer = 0.0
                self.generate()
        self.try_release()
        self.animate(global_time)

    def generate(self):
        spawn_position = self.position
        self.output_buffer = ResourceEntity(
            spawn_position, self.world, self.resource_type
        )

    def try_release(self):
        if self.output_buffer is None:
            return

        output_positon = self.position + self.direction * self.world.game.TILE_SIZE
        infront = check_tile_at(output_positon.x, output_positon.y, self.world.game, self.world.map.grid)
        if infront is None:
            return
        if infront.accept(self.output_buffer):
            self.output_buffer = None

    def animate(self, global_time):
        self.image = self.get_frame_animation(None, global_time)

    def apply_direction(self, direction):
        self.direction = direction