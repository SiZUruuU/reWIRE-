import pygame
from .states import State
from ..utils import Fonts, AudioType, SFX

class LoseScreen(State):
    def __init__(self, game):        
        super().__init__(game)
        self.game.audio_handler.play_sfx(AudioType.SFX, SFX.LOSS, 1.0)

    def update(self, delta_time, actions):
        if actions["key_enter"]:
            self.game.reset_key("key_enter")
            prev = self.prev_state

            def do_transition():
                self.game.audio_handler.stop_ost()
                self.exit_state()
                prev.exit_state()
            self.game.fade_trans.start(do_transition)

    def render(self, display):
        display.fill((30, 10, 10))
        font = self.game.assets[Fonts.HEADER]
        text = font.render("QUOTA NOT MET - Press ENTER to return to title", False, (255, 90, 90))
        text_rect = text.get_rect(center=(self.game.GAME_WIDTH // 2, self.game.GAME_HEIGHT // 2))
        display.blit(text, text_rect)