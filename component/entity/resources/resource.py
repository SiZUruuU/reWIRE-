from ..entity import BaseEntity
from ...utils import EntityType, ResourceState, check_tile_at
import pygame

class ResourceEntity(BaseEntity):
    def __init__(self, position: pygame.Vector2, world, entity_type: EntityType, resource_type):
        super().__init__(position, world, entity_type)
        self.resource_type = resource_type
        self.direction = pygame.Vector2(0,0)
        self.velocity = pygame.Vector2(0,0)
        self.current_machine = None
        self.state = ResourceState.ON_BELT

        # realign position to match the center of the tile
        offset = world.game.TILE_SIZE/2
        self.position += pygame.Vector2(offset, offset)
        
        self.image = world.game.assets[entity_type][resource_type]        
        self.rect = self.image.get_rect(center=(position.x, position.y))
    
    def update(self, global_time, delta_time, actions):
        if self.state != ResourceState.ON_BELT:
            return
        self.move_on_belt(delta_time)

    def has_space_ahead(self):
        # Use self.direction to check the machine's space infront
        # return False if distance between next resource is small
        pass

    # Methods called by machine:
    def take_resource(self, machine):
        self.current_machine = machine
        self.state = ResourceState.HELD
        self.velocity = pygame.Vector2(0, 0)

    def release(self, position, direction):
        self.current_machine = None
        self.state = ResourceState.ON_BELT
        self.position = position
        self.direction = direction

    def move_on_belt(self, delta_time):
        # check tile on grid:
        tile = check_tile_at(self.position.x, self.position.y, self.world.game, self.world.map.grid)

        # if tile has machine move resource:
        if not tile is None:
            # if there's a new direction snap it to align
            if tile.direction != self.direction:
                if tile.direction.x != 0:
                    self.position.y = tile.position.y + tile.height/2
                if tile.direction.y != 0:
                    self.position.x = tile.position.x + tile.width/2
            self.direction = tile.direction
            self.velocity = self.direction * tile.speed
        else:
            # dampen speed to 0 instead of stopping immediately
            self.velocity.x -= self.velocity.x * 2 * delta_time
            self.velocity.y -= self.velocity.y * 2 * delta_time
        # update positon:
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time
        # update bounding box pos:
        self.rect.center = (round(self.position.x), round(self.position.y))
    