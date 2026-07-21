from ..entity import BaseEntity
from ...utils import EntityType, Direction, Animation, check_tile_at
from pygame import Vector2

class MachineEntity(BaseEntity):
    def __init__(self, position: Vector2, direction: Vector2, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        self.direction = direction
        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animations = self.world.game.assets[entity_type][Animation.STRAIGHT][dir_key]
        self.image = self.animations[0]
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
        
        # Overrided by sub classes:
        self.input_buffer = {"material": None}
        self.output_buffer = None

        self.recipes = {}
        self.process_time = 0.0
        self.is_processing = False
        self.active_recipe = None
    
    def update(self, global_time, delta_time, actions):
        self.process(delta_time)
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
        input_resource.image = self.world.game.assets[EntityType.RESOURCE][input_resource.resource_type]

        self.output_buffer = input_resource
        self.is_processing = False
        self.process_time = 0.0
        self.active_recipe = None
    
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