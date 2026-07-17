import pygame
from .base_entity import BaseEntity

class Player(BaseEntity):
    def __init__(self, x, y, groups):
        # initialize with parent class
        super().__init__(groups)
        # set starting pos
        self.x, self.y = x, y
        # set size
        self.width, self.height = 64, 64
        # display size, can be used for collisions
        self.image = pygame.image.load("asset/sprites/player/base.png").convert_alpha()
        # bounding box, sets topleft as origin
        self.rect = self.image.get_rect(topleft=(x,y))

        # animation
        self.animations = {}
        self.current_frame = 0
        self.animation_speed = .3

        # load sprite animations
        self.load_animations()

        # sprite flags
        self.facing_right = False
        self.facing_back = False

        # player attributes
        self.velocity = pygame.Vector2()
        self.speed = 50

    # player key inputs
    def handle_input(self, actions):
        # turn key actions into 1, -1 and 0 in a Vector2
        direction = pygame.Vector2(
            # x-axis: right = 1, left = -1
            actions["right"] - actions["left"],
            # y-axis: down = 1, up = -1
            actions["down"] - actions["up"]
        )
        # change flag based on direction
        if direction.x > 0:
            self.facing_right = True
        if direction.x < 0:
            self.facing_right = False            
        # check if there's movement:
        if direction.length_squared() > 0:
            # normalize vector, basically clamp it from -1.0 to 1.0
            # so when pressing both "up" and "right" won't go beyond 1.0
            direction = direction.normalize()

        # finally update velocity:
        self.velocity = direction * self.speed

    def load_animations(self):
        self.animations[1] = self.load_frames("asset/sprites/player/run_spritesheet.png", 0, 0, 32, 46, 8)
        
    def update(self, global_time, delta_time, actions):
        # input key actions
        self.handle_input(actions)

        # update position:
        self.x += self.velocity.x * delta_time
        self.y += self.velocity.y * delta_time

        # update animation:
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.animations[1]):
            self.current_frame = 0
        frame = self.animations[1][int(self.current_frame)]
        
        if self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
            
        self.image = frame

        # update bounding box:
        self.rect.topleft = (round(self.x), round(self.y))
