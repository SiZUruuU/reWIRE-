import pygame
from .states import State as Base
from .level_factory import FactoryLevel
from .level_office import OfficeLevel
from ..utils import Animation, Layers, Fonts, get_scaled_mouse_pos
from component.utils.enums import AudioType, OST, SFX
from component.utils.audio import AudioComp

# shift configs, how far should the images move
BG_MAX_SHIFT_X = 12
BG_MAX_SHIFT_Y = 6
CHAR_MAX_SHIFT_X = 18
CHAR_MAX_SHIFT_Y = 9

PARALLAX_SMOOTHING = 10

# for darkening overlay effect when lookin up
MAX_DARKEN_ALPHA = 10

# button configs
BUTTON_SIZE = (80, 30)
BUTTON_GAP = 20

class TitleScreen(Base):
    def __init__(self, game):
        super().__init__(game)

        self.background = game.assets[Animation.TITLE_SCREEN][Layers.FLOOR_0]
        self.character = game.assets[Animation.TITLE_SCREEN][Layers.MIDDLE_0]
        self.foreground = game.assets[Animation.TITLE_SCREEN][Layers.FRONT_0]

        self.ost = AudioComp(game)
        self.ost.play_ost(AudioType.OST, OST.TITLE)

        # base smoothing offsets (start centered)
        self.bg_offset = pygame.Vector2(0, 0)
        self.char_offset = pygame.Vector2(0, 0)

        self.darken_overlay = pygame.Surface((game.GAME_WIDTH, game.GAME_HEIGHT), pygame.SRCALPHA)

        self.buttons = self.build_buttons()

    def update(self, delta_time, actions):
        self.update_parallax(delta_time)
        self.handle_button_clicks(actions)


    def update_parallax(self, delta_time):
        mx, my = pygame.mouse.get_pos()
        # normalize mouse position to -1 to 1 range relative to screen center
        scaled_x, scaled_y = get_scaled_mouse_pos(self.game)

        norm_x = (scaled_x - self.game.GAME_WIDTH / 2) / (self.game.GAME_WIDTH / 2)
        norm_y = (scaled_y - self.game.GAME_HEIGHT / 2) / (self.game.GAME_HEIGHT / 2)
        norm_x = max(-1.0, min(1.0, norm_x))
        norm_y = max(-1.0, min(1.0, norm_y))

        target_bg = pygame.Vector2(norm_x * BG_MAX_SHIFT_X, norm_y * BG_MAX_SHIFT_Y)
        target_char = pygame.Vector2(norm_x * CHAR_MAX_SHIFT_X, norm_y * CHAR_MAX_SHIFT_Y)

        # smoothly move towards the target
        t = min(PARALLAX_SMOOTHING * delta_time, 1.0)
        self.bg_offset += (target_bg - self.bg_offset) * t
        self.char_offset += (target_char - self.char_offset) * t

        # darken based on vertical mouse look
        self._darken_strength = abs(norm_y)

    def render(self, display):
        bg_pos = (
            (self.game.GAME_WIDTH - self.background.get_width()) // 2 + self.bg_offset.x,
            (self.game.GAME_HEIGHT - self.background.get_height()) // 2 + self.bg_offset.y,
        )
        display.blit(self.background, bg_pos)

        char_pos = (
            (self.game.GAME_WIDTH - self.character.get_width()) // 2 + self.char_offset.x,
            (self.game.GAME_HEIGHT - self.character.get_height()) // 2 + self.char_offset.y,
        )
        display.blit(self.character, char_pos)

        # darken overlay (vertical mouse look)
        alpha = int(MAX_DARKEN_ALPHA * getattr(self, "_darken_strength", 0.0))
        if alpha > 0:
            self.darken_overlay.fill((0, 0, 0, alpha))
            display.blit(self.darken_overlay, (0, 0))

        # foreground remains 
        fg_pos = (
            (self.game.GAME_WIDTH - self.foreground.get_width()) // 2,
            (self.game.GAME_HEIGHT - self.foreground.get_height()) // 2,
        )
        display.blit(self.foreground, fg_pos)
        # buttons 
        self.draw_button(display, self.buttons["play"], "PLAY", (80, 100, 50, 100))
        self.draw_button(display, self.buttons["exit"], "EXIT", (100, 50, 0, 100))

    def build_buttons(self):
        cx = 120
        cy = 150

        play_rect = pygame.Rect(0, 0, *BUTTON_SIZE)
        play_rect.center = (cx, cy)

        exit_rect = pygame.Rect(0, 0, *BUTTON_SIZE)
        exit_rect.center = (cx, cy + BUTTON_SIZE[1] + BUTTON_GAP)

        return {
            "play": play_rect,
            "exit": exit_rect,
        }

    def draw_button(self, display, rect, label, color=(255,255,255,100)):
        col = color
        mx, my = get_scaled_mouse_pos(self.game)
        if rect.collidepoint(mx, my):
            col = (255, 255, 255)
        
        pygame.draw.rect(display, col, rect)
        pygame.draw.rect(display, (255, 255, 255), rect, 2)
        
        font = self.game.assets[Fonts.HEADER]
        text = font.render(label, True, (255, 255, 255))
        display.blit(text, text.get_rect(center=rect.center))

    def handle_button_clicks(self, actions):
        if not actions["LMB"]:
            return
        mx, my = get_scaled_mouse_pos(self.game)

        if self.buttons["play"].collidepoint(mx, my):
            self.game.reset_key("LMB")
            AudioComp.play_sfx(self, AudioType.SFX, SFX.CLICK)
            self.ost.stop_ost()
            def do_transition():
                #new_state = OfficeLevel(self.game) # for debugging
                new_state = FactoryLevel(self.game)
                new_state.enter_state()
            self.game.fade_trans.start(do_transition)
        elif self.buttons["exit"].collidepoint(mx, my):
            AudioComp.stop_ost(self)
            self.game.reset_key("LMB")
            self.game.isRunning = False
            self.game.isPlaying = False