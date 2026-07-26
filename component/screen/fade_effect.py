import pygame

class FadeTransition:
    def __init__(self, game, duration=3.0):
        self.game = game
        self.duration = duration
        self.timer = 0.0
        self.phase = None
        self.on_midpoint = None

        self.overlay = pygame.Surface((game.GAME_WIDTH, game.GAME_HEIGHT))
        self.overlay.fill((0, 0, 0))

    def start(self, on_midpoint):
        self.phase = "out"
        self.timer = 0.0
        self.on_midpoint = on_midpoint

    @property
    def is_active(self):
        return self.phase is not None

    def update(self, delta_time):
        if self.phase is None:
            return

        self.timer += delta_time
        half = self.duration / 2

        if self.phase == "out" and self.timer >= half:
            if self.on_midpoint is not None:
                self.on_midpoint()
                self.on_midpoint = None
            self.phase = "in"
            self.timer = 0.0
        elif self.phase == "in" and self.timer >= half:
            self.phase = None

    def draw(self, display):
        if self.phase is None:
            return
        half = self.duration / 2
        progress = min(self.timer / half, 1.0) if half > 0 else 1.0

        if self.phase == "out":
            alpha = int(255 * progress)
        else:
            alpha = int(255 * (1.0 - progress))

        self.overlay.set_alpha(alpha)
        display.blit(self.overlay, (0, 0))