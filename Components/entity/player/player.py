import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, groups):
        # initialize with parent class
        super().__init__(groups)
        # set starting pos
        self.x, self.y = x, y
        # set size
        self.width, self.height = 64, 64
        # display size, can be used for collisions
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 255, 0))
        # bounding box, sets topleft as origin
        self.rect = self.image.get_rect(topleft=(x,y))

        # player attributes
        self.velocity = pygame.Vector2()
        self.speed = 100

    # player key inputs
    def handle_input(self, actions):
        # turn key actions into 1, -1 and 0 in a Vector2
        direction = pygame.Vector2(
            # x-axis: right = 1, left = -1
            actions["right"] - actions["left"],
            # y-axis: down = 1, up = -1
            actions["down"] - actions["up"]
        )
        # check if there's movement:
        if direction.length_squared() > 0:
            # normalize vector, basically clamp it from -1.0 to 1.0
            # so when pressing both "up" and "right" won't go beyond 1.0
            direction = direction.normalize()
        # finally update velocity:
        self.velocity = direction * self.speed
    
    def update(self, delta_time, actions):
        self.handle_input(actions)
        # update position:
        self.x += self.velocity.x * delta_time
        self.y += self.velocity.y * delta_time
        # update bounding box:
        self.rect.topleft = (round(self.x), round(self.y))