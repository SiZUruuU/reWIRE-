import pygame
from Components.game import Game as game

# game loop
while game.isRunning:
    # poll for events
    game.poll_events()

    # logic
    game.update()

    # renderer
    game.render()

pygame.quit()