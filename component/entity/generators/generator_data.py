from utils import ResourceType

# all types of generator right here
GENERATOR_DATA = {
    "wood": {
        "resource_type": ResourceType.WOOD, 
        "cooldown": 2.0, # cooldown to produce the next resource
        "footprint": (2, 1) # if you haven't seen machine.py footprint is essentially the amount of tiles a macine occupies
    },
    "stone": {
        "resource_type": ResourceType.STONE,
        "cooldown": 3.0,
        "footprint": (1, 1)
    }
}