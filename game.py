import pygame, os, time
from Components.screen.title_screen import TitleScreen

class Game:
    def __init__(self):
        # initalize pygame
        pygame.init()

        # configs #
        # game world size
        self.GAME_WIDTH, self.GAME_HEIGHT = 640, 320
        # tile size
        self.TILE_WIDTH, self.TILE_HEIGHT = 32, 32
        # upscale size
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.GAME_WIDTH*2, self.GAME_HEIGHT*2
        # game world and screen set-up
        self.game_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # game loop flags
        self.isRunning, self.isPlaying = True, True
        # action key dictionary
        self.action_keys = {
            "left":False,
            "right":False,
            "up":False,
            "down":False,
            "interact":False,
            "space":False,
            "Lshift": False
        }
        # delta time for frame-rate independence
        self.delta_time, self.prev_time = 0, 0
        # Stack data struct, push() and pop()
        self.state_stack = []
        # os.path.join() for asset dir
        self.load_assets()
        # load states to stack, must be in order
        self.load_states()

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
                    self.action_keys["up"] = True
                if event.key == pygame.K_a:
                    self.action_keys["left"] = True
                if event.key == pygame.K_s:
                    self.action_keys["down"] = True
                if event.key == pygame.K_d:
                    self.action_keys["right"] = True
                if event.key == pygame.K_SPACE: 
                    self.action_keys["space"] = True                    
                if event.key == pygame.K_e:
                    self.action_keys["interact"] = True
                if event.key == pygame.K_LSHIFT:
                    self.action_keys["Lshift"] = True

            # KEYUP events
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.isPlaying = False
                if event.key == pygame.K_w:
                    self.action_keys["up"] = False
                if event.key == pygame.K_a:
                    self.action_keys["left"] = False
                if event.key == pygame.K_s:
                    self.action_keys["down"] = False
                if event.key == pygame.K_d:
                    self.action_keys["right"] = False
                if event.key == pygame.K_SPACE:
                    self.action_keys["space"] = False                    
                if event.key == pygame.K_e:
                    self.action_keys["interact"] = False
                if event.key == pygame.K_LSHIFT:
                    self.action_keys["Lshift"] = True

    def get_delta_time(self):
        current_time = time.time()
        self.delta_time = current_time - self.prev_time
        self.prev_time = current_time

    # logic update
    def update(self):
        # peek the top and update
        self.state_stack[-1].update(self.delta_time, self.action_keys)

    # render update
    def render(self):
        # RENDER
        self.state_stack[-1].render(self.game_canvas)

        # upscale the game world to the screen dimensions
        self.screen.blit(pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0, 0))        
        # swap buffers
        pygame.display.flip()

    # handle text drawing on screen
    def draw_text(self, surface, text, color, x, y):
        text_surface = self.main_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    # handle asset loading
    def load_assets(self):
        self.assets_dir = os.path.join("Assets")
        self.sprite_dir = os.path.join(self.assets_dir, "sprites")
        self.font_dir = os.path.join(self.assets_dir, "fonts")
        self.main_font = pygame.font.Font(os.path.join(self.font_dir, "retganon.ttf"), 18)

    # add states to the stack
    def load_states(self):
        #initialize
        self.title_screen = TitleScreen(self)

        # add to stack
        self.state_stack.append(self.title_screen)

    # reset all action key state to 'False'
    def reset_keys(self):
        for action in self.action_keys:
            self.action_keys[action] ==  False

# entry point
if __name__ == "__main__":
    game = Game()
    while game.isRunning:
        game.game_loop()