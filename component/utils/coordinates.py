import pygame

def get_world_mousePos(game, camera):
    # base values:
    mx, my = pygame.mouse.get_pos()
    game_w = game.GAME_WIDTH
    game_h = game.GAME_HEIGHT
    screen_w = game.SCREEN_WIDTH
    screen_h = game.SCREEN_HEIGHT
    tile_s = game.TILE_SIZE

    # handle mouse pos with respect to screen and game display:
    scaled_x = mx * (game_w/screen_w)
    scaled_y = my * (game_h/screen_h)

    # apply camera offset:
    # getattr basically automates if a camera has an offset or not
    # and use a default value if there are no offsets def=(Vector2(0,0))
    offset = getattr(camera, 'offset', pygame.Vector2(0,0))
    world_x = scaled_x + int(offset.x)
    world_y = scaled_y + int(offset.y)

    # convert processed mouse pos to respect the 32x32 world grid:
    tile_x = int(world_x//tile_s) # becomes a number divisible by 32 (tile_h)
    tile_y = int(world_y//tile_s)

    # ex: returns world coords at {x32, y32} tile coords at tile[1][1]
    # use tile_x/y for index and world_x/y for world coordinates
    return {
            "tile_x": tile_x, 
            "tile_y": tile_y, 
            "world_x": tile_x * tile_s,
            "world_y": tile_y * tile_s
            }

def check_tile_at(world_x, world_y, game, grid_map):
    tile_x = int(world_x // game.TILE_SIZE)
    tile_y = int(world_y // game.TILE_SIZE)
    if tile_x < 0 or tile_y < 0:
        return None
    try:
        tile = grid_map[tile_x][tile_y]
    except IndexError:
        return None
    return tile