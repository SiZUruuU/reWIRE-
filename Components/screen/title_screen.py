from .states import State as Base
from .test_world import TestWorld

class TitleScreen(Base):
    def __init__(self, game):
        #print("TitleScreen initialized")
        Base.__init__(self, game)

    def update(self, delta_time, actions):
        if actions["space"]:            
            new_state = TestWorld(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, display):
        display.fill((255, 255, 255))
        self.game.draw_text(display, "Title Screen demo", (0, 0, 0), self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)
        self.game.draw_text(display, "press 'SPACE' to proceed to test world", (0, 0, 0), self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 + 30)
