from enum import Enum, auto

class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

class Layers(Enum):
    FLOOR_0 = 0 # floor entities
    FLOOR_1 = 1 # for resources
    MIDDLE_0 = 2
    MIDDLE_1 = 3
    FRONT_0 = 4
    FRONT_1 = 5

class EntityType(Enum):
    NONE = ("none", None)
    PLAYER = ("player", Layers.FRONT_0)

    CONVEYOR = ("conveyor", Layers.FLOOR_0)

    RESOURCE = ("resource", Layers.FLOOR_1)

    BUZZSAW = ("buzzsaw", Layers.MIDDLE_0)
    CRUSHER = ("cruhser", Layers.MIDDLE_0)
    FURNACE = ("furnace", Layers.MIDDLE_0)

    GENERATOR = ("generator", Layers.MIDDLE_1)
    WOOD_GENERATOR = ("wood_generator", Layers.MIDDLE_1)
    STONE_GENERATOR = ("stone_generator", Layers.MIDDLE_1)

    # special dev item, 999 robux
    SELLBOX = ("sellbox", Layers.FLOOR_0)

    def __init__(self, type, layer):
        self.type = type
        # apparently 0 is not an int AHAHHHAHA
        # adjusted it to to use .value to make sure it's an int data type
        self._layer = layer.value if (layer is not None) else None
    
    @property
    def layer(self):
        return self._layer

class WorldType(Enum):
    FACTORY = "factory"
    OFFICE = "office"

class ResourceType(Enum):
    WOOD = "wood"
    BOARDS = "boards"

    STONE = "stone"
    STONE_BLOCKS = "stone_block"

    SAND = "sand"
    GLASS = "glass"

    CHARCOAL = "charcoal"

    # These resources are for the economoy features:
    GEAR = "gear"
    PLATE = "plate"
    ENGINE = "engine"
    
class Animation(Enum):
    # for player:
    IDLE = auto()
    RUN = auto()
    
    STRAIGHT = auto()
    ACTIVE = auto()
    INACTIVE = auto()
    # specifically for conveyors
    CORNER = auto()
    BOTLEFT = auto()
    BOTLEFT_F = auto()
    TOPLEFT = auto()
    TOPLEFT_F = auto()
    TOPRIGHT = auto()
    TOPRIGHT_F = auto()
    BOTRIGHT = auto()
    BOTRIGHT_F = auto()

    ICONS = auto()
    ICONS_BLUEPRINT = auto()
    RESOURCE_ICONS = auto()
    SHOP_PANEL = auto()
    WORKSHOP_PANEL = auto()
    REWIRE_BOX_PANEL = auto()
    MANUAL_PANEL_PAGES = auto()
    TITLE_SCREEN = auto()

class Fonts(Enum):
    TITLE = auto()
    HEADER = auto()
    BODY = auto()

class AudioType(Enum):
    SFX = "sfx"
    OST = "ost"
    ENTITY = "entity"
    
class SFX(Enum):
    HOVER = auto()
    CLICK = auto()
    WALK = auto()
    HOTBAR_SELECT = auto()
    MACHINE_BROKEN = auto()
    MACHINE_PLACED = auto()
    BUZZSAW = auto()
    CRUSHER = auto()
    CONVEYER = auto()
    FURNACE = auto()
    GENERATOR = auto()
    LOSS = auto()
    SELL = auto()
    PICKUP = auto()

class OST(Enum):
    TITLE = auto()
    OFFICE = auto()
    FACTORY = auto()