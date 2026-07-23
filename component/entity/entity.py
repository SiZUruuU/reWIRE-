from abc import ABC, abstractmethod
from ..utils import EntityType
import pygame

# ABSTRACT CLASS FOR ENTITIES
class BaseEntity(ABC, pygame.sprite.Sprite):
    def __init__(self, position: pygame.Vector2, world, entity_type: EntityType):
        # weird bug I found, so to fix layering we need to set the ._layer first
        # before doing super().__init__()
        self._layer = entity_type.layer
        super().__init__(world.all_sprites)
        self.entity_type = entity_type
        self.position = position
        self.world = world

        # Default values, override if you want to
        self.image = pygame.Surface((world.game.TILE_SIZE, world.game.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(position.x, position.y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # specific for machines and generators
        self.direction = pygame.Vector2(0, 0)
        self.output_offset = (0, 0)
        
        self.animations = {}
        self.current_frame = 0
        self.animation_speed = 0
        
    @abstractmethod
    def update(self, global_time, delta_time, actions):
        pass

    def get_frame_animation(self, state, global_time):
        # checks if there's only one animation type:
        if state is None:
            total = len(self.animations)
            frame = int(global_time * self.animation_speed) % total
            return self.animations[frame]
        else:
            frames = self.animations[state]
            total = len(frames)
            frame = int(global_time * self.animation_speed) % total
            return frames[frame]


    def set_layout(self, animation_type, key):
        self.animations = self.world.game.assets[self.entity_type][animation_type][key]
        self.image = self.animations[0]

    # Use only when necessary (machines)
    def rotate_offset(self, offset):
        dir_int = (int(self.direction.x), int(self.direction.y))
        rotations = {
            (-1, 0): lambda ox, oy: (ox, oy),
            (0, -1): lambda ox, oy: (-oy, ox),
            (1, 0):  lambda ox, oy: (-ox, -oy),
            (0, 1):  lambda ox, oy: (oy, -ox),
        }
        transform = rotations.get(dir_int, lambda ox, oy: (ox, oy))
        return transform(*offset)
    
    def rotate_footprint_offset(self, offset):
        dir_int = (int(self.direction.x), int(self.direction.y))
        rotations = {
            (-1, 0): lambda ox, oy: (ox, oy),
            (0, -1): lambda ox, oy: (-oy, ox),
            (1, 0):  lambda ox, oy: (-ox, -oy),
            (0, 1):  lambda ox, oy: (oy, -ox),
        }
        transform = rotations.get(dir_int, lambda ox, oy: (ox, oy))

        fw, fh = getattr(self, "footprint", (1, 1))
        base_offset = [(dx, dy) for dx in range(fw) for dy in range(fh)]
        transformed_all = [transform(ox, oy) for ox, oy in base_offset]
        min_x = min(t[0] for t in transformed_all)
        min_y = min(t[1] for t in transformed_all)

        tx, ty = transform(*offset)
        return (tx - min_x, ty - min_y)

    def rotate_continuous_offset(self, point):
        dir_int = (int(self.direction.x), int(self.direction.y))
        rotations = {
            (-1, 0): lambda ox, oy: (ox, oy),
            (0, -1): lambda ox, oy: (-oy, ox),
            (1, 0):  lambda ox, oy: (-ox, -oy),
            (0, 1):  lambda ox, oy: (oy, -ox),
        }
        transform = rotations.get(dir_int, lambda ox, oy: (ox, oy))

        fw, fh = getattr(self, "footprint", (1, 1))
        corners = [(0, 0), (fw, 0), (0, fh), (fw, fh)]
        transformed_corners = [transform(cx, cy) for cx, cy in corners]
        min_x = min(c[0] for c in transformed_corners)
        min_y = min(c[1] for c in transformed_corners)

        px, py = transform(*point)
        return (px - min_x, py - min_y)

    def get_output_position(self):
        size = self.world.game.TILE_SIZE
        rotated = self.rotate_footprint_offset(self.output_offset)
        origin = self.position + pygame.Vector2(rotated[0]*size, rotated[1]*size)
        return origin + self.direction * size

    def rect_from_covered_tiles(self, covered_tiles):
        size = self.world.game.TILE_SIZE
        min_x = min(tx for tx, ty in covered_tiles) * size
        min_y = min(ty for tx, ty in covered_tiles) * size
        max_x = (max(tx for tx, ty in covered_tiles) + 1) * size
        max_y = (max(ty for tx, ty in covered_tiles) + 1) * size
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def get_rotated_image(self, base_frame, direction):
        angle_by_direction = {
            (-1, 0): 0, (0, -1): 90, (1, 0): 180, (0, 1): 270,
        }
        dir_int = (int(direction.x), int(direction.y))
        angle = angle_by_direction.get(dir_int, 0)
        return pygame.transform.rotate(base_frame, angle)