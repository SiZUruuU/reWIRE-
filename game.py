import pygame, os, time
from component.screen.title_screen import TitleScreen
from component.utils import EntityType, Animation, Direction, Fonts, ResourceType
from component.utils.enums import AudioType, OST, SFX
from component.utils.audio import AudioComp

class Game:
    def __init__(self):
        # Initalize pygame:
        pygame.mixer.pre_init(48000, -16, 2, 2158, None)
        pygame.init()

        # Set dimension values:
        # game world size
        self.GAME_WIDTH, self.GAME_HEIGHT = 384, 192        
        self.TILE_SIZE = 32
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
            "RMB":False,

            "key_b":False, #Build mode
            "key_r":False, #Conveyer rotate key
            "key_q":False, #Clear hotbar key
            "key_f":False, #Item spawn test key WOOD
            "key_g":False, #Item spawn test key STONE

            "key_1":False,
            "key_2":False,
            "key_3":False,
            "key_4":False,
            "key_5":False,
            "key_6":False,
            "key_7":False,
            "key_8":False,
            "key_9":False,
            "key_0":False,

            "sfx_played":False
        }

        # Timers:
        # delta time for frame-rate independence
        self.delta_time, self.prev_time = 0, time.time()
        # clock to limit fps
        self.clock = pygame.time.Clock()
        # global timer for animations sync
        self.global_time = 0

        # Game state:
        # Stack data struct, push() and pop()
        self.state_stack = []

        self.assets = {}
        # load stuff:
        # os.path.join() for asset dir
        self.load_assets()
        # load states to stack, must be in order
        self.load_states()
        AudioComp(self)

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
                if event.button == 3:
                    self.action_keys["RMB"] = True

            # MOUSEBUTTONUP events
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.action_keys["LMB"] = False
                if event.button == 3:
                    self.action_keys["RMB"] = False                    
                
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
                if event.key == pygame.K_r:
                    self.action_keys["key_r"] = True
                if event.key == pygame.K_q:
                    self.action_keys["key_q"] = True
                if event.key == pygame.K_0:
                    self.action_keys["key_0"] = True
                
                # item spawn test
                if event.key == pygame.K_f:
                    self.action_keys["key_f"] = True
                if event.key == pygame.K_g:
                    self.action_keys["key_g"] = True

                # number keys
                if event.key == pygame.K_1:
                    self.action_keys["key_1"] = True
                if event.key == pygame.K_2:
                    self.action_keys["key_2"] = True
                if event.key == pygame.K_3:
                    self.action_keys["key_3"] = True
                if event.key == pygame.K_4:
                    self.action_keys["key_4"] = True
                if event.key == pygame.K_5:
                    self.action_keys["key_5"] = True
                if event.key == pygame.K_6:
                    self.action_keys["key_6"] = True
                if event.key == pygame.K_7:
                    self.action_keys["key_7"] = True
                if event.key == pygame.K_8:
                    self.action_keys["key_8"] = True
                if event.key == pygame.K_9:
                    self.action_keys["key_9"] = True

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
                    self.action_keys["Lshift"] = False

    # delta time calculation
    def get_delta_time(self):
        current_time = time.time()
        self.delta_time = current_time - self.prev_time
        self.prev_time = current_time

    # global update loop
    def update(self):
        self.global_time = pygame.time.get_ticks() / 1000.0 # convert to seconds
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
        main_font = self.assets[Fonts.TITLE]
        text_surface = main_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    # handle asset loading
    def load_assets(self):
        self.assets_dir = os.path.join("asset")
        self.sprite_dir = os.path.join(self.assets_dir, "sprites")
        self.font_dir = os.path.join(self.assets_dir, "fonts")
        self.sfx_dir = os.path.join(self.assets_dir, "sfx")
        self.ost_dir = os.path.join(self.assets_dir, "ost")
        
        # load fonts:
        self.assets[Fonts.TITLE] = pygame.font.Font(os.path.join(self.font_dir, "retganon.ttf"), 18)
        self.assets[Fonts.HEADER] = pygame.font.Font(os.path.join(self.font_dir, "HomeVideo-Bold.ttf"), 12)
        self.assets[Fonts.BODY] = pygame.font.Font(os.path.join(self.font_dir, "reindeer-typewriter.ttf"), 8)

        # load sfx
        self.assets[AudioType.SFX] = {
            SFX.HOVER : pygame.mixer.Sound(os.path.join(self.sfx_dir, "hover_SFX.mp3")),
            SFX.HOTBAR_SELECT :  pygame.mixer.Sound(os.path.join(self.sfx_dir, "hotbar-select_v2_SFX.ogg")),
        }

        # load ost 
        self.assets[AudioType.OST] = {
            OST.TITLE : pygame.mixer.Sound(os.path.join(self.ost_dir, "OST #1 Original + Extended.mp3"))
        }
        # load sprites
        # player:
        self.assets[EntityType.PLAYER] = {
            Animation.RUN : self.load_frames(
                os.path.join(self.sprite_dir, "player_spritesheet.png"),
                0, 46, 32, 46, 8),
            Animation.IDLE : self.load_frames(
                os.path.join(self.sprite_dir, "player_spritesheet.png"),
                0, 46*2, 32, 46, 5),
        }

        # resources:
        self.assets[EntityType.RESOURCE] = {
            ResourceType.WOOD : self.load_frame(os.path.join(self.sprite_dir, "wood.png")),
            ResourceType.BOARDS : self.load_frame(os.path.join(self.sprite_dir, "boards.png")),
            ResourceType.CHARCOAL : self.load_frame(os.path.join(self.sprite_dir, "charcoal.png")),
            ResourceType.STONE : self.load_frame(os.path.join(self.sprite_dir, "stone.png")),
            ResourceType.STONE_BLOCKS : self.load_frame(os.path.join(self.sprite_dir, "stone_blocks.png")),
            ResourceType.GLASS : self.load_frame(os.path.join(self.sprite_dir, "glass.png")),
            ResourceType.SAND : self.load_frame(os.path.join(self.sprite_dir, "sand.png")),
        }

        # conveyor belt:
        conveyor_horizontal = self.load_frames(
            os.path.join(self.sprite_dir, "conveyor_spritesheet.png"),
            0, 0, 32, 32, 5            
        )
        conveyor_vertical = [pygame.transform.rotate(f, 90) for f in conveyor_horizontal]
        conveyor_corner = self.load_frames(
            os.path.join(self.sprite_dir, "conveyor_spritesheet.png"),
            0, 32, 32, 32, 5
        )
        conveyor_corner_f = [pygame.transform.flip(f, True, False) for f in conveyor_corner]

        self.assets[EntityType.CONVEYOR] = {
            Animation.STRAIGHT : {
                Direction.NORTH : conveyor_vertical,
                Direction.SOUTH : [pygame.transform.flip(f, False, True) for f in conveyor_vertical],
                Direction.EAST : conveyor_horizontal,
                Direction.WEST : [pygame.transform.flip(f, True, False) for f in conveyor_horizontal],
            },
            Animation.CORNER : {
                # clockwise:
                Animation.BOTRIGHT : [pygame.transform.rotate(f, 90) for f in conveyor_corner_f],
                Animation.TOPLEFT : [pygame.transform.rotate(f, -90) for f in conveyor_corner_f],
                Animation.TOPRIGHT : [pygame.transform.rotate(f, -180) for f in conveyor_corner_f],
                Animation.BOTLEFT : conveyor_corner_f,
                # counter-clockwise:
                Animation.TOPLEFT_F : [pygame.transform.rotate(f, 180) for f in conveyor_corner],
                Animation.BOTLEFT_F : [pygame.transform.rotate(f, 270) for f in conveyor_corner],
                Animation.TOPRIGHT_F : [pygame.transform.rotate(f, 90) for f in conveyor_corner],
                Animation.BOTRIGHT_F : conveyor_corner
            }
        }        

        # buzzsaw:
        buzzsaw = self.load_frames(
            os.path.join(self.sprite_dir, "buzzsaw_spritesheet.png"),
            0, 0, 34, 32, 5
        )
        self.assets[EntityType.BUZZSAW] = {
            Animation.STRAIGHT : {
                Direction.NORTH : [pygame.transform.rotate(f, 90) for f in buzzsaw],
                Direction.SOUTH : [pygame.transform.rotate(f, -90) for f in buzzsaw],
                Direction.EAST : buzzsaw,
                Direction.WEST : [pygame.transform.flip(f, True, False) for f in buzzsaw],
            }
        }

        #crusher
        crusher = self.load_frames(
            os.path.join(self.sprite_dir, "crusher_spritesheet.png"),
            0, 0, 34, 32, 15
        )
        self.assets[EntityType.CRUSHER] = {
            Animation.STRAIGHT : {
                Direction.NORTH : [pygame.transform.rotate(f, 90) for f in crusher],
                Direction.SOUTH : [pygame.transform.rotate(f, -90) for f in crusher],
                Direction.EAST : buzzsaw,
                Direction.WEST : [pygame.transform.flip(f, True, False) for f in crusher],
            }
        }

        # furnace
        furnace = self.load_frames(
            os.path.join(self.sprite_dir, "furnace_spritesheet.png"),
            0, 0, 34, 64, 3
        )
        furnace_f = self.load_frames(
            os.path.join(self.sprite_dir, "furnace_spritesheet.png"),
            0, 64, 34, 64, 3
        )
        self.assets[EntityType.FURNACE] = {
            Animation.STRAIGHT : {
                Direction.NORTH : [pygame.transform.rotate(f, -90) for f in furnace],
                Direction.SOUTH : [pygame.transform.rotate(f, 90) for f in furnace],
                Direction.EAST : [pygame.transform.flip(f, True, False) for f in furnace],
                Direction.WEST : furnace,
            },
            Animation.ACTIVE : {
                Direction.NORTH : [pygame.transform.rotate(f, -270) for f in furnace_f],
                Direction.SOUTH : [pygame.transform.rotate(f, -180) for f in furnace_f],
                Direction.EAST : [pygame.transform.rotate(f, -90) for f in furnace_f],
                Direction.WEST : furnace_f,
            }
        }

        # sellbox
        sellbox = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
        sellbox.fill((50, 200, 50))
        sellbox_frame = [sellbox]

        self.assets[EntityType.SELLBOX] = {
            Animation.STRAIGHT: {
                Direction.NORTH: sellbox_frame,
                Direction.SOUTH: sellbox_frame,
                Direction.EAST: sellbox_frame,
                Direction.WEST: sellbox_frame,
            }
        }

        # wood generator
        wood_gen = self.load_frames(
            os.path.join(self.sprite_dir, "wood_generator_spritesheet.png"),
            0, 0, 64, 34, 3
        )

        self.assets[EntityType.WOOD_GENERATOR] = {
            Animation.STRAIGHT: {
                Direction.NORTH: [pygame.transform.rotate(f, -90) for f in wood_gen],
                Direction.SOUTH: [pygame.transform.rotate(f, 90) for f in wood_gen],
                Direction.EAST: [pygame.transform.flip(f, True, False) for f in wood_gen],
                Direction.WEST: wood_gen,
            }
        }

        # stone generator
        stone_gen = self.load_frames(
            os.path.join(self.sprite_dir, "stone_generator_spritesheet.png"),
            0, 0, 63, 64, 3
        )
        stone_gen_f = self.load_frames(
            os.path.join(self.sprite_dir, "stone_generator_spritesheet.png"),
            63*3, 0, 63, 64, 3
        )

        self.assets[EntityType.STONE_GENERATOR] = {
            Animation.STRAIGHT: {
                Direction.NORTH: [pygame.transform.rotate(f, -90) for f in stone_gen],
                Direction.SOUTH: [pygame.transform.rotate(f, 90) for f in stone_gen],
                Direction.EAST: [pygame.transform.flip(f, True, False) for f in stone_gen],
                Direction.WEST: stone_gen,
            },
            Animation.ACTIVE: {
                Direction.NORTH: [pygame.transform.rotate(f, -90) for f in stone_gen_f],
                Direction.SOUTH: [pygame.transform.rotate(f, 90) for f in stone_gen_f],
                Direction.EAST: [pygame.transform.flip(f, True, False) for f in stone_gen_f],
                Direction.WEST: stone_gen_f,
            }
        }

    # helper method for loading assets:
    def load_frames(self, filename, x, y, width, height, amount):
        sprite_sheet = pygame.image.load(filename).convert_alpha()
        frames = []
        for i in range(amount):
            frame = sprite_sheet.subsurface(pygame.Rect(x+(i*width), y, width, height))
            frames.append(frame)
        return frames
    
    def load_frame(self, filename):
        return pygame.image.load(filename).convert_alpha()

    # starting game state, preferably 'Title Screen'
    def load_states(self):
        #initialize
        self.title_screen = TitleScreen(self)

        # add to stack
        self.state_stack.append(self.title_screen)

    # reset action key state to 'False'
    def reset_key(self, action):
        self.action_keys[action] = False

    def reset_allkeys(self):
        for key in self.action_keys:
            self.action_keys[key] = False

# entry point
if __name__ == "__main__":
    game = Game()
    while game.isRunning:
        game.game_loop()
        game.clock.tick(60)
        pygame.display.set_caption(f"FPS: {int(game.clock.get_fps())}")