import pygame
from . import EntityType

PICKUP_DURATIONS = {
    EntityType.CONVEYOR: 2.0,
    EntityType.BUZZSAW: 5.0,
    EntityType.CRUSHER: 5.0,
    EntityType.FURNACE: 8.5,
    EntityType.WOOD_GENERATOR: 15.0,
    EntityType.STONE_GENERATOR: 15.0,
}
PREP_STAGE_DURATION = 0.5

class PickupManager:
    def __init__(self, world):
        self.world = world
        self.target = None       # entity currently being picked up
        self.progress = 0.0      # seconds held so far
        self.required = 0.0      # duration needed for this entity

    def get_required_duration(self, entity, is_prep_stage):
        if is_prep_stage:
            return PREP_STAGE_DURATION
        return PICKUP_DURATIONS.get(entity.entity_type, 2.0)

    def update(self, delta_time, mouse_tile_x, mouse_tile_y, rmb_held, is_prep_stage):
        entity = None
        if self.world.map.is_tile_valid(mouse_tile_x, mouse_tile_y):
            entity = self.world.map.grid[mouse_tile_x][mouse_tile_y]

        # cancel conditions: button released, moved off target, or tile emptied
        if not rmb_held or entity is not self.target:
            self.target = None
            self.progress = 0.0
            self.required = 0.0

        if not rmb_held:
            return

        if entity is None:
            return

        if self.target is None:
            self.target = entity
            self.progress = 0.0
            self.required = self.get_required_duration(entity, is_prep_stage)

        self.progress += delta_time
        if self.progress >= self.required:
            self.complete_pickup()

    def complete_pickup(self):
        entity = self.target
        covered = getattr(entity, "covered_tiles", [(int(entity.position.x // self.world.game.TILE_SIZE),
                                                       int(entity.position.y // self.world.game.TILE_SIZE))])
        for tx, ty in covered:
            if self.world.map.is_tile_valid(tx, ty):
                self.world.map.grid[tx][ty] = None
        self.world.all_sprites.remove(entity)
        # TODO: return resources to player inventory here, once that system exists
        self.target = None
        self.progress = 0.0
        self.required = 0.0

    @property
    def fill_ratio(self):
        if self.target is None or self.required <= 0:
            return 0.0
        return min(self.progress / self.required, 1.0)

    def draw(self, display, mouse_pos):
        if self.target is None:
            return
        bar_width, bar_height = 40, 6
        x = mouse_pos[0] - bar_width // 2
        y = mouse_pos[1] + 18
        pygame.draw.rect(display, (40, 40, 40), (x, y, bar_width, bar_height))
        pygame.draw.rect(display, (220, 60, 60), (x, y, int(bar_width * self.fill_ratio), bar_height))