from ...utils import EntityType, ResourceType

MACHINE_RECIPES = {
    EntityType.CONVEYOR: {ResourceType.GEAR: 3, ResourceType.PLATE: 3},
    EntityType.BUZZSAW: {ResourceType.ENGINE: 1, ResourceType.GEAR: 3, ResourceType.PLATE: 2},
    EntityType.CRUSHER: {ResourceType.ENGINE: 1, ResourceType.GEAR: 6, ResourceType.PLATE: 10},
    EntityType.FURNACE: {ResourceType.ENGINE: 1, ResourceType.GEAR: 12, ResourceType.PLATE: 20},
    EntityType.WOOD_GENERATOR: {ResourceType.ENGINE: 2, ResourceType.GEAR: 30, ResourceType.PLATE: 30},
    EntityType.STONE_GENERATOR: {ResourceType.ENGINE: 3, ResourceType.GEAR: 50, ResourceType.PLATE: 50},
}

# cost to buy parts
SHOP_PRICES = {
    ResourceType.GEAR: 2,
    ResourceType.PLATE: 3,
    ResourceType.ENGINE: 25,
}