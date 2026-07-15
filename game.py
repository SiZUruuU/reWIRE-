import pygame

# intializtions
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

# game loop var
isRunning:bool = pygame.display.get_init()

# game loop
while isRunning:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
    
    # clear color
    screen.fill((0, 0, 0))

    # renderer

    # swaps buffer
    pygame.display.flip()

    clock.tick(60) # limits FPS
pygame.quit()