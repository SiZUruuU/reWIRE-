from ..utils import WorldType, Layers
from pygame import draw, Surface, SRCALPHA, Rect

class OfficeMap:
    def __init__(self, world):
        self.world = world
        self.tile_size = world.game.TILE_SIZE

        self.background = world.game.assets[WorldType.OFFICE][Layers.FLOOR_0]
        self.background_pos = (0, 0)

        self.foreground = world.game.assets[WorldType.OFFICE][Layers.FRONT_1]
        self.foreground.set_alpha(180)
        self.foreground_pos = (0, 0)

        self.bounds = Rect(48, 16, world.WIDTH - 96, world.HEIGHT - 64)
        self.obstacles = [
            Rect(32, 32, 80, 30), # tool cabinet
            Rect(48, 78, 48, 18), # workshop table
            Rect(224, 64, 16, 32), # desk part 1
            Rect(224, 78, 48, 16), # desk part 2
            Rect(32, 160, 80, 32), # bed
        ]

    def clamp_to_bounds(self, rect):
        clamped = rect.copy()
        clamped.left = max(self.bounds.left, min(clamped.left, self.bounds.right - clamped.width))
        clamped.top = max(self.bounds.top, min(clamped.top, self.bounds.bottom - clamped.height))
        return clamped

    def draw(self, display, camera):
        screen_x = self.background_pos[0] - camera.offset.x
        screen_y = self.background_pos[1] - camera.offset.y
        display.blit(self.background, (screen_x, screen_y))

    def draw_foreground(self, display, camera):
        fg_x = self.foreground_pos[0] - camera.offset.x
        fg_y = self.foreground_pos[1] - camera.offset.y
        display.blit(self.foreground, (fg_x, fg_y))

    def world_to_absolute_tile(self, world_x, world_y):
        return int(world_x // self.tile_size), int(world_y // self.tile_size)

    def absolute_tile_to_world(self, tile_x, tile_y):
        return (tile_x * self.tile_size, tile_y * self.tile_size)
    
    def resolve_collisions(self, player_rect, prev_rect):
        # feet feet feet 
        feet_height = 8
        feet_rect = Rect(
            player_rect.x, player_rect.bottom - feet_height,
            player_rect.width, feet_height
        )
        prev_feet_rect = Rect(
            prev_rect.x, prev_rect.bottom - feet_height,
            prev_rect.width, feet_height
        )

        for obstacle in self.obstacles:
            if not feet_rect.colliderect(obstacle):
                continue

            test_rect = Rect(feet_rect.x, prev_feet_rect.y, feet_rect.width, feet_rect.height)
            if test_rect.colliderect(obstacle):
                if feet_rect.centerx < obstacle.centerx:
                    feet_rect.right = obstacle.left
                else:
                    feet_rect.left = obstacle.right

            test_rect = Rect(feet_rect.x, feet_rect.y, feet_rect.width, feet_rect.height)
            if test_rect.colliderect(obstacle):
                if feet_rect.centery < obstacle.centery:
                    feet_rect.bottom = obstacle.top
                else:
                    feet_rect.top = obstacle.bottom

        resolved = player_rect.copy()
        resolved.x = feet_rect.x
        resolved.y = feet_rect.y - (player_rect.height - feet_height)
        return resolved