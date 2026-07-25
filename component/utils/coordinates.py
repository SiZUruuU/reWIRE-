import pygame

def get_world_mousePos(game, camera):
    # base values:
    mx, my = pygame.mouse.get_pos()
    game_w = game.GAME_WIDTH
    game_h = game.GAME_HEIGHT
    screen_w = game.SCREEN_WIDTH
    screen_h = game.SCREEN_HEIGHT

    # handle mouse pos with respect to screen and game display:
    scaled_x = mx * (game_w / screen_w)
    scaled_y = my * (game_h / screen_h)

    # apply camera offset:
    # getattr basically automates if a camera has an offset or not
    # and use a default value if there are no offsets def=(Vector2(0,0))
    offset = getattr(camera, 'offset', pygame.Vector2(0, 0))
    world_x = scaled_x + offset.x
    world_y = scaled_y + offset.y

    return {
        "world_x": world_x,
        "world_y": world_y,
    }

def check_tile_at(world_x, world_y, game, world_map):
    tile_x, tile_y = world_map.world_to_tile(world_x, world_y)
    if tile_x < 0 or tile_y < 0:
        return None
    try:
        tile = world_map.grid[tile_x][tile_y]
    except IndexError:
        return None
    return tile

def get_scaled_mouse_pos(game):
    mx, my = pygame.mouse.get_pos()
    scaled_x = mx * (game.GAME_WIDTH / game.SCREEN_WIDTH)
    scaled_y = my * (game.GAME_HEIGHT / game.SCREEN_HEIGHT)
    return scaled_x, scaled_y