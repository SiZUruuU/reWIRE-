import pygame

class State:

    def __init__(self, game):
        self.game = game
        self.entityState = {
            "walk": True,
            "run": False,
            "jump": False,
            "action": False,
        }
        
        self.moveDir = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        self.moveSpd = 2
        self.runSpd = self.moveSpd * 2

    def actions(self):
        pass

    def movementCalc(self):
        pass
   