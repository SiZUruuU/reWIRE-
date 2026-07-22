from ...utils import ResourceType, EntityType

# all types of generator right here
GENERATOR_DATA = {
    EntityType.WOOD_GENERATOR : {
        "resource_type": ResourceType.WOOD, 
        "cooldown": 3.5, # cooldown to produce the next resource
        "footprint": (2, 1) # if you haven't seen machine.py footprint is essentially the amount of tiles a macine occupies
    },
    EntityType.STONE_GENERATOR : {
        "resource_type": ResourceType.STONE,
        "cooldown": 5.0,
        "footprint": (1, 1)
    }
}