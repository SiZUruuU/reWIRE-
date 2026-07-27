from ..entity import BaseEntity
from ...utils import EntityType, Direction, Animation, check_tile_at, Layers
from pygame import Vector2
from .breakdown import BreakdownComponent
from component.utils.enums import AudioType, OST, SFX
from component.utils.audio import AudioComp

class MachineEntity(BaseEntity):
    # important! when making machines that are bigger than 1x1, make sure
    # to create the footprint data here before passing to __init__
    FOOTPRINT = (1, 1)
    # default facing west, material must arrive east
    PORT_MAP = {
        (0, 0): {
            "port": "material",
            "input_direction": (-1, 0)
        }
    }
    OUTPUT_OFFSET = (0, 0)

    def __init__(self, position: Vector2, direction: Vector2, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        self.footprint = self.FOOTPRINT # how much tiles the machine takes up
        self.port_map = self.PORT_MAP
        self.output_offset = self.OUTPUT_OFFSET
        self.sfx = AudioComp(self.world.game)
        self.direction = direction
        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animations = self.world.game.assets[entity_type][Animation.STRAIGHT][dir_key]
        self.image = self.animations[0]
        # footprint width and height
        fw, fh = getattr(self, "footprint", (1, 1))
        # image must be exactly same as footprint        
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
        
        # Overrided by sub classes:
        self.input_buffer = {p["port"]: None for p in self.port_map.values()}
        self.output_buffer = None

        size = self.world.game.TILE_SIZE
        local_entry = (fw, fh / 2)
        local_exit = (0, fh / 2)
        rot_entry = self.rotate_continuous_offset(local_entry)
        rot_exit = self.rotate_continuous_offset(local_exit)
        self.entry = self.position + Vector2(rot_entry[0] * size, rot_entry[1] * size)
        self.exit = self.position + Vector2(rot_exit[0] * size, rot_exit[1] * size)

        self.recipes = {}
        self.process_time = 0.0
        self.is_processing = False
        self.active_recipe = None
        self.breakdown = BreakdownComponent()
    
    def update(self, global_time, delta_time, actions):

        if self.world.is_prep_stage or self.world.day_over:
            self.animate(global_time)
            return
        self.process(delta_time)
        self.sync_resource()
        self.try_release()
        self.animate(global_time)

#    def animate(self, global_time):
#        self.image = self.get_frame_animation(None, global_time)

    def animate(self, global_time):
        if self.breakdown.is_broken:
            self.apply_shake(self.position, global_time % 0.3, 0.3, max_intensity=3.0)
            was_broken = False
            is_currently_broken = bool(self.breakdown.is_broken)

            if is_currently_broken and not was_broken:
                self.world.audio.play_sfx(AudioType.SFX, SFX.MACHINE_BROKEN)

            was_broken = is_currently_broken
        elif self.is_processing and self.active_recipe is not None:
            duration = self.active_recipe["duration"]
            elapsed = duration - self.process_time
            self.apply_shake(self.position, elapsed, duration, max_intensity=0.1)
        else:
            self.rect.topleft = (int(self.position.x), int(self.position.y))

        self.image = self.get_frame_animation(None, global_time)

    def can_accept(self, resource, port="material"):
        if port is None:
            return False
        if self.input_buffer.get(port) is not None:
            return False
        return resource.resource_type in self.recipes

    def accept(self, resource, tile_x=None, tile_y=None, from_direction=None):
        port = self.get_port(tile_x, tile_y, from_direction)
        if not self.can_accept(resource, port):
            return False
        self.input_buffer[port] = resource
        resource.take_resource(self)
        return True

    def process(self, delta_time):
        if self.breakdown.is_fully_stopped:
            return

        if self.is_processing:
            self.process_time -= delta_time
            if self.process_time <= 0.0:
                self.complete_processing()
            return

        material = self.input_buffer.get("material")
        if material is None or self.output_buffer is not None:
            return

        recipe = self.recipes.get(material.resource_type)
        if recipe is None:
            return
        self.active_recipe = recipe
        self.process_time = recipe["duration"] * self.breakdown.slowdown_multiplier
        self.is_processing = True
    
    def complete_processing(self):
        input_resource = self.input_buffer["material"]
        self.input_buffer["material"] = None

        input_resource.resource_type = self.active_recipe["output"]
        input_resource.image = self.world.game.assets[EntityType.RESOURCE][input_resource.resource_type].copy()
        input_resource.image.set_alpha(255)
        self.world.all_sprites.change_layer(input_resource, Layers.FLOOR_1.value)

        self.output_buffer = input_resource
        self.is_processing = False
        self.process_time = 0.0
        self.active_recipe = None
        self.breakdown.register_cycle()
    
    def sync_resource(self):
        resource = self.input_buffer.get("material")
        if resource is None or self.active_recipe is None:
            return
        
        duration = self.active_recipe["duration"]
        progress = 1.0 - (self.process_time / duration) if duration > 0 else 1.0
        progress = max(0.0, min(progress, 1.0))

        size = self.world.game.TILE_SIZE
        position = self.entry.lerp(self.exit, progress)
        resource.rect.center = (round(position.x), round(position.y))

        alpha = int(150 * (1.0 - progress * 0.7))
        self.world.all_sprites.change_layer(resource, Layers.MIDDLE_1.value)
        resource.image.set_alpha(alpha)

    def try_release(self):
        if self.output_buffer is None:
            return
        output_position = self.get_output_position()
        tile_x, tile_y = self.world.map.world_to_tile(output_position.x, output_position.y)
        infront = check_tile_at(
            output_position.x, output_position.y,
            self.world.game, self.world.map
        )
        if infront is None:
            return
        if infront.accept(self.output_buffer, tile_x, tile_y, self.direction):
            self.output_buffer = None

    # new port checking feature for multi port machines:
    # made it support footprint feature
    def get_port(self, tile_x, tile_y, from_direction=None):
        if tile_x is None or tile_y is None:
            return next(iter(self.port_map.values()))["port"]

        self_tile_x, self_tile_y = self.world.map.world_to_tile(self.position.x, self.position.y)
        raw_offset = (tile_x - self_tile_x, tile_y - self_tile_y)

        for local_offset, port_data in self.port_map.items():
            if self.rotate_footprint_offset(local_offset) != raw_offset:
                continue
            expected_dir = self.rotate_offset(port_data["input_direction"])
            if from_direction is not None and tuple(from_direction) != expected_dir:
                continue
            return port_data["port"]
        return None
    
    def apply_direction(self, direction):
        self.direction = direction
        base_frame = self.world.game.assets[self.entity_type][Animation.STRAIGHT][Direction((-1,0))][0]
        self.image = self.get_rotated_image(base_frame, direction)

    def is_full(self, port="material"):
        return self.input_buffer.get(port) is not None