import pygame

from .states import State
from ..map.office_map import OfficeMap
from ..camera import Camera, Follow
from ..entity import Player, SHOP_PRICES
from ..utils import EntityType, Fonts, Animation, ResourceType
from component.utils.enums import AudioType, OST, SFX
from component.utils.audio import AudioComp
from .gui.shop_gui import ShopGUI
from .gui.workshop_gui import WorkshopGUI
from .economy import Economy
from .machine_inventory import MachineInventory

BED_HOLD_DURATION = 3.0

class OfficeLevel(State):
    def __init__(self, game, economy=None, day_number=1, quota=None, machine_inventory=None, placed_machines=None):
        super().__init__(game)

        TILE_SIZE = game.TILE_SIZE
        self.WIDTH = 10 * TILE_SIZE
        self.HEIGHT = 8 * TILE_SIZE

        # to remember things
        self.economy = economy if economy is not None else Economy(starting_cash=0)
        self.day_number = day_number
        self.quota = quota if quota is not None else 0
        self.placed_machines = placed_machines

        self.machine_inventory = machine_inventory if machine_inventory is not None else MachineInventory({
            EntityType.CONVEYOR: 0,
            EntityType.BUZZSAW: 0,
            EntityType.CRUSHER: 0,
            EntityType.FURNACE: 0,
            EntityType.WOOD_GENERATOR: 0,
            EntityType.STONE_GENERATOR: 0,
        })        

        self.shop_gui = ShopGUI(self)
        self.workshop_gui = WorkshopGUI(self)

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.game = game
        self.map = OfficeMap(self)
        
        self.player = Player(pygame.Vector2(self.WIDTH / 2, self.HEIGHT / 2), self, EntityType.PLAYER)
        self.camera = Camera(self.player, game.GAME_WIDTH, game.GAME_HEIGHT)
        self.camera.setmethod(Follow(self.camera, self.player))

        # interactive triggers tile coordinates:
        self.bed_position = (2, 5)
        self.desk_position = (7, 2)
        self.workshop_position = (2, 2)

        # for tracking interacitons:
        self.bed_hold_progress = 0.0
        self.is_near_bed = False

        self.desk_open = False
        self.is_near_desk = False

        self.workshop_open = False
        self.is_near_workshop = False

        self.debug_mode = False

        self.ost = AudioComp(game)
        self.ost.play_ost(AudioType.OST, OST.OFFICE)


    ## LOGIC METHODS ##
    def update(self, delta_time, actions):
        prev_rect = self.player.rect.copy()
        
        self.handle_inputs(actions)
        self.all_sprites.update(self.game.global_time, delta_time, actions)
        self.camera.scroll(delta_time)
        
        # keep player inside office bounds
        clamped = self.map.clamp_to_bounds(self.player.rect)
        self.player.rect.topleft = clamped.topleft
        self.player.position = pygame.Vector2(self.player.rect.topleft)

        # resolve player collision with obstacles
        resolved = self.map.resolve_collisions(self.player.rect, prev_rect)
        self.player.rect.topleft = resolved.topleft
        self.player.position = pygame.Vector2(self.player.rect.topleft)

    def handle_inputs(self, actions):
        self.handle_bed_interact(actions)
        self.handle_desk_interact(actions)
        self.handle_workshop_interact(actions)

        if actions["Lctrl"] and actions["key_d"]:
            self.debug_mode = True if not self.debug_mode else False
            self.game.reset_key("Lctrl")
            self.game.reset_key("key_d")

    def _is_near(self, target_position):
        player_tile_x, player_tile_y = self.map.world_to_absolute_tile(
            self.player.rect.centerx, self.player.rect.centery
        )
        tx, ty = target_position
        return max(abs(player_tile_x - tx), abs(player_tile_y - ty)) <= 1

    ## BED (next day) ##
    def handle_bed_interact(self, actions):
        self.is_near_bed = self._is_near(self.bed_position)

        if self.is_near_bed and actions["interact"]:
            self.bed_hold_progress += self.game.delta_time
            if self.bed_hold_progress >= BED_HOLD_DURATION:
                self.bed_hold_progress = 0.0
                self.next_day()
        else:
            self.bed_hold_progress = 0.0

    def next_day(self):
        from .level_factory import FactoryLevel
        def do_transition():
            self.exit_state()
            factory = FactoryLevel(
                self.game,
                economy=self.economy,
                day_number=self.day_number,
                quota=self.quota,
                machine_inventory=self.machine_inventory,
                placed_machines=self.placed_machines,
            )
            factory.enter_state()
        self.game.fade_trans.start(do_transition)


    ## DESK (shop) ##
    # method when player starts to interact with the shop 
    def handle_desk_interact(self, actions):
        self.is_near_desk = self._is_near(self.desk_position)

        if self.is_near_desk and actions["interact"] and not self.desk_open:
            self.desk_open = True
            self.game.reset_key("interact")
        elif self.desk_open and actions["interact"]:
            self.desk_open = False
            self.shop_gui.clear_cart()
            self.game.reset_key("interact")

        if self.desk_open:
            self.shop_gui.handle_shop_click(actions)



    ## WORKSHOP (build machines) ##
    def handle_workshop_interact(self, actions):
        self.is_near_workshop = self._is_near(self.workshop_position)

        if self.is_near_workshop and actions["interact"] and not self.workshop_open:
            self.workshop_open = True
            self.game.reset_key("interact")
        elif self.workshop_open and actions["interact"]:
            self.workshop_open = False
            self.game.reset_key("interact")

        if self.workshop_open:
            self.workshop_gui.handle_input(actions)



    # MAIN RENDER
    def render(self, display):
        display.fill((0, 0, 0))

        self.map.draw(display, self.camera)

        for sprite in self.all_sprites:
            camera = sprite.rect.topleft - self.camera.offset
            display.blit(sprite.image, camera)

        self.map.draw_foreground(display, self.camera)

        self.draw_cash_display(display)
        self.draw_mats_display(display)
        self.draw_bed_prompt(display)
        self.draw_desk_prompt(display)
        self.draw_workshop_prompt(display)

        if self.desk_open:
            self.draw_shop_gui(display)
        if self.workshop_open:
            self.draw_workshop_gui(display)

        self.show_all_obstacles(display)


    ## Display methods
    def draw_cash_display(self, display):
        font = self.game.assets[Fonts.HEADER]
        text = font.render(f"${self.economy.cash}", True, (100, 255, 100))
        text_rect = text.get_rect(topleft=(20, 20))
        bg = pygame.Surface((text_rect.width + 16, text_rect.height + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        display.blit(bg, (text_rect.x - 8, text_rect.y - 5))
        display.blit(text, text_rect)

    def draw_bed_prompt(self, display):
        if not self.is_near_bed:
            return
        self.draw_prompt(display, self.bed_position, "Hold 'E' to sleep", self.bed_hold_progress, BED_HOLD_DURATION)

    def draw_desk_prompt(self, display):
        if not self.is_near_desk or self.desk_open:
            return
        self.draw_prompt(display, self.desk_position, "Press 'E' to shop", 0, 0)

    def draw_workshop_prompt(self, display):
        if not self.is_near_workshop or self.workshop_open:
            return
        self.draw_prompt(display, self.workshop_position, "Press 'E' to build", 0, 0)

    def draw_prompt(self, display, tile_position, label, progress, duration):
        tile_size = self.game.TILE_SIZE
        world_x, world_y = self.map.absolute_tile_to_world(*tile_position)
        screen_x = world_x - self.camera.offset.x
        screen_y = world_y - self.camera.offset.y - 30

        font = self.game.assets[Fonts.BODY]
        text = font.render(label, True, (255, 230, 120))
        text_rect = text.get_rect(center=(screen_x + tile_size // 2, screen_y))

        bg = pygame.Surface((text_rect.width + 12, text_rect.height + 6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        display.blit(bg, (text_rect.x - 6, text_rect.y - 3))
        display.blit(text, text_rect)

        if duration > 0 and progress > 0:
            ratio = min(progress / duration, 1.0)
            bar_w, bar_h = 40, 6
            bx = text_rect.centerx - bar_w // 2
            by = text_rect.bottom + 4
            pygame.draw.rect(display, (40, 40, 40), (bx, by, bar_w, bar_h))
            pygame.draw.rect(display, (100, 255, 100), (bx, by, int(bar_w * ratio), bar_h))
            pygame.draw.rect(display, (10, 10, 10), (bx, by, bar_w, bar_h), 1)

    def draw_mats_display(self, display):
        font = self.game.assets[Fonts.HEADER]
        icons = self.game.assets.get(Animation.RESOURCE_ICONS, {})

        mats = [ResourceType.GEAR, ResourceType.PLATE, ResourceType.ENGINE]
        x = 10
        y = 50  # sits below the existing cash display

        for resource_type in mats:
            icon = icons.get(resource_type)
            count = self.economy.get_resource_count(resource_type)
            icon_w = icon.get_width() if icon is not None else 20
            icon_h = icon.get_height() if icon is not None else 20

            text = font.render(str(count), True, (100, 100, 100))
            text_h = text.get_height()

            row_h = max(icon_h, text_h)
            total_w = icon_w + 4 + text.get_width()

            bg = pygame.Surface((total_w + 16, row_h + 10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            display.blit(bg, (x - 8, y - 5))

            if icon is not None:
                display.blit(icon, (x, y + (row_h - icon_h) // 2))
            display.blit(text, (x + icon_w + 4, y + (row_h - text_h) // 2))

            y += row_h + 14


    # SHOP DISPLAY
    def draw_shop_gui(self, display):
        self.shop_gui.draw_shop_gui(display)

    def draw_workshop_gui(self, display):
        self.workshop_gui.draw(display)

    # for debugging
    def show_all_obstacles(self, display):
        if not self.debug_mode:
            return

        # static obstacles (these are dev defined obstacles)
        for obstacle in self.map.obstacles:
            screen_x = obstacle.x - self.camera.offset.x
            screen_y = obstacle.y - self.camera.offset.y
            rect = pygame.Rect(screen_x, screen_y, obstacle.width, obstacle.height)
            pygame.draw.rect(display, (255, 0, 255), rect, 2)

        # player's mmmmmm feet collision box
        feet_height = 8
        feet_width_inset = 8
        feet_x = self.player.rect.x + feet_width_inset - self.camera.offset.x
        feet_y = self.player.rect.bottom - feet_height - self.camera.offset.y
        feet_width = self.player.rect.width - feet_width_inset * 2
        feet_rect = pygame.Rect(feet_x, feet_y, feet_width, feet_height)
        pygame.draw.rect(display, (0, 255, 0), feet_rect, 2)