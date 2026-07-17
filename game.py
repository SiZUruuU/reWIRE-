import pygame, os, time
from component.screen.title_screen import TitleScreen

class Game:
    def __init__(self):
        # Initalize pygame:
        pygame.init()

        # Set dimension values:
        # game world size
        self.GAME_WIDTH, self.GAME_HEIGHT = 384, 192
        # tile size
        self.TILE_WIDTH, self.TILE_HEIGHT = 32, 32
        # upscale size - basically just thrice the game surface
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.GAME_WIDTH*3, self.GAME_HEIGHT*3

        # Create game world and display surface:
        # game_canvas is where the game logic happens so use this for world coords
        self.game_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
        # screen is simply the upscaled version of game_canvas
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Game loop flags:
        self.isRunning, self.isPlaying = True, True

        # Action keys dict:
        self.action_keys = {
            "left":False,
            "right":False,
            "up":False,
            "down":False,
            "interact":False,
            "space":False,
            "Lshift":False,
            "LMB":False,
            "b_key":False, #Build mode
            "r_key":False #Conveyer rotate key
        }

        # Timers:
        # delta time for frame-rate independence
        self.delta_time, self.prev_time = 0, 0
        # clock to limit fps
        self.clock = pygame.time.Clock()
        # global timer for animations sync
        self.global_time = 0

        # Game state:
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

            # MOUSEBUTTONDOWN events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.action_keys["LMB"] = True

            # MOUSEBUTTONUP events
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.action_keys["LMB"] = False

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

    # delta time calculation
    def get_delta_time(self):
        current_time = time.time()
        self.delta_time = current_time - self.prev_time
        self.prev_time = current_time

    # global update loop
    def update(self):
        self.global_time = pygame.time.get_ticks()
        # peek the top and update
        self.state_stack[-1].update(self.delta_time, self.action_keys)

    # global render loop
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
        self.assets_dir = os.path.join("asset")
        self.sprite_dir = os.path.join(self.assets_dir, "sprites")
        self.font_dir = os.path.join(self.assets_dir, "fonts")
        self.main_font = pygame.font.Font(os.path.join(self.font_dir, "retganon.ttf"), 18)

    # starting game state, preferably 'Title Screen'
    def load_states(self):
        #initialize
        self.title_screen = TitleScreen(self)

        # add to stack
        self.state_stack.append(self.title_screen)

    # reset all action key state to 'False'
    def reset_keys(self):
        for action in self.action_keys:
            self.action_keys[action] = False

# entry point
if __name__ == "__main__":
    game = Game()
    while game.isRunning:
        game.game_loop()
        game.clock.tick(60)
        pygame.display.set_caption(f"FPS: {int(game.clock.get_fps())}")
