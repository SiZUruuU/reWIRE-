import pygame, random, math

from .states import State
from ..map.factory_map import FactoryMap
from ..camera import Camera, Follow
from ..entity import Player
from .lose_screen import LoseScreen
from ..utils import get_world_mousePos, EntityType, Animation, Direction, Fonts, ParticleSystem
from component.utils.enums import AudioType, OST, SFX
from .economy import Economy
from .machine_inventory import MachineInventory
from .gui.rewire_gui import RewireGUI
from .gui.manual_gui import ManualGUI

# FACTORY LEVEL CONFIG
DAY_DURATION = 180  # 3 mins
STARTING_QUOTA = round(random.uniform(20, 30), 2)
PREP_STAGE_PICKUP_DURATION = 0.5
DOOR_HOLD_DURATION = 3.0
SPARK_INTERVAL = 0.15
PICKUP_DURATIONS = {
    EntityType.CONVEYOR: 2.0,
    EntityType.BUZZSAW: 3.0,
    EntityType.CRUSHER: 4.0,
    EntityType.FURNACE: 5.5,
    EntityType.WOOD_GENERATOR: 7.0,
    EntityType.STONE_GENERATOR: 8.5,
}
STARTING_MACHINE_KIT = {
    EntityType.CONVEYOR: 99,
    EntityType.BUZZSAW: 99,
    EntityType.CRUSHER: 99,
    EntityType.FURNACE: 99,
    EntityType.WOOD_GENERATOR: 99,
    EntityType.STONE_GENERATOR: 99,
}

