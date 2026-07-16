from .states import State as Base

class TitleScreen(Base):
    def __init__(self, game):
        #print("TitleScreen initialized")
        Base.__init__(self, game)

    def update(self, delta_time, actions):
        self.game.reset_keys()

    def render(self, display):
        display.fill((255, 255, 255))
        self.game.draw_text(display, "Title Screen demo", (0, 0, 0), self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)
