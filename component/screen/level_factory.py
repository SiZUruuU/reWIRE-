import pygame

from .states import State
from ..map.factory_map import FactoryMap
from ..camera import Camera, Follow
from ..entity import Player
from .lose_screen import LoseScreen
from ..utils import get_world_mousePos, EntityType, Animation, Direction, Fonts
from component.utils.enums import AudioType, OST, SFX
from component.utils.audio import AudioComp
from .economy import Economy

# FACTORY LEVEL CONFIG
DAY_DURATION = 180.0 # 3 minutes
STARTING_QUOTA = 100
PREP_STAGE_PICKUP_DURATION = 0.5
DOOR_HOLD_DURATION = 3.0
PICKUP_DURATIONS = {
    EntityType.CONVEYOR: 2.0,
    EntityType.BUZZSAW: 5.0,
    EntityType.CRUSHER: 5.0,
    EntityType.FURNACE: 8.5,
    EntityType.WOOD_GENERATOR: 15.0,
    EntityType.STONE_GENERATOR: 15.0,
}

# p.s for method explanations etc, check test world. Code here should be clean.
class FactoryLevel(State):
    def __init__(self, game, economy=None):
        super().__init__(game)

        # FACTORY WORLD CONFIG
        PADDING_TILES = 6
        TILE_SIZE = game.TILE_SIZE
        GRID_COLS, GRID_ROWS = 19, 9
        TILE_SIZE = game.TILE_SIZE
        # wall thickness per side, in tiles
        NORTH_WALL_TILES = 1.8
        SOUTH_WALL_TILES = 3.2
        EAST_WALL_TILES = 2.9
        WEST_WALL_TILES = 1.8

        # basically the bounds of this world, automatically calculated
        # use the values above
        self.WIDTH = (GRID_COLS + PADDING_TILES * 2) * TILE_SIZE
        self.HEIGHT = (GRID_ROWS + PADDING_TILES * 2) * TILE_SIZE

        self.bounds_left = WEST_WALL_TILES * TILE_SIZE
        self.bounds_top = NORTH_WALL_TILES * TILE_SIZE
        self.bounds_right = self.WIDTH - EAST_WALL_TILES * TILE_SIZE
        self.bounds_bottom = self.HEIGHT - SOUTH_WALL_TILES * TILE_SIZE

        # should carry on to other levels that has economy
        self.economy = economy if economy is not None else Economy(starting_cash=0)
        self.quota = STARTING_QUOTA # grows over days

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.game = game
        self.map = FactoryMap(self)        

        self.player = Player(pygame.Vector2(self.WIDTH/2, self.HEIGHT/2), self, EntityType.PLAYER)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))

        self.directions = [
            pygame.Vector2(-1, 0),
            pygame.Vector2(0, -1),
            pygame.Vector2(1, 0),
            pygame.Vector2(0, 1)
        ]

        # add sellbox to world
        for y in range (3,6):
            self.map.place_entity(
                pygame.Vector2(0,y),
                self.directions[0], 
                EntityType.SELLBOX
            )
        
        self.dir_index = 0
        self.direction = self.directions[0]

        self.selected_entity = EntityType.NONE
        
        self.hotbar = [
            EntityType.CONVEYOR,
            EntityType.BUZZSAW,
            EntityType.CRUSHER,
            EntityType.FURNACE,
            EntityType.WOOD_GENERATOR,
            EntityType.STONE_GENERATOR,
        ]

        self.pickup_target = None
        self.pickup_progress = 0.0
        self.pickup_required = 0.0

        # stage tracking:
        self.is_prep_stage = True   # level always opens in prep stage
        self.day_timer = 0.0
        self.day_ended = False

        self.door_position = (24, 4)
        self.door_hold_progress = 0.0

        self.day_over = False

        self.night_overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.day_duration = DAY_DURATION

        self.debug_mode = False

        AudioComp.play_ost(self, AudioType.OST, OST.TITLE)


    ## LOGIC METHODS ##
    def update(self, delta_time, actions):
        if not self.day_ended and not self.is_prep_stage and not self.day_over:
            self.day_timer += delta_time*10
            if self.day_timer >= DAY_DURATION:
                self.day_over = True

        self.handle_inputs(actions)
        self.all_sprites.update(self.game.global_time, delta_time, actions)
        self.camera.scroll(delta_time)

    def handle_inputs(self, actions):
        mouse = get_world_mousePos(self.game, self.camera)
        tile_x, tile_y = self.map.world_to_tile(mouse['world_x'], mouse['world_y'])

        # for cycling through inventory
        for k in range(len(self.hotbar)):
            key_string = f"key_{k+1}"
            if actions[key_string]:
                self.selected_entity = self.hotbar[k]
                AudioComp.play_sfx(self, AudioType.SFX, SFX.HOTBAR_SELECT)
                self.game.reset_key(key_string)

        # clear held machine
        if actions["key_q"]:
            self.selected_entity = EntityType.NONE
            self.game.reset_key("key_q")

        # rotating machines
        if actions["key_r"]:
            if actions["Lshift"]:
                self.dir_index -= 1
            else:
                self.dir_index += 1
            self.dir_index %= 4
            self.direction = self.directions[self.dir_index]
            self.game.reset_key("key_r")

        # placing down machines
        if actions["LMB"] and self.selected_entity != EntityType.NONE:
            location = pygame.Vector2(tile_x, tile_y)
            self.map.place_entity(location, self.direction, self.selected_entity)
            AudioComp.play_sfx(self, AudioType.SFX, SFX.HOVER)
            self.game.reset_key("LMB")

        # for the machine removal feature
        self.handle_pickup(actions, tile_x, tile_y)

        # for picking up items
        if actions["space"]:
            self.player.try_interact(self.map, self.game, self.camera)
            self.game.reset_key("space")

        # end prep stage, starts the day proper
        if actions["key_enter"] and self.is_prep_stage:
            self.start_stage_transition()
            self.game.reset_key("key_enter")

        # end day, go to door and hold 'e', only works if day is done
        if self.day_over and self.door_position is not None:
            self.handle_door_interact(actions)

        # enable debug mode
        if actions["Lctrl"] and actions["key_d"]:
            if not self.debug_mode:
                self.debug_mode = True
            else:
                self.debug_mode = False
            self.game.reset_key("Lctrl")
            self.game.reset_key("key_d")

    ## PICKUP LOGIC 
    def handle_pickup(self, actions, tile_x, tile_y):
        entity = self.map.grid[tile_x][tile_y] if self.map.is_tile_valid(tile_x, tile_y) else None
        rmb_held = actions["RMB"]

        if not rmb_held or entity is not self.pickup_target:
            self.pickup_target = None
            self.pickup_progress = 0.0
            self.pickup_required = 0.0

        if not rmb_held or entity is None:
            return

        if self.pickup_target is None:
            self.pickup_target = entity
            self.pickup_progress = 0.0
            self.pickup_required = (
                PREP_STAGE_PICKUP_DURATION if self.is_prep_stage
                else PICKUP_DURATIONS.get(entity.entity_type, 2.0)
            )

        self.pickup_progress += self.game.delta_time
        if self.pickup_progress >= self.pickup_required:
            self.complete_pickup(entity)

    def complete_pickup(self, entity):
        covered = getattr(entity, "covered_tiles", None)
        if covered is None:
            size = self.game.TILE_SIZE
            tx = int(entity.position.x // size)
            ty = int(entity.position.y // size)
            covered = [(tx, ty)]

        # release/destroy any resources held
        self._release_held_resources(entity)

        for tx, ty in covered:
            if self.map.is_tile_valid(tx, ty):
                self.map.grid[tx][ty] = None
        self.all_sprites.remove(entity)

        for tx, ty in covered:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.map.belt_neighbor_recalculation(tx + dx, ty + dy)

        self.pickup_target = None
        self.pickup_progress = 0.0
        self.pickup_required = 0.0

    # helper method for releasing/removing items
    def _release_held_resources(self, entity):
        # conveyors' list of items
        if hasattr(entity, "items"):
            for item in entity.items:
                self.all_sprites.remove(item["resource"])
            entity.items = []

        # machines/generators' input ports
        if hasattr(entity, "input_buffer"):
            for port, resource in entity.input_buffer.items():
                if resource is not None:
                    self.all_sprites.remove(resource)
            entity.input_buffer = {p: None for p in entity.input_buffer}

        # for machines/generators with single output/port
        if hasattr(entity, "output_buffer") and entity.output_buffer is not None:
            self.all_sprites.remove(entity.output_buffer)
            entity.output_buffer = None

    @property
    def pickup_fill_ratio(self):
        if self.pickup_target is None or self.pickup_required <= 0:
            return 0.0
        return min(self.pickup_progress / self.pickup_required, 1.0)

    def handle_door_interact(self, actions):
        player_tile_x, player_tile_y = self.map.world_to_absolute_tile(
            self.player.rect.centerx, self.player.rect.centery
        )
        door_x, door_y = self.door_position

        self.is_near_door = max(abs(player_tile_x - door_x), abs(player_tile_y - door_y)) <= 1

        if self.is_near_door and actions["interact"]:
            self.door_hold_progress += self.game.delta_time
            if self.door_hold_progress >= DOOR_HOLD_DURATION:
                self.door_hold_progress = 0.0
                self.end_day()
        else:
            self.door_hold_progress = 0.0

    ## DAY/STAGE/QUOTA LOGIC
    def end_day(self):
        self.day_over = False
        self.day_ended = True
        self.is_prep_stage = True
        if self.economy.cash >= STARTING_QUOTA:
            self.quota = round(self.quota + self.quota * 0.25, 5)
            self.economy.cash = round(self.economy.cash - int(STARTING_QUOTA * 0.5), 5)
            self.on_day_won()
        else:
            self.on_day_lost()

    def on_day_won(self):
        # TODO: transition to office level
        pass

    def on_day_lost(self):
        self.day_ended = False
        self.is_prep_stage = True
        self.day_timer = 0.0
        lose_screen = LoseScreen(self.game)
        lose_screen.enter_state()

    def start_stage_transition(self):
        self.is_prep_stage = False

    # (> w <)?

    ## DISPLAY ##
    def render(self, display):
        # 0.0 = full day, 1.0 = full night
        night_factor = 0.0
        base_color = self._lerp_color((50, 60, 90), (10, 12, 25), night_factor)
        display.fill((0, 0, 0))

        world_screen_x = -self.camera.offset.x
        world_screen_y = -self.camera.offset.y
        world_rect = pygame.Rect(world_screen_x, world_screen_y, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(display, base_color, world_rect)

        # draws map background
        self.map.draw(display, self.camera)

        for sprite in self.all_sprites:
            camera = sprite.rect.topleft - self.camera.offset
            display.blit(sprite.image, camera)

        # draws map foreground
        self.map.draw_foreground(display, self.camera)

        self.draw_night_overlay(display)

        if self.selected_entity != EntityType.NONE:
            self.draw_placement_preview(display)

        self.draw_player_shadow(display)
        self.draw_interact_highlight(display)
        self.draw_item_count(display)
        #self.draw_cash_display(display)
        self.draw_pickup_bar(display)
        self.draw_day_timer(display)
        self.draw_prep_text(display)
        self.draw_quota(display)
        self.draw_day_over_text(display)
        self.draw_door_prompt(display)
        self.draw_door_debug(display)

    @staticmethod
    def _lerp_color(c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    ## DRAW METHODS
    def draw_placement_preview(self, display):
        mouse = get_world_mousePos(self.game, self.camera)
        tile_x, tile_y = self.map.world_to_tile(mouse['world_x'], mouse['world_y'])
        sprite = self.get_preview_sprite(self.selected_entity, self.direction)
        if sprite is None:
            return
        preview = sprite.copy()

        valid = self.map.is_tile_valid(tile_x, tile_y) and self.map.is_tile_free(tile_x, tile_y)
        tint = (100, 255, 100) if valid else (255, 100, 100)

        s_tint = pygame.Surface(preview.get_size(), pygame.SRCALPHA)
        s_tint.fill((*tint, 255))
        preview.blit(s_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        preview.set_alpha(140)

        world_x, world_y = self.map.tile_to_world(tile_x, tile_y)
        screen_x = world_x - self.camera.offset.x
        screen_y = world_y - self.camera.offset.y
        display.blit(preview, (screen_x, screen_y))
    
    def draw_player_shadow(self, display):
        shadow_rect = self.player.shadow_image.get_rect(center=self.player.rect.midbottom)
        screen_x = shadow_rect.x - self.camera.offset.x
        screen_y = shadow_rect.y - self.camera.offset.y
        display.blit(self.player.shadow_image, (screen_x, screen_y))

    def draw_interact_highlight(self, display):
        tile_x, tile_y = self.player.get_interact_tile(self.map, self.game, self.camera)
        if tile_x is None:
            return
        has_item = self.map.get_ground_item(tile_x, tile_y) is not None
        tile = self.map.grid[tile_x][tile_y] if self.map.is_tile_valid(tile_x, tile_y) else None
        has_output = hasattr(tile, "output_buffer") and tile.output_buffer is not None
        color = (255, 255, 0, 90) if (has_item or has_output) else (255, 255, 255, 40)

        world_x, world_y = self.map.tile_to_world(tile_x, tile_y)
        screen_x = world_x - self.camera.offset.x
        screen_y = world_y - self.camera.offset.y

        highlight = pygame.Surface((self.map.tile_size, self.map.tile_size), pygame.SRCALPHA)
        highlight.fill(color)
        display.blit(highlight, (screen_x, screen_y))

    # helper method for draw_placement_preview
    def get_preview_sprite(self, entity_type, direction):
        assets = self.game.assets.get(entity_type)
        if not assets:
            return None
        straight = assets.get(Animation.STRAIGHT)
        if not straight:
            return None
        dir_key = Direction((int(direction.x), int(direction.y)))
        frames = straight.get(dir_key)
        if not frames:
            return None
        return frames[0]

    def draw_item_count(self, display):
        font = self.game.assets[Fonts.BODY]
        for (tile_x, tile_y), items in self.map.ground_items.items():
            if len(items) <= 1:
                continue
            world_x, world_y = self.map.tile_to_world(tile_x, tile_y)
            screen_x = world_x - self.camera.offset.x
            screen_y = world_y - self.camera.offset.y

            text = font.render(str(len(items)), True, (255, 255, 255))
            text_rect = text.get_rect(bottomright=(screen_x + self.map.tile_size - 2, screen_y + self.map.tile_size - 2))

            bg = pygame.Surface((text_rect.width + 4, text_rect.height + 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            display.blit(bg, (text_rect.x - 2, text_rect.y - 1))
            display.blit(text, text_rect)

    def draw_cash_display(self, display):
        font = self.game.assets[Fonts.HEADER]
        text = font.render(f"${self.economy.cash}", True, (100, 255, 100))
        text_rect = text.get_rect(topleft=(10, 10))
        bg = pygame.Surface((text_rect.width + 16, text_rect.height + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        display.blit(bg, (text_rect.x - 8, text_rect.y - 5))
        display.blit(text, text_rect)

    def draw_pickup_bar(self, display):
        if self.pickup_target is None:
            return
        mx, my = pygame.mouse.get_pos()
        scaled_x = mx * (self.game.GAME_WIDTH / self.game.SCREEN_WIDTH)
        scaled_y = my * (self.game.GAME_HEIGHT / self.game.SCREEN_HEIGHT)
        bar_width, bar_height = 40, 6
        x = scaled_x - bar_width // 2
        y = scaled_y + 18
        pygame.draw.rect(display, (40, 40, 40), (x, y, bar_width, bar_height))
        pygame.draw.rect(display, (220, 60, 60), (x, y, int(bar_width * self.pickup_fill_ratio), bar_height))
        pygame.draw.rect(display, (10, 10, 10), (x, y, bar_width, bar_height), 1)

    def draw_day_timer(self, display):
        # Placeholder for timer
        font = self.game.assets[Fonts.HEADER]
        remaining = max(0, DAY_DURATION - self.day_timer)        
        if self.is_prep_stage:
            text = font.render(f"PREPARATORY", True, (255, 255, 255))
            display.blit(text, (self.game.GAME_WIDTH - 120, 10))
        else:
            text = font.render(f"TIME: {int(remaining)}", True, (255, 255, 255))
            display.blit(text, (self.game.GAME_WIDTH - 100, 10))

    def draw_prep_text(self, display):
        if not self.is_prep_stage:
            return
        font = self.game.assets[Fonts.BODY]
        text = font.render("PREP STAGE - Press 'ENTER' to start day", True, (255, 230, 120))
        text_rect = text.get_rect(midbottom=(self.game.GAME_WIDTH // 2, self.game.GAME_HEIGHT - 30))

        bg = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        display.blit(bg, (text_rect.x - 10, text_rect.y - 5))
        display.blit(text, text_rect)

    def draw_quota(self, display):
        font = self.game.assets[Fonts.HEADER]
        text_1 = font.render("TODAY'S QUOTA", True, (255, 255, 255))
        text_2 = font.render(f"${self.economy.cash} / ${self.quota}", True, (100, 255, 100))

        padding = 8
        line_gap = 2
        content_width = max(text_1.get_width(), text_2.get_width())
        content_height = text_1.get_height() + text_2.get_height() + line_gap

        bg = pygame.Surface((content_width + padding * 2, content_height + padding * 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        display.blit(bg, (10, 10))

        text_rect_1 = text_1.get_rect(topleft=(10 + padding, 10 + padding))
        text_rect_2 = text_2.get_rect(topleft=(10 + padding, text_rect_1.bottom + line_gap))

        display.blit(text_1, text_rect_1)
        display.blit(text_2, text_rect_2)

    def draw_night_overlay(self, display):
        progress = min(self.day_timer / DAY_DURATION, 1.0)
        max_alpha = 120
        alpha = int(max_alpha * progress)
        if alpha <= 0:
            return
        self.night_overlay.fill((20, 1, 26, alpha))
        screen_x = -self.camera.offset.x
        screen_y = -self.camera.offset.y
        display.blit(self.night_overlay, (screen_x, screen_y))

    def draw_day_over_text(self, display):
        if not self.day_over:
            return
        font = self.game.assets[Fonts.HEADER]
        text = font.render("DAY COMPLETE! head to the door", True, (255, 230, 120))
        text_rect = text.get_rect(midtop=(self.game.GAME_WIDTH // 2, 10))
        bg = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        display.blit(bg, (text_rect.x - 10, text_rect.y - 5))
        display.blit(text, text_rect)

    def draw_door_prompt(self, display):
        if not self.day_over or not self.is_near_door:
            return

        tile_size = self.game.TILE_SIZE
        world_x, world_y = self.map.absolute_tile_to_world(*self.door_position)
        screen_x = world_x - self.camera.offset.x
        screen_y = world_y - self.camera.offset.y - 30

        font = self.game.assets[Fonts.BODY]
        text = font.render("Hold 'E'", True, (255, 230, 120))
        text_rect = text.get_rect(center=(screen_x + tile_size // 2, screen_y))

        bg = pygame.Surface((text_rect.width + 12, text_rect.height + 6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        display.blit(bg, (text_rect.x - 6, text_rect.y - 3))
        display.blit(text, text_rect)

        if self.door_hold_progress > 0:
            ratio = min(self.door_hold_progress / DOOR_HOLD_DURATION, 1.0)
            bar_w, bar_h = 40, 6
            bx = text_rect.centerx - bar_w // 2
            by = text_rect.bottom + 4

            pygame.draw.rect(display, (40, 40, 40), (bx, by, bar_w, bar_h))
            pygame.draw.rect(display, (100, 255, 100), (bx, by, int(bar_w * ratio), bar_h))
            pygame.draw.rect(display, (10, 10, 10), (bx, by, bar_w, bar_h), 1)


    # debug
    def draw_door_debug(self, display):
        if self.debug_mode:
            if self.door_position is None:
                return

            tile_size = self.game.TILE_SIZE
            door_x, door_y = self.door_position

            # the door tile itself, in red
            world_x, world_y = self.map.absolute_tile_to_world(door_x, door_y)
            screen_x = world_x - self.camera.offset.x
            screen_y = world_y - self.camera.offset.y
            door_rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
            pygame.draw.rect(display, (255, 0, 0), door_rect, 2)

            # the 3x3 trigger zone
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    tx, ty = door_x + dx, door_y + dy
                    wx, wy = self.map.absolute_tile_to_world(tx, ty)
                    sx = wx - self.camera.offset.x
                    sy = wy - self.camera.offset.y
                    zone_rect = pygame.Rect(sx, sy, tile_size, tile_size)
                    pygame.draw.rect(display, (255, 255, 0), zone_rect, 1)

            # player's current tile relative to the zone
            player_tile_x, player_tile_y = self.map.world_to_absolute_tile(self.player.rect.centerx, self.player.rect.centery)
            pwx, pwy = self.map.absolute_tile_to_world(player_tile_x, player_tile_y)
            psx = pwx - self.camera.offset.x
            psy = pwy - self.camera.offset.y
            pygame.draw.rect(display, (0, 255, 255), (psx, psy, tile_size, tile_size), 2)

            # print actual distance check
            font = self.game.assets[Fonts.BODY]
            near = getattr(self, "is_near_door", False)
            text = font.render(f"near_door={near} day_over={self.day_over} hold={self.door_hold_progress:.2f}", True, (255, 255, 255))
            display.blit(text, (10, self.game.GAME_HEIGHT - 30))