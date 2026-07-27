import pygame

from ..entity import BaseEntity
from ..machines.conveyor import Conveyor
from ...utils import EntityType, Animation, Layers, get_world_mousePos
from component.utils.enums import AudioType, OST, SFX
from component.utils.audio import AudioComp

class PlayerEntity(BaseEntity):
    def __init__(self, position, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        self.width, self.height = 64, 64

        self.facing = pygame.Vector2(0, 1)
        # sprite flags
        self.facing_right = False
        self.facing_back = False  

        # animation settings:
        self.animations = {
            Animation.RUN : world.game.assets[EntityType.PLAYER][Animation.RUN],
            Animation.IDLE : world.game.assets[EntityType.PLAYER][Animation.IDLE]
        }
        self.animation_speed = 12
        self.image = self.animations[Animation.RUN][0]
        self.rect = self.image.get_rect(topleft=(self.position.x,self.position.y))
        self.state = Animation.IDLE
        self.held_item = None  

        self.shadow_image = pygame.Surface((30, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_image, (0, 0, 0, 90), self.shadow_image.get_rect())

        # init audio handler
        self.audio_handler = AudioComp(self.world.game)

        # player attributes
        self.speed = 50


    def update(self, global_time, delta_time, actions):
        # input key actions
        self.handle_input(actions)

        # sound effects
        if self.velocity.length_squared() > 0:
            self.audio_handler.play_loop("walk", AudioType.SFX, SFX.WALK)
        else:
            self.audio_handler.stop_loop("walk")

        # update position:
        # added world collision
        new_x = self.position.x + self.velocity.x * delta_time
        new_y = self.position.y + self.velocity.y * delta_time

        # only apply this collision check on factory level
        if self.world.__class__.__name__=="FactoryLevel":
            half_w = self.width / 2
            half_h = self.height / 2

            new_x = max(self.world.bounds_left + half_w, min(new_x, self.world.bounds_right - half_w))
            new_y = max(self.world.bounds_top + half_h, min(new_y, self.world.bounds_bottom - half_h))

        self.position.x = new_x
        self.position.y = new_y

        self.update_state()

        frame = self.get_frame_animation(self.state, global_time)  
        if self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

        # update bounding box:
        self.rect.topleft = (round(self.position.x), round(self.position.y))

        # for holding items
        if self.held_item is not None:
            self.held_item.rect.midbottom = self.rect.midtop
            self.held_item.position = pygame.Vector2(self.held_item.rect.center)

    def update_state(self):
        self.state = Animation.RUN if self.velocity.length_squared() > 0 else Animation.IDLE

    def try_interact(self, map, game, camera):
        if self.held_item is not None:
            self.try_drop(map, game, camera)
        else:
            self.try_pickup(map, game, camera)
    
    def try_drop(self, map, game, camera):
        tile_x, tile_y = self.get_interact_tile(map, game, camera)
        if tile_x is None:
            return
        
        tile = map.grid[tile_x][tile_y] if map.is_tile_valid(tile_x, tile_y) else None

        if tile is not None and tile.accept(self.held_item, tile_x, tile_y):
            if self.held_item.alive():
                self.world.all_sprites.change_layer(self.held_item, Layers.FLOOR_1.value)
            self.held_item = None
            return

        if tile is None:
            # only drop item if the item on the ground is None or same item
            if map.map_ground_item(tile_x, tile_y, self.held_item):
                world_x, world_y = map.tile_to_world(tile_x, tile_y)
                snapped = pygame.Vector2(world_x, world_y) + pygame.Vector2(game.TILE_SIZE/2, game.TILE_SIZE/2)
                self.held_item.position = snapped
                self.held_item.rect.center = (round(snapped.x), round(snapped.y))
                self.world.all_sprites.change_layer(self.held_item, Layers.FLOOR_1.value)
                self.held_item = None
    
    def try_pickup(self, map, game, camera):
        tile_x, tile_y = self.get_interact_tile(map, game, camera)
        if tile_x is None:
            return

        ground = map.get_ground_item(tile_x, tile_y)
        if ground:
            picked = ground[-1]
            self.held_item = picked
            picked.take_resource(self)
            map.clear_ground_item(tile_x, tile_y, picked)
            self.world.all_sprites.change_layer(self.held_item, Layers.FRONT_1.value)
            return

        tile = map.grid[tile_x][tile_y] if map.is_tile_valid(tile_x, tile_y) else None

        if isinstance(tile, Conveyor) and tile.items:
            item = tile.items.pop(0)   # grab whichever is nearest the exit
            self.held_item = item["resource"]
            self.held_item.take_resource(self)
            self.world.all_sprites.change_layer(self.held_item, Layers.FRONT_1.value)
            return

        if hasattr(tile, "output_buffer") and tile.output_buffer is not None:
            self.held_item = tile.output_buffer
            tile.output_buffer = None
            self.held_item.take_resource(self)
            self.world.all_sprites.change_layer(self.held_item, Layers.FRONT_1.value)

    def get_interact_tile(self, map, game, camera):
        mouse = get_world_mousePos(game, camera)
        tile_x, tile_y = map.world_to_tile(mouse['world_x'], mouse['world_y'])

        player_tile_x, player_tile_y = map.world_to_tile(self.rect.centerx, self.rect.centery)

        # Chebyshev distance: allows straight and diagonal adjacency, both count as "1 tile away"
        if max(abs(tile_x - player_tile_x), abs(tile_y - player_tile_y)) > 1:
            return None, None

        return tile_x, tile_y



    # player key inputs
    def handle_input(self, actions):
        # turn key actions into 1, -1 and 0 in a Vector2
        direction = pygame.Vector2(
            # x-axis: right = 1, left = -1
            actions["right"] - actions["left"],
            # y-axis: down = 1, up = -1
            actions["down"] - actions["up"]
        )
        
        # change flag based on direction
        if direction.x > 0:
            self.facing_right = True
        if direction.x < 0:
            self.facing_right = False            
        # check if there's movement:
        if direction.length_squared() > 0:
            # normalize vector, basically clamp it from -1.0 to 1.0
            # so when pressing both "up" and "right" won't go beyond 1.0
            direction = direction.normalize()
            self.facing = direction

        # finally update velocity:
        self.velocity = direction * self.speed