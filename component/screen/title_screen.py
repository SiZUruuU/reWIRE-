from .states import State as Base
from .level_factory import FactoryLevel
from .level_office import OfficeLevel

class TitleScreen(Base):
    def __init__(self, game):
        # intialize using the parent __init__
        super().__init__(game)

    def update(self, delta_time, actions):
        # condition check to move next screen
        if actions["space"]:
            new_state = FactoryLevel(self.game)
            #new_state = OfficeLevel(self.game)
            new_state.enter_state()
        self.game.reset_key("space")

    def render(self, display):
        display.fill((255, 255, 255))
        self.game.draw_text(display, "Title Screen demo", (0, 0, 0), self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)
        self.game.draw_text(display, "press 'SPACE' to proceed play test", (0, 0, 0), self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2 + 30)
