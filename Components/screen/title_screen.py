from .states import State as Base
from .test_world import TestWorld

class TitleScreen(Base):
    def __init__(self, game):
        # intialize using the parent __init__
        super().__init__(game)

    def update(self, delta_time, actions):
        # condition check to move next screen
        if actions["space"]:
            new_state = TestWorld(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, display):
        display.fill((255, 255, 255))
        self.game.draw_text(display, "Title Screen demo", (0, 0, 0), self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)
        self.game.draw_text(display, "press 'SPACE' to proceed to test world", (0, 0, 0), self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 + 30)
