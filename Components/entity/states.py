import pygame

class State:

    def __init__(self, game, actions):
        self.game = game        
        self.moveDir = actions

    def walk(self):
        pass

    def run(self):
        pass
    

   