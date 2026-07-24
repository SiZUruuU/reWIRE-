import pygame
from .states import State
from ..utils import Fonts

class LoseScreen(State):
    def __init__(self, game):
        super().__init__(game)

    def update(self, delta_time, actions):
        if actions["key_enter"]:
            self.game.reset_key("key_enter")
            self.exit_state()
            self.prev_state.exit_state()

    def render(self, display):
        display.fill((15, 10, 10))
        font = self.game.assets[Fonts.HEADER]
        text = font.render("QUOTA NOT MET - Press ENTER to return to title", True, (255, 90, 90))
        text_rect = text.get_rect(center=(self.game.GAME_WIDTH // 2, self.game.GAME_HEIGHT // 2))
        display.blit(text, text_rect)