# p.s for method explanations etc, check test world. Code here should be clean.
class FactoryLevel(State):
    def __init__(self, game, economy=None, day_number=1, quota=None, machine_inventory=None, placed_machines=None):
        super().__init__(game)

        # FACTORY WORLD CONFIG
        PADDING_TILES = 6
        TILE_SIZE = game.TILE_SIZE
        GRID_COLS, GRID_ROWS = 19, 9
        # wall thickness per side, in tiles
        NORTH_WALL_TILES = 1.8
        SOUTH_WALL_TILES = 3.2
        EAST_WALL_TILES = 2.9
        WEST_WALL_TILES = 1.8

        self.WIDTH = (GRID_COLS + PADDING_TILES * 2) * TILE_SIZE
        self.HEIGHT = (GRID_ROWS + PADDING_TILES * 2) * TILE_SIZE

        self.bounds_left = WEST_WALL_TILES * TILE_SIZE
        self.bounds_top = NORTH_WALL_TILES * TILE_SIZE
        self.bounds_right = self.WIDTH - EAST_WALL_TILES * TILE_SIZE
        self.bounds_bottom = self.HEIGHT - SOUTH_WALL_TILES * TILE_SIZE

        self.economy = economy if economy is not None else Economy(starting_cash=0)
        self.day_number = day_number
        self.quota = quota if quota is not None else STARTING_QUOTA

        self.rewire_gui = RewireGUI(self)
        self.manual_gui = ManualGUI(self)

        # apply starter kit
        if machine_inventory is not None:
            self.machine_inventory = machine_inventory
        elif day_number == 1:
            self.machine_inventory = MachineInventory(dict(STARTING_MACHINE_KIT))
        else:
            self.machine_inventory = MachineInventory({})

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.game = game
        self.map = FactoryMap(self)

        #Walking State 
        #self.iswalking = False

        self.audio = self.game.audio_handler

        self.player = Player(pygame.Vector2(self.WIDTH/2, self.HEIGHT/2), self, EntityType.PLAYER)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))

        # cash particles and machine breakdown
        self.particles = ParticleSystem()
        self.spark_timer = 0.0

        self.directions = [
            pygame.Vector2(-1, 0),
            pygame.Vector2(0, -1),
            pygame.Vector2(1, 0),
            pygame.Vector2(0, 1)
        ]

        # add sellbox to world
        for y in range(3, 6):
            self.map.place_entity(
                pygame.Vector2(0, y),
                self.directions[0],
                EntityType.SELLBOX
            )

        self.tutorial_seen = True
        self.manual_hint_seen = True

        if day_number == 1 and placed_machines is None:

            self.map.place_entity(
                pygame.Vector2(6, 4),
                self.directions[0],
                EntityType.WOOD_GENERATOR
            )
            self.map.place_entity(
                pygame.Vector2(4, 4),
                self.directions[0],
                EntityType.BUZZSAW
            )

        self.tutorial_seen = False
        self.manual_hint_seen = False

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
        self.earned_cash_today = 0.0

        self.door_position = (24, 4)
        self.door_hold_progress = 0.0

        self.day_over = False

        self.night_overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.day_duration = DAY_DURATION

        # restore placed machines
        self.restore_placed_machines(placed_machines)

        self.debug_mode = False

    ## LOGIC METHODS ##
    def update(self, delta_time, actions):

        # Check if any entity in all_sprites with a breakdown component is broken
        any_machine_broken = any(
            getattr(sprite, "breakdown", None) and sprite.breakdown.is_broken
            for sprite in self.all_sprites
        )

        if any_machine_broken:
            self.audio.play_loop("machine_broken_loop", AudioType.SFX, SFX.MACHINE_BROKEN, 0.3)
        else:
            self.audio.stop_loop("machine_broken_loop")

        if not self.day_ended and not self.is_prep_stage and not self.day_over:
            self.day_timer += delta_time
            if self.day_timer >= DAY_DURATION:
                self.day_over = True

        prev_rect = self.player.rect.copy()
        self.handle_inputs(delta_time, actions)
        self.all_sprites.update(self.game.global_time, delta_time, actions)
        self.camera.scroll(delta_time)

        # resolve player collision with obstacles
        resolved = self.map.resolve_collisions(self.player.rect, prev_rect)
        self.player.rect.topleft = resolved.topleft
        self.player.position = pygame.Vector2(self.player.rect.topleft)

        self.spark_timer += delta_time
        if self.spark_timer >= SPARK_INTERVAL:
            self.spark_timer = 0.0
            self.spawn_breakdown_sparks()

        self.particles.update(delta_time)

    def handle_inputs(self, delta_time, actions):
        mouse = get_world_mousePos(self.game, self.camera)
        tile_x, tile_y = self.map.world_to_tile(mouse['world_x'], mouse['world_y'])

        # for cycling through inventory
        for k in range(len(self.hotbar)):
            key_string = f"key_{k+1}"
            if actions[key_string]:
                self.selected_entity = self.hotbar[k]
                self.audio.play_sfx(AudioType.SFX, SFX.HOTBAR_SELECT)
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
            self.audio.play_sfx(AudioType.SFX, SFX.MACHINE_PLACED, 0.3)
            if self.machine_inventory.has(self.selected_entity):
                location = pygame.Vector2(tile_x, tile_y)
                placed = self.map.place_entity(location, self.direction, self.selected_entity)
                if placed is True:
                    self.machine_inventory.remove(self.selected_entity)
            self.game.reset_key("LMB")

        # for manual activation
        if actions["key_g"]:
            self.manual_gui.toggle()
            self.manual_hint_seen = True
            self.game.reset_key("key_g")

        if self.manual_gui.is_open:
            self.manual_gui.handle_input(actions)

        # for the machine removal feature
        self.handle_pickup(actions, tile_x, tile_y)

        # for picking up items and fixing broken machines
        if actions["space"]:
            self.selected_entity = EntityType.NONE
            interact_tile_x, interact_tile_y = self.player.get_interact_tile(self.map, self.game, self.camera)
            target = (
                self.map.grid[interact_tile_x][interact_tile_y]
                if interact_tile_x is not None and self.map.is_tile_valid(interact_tile_x, interact_tile_y)
                else None
            )

            if target is not None and hasattr(target, "breakdown") and target.breakdown.is_broken:
                if not self.rewire_gui.is_open:
                    self.rewire_gui.open(target)
            else:
                self.player.try_interact(self.map, self.game, self.camera)
            self.game.reset_key("space")

        # rewiring minigame
        if self.rewire_gui.is_open:
            self.rewire_gui.handle_input(actions, delta_time)

        # end prep stage, starts the day proper
        if actions["key_enter"] and self.is_prep_stage:
            self.start_stage_transition()
            self.audio.play_ost(AudioType.OST, OST.FACTORY)
            self.game.reset_key("key_enter")

        # end day, go to door and hold 'e', only works if day is done
        if self.day_over and self.door_position is not None:
            self.handle_door_interact(actions)

        # enable debug mode
        if actions["Lctrl"] and actions["key_d"]:
            self.debug_mode = not self.debug_mode
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

        # get machine back to inv
        self.machine_inventory.add(entity.entity_type)

        for tx, ty in covered:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.map.belt_neighbor_recalculation(tx + dx, ty + dy)

        self.pickup_target = None
        self.pickup_progress = 0.0
        self.pickup_required = 0.0

    # helper method for releasing/removing items
    def _release_held_resources(self, entity):
        if hasattr(entity, "items"):
            for item in entity.items:
                self.all_sprites.remove(item["resource"])
            entity.items = []

        if hasattr(entity, "input_buffer"):
            for port, resource in entity.input_buffer.items():
                if resource is not None:
                    self.all_sprites.remove(resource)
            entity.input_buffer = {p: None for p in entity.input_buffer}

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
                self.audio.stop_ost()
                self.end_day()
        else:
            self.door_hold_progress = 0.0

    ## DAY/STAGE/QUOTA LOGIC
    def end_day(self):
        self.day_over = False
        self.day_ended = True
        self.is_prep_stage = True

        if self.earned_cash_today >= self.quota:
            self.economy.add_cash(self.earned_cash_today)
            self.economy.cash = round(self.economy.cash - self.quota * 0.5, 3)
            self.quota = round(self.quota + self.economy.cash * 0.35 + self.quota * 0.35, 3)
            self.day_number += 1
            self.on_day_won()
        else:
            self.reset_progress()
            self.on_day_lost()

        self.earned_cash_today = 0

    def on_day_won(self):
        from .level_office import OfficeLevel
        def do_transition():
            self.exit_state()
            office = OfficeLevel(
                self.game,
                economy=self.economy,
                day_number=self.day_number,
                quota=self.quota,
                machine_inventory=self.machine_inventory,
                placed_machines=self.snapshot_placed_machines(),
            )
            office.enter_state()
        self.game.fade_trans.start(do_transition)

    def on_day_lost(self):
        self.day_ended = False
        self.is_prep_stage = True
        self.day_timer = 0.0

        def do_transition():
            lose_screen = LoseScreen(self.game)
            lose_screen.enter_state()
        self.game.fade_trans.start(do_transition)

    def start_stage_transition(self):
        self.is_prep_stage = False

    def reset_progress(self):
        self.economy.cash = 0
        self.economy.resources = {}
        self.quota = STARTING_QUOTA
        self.day_number = 1
        self.machine_inventory = MachineInventory(dict(STARTING_MACHINE_KIT))

    ## DISPLAY ##
    def render(self, display):
        night_factor = 0.0
        base_color = self._lerp_color((50, 60, 90), (10, 12, 25), night_factor)
        display.fill((0, 0, 0))

        world_screen_x = -self.camera.offset.x
        world_screen_y = -self.camera.offset.y
        world_rect = pygame.Rect(world_screen_x, world_screen_y, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(display, base_color, world_rect)

        self.map.draw(display, self.camera)

        for sprite in self.all_sprites:
            camera = sprite.rect.topleft - self.camera.offset
            display.blit(sprite.image, camera)

        self.map.draw_foreground(display, self.camera)

        self.particles.draw(display, self.camera.offset)
        self.draw_night_overlay(display)

        if self.selected_entity != EntityType.NONE:
            self.draw_placement_preview(display)

        self.draw_player_shadow(display)
        self.draw_interact_highlight(display)
        self.draw_item_count(display)
        #self.draw_cash_display(display)
        self.draw_pickup_bar(display)
        self.draw_manual_hint(display)

        # HUD stuff
        self.draw_day_timer(display)
        self.draw_prep_text(display)
        self.draw_quota(display)
        self.draw_day_over_text(display)
        self.draw_door_prompt(display)
        self.draw_machine_inventory(display)
        self.draw_day_counter(display)
        self.draw_broken_indicators(display)
        self.draw_rewire_prompt(display)        

        self.rewire_gui.draw(display)
        self.manual_gui.draw(display)

        # debugs
        self.show_all_obstacles(display)

    @staticmethod
    def _lerp_color(c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    ## DRAW METHODS
    def draw_placement_preview(self, display):
        if not self.machine_inventory.has(self.selected_entity):
            return

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
        text = font.render(f"${self.economy.cash}", False, (100, 255, 100))
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
        font = self.game.assets[Fonts.HEADER]
        remaining = max(0, DAY_DURATION - self.day_timer)
        if self.is_prep_stage:
            text = font.render(f"PREPARATORY", False, (255, 255, 255))
            display.blit(text, (self.game.GAME_WIDTH - 120, 10))
        else:
            text = font.render(f"TIME: {int(remaining)}", True, (255, 255, 255))
            display.blit(text, (self.game.GAME_WIDTH - 100, 10))

    def draw_prep_text(self, display):
        if not self.is_prep_stage:
            return

        duration = 3.0
        phase = (self.game.global_time / duration) * (2 * math.pi)
        weight = (math.sin (phase) + 1.0) / 2.0

        text_alpha = int(pygame.math.lerp(0, 255, weight))
        bg_alpha = int(pygame.math.lerp(0, 150, weight))

        font = self.game.assets[Fonts.BODY]
        text = font.render("PREP STAGE - Press 'ENTER' to start day", False, (255, 230, 120))
        text.set_alpha(text_alpha)

        text_rect = text.get_rect(midbottom=(self.game.GAME_WIDTH // 2, self.game.GAME_HEIGHT - 30))

        bg = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, bg_alpha))

        display.blit(bg, (text_rect.x - 10, text_rect.y - 5))
        display.blit(text, text_rect)

    def draw_quota(self, display):
        font = self.game.assets[Fonts.HEADER]
        text_1 = font.render("TODAY'S QUOTA", True, (255, 255, 255))
        text_2 = font.render(f"${self.earned_cash_today} / ${self.quota}", True, (100, 255, 100))

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
        text = font.render("DAY COMPLETE! head to the door", False, (255, 230, 120))
        text_rect = text.get_rect(midtop=(self.game.GAME_WIDTH // 2, self.game.GAME_HEIGHT - 30))
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
        text = font.render("Hold 'E'", False, (255, 230, 120))
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

    def draw_machine_inventory(self, display):
        icons = self.game.assets[Animation.ICONS]
        font = self.game.assets[Fonts.BODY]

        icon_size = 32
        padding = 6
        start_y = 60
        x = self.game.GAME_WIDTH - icon_size - 16

        strip_padding = 4
        strip_height = len(self.hotbar) * (icon_size + padding) - padding + strip_padding * 2
        strip = pygame.Surface((icon_size + strip_padding * 2, strip_height), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 150))
        display.blit(strip, (x - strip_padding, start_y - strip_padding))

        for i, entity_type in enumerate(self.hotbar):
            icon = icons.get(entity_type)
            if icon is None:
                continue

            y = start_y + i * (icon_size + padding)
            count = self.machine_inventory.get_count(entity_type)
            owned = count > 0

            display_icon = icon.copy()
            if not owned:
                dark = pygame.Surface(display_icon.get_size(), pygame.SRCALPHA)
                dark.fill((60, 60, 60, 255))
                display_icon.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                display_icon.set_alpha(160)

            if self.selected_entity == entity_type:
                highlight_rect = pygame.Rect(x - 4, y - 4, icon_size + 8, icon_size + 8)
                pygame.draw.rect(display, (255, 230, 120), highlight_rect, 2)

            display.blit(display_icon, (x, y))

            key_text = font.render(str(i + 1), False, (50, 50, 80))
            key_rect = key_text.get_rect(topleft=(x + 2, y + 1))

            key_bg = pygame.Surface((key_text.get_width() + 4, key_text.get_height() + 2), pygame.SRCALPHA)
            key_bg.fill((0, 0, 0, 170))
            display.blit(key_bg, (key_rect.x - 2, key_rect.y - 1))
            display.blit(key_text, key_rect)

            text = font.render(str(count), False, (255, 255, 255))
            text_rect = text.get_rect(bottomright=(x + icon_size - 2, y + icon_size - 2))

            bg = pygame.Surface((text_rect.width + 4, text_rect.height + 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            display.blit(bg, (text_rect.x - 2, text_rect.y - 1))
            display.blit(text, text_rect)

    def draw_day_counter(self, display):
        font = self.game.assets[Fonts.HEADER]
        text = font.render(f"DAY {self.day_number}", False, (255, 255, 255))
        display.blit(text, (self.game.GAME_WIDTH // 2 - text.get_width() // 2, 10))

    def draw_broken_indicators(self, display):
        font = self.game.assets[Fonts.HEADER]
        blink_on = int(self.game.global_time * 4) % 2 == 0
        if not blink_on:
            return

        seen = set()
        for sprite in self.all_sprites:
            if not hasattr(sprite, "breakdown"):
                continue
            if not sprite.breakdown.is_broken:
                continue
            if id(sprite) in seen:
                continue
            seen.add(id(sprite))

            screen_x = sprite.rect.centerx - self.camera.offset.x
            screen_y = sprite.rect.top - self.camera.offset.y - 20

            text = font.render("!", False, (255, 220, 40))
            text_rect = text.get_rect(center=(screen_x, screen_y))
            bg = pygame.Surface((text_rect.width + 8, text_rect.height + 4), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            display.blit(bg, (text_rect.x - 4, text_rect.y - 2))
            display.blit(text, text_rect)

    def draw_rewire_prompt(self, display):
        tile_x, tile_y = self.player.get_interact_tile(self.map, self.game, self.camera)
        if tile_x is None:
            return
        target = self.map.grid[tile_x][tile_y] if self.map.is_tile_valid(tile_x, tile_y) else None
        if target is None or not hasattr(target, "breakdown") or not target.breakdown.is_broken:
            return

        font = self.game.assets[Fonts.BODY]
        text = font.render("Press 'SPACE' to fix", False, (255, 220, 40))
        screen_x = target.rect.centerx - self.camera.offset.x
        screen_y = target.rect.top - self.camera.offset.y - 40
        text_rect = text.get_rect(center=(screen_x, screen_y))
        bg = pygame.Surface((text_rect.width + 12, text_rect.height + 6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        display.blit(bg, (text_rect.x - 6, text_rect.y - 3))
        display.blit(text, text_rect)

    # machine persistence
    def snapshot_placed_machines(self):
        seen = set()
        snapshot = []
        for x in range(len(self.map.grid)):
            for y in range(len(self.map.grid[0])):
                entity = self.map.grid[x][y]
                if entity is None or entity.entity_type == EntityType.SELLBOX:
                    continue
                if id(entity) in seen:
                    continue
                seen.add(id(entity))
                snapshot.append({
                    "entity_type": entity.entity_type,
                    "position": (entity.position.x, entity.position.y),
                    "direction": (entity.direction.x, entity.direction.y),
                })
        return snapshot

    def restore_placed_machines(self, snapshot):
        if not snapshot:
            return
        for entry in snapshot:
            world_x, world_y = entry["position"]
            tile_x, tile_y = self.map.world_to_tile(world_x, world_y)
            direction = pygame.Vector2(*entry["direction"])
            placed = self.map.place_entity(pygame.Vector2(tile_x, tile_y), direction, entry["entity_type"])
            if placed is not True:
                print(f"RESTORE FAILED for {entry['entity_type']} at tile ({tile_x},{tile_y}), result: {placed}")

    def spawn_breakdown_sparks(self):
        for sprite in self.all_sprites:
            if not hasattr(sprite, "breakdown") or not sprite.breakdown.is_broken:
                continue
            rect = sprite.rect
            spark_pos = (
                random.uniform(rect.left, rect.right),
                random.uniform(rect.top, rect.bottom)
            )
            # bright orange
            self.particles.emit_burst(
                spark_pos,
                color=(255, 69, 0),
                count=random.randint(1, 3),
                size_range=(1, 6),
                speed_range=(50, 200),
                lifetime_range=(0.15, 2)
            )
            # yellow
            self.particles.emit_burst(
                spark_pos,
                color=(255, 165, 0),
                count=random.randint(1, 3),
                size_range=(1, 6),
                speed_range=(50, 200),
                lifetime_range=(0.15, 2)
            )

    def draw_manual_hint(self, display):
        if self.manual_hint_seen or self.manual_gui.is_open:
            return
        font = self.game.assets[Fonts.BODY]
        text = font.render('Press "G" to open the manual', False, (200, 200, 220))
        text_rect = text.get_rect(center=(self.game.GAME_WIDTH/2, 50))

        bg = pygame.Surface((text_rect.width + 16, text_rect.height + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        display.blit(bg, (text_rect.x - 8, text_rect.y - 5))
        display.blit(text, text_rect)



    # for debugging
    def show_all_obstacles(self, display):
        if not self.debug_mode:
            return

        for obstacle in self.map.obstacles:
            screen_x = obstacle.x - self.camera.offset.x
            screen_y = obstacle.y - self.camera.offset.y
            rect = pygame.Rect(screen_x, screen_y, obstacle.width, obstacle.height)
            pygame.draw.rect(display, (255, 0, 255), rect, 2)

        from ..map.factory_map import SOLID_ENTITY_TYPES
        for sprite in self.all_sprites:
            if getattr(sprite, "entity_type", None) in SOLID_ENTITY_TYPES:
                screen_x = sprite.rect.x - self.camera.offset.x
                screen_y = sprite.rect.y - self.camera.offset.y
                rect = pygame.Rect(screen_x, screen_y, sprite.rect.width, sprite.rect.height)
                pygame.draw.rect(display, (255, 0, 255), rect, 2)

        feet_height = 16
        feet_width_inset = 12
        feet_x = self.player.rect.x + feet_width_inset - self.camera.offset.x
        feet_y = self.player.rect.bottom - feet_height - self.camera.offset.y
        feet_width = self.player.rect.width - feet_width_inset * 2
        feet_rect = pygame.Rect(feet_x, feet_y, feet_width, feet_height)
        pygame.draw.rect(display, (0, 255, 0), feet_rect, 2)