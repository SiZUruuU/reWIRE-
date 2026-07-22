from utils import EntityType, check_tile_at
from ..resources.resource import ResourceEntity
from entity import BaseEntity
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

        self.image = world.game.assets[EntityType.GENERATOR][generator_type]

    def update(self, global_time, delta_time, actions):
        if self.output_buffer is None:
            self.timer += delta_time
            if self.timer >= self.cooldown:
                self.timer = 0.0
                self.generate()
        self.try_release()

    def generate(self):
        size = self.world.game.TILE_SIZE
        spawn_position = self.position + Vector2(size/2, size/2)
        self.output_buffer = ResourceEntity(
            spawn_position, self.world, EntityType.RESOURCE, self.resource_type
        )

    def try_release(self):
        if self.output_buffer is None:
            return

        output_positon = self.position + self.direction * self.world.game.TILE_SIZE
        infront = check_tile_at(output_positon.x, output_positon.y, self.world, self.world.map.grid)
        if infront is None:
            return
        if infront.accept(self.output_buffer):
            self.output_buffer = None

    def apply_direction(self, direction):
        self.direction = direction