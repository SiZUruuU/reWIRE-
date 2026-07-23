from ...utils import EntityType, check_tile_at
from .machine import MachineEntity
from pygame import Vector2

class Conveyor(MachineEntity):
    def __init__(self, position: Vector2, direction: Vector2, world, entity_type: EntityType):
        super().__init__(position, direction, world, entity_type)
        self.animation_speed = 7.5 # in seconds
        self.speed = 20

        self.items = []
        self.min_gap = 0.3
        
        self.apply_direction(direction)

    def update(self, global_time, delta_time, actions):
        self.animate(global_time)
        self.move_items(delta_time)
        
    def move_items(self, delta_time):
        step = (self.speed * delta_time) / self.world.game.TILE_SIZE

        for i, item in enumerate(self.items):
            limit = 1.0 if i == 0 else self.items[i - 1]["progress"] - self.min_gap
            item["progress"] = min(item["progress"] + step, max(item["progress"], limit))
            self.sync_position(item)
        
        if self.items and self.items[0]["progress"] >= 1.0:
            self.try_pass()
    
    def sync_position(self, item):
        position = self.entry.lerp(self.exit, item["progress"])
        item["resource"].position = position
        item["resource"].rect.center = (round(position.x), round(position.y))
        item["resource"].direction = self.direction

    def try_pass(self):
        head = self.items[0]
        offset_point = self.exit + self.direction * 1
        size = self.world.game.TILE_SIZE
        tile_x = int(offset_point.x // size)
        tile_y = int(offset_point.y // size)
        next = check_tile_at(
            offset_point.x, offset_point.y,
            self.world.game, self.world.map.grid
        )
        if next is None:
            return
        if next.accept(head["resource"], tile_x, tile_y):
            self.items.pop(0)
    
    def accept(self, resource, tile_x=None, tile_y=None):
        if self.items and self.items[-1]["progress"] < self.min_gap:
            return False
        item = {
            "resource": resource,
            "progress": 0.0
        }
        self.items.append(item)
        resource.take_resource(self)
        self.sync_position(item)
        return True
    
    def apply_corner(self, incoming_direction, outgoing_direction):
        self.direction = outgoing_direction
        size = self.world.game.TILE_SIZE
        center = self.position + Vector2(size/2, size/2)
        self.entry = center - incoming_direction * (size/2)
        self.exit = center + outgoing_direction * (size/2)

    def apply_direction(self, direction):
        self.apply_corner(direction, direction)

    def is_full(self):
        return bool(self.items) and self.items[-1]["progress"] < self.min_gap