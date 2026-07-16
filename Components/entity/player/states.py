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
        for event in pygame.event.get():
            if event.key == pygame.KEYDOWN:
                #Entity movement directions
                if event.key == pygame.K_w:
                    self.moveDir["up"] = True
                if event.key == pygame.K_s:
                    self.moveDir["down"] = True
                if event.key == pygame.K_a:
                    self.moveDir["left"] = True
                if event.key == pygame.K_d:
                    self.moveDir["right"] = True
                #Entity State
                if event.key == pygame.K_LSHIFT:
                    self.entityState["run"] = True
                    self.entityState["walk"] = False

            if event.key == pygame.KEYUP:
                #Entity movement directions
                if event.key == pygame.K_w:
                    self.moveDir["up"] = False
                if event.key == pygame.K_s:
                    self.moveDir["down"] = False
                if event.key == pygame.K_a:
                    self.moveDir["left"] = False
                if event.key == pygame.K_d:
                    self.moveDir["right"] = False
                #Entity State
                if event.key == pygame.K_LSHIFT:
                    self.entityState["run"] = False
                    self.entityState["walk"] = True

    def movementCalc(self):
        pass 
   