import pygame
from ..entity import BaseEntity
from ...utils import EntityType, Animation

class PlayerEntity(BaseEntity):
    def __init__(self, position, world, entity_type: EntityType):
        super().__init__(position, world, entity_type)
        self.width, self.height = 64, 64        

        # sprite flags
        self.facing_right = False
        self.facing_back = False        

        # animation settings:
        self.animations = {
            Animation.RUN : world.game.assets[EntityType.PLAYER][Animation.RUN]
        }
        self.animation_speed = 12
        self.image = self.animations[Animation.RUN][0]
        self.rect = self.image.get_rect(topleft=(position.x,position.y))        

        # player attributes
        self.speed = 50


    def update(self, global_time, delta_time, actions):
        # input key actions
        self.handle_input(actions)

        # update position:
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        frame = self.get_frame_animation(Animation.RUN, global_time)  
        if self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

        # update bounding box:
        self.rect.topleft = (round(self.position.x), round(self.position.y))


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