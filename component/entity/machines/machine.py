from ..entity import BaseEntity
from ...utils import EntityType, Direction, Animation, check_tile_at, Layers
from pygame import Vector2

class MachineEntity(BaseEntity):
    # important! when making machines that are bigger than 1x1, make sure
    # to create the footprint here before passing to __init__
    FOOTPRINT = (1, 1)
    def __init__(self, position: Vector2, direction: Vector2, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        self.footprint = self.FOOTPRINT # how much tiles the machine takes up
        self.direction = direction
        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animations = self.world.game.assets[entity_type][Animation.STRAIGHT][dir_key]
        self.image = self.animations[0]
        # footprint width and height
        fw, fh = getattr(self, "footprint", (1, 1))
        # image must be exactly same as footprint        
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
        
        # Overrided by sub classes:
        self.input_buffer = {"material": None}
        self.output_buffer = None
        
        self.entry = self.position + Vector2(self.width, self.height/2)
        self.exit = self.position + Vector2(0, self.height/2)

        self.recipes = {}
        self.process_time = 0.0
        self.is_processing = False
        self.active_recipe = None
    
    def update(self, global_time, delta_time, actions):
        self.process(delta_time)
        self.sync_resource()
        self.try_release()
        self.animate(global_time)

    def animate(self, global_time):
        self.image = self.get_frame_animation(None, global_time)

    def can_accept(self, resource, port="material"):
        if self.input_buffer.get(port) is not None:
            return False
        return resource.resource_type in self.recipes

    def accept(self, resource, port="material"):
        if not self.can_accept(resource, port):
            return False
        self.input_buffer[port] = resource
        resource.take_resource(self)
        return True

    def process(self, delta_time):
        # if machine's state is currently processing:
        if self.is_processing:
            # starts processing
            self.process_time -= delta_time
            # process finished
            if self.process_time <= 0.0:
                self.complete_processing()
            return

        # check if there's no material to process or is still holding on a material:
        material = self.input_buffer.get("material")
        if material is None or self.output_buffer is not None:
            return
        
        # build the new material:
        recipe = self.recipes.get(material.resource_type)        
        if recipe is None:
            return
        self.active_recipe = recipe
        self.process_time = recipe["duration"]
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
        # if there's nothing to release:
        if self.output_buffer is None:
            return
        # if there is, check if the output tile is open:
        output_position = self.position + self.direction * self.world.game.TILE_SIZE
        infront =  check_tile_at(
            output_position.x, output_position.y, 
            self.world.game, self.world.map.grid
        )
        if infront is None:
            return        
        # if it is, release the BABY:
        if infront.accept(self.output_buffer):
            self.output_buffer = None

    
    def apply_direction(self, direction):
        self.direction = direction
        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animations = self.world.game.assets[self.entity_type][Animation.STRAIGHT][dir_key]
        self.image = self.animations[0]