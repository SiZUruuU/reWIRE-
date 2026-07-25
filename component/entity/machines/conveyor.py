from ...utils import EntityType, check_tile_at
from .machine import MachineEntity
from pygame import Vector2
from .breakdown import BreakdownComponent
from .breakdown import BreakdownComponent

class Conveyor(MachineEntity):
    def __init__(self, position: Vector2, direction: Vector2, world, entity_type: EntityType):
        super().__init__(position, direction, world, entity_type)
        self.animation_speed = 7.5 # in seconds
        self.speed = 20

        self.items = []
        self.min_gap = 0.3

        # override with lower chances
        self.breakdown = BreakdownComponent(
            wear_per_cycle=2,
            break_chance_base=0.005,
            break_chance_per_wear=0.0005,
            full_break_chance=0.0005
        )
        self.apply_direction(direction)

    def update(self, global_time, delta_time, actions):
        self.animate(global_time)
        if self.world.is_prep_stage or self.world.day_over:
            return
        if self.breakdown.is_fully_stopped:
            return
        if self.breakdown.is_fully_stopped:
            return
        self.move_items(delta_time)
        
    def move_items(self, delta_time):
        effective_speed = self.speed / self.breakdown.slowdown_multiplier
        step = (effective_speed * delta_time) / self.world.game.TILE_SIZE
        effective_speed = self.speed / self.breakdown.slowdown_multiplier
        step = (effective_speed * delta_time) / self.world.game.TILE_SIZE

        for i, item in enumerate(self.items):
            limit = 1.0 if i == 0 else self.items[i - 1]["progress"] - self.min_gap
            item["progress"] = min(item["progress"] + step, max(item["progress"], limit))
            self.sync_position(item)
        if self.items and self.items[0]["progress"] >= 1.0:
            self.try_pass()

    def get_port(self, tile_x, tile_y, from_direction=None):
        if from_direction is not None and tuple(from_direction) == tuple(-self.direction):
            return None
        return "material"
    
    def sync_position(self, item):
        position = self.entry.lerp(self.exit, item["progress"])
        item["resource"].position = position
        item["resource"].rect.center = (round(position.x), round(position.y))
        item["resource"].direction = self.direction

    def try_pass(self):
        head = self.items[0]
        offset_point = self.exit + self.direction * 1
        tile_x, tile_y = self.world.map.world_to_tile(offset_point.x, offset_point.y)
        next = check_tile_at(offset_point.x, offset_point.y, self.world.game, self.world.map)
        next = check_tile_at(offset_point.x, offset_point.y, self.world.game, self.world.map)
        if next is None:
            return
        if next.accept(head["resource"], tile_x, tile_y, self.direction):
            self.items.pop(0)
            self.breakdown.register_cycle()
            self.breakdown.register_cycle()
        
    def accept(self, resource, tile_x=None, tile_y=None, from_direction=None):
        if from_direction is not None and tuple(from_direction) == tuple(-self.direction):
            return False
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
        self.incoming_direction = Vector2(incoming_direction)
        size = self.world.game.TILE_SIZE
        center = self.position + Vector2(size/2, size/2)
        self.entry = center - incoming_direction * (size/2)
        self.exit = center + outgoing_direction * (size/2)

    def apply_direction(self, direction):
        self.apply_corner(direction, direction)

    def is_full(self, port=None):
        return bool(self.items) and self.items[-1]["progress"] < self.min_gap