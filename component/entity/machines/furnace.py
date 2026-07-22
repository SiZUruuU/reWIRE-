from ...utils import ResourceType, EntityType, Animation, Layers, Direction
from .machine import MachineEntity
from pygame import Vector2

# this machine needs two inputs a fuel source and the processable source
# input1:fuel input2:material = output:metals,glass,charcoal

FUEL_VALUES = {
    ResourceType.WOOD: 1,
    ResourceType.CHARCOAL: 4
}

class Furnace(MachineEntity):
    # important! when making machines that are bigger than 1x1, make sure
    # to create the footprint here before passing to __init__
    FOOTPRINT = (1, 2)
    PORT_MAP = {
        (0, 0): "fuel",
        (0, 1): "material",        
    }
    OUTPUT_OFFSET = (0, 1)

    def __init__(self, position, direction, world, entity_type):       
        super().__init__(position, direction, world, entity_type)
        self.footprint = self.FOOTPRINT
        self.width, self.height = 32, 64
        self.animation_speed = 2.5 # in seconds
        self.entry = self.entry + Vector2(0, self.world.game.TILE_SIZE/2)
        self.exit = self.exit + Vector2(0, self.world.game.TILE_SIZE/2)

        self.input_buffer = {
            "fuel": None, "material": None
        }
        self.fuel_left = 0

        self.recipes = {
            ResourceType.WOOD : {
                "output": ResourceType.CHARCOAL, "duration": 4.0
            },
            ResourceType.SAND : {
                "output": ResourceType.GLASS, "duration": 6.0
            }
        }

        dir_key = Direction((int(direction.x), int(direction.y)))
        self.animations = {
            Animation.INACTIVE: world.game.assets[EntityType.FURNACE][Animation.STRAIGHT][dir_key],
            Animation.ACTIVE: world.game.assets[EntityType.FURNACE][Animation.ACTIVE][dir_key]
        }         
        self.image = self.animations[Animation.INACTIVE][0]
    
    def can_accept(self, resource, port):
        if self.input_buffer.get(port) is not None:
            return False
        if port == "fuel":
            return resource.resource_type in FUEL_VALUES
        return resource.resource_type in self.recipes
    
    def accept(self, resource, tile_x=None, tile_y=None):
        port = self.get_port(tile_x, tile_y)
        print(f"ACCEPT: resource={resource.resource_type} tile=({tile_x},{tile_y}) resolved_port={port} can_accept={self.can_accept(resource, port)}")
        if not self.can_accept(resource, port):
            return False
        self.input_buffer[port] = resource
        resource.take_resource(self)
        if port == "fuel":
            self.fuel_left = FUEL_VALUES[resource.resource_type]
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

        # furnace specific: fuel
        fuel = self.input_buffer.get("fuel")        
        material = self.input_buffer.get("material")
        if fuel is None or material is None or self.output_buffer is not None:
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

        # furnace specific stuff
        self.fuel_left -= 1
        if self.fuel_left <= 0:
            fuel = self.input_buffer["fuel"]
            self.input_buffer["fuel"] = None
            if fuel is not None:
                self.world.all_sprites.remove(fuel)

        self.output_buffer = input_resource
        self.is_processing = False
        self.process_time = 0.0
        self.active_recipe = None
    
    def animate(self, global_time):
        state = Animation.ACTIVE if self.input_buffer.get("fuel") is not None else Animation.INACTIVE
        self.image = self.get_frame_animation(state, global_time)