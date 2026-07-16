import pygame

class Camera:
    def __init__(self, target, width, height):
        self.target = target
        self.offset = pygame.Vector2()
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)
    
    def setmethod(self, style):
        self.style = style
    
    def scroll(self, delta_time):
        self.style.scroll(delta_time)
