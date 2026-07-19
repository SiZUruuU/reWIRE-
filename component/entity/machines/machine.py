from ..base import BaseEntity
from ...utils import EntityType
from pygame import Vector2

class MachineEntity(BaseEntity):
    def __init__(self, position: Vector2, direction: Vector2, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        self.direction = direction
        self.input_buffer = []
        self.output_buffer = []
    
    def update(self):
        pass