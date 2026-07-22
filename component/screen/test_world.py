import pygame

from .states import State
from ..map.test_map import TestMap
from ..camera import Camera, Follow
from ..entity import Player, ResourceEntity
from ..utils import get_world_mousePos, EntityType, Animation, Direction, ResourceType, check_tile_at, Fonts

## THIS IS A TESTING WORLD TO TEST FEATURES AND THEORIES ##
# Use this world as reference in making other levels as all
# features is applied in this class

# A world or level is composed of components of different varieties
# MAP components holds the value of where each entity should be 
# ENTITIES are components that does something based off of their script (includes PLAYER, MACHINES, etc)
# CAMERA components acts as a viewport for the world REMEMBER TO APPLY CAMERA OFFSET IN DISPLAY TO AVOID 
# WRONG DISPLAY OF OBJECTS. (ex. object_position = some_value - camera.offset)
# UTILS are useful for the Enums and a few screen to world coordinates methods such as get_world_mousePos

class TestWorld(State):
    def __init__(self, game):
        super().__init__(game)

        # world values
        self.cash = 0

        # sprite groups to group all sprites with layer feature
        self.all_sprites = pygame.sprite.LayeredUpdates()        

        # copy of the entry point
        self.game = game
        self.map = TestMap(self) # map, be advised every placable is only tracked inside a map's grid        

        # initalize the player and camera (with camera type):
        self.player = Player(pygame.Vector2(game.GAME_WIDTH/2, game.GAME_HEIGHT/2), self, EntityType.PLAYER)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))

        # entity data:
        self.directions = [
                pygame.Vector2(-1, 0), # left
                pygame.Vector2(0, -1), # up
                pygame.Vector2(1, 0), # right
                pygame.Vector2(0, 1) # down
        ] 
        
        self.dir_index = 0
        self.direction = self.directions[0]

        # entity tracking:        
        self.selected_entity = EntityType.NONE
        # hotbar use keys 1-9
        self.hotbar = [
            EntityType.CONVEYOR,
            EntityType.BUZZSAW,
            EntityType.CRUSHER,
            EntityType.FURNACE,
            EntityType.SELLBOX, # DO NOT ADD TO FINAL GAME WORLD
        ]

    ## LOGIC RELATED METHODS ##
    def update(self, delta_time, actions):        
        # World related actions:
        self.handle_inputs(actions)        

        # update all sprites' data in this world:
        self.all_sprites.update(self.game.global_time, delta_time, actions)
        self.camera.scroll(delta_time)

    def handle_inputs(self, actions):                
        mouse = get_world_mousePos(self.game, self.camera)

        # hotbar selection:
        for k in range(len(self.hotbar)):
            key_string = f"key_{k+1}"
            if actions[key_string]:
                self.selected_entity = self.hotbar[k]
                self.game.reset_key(key_string)
            
        # clear selection:
        if actions["key_q"]:
            self.selected_entity = EntityType.NONE
            self.game.reset_key("key_q")

        # handle rotation data:
        if actions["key_r"]:
            if actions["Lshift"]:
                self.dir_index -= 1
            else:
                self.dir_index += 1
            self.dir_index %= 4
            self.direction = self.directions[self.dir_index]
            self.game.reset_key("key_r")

        # handle object placement:
        if actions["LMB"] and self.selected_entity != EntityType.NONE:
            x, y = mouse['tile_x'], mouse['tile_y']
            location = pygame.Vector2(x, y)
            self.map.place_entity(
                location,
                self.direction,
                self.selected_entity
            )                        
            self.game.reset_key("LMB")

        # resource placement test:
        if actions["key_f"]:
            position = pygame.Vector2(mouse['world_x'], mouse['world_y'])
            resource = ResourceEntity(position, self, ResourceType.WOOD)
            
            tile = check_tile_at(position.x, position.y, self.game, self.map.grid)
            if tile is not None and tile.accept(resource):
                pass
            else:
                tile_x = int(position.x // self.game.TILE_SIZE)
                tile_y = int(position.y // self.game.TILE_SIZE)
                if not self.map.map_ground_item(tile_x, tile_y, resource):
                    resource.kill()

            self.game.reset_key("key_f")

        if actions["key_g"]:
            position = pygame.Vector2(mouse['world_x'], mouse['world_y'])
            resource = ResourceEntity(position, self, ResourceType.STONE)
            
            tile = check_tile_at(position.x, position.y, self.game, self.map.grid)
            if tile is not None and tile.accept(resource):
                pass
            else:
                tile_x = int(position.x // self.game.TILE_SIZE)
                tile_y = int(position.y // self.game.TILE_SIZE)
                if not self.map.map_ground_item(tile_x, tile_y, resource):
                    resource.kill()
                    
            self.game.reset_key("key_g")
        
        # player take or drop resource:
        if actions["space"]:
            self.player.try_interact(self.map, self.game, self.camera)
            self.game.reset_key("space")



    ## DISPLAY RELATED METHODS ##
    # main render method, call any rendering here
    def render(self, display):
        display.fill((50, 60, 90))

        # render the map:
        self.map.draw(display, self.camera)

        # render all sprites in this world:
        # updated it with layering
        for sprite in self.all_sprites:
            camera = sprite.rect.topleft - self.camera.offset
            display.blit(sprite.image, camera)
        
        # preview selected item:
        if self.selected_entity != EntityType.NONE:
            self.draw_placement_preview(display)
        
        # tile interaction highlight:
        self.draw_interact_highlight(display)

        # ground item count:
        self.draw_item_count(display)

        # cash amount:
        self.draw_cash_display(display)

    # shows green or red tinted entity ghost preview
    # red = invalid, green = valid
    def draw_placement_preview(self, display):
        mouse = get_world_mousePos(self.game, self.camera)
        tile_x = mouse['tile_x']
        tile_y = mouse['tile_y']

        # check if that sprite HAS a sprite
        sprite = self.get_preview_sprite(self.selected_entity, self.direction)
        if sprite is None:
            return
        
        # make a copy of that sprite
        preview = sprite.copy()

        # check if the position will be valid, invalid, or obstructed:
        valid = self.map.is_tile_valid(tile_x, tile_y) and self.map.is_tile_free(tile_x, tile_y)
        tint = (100, 255, 100) if valid else (255, 100, 100)

        # surface tint, creates a surface with the item's exact size then tint it based on valid
        s_tint = pygame.Surface(preview.get_size(), pygame.SRCALPHA)
        s_tint.fill((*tint, 255))
        preview.blit(s_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        preview.set_alpha(140)

        # finally show the item's ghost:
        screen_x = mouse['world_x'] - self.camera.offset.x
        screen_y = mouse['world_y'] - self.camera.offset.y
        display.blit(preview, (screen_x, screen_y))

    # shows where the interactable range is by highlighting the tile
    # if a tile is highlighted any interaction actions will work
    def draw_interact_highlight(self, display):
        tile_x, tile_y = self.player.get_interact_tile(self.map, self.game, self.camera)
        if tile_x is None:
            return

        tile_size = self.game.TILE_SIZE
        has_item = self.map.get_ground_item(tile_x, tile_y) is not None
        tile = self.map.grid[tile_x][tile_y] if self.map.is_tile_valid(tile_x, tile_y) else None
        has_output = hasattr(tile, "output_buffer") and tile.output_buffer is not None
        color = (255, 255, 0, 90) if (has_item or has_output) else (255, 255, 255, 40)

        screen_x = tile_x * tile_size - self.camera.offset.x
        screen_y = tile_y * tile_size - self.camera.offset.y

        highlight = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        highlight.fill(color)
        display.blit(highlight, (screen_x, screen_y))

    # when equipping a machine, shows the current machine and direction it is facing
    def get_preview_sprite(self, entity_type: EntityType, direction: pygame.Vector2):
        assets = self.game.assets.get(entity_type)
        if not assets:
            return None
        straight = assets.get(Animation.STRAIGHT)
        if not straight:
            return None
        
        dir_key = Direction(int(direction.x),int(direction.y))
        frames = straight.get(dir_key)
        if not frames:
            return None
        return frames[0]

    # adds a floating text near the item on the floor that shows how many are there 
    def draw_item_count(self, display):
        size = self.game.TILE_SIZE
        font = self.game.assets[Fonts.BODY]
        for (tile_x, tile_y), items in self.map.ground_items.items():
            if len(items) <= 1:
                continue
            screen_x = tile_x * size - self.camera.offset.x
            screen_y = tile_y * size - self.camera.offset.y

            text = font.render(str(len(items)), True, (255, 255, 255))
            text_rect = text.get_rect(bottomright=(screen_x + size - 2, screen_y + size - 2))

            bg = pygame.Surface((text_rect.width + 4, text_rect.height + 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            display.blit(bg, (text_rect.x - 2, text_rect.y - 1))
            display.blit(text, text_rect)

    # displays cash amount
    def draw_cash_display(self, display):
        font = self.game.assets[Fonts.HEADER]
        text = font.render(f"${self.cash}", True, (100, 255, 100))
        text_rect = text.get_rect(topleft=(10,10))

        bg = pygame.Surface((text_rect.width + 16, text_rect.height + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        display.blit(bg, (text_rect.x - 8, text_rect.y - 5))
        display.blit(text, text_rect)
