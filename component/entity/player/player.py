import pygame
from ..base_entity import BaseEntity
from ...utils import Animation, EntityType

class Player(BaseEntity):
    def __init__(self, x, y, world):
        # initialize with parent class
        super().__init__(world)
        self.x, self.y = x, y
        self.width, self.height = 64, 64
        # player attributes
        self.velocity = pygame.Vector2()
        self.speed = 50
        # sprite flags
        self.facing_right = False
        self.facing_back = False        

        self.animations = {
            Animation.RUN : world.game.assets[EntityType.PLAYER][Animation.RUN]
        }        

        self.image = self.animations[Animation.RUN][0]
        self.rect = self.image.get_rect(topleft=(x,y))

        self.animation_speed = 12
        
    def update(self, global_time, delta_time, actions):
        # input key actions
        self.handle_input(actions)

        # update position:
        self.x += self.velocity.x * delta_time
        self.y += self.velocity.y * delta_time

        frame = self.get_frame_animation(Animation.RUN, global_time)  
        if self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

        # update bounding box:
        self.rect.topleft = (round(self.x), round(self.y))

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