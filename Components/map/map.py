from abc import ABC, abstractmethod

class BaseMap(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def draw(self, display, camera):
        pass