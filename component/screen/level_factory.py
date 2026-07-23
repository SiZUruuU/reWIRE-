import pygame

from .states import State
from ..map.factory_map import FactoryMap
from ..camera import Camera, Follow
from ..entity import Player, ResourceEntity
from ..utils import get_world_mousePos, EntityType, Animation, Direction, ResourceType, check_tile_at, Fonts
from component.utils.enums import AudioType, OST, SFX
from component.utils.audio import AudioComp
from .economy import Economy

# FACTORY LEVEL CONFIG
DAY_DURATION = 180.0 # 3 minutes
CASH_QUOTA = 500
PREP_STAGE_PICKUP_DURATION = 0.5
PICKUP_DURATIONS = {
    EntityType.CONVEYOR: 2.0,
    EntityType.BUZZSAW: 5.0,
    EntityType.CRUSHER: 5.0,
    EntityType.FURNACE: 8.5,
    EntityType.WOOD_GENERATOR: 15.0,
    EntityType.STONE_GENERATOR: 15.0,
}

class FactoryLevel(State):
    def __init__(self, game, economy=None):
        super().__init__(game)
        
        self.economy = economy if economy is not None else Economy(starting_cash=0)

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.game = game
        self.map = FactoryMap(self)

        self.player = Player(pygame.Vector2(game.GAME_WIDTH/2, game.GAME_HEIGHT/2), self, EntityType.PLAYER)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))

        self.directions = [
            pygame.Vector2(-1, 0),
            pygame.Vector2(0, -1),
            pygame.Vector2(1, 0),
            pygame.Vector2(0, 1)
        ]
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

        AudioComp.play_ost(self, AudioType.OST, OST.TITLE)


    ## LOGIC METHODS ##
    def update(self, delta_time, actions):
        if not self.day_ended:
            self.day_timer += delta_time
            if self.day_timer >= DAY_DURATION:
                self.end_day()

        self.handle_inputs(actions)
        self.all_sprites.update(self.game.global_time, delta_time, actions)
        self.camera.scroll(delta_time)

    def handle_inputs(self, actions):
        mouse = get_world_mousePos(self.game, self.camera)

        for k in range(len(self.hotbar)):
            key_string = f"key_{k+1}"
            if actions[key_string]:
                self.selected_entity = self.hotbar[k]
                AudioComp.play_sfx(self, AudioType.SFX, SFX.HOTBAR_SELECT)
                self.game.reset_key(key_string)

        if actions["key_q"]:
            self.selected_entity = EntityType.NONE
            self.game.reset_key("key_q")

        if actions["key_r"]:
            if actions["Lshift"]:
                self.dir_index -= 1
            else:
                self.dir_index += 1
            self.dir_index %= 4
            self.direction = self.directions[self.dir_index]
            self.game.reset_key("key_r")

        if actions["LMB"] and self.selected_entity != EntityType.NONE:
            x, y = mouse['tile_x'], mouse['tile_y']
            location = pygame.Vector2(x, y)
            self.map.place_entity(location, self.direction, self.selected_entity)
            AudioComp.play_sfx(self, AudioType.SFX, SFX.HOVER)  # swap for SFX.PLACE_MACHINE once added
            self.game.reset_key("LMB")

        self.handle_pickup(actions, mouse)

        if actions["space"]:
            self.player.try_interact(self.map, self.game, self.camera)
            self.game.reset_key("space")

    ## PICKUP LOGIC 
    def handle_pickup(self, actions, mouse):
        tile_x, tile_y = mouse['tile_x'], mouse['tile_y']
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

    @property
    def pickup_fill_ratio(self):
        if self.pickup_target is None or self.pickup_required <= 0:
            return 0.0
        return min(self.pickup_progress / self.pickup_required, 1.0)

    ## DAY/STAGE/QUOTA LOGIC
    def end_day(self):
        self.day_ended = True
        self.is_prep_stage = True  # next day always reopens in prep
        # Assumption: quota check subtracts half the quota from cash regardless of outcome,
        # per your spec "total cash - (quota*0.5)" — confirm this applies win AND lose, or win only.
        if self.economy.cash >= CASH_QUOTA:
            self.economy.cash -= int(CASH_QUOTA * 0.5)
            self.on_day_won()
        else:
            self.on_day_lost()

    def on_day_won(self):
        # TODO: transition to office level
        pass

    def on_day_lost(self):
        # TODO: reset to day one, loose everything
        pass

    def start_stage_transition(self):
        # call this method when prep stage ends
        self.is_prep_stage = False

    # (> w <)?

    ## DISPLAY ##
    def render(self, display):
        # 0.0 = full day, 1.0 = full night
        night_factor = 0.0
        base_color = self._lerp_color((50, 60, 90), (10, 12, 25), night_factor)
        display.fill(base_color)

        self.map.draw(display, self.camera)

        for sprite in self.all_sprites:
            camera = sprite.rect.topleft - self.camera.offset
            display.blit(sprite.image, camera)

        if self.selected_entity != EntityType.NONE:
            self.draw_placement_preview(display)

        self.draw_player_shadow(display)
        self.draw_interact_highlight(display)
        self.draw_item_count(display)
        self.draw_cash_display(display)
        self.draw_pickup_bar(display)
        self.draw_day_timer(display)

    @staticmethod
    def _lerp_color(c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    ## DRAW METHODS
    def draw_placement_preview(self, display):
        mouse = get_world_mousePos(self.game, self.camera)
        tile_x, tile_y = mouse['tile_x'], mouse['tile_y']

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

        screen_x = mouse['world_x'] - self.camera.offset.x
        screen_y = mouse['world_y'] - self.camera.offset.y
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
        text = font.render(f"TIME: {int(remaining)}", True, (255, 255, 255))
        display.blit(text, (self.game.GAME_WIDTH - 100, 10))