import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, groups):
        pygame.sprite.Sprite.__init__(self, groups)
        self.x, self.y = x, y
        self.width, self.height = 64, 64
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = 10
        self.moveSpd = 0

    def action_handle(self, action):
        #Handles sprint
        if action["Lshift"]:
            self.moveSpd = self.speed * 2
        elif not action["Lshift"]:
            self.moveSpd = self.speed

        if action["up"]:
            self.y -= self.moveSpd
        if action["down"]:
            self.y += self.moveSpd
        if action["left"]:
            self.x -= self.moveSpd
        if action["right"]:
            self.x += self.moveSpd
        if action["interact"]:
            pass #Interact action
