import pygame

class Camera:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)
    
    def update(self, target):
        x = int(self.game.GAME_WIDTH/2) - target.rect.center_x
        y = int(self.game.GAME_HEIGHT/2) - target.rect.center_y