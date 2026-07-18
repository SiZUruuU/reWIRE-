from enum import Enum, auto

class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

class EntityType(Enum):
# Entity = automatic int values
    NONE = auto()
    PLAYER = auto()
    CONVEYOR = auto()

class Animation(Enum):
    # for player:
    IDLE = auto()
    RUN = auto()
    
    STRAIGHT = auto()
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

class Fonts(Enum):
    TITLE = auto()
    HEADER = auto()
    BODY = auto()