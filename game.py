import pygame, os, time

class Game:
    def __init__(self):
        # initalize pygame
        pygame.init()

        # configs #
        # game world size
        self.GAME_WIDTH, self.GAME_HEIGHT = 600, 320
        # upscale size
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.GAME_WIDTH*2, self.GAME_HEIGHT*2
        # game world and screen set-up
        self.game_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # game loop flags
        self.isRunning, self.isPlaying = True, True
        # action key dictionary
        self.action_key = {
            "left":False,
            "right":False,
            "up":False,
            "down":False,
            "interact":False,
            "space":False
        }
        # delta time for frame-rate independence
        self.delta_time, self.prev_time = 0, 0
        self.load_assets()

    # main game loop
    def game_loop(self):
        self.get_delta_time()
        self.poll_events()
        self.update()
        self.render()

    # handle poll events and key inputs
    def poll_events(self):
        for event in pygame.event.get():
            # Decorator event
            if event.type == pygame.QUIT:
                self.isRunning = False
                self.isPlaying = False

            # KEYDOWN events                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isPlaying = False
                if event.key == pygame.K_w:
                    self.action_key["up"] == True
                if event.key == pygame.K_a:
                    self.action_key["left"] == True
                if event.key == pygame.K_s:
                    self.action_key["down"] == True
                if event.key == pygame.K_d:
                    self.action_key["right"] == True
                if event.key == pygame.K_SPACE:
                    self.action_key["space"] == True
                if event.key == pygame.K_e:
                    self.action_key["interact"] == True

            # KEYUP events
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.isPlaying = False
                if event.key == pygame.K_w:
                    self.action_key["up"] == False
                if event.key == pygame.K_a:
                    self.action_key["left"] == False
                if event.key == pygame.K_s:
                    self.action_key["down"] == False
                if event.key == pygame.K_d:
                    self.action_key["right"] == False
                if event.key == pygame.K_SPACE:
                    self.action_key["space"] == False
                if event.key == pygame.K_e:
                    self.action_key["interact"] == False

    def get_delta_time(self):
        current_time = time.time()
        self.delta_time = current_time - self.prev_time
        self.prev_time = current_time

    # logic update
    def update(self):
        pass

    # render update
    def render(self):
        # upscale the game world to the screen dimensions
        self.screen.blit(pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0, 0))
        # swap buffers
        pygame.display.flip()

    def load_assets(self):
        self.assets_dir = os.path.join("Assets")
        self.sprite_dir = os.path.join(self.assets_dir, "sprites")
        self.font_dir = os.path.join(self.assets_dir, "fonts")
        self.header_font = None

if __name__ == "__main__":
    game = Game()
    while game.isRunning:
        game.game_loop()