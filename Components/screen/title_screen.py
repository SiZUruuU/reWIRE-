from states import State as Base

class TitleScreen(Base):
    def __init__(self, game):
        self.game = game

    def update(self, delta_time, actions):
        pass

    def render(self, surface):
        pass