from ...utils import EntityType, ResourceType

MACHINE_RECIPES = {
    EntityType.CONVEYOR: {ResourceType.GEAR: 5, ResourceType.PLATE: 3},
    EntityType.BUZZSAW: {ResourceType.ENGINE: 1, ResourceType.GEAR: 8, ResourceType.PLATE: 10},
    EntityType.CRUSHER: {ResourceType.ENGINE: 2, ResourceType.GEAR: 10, ResourceType.PLATE: 15},
    EntityType.FURNACE: {ResourceType.ENGINE: 2, ResourceType.GEAR: 12, ResourceType.PLATE: 20},
    EntityType.WOOD_GENERATOR: {ResourceType.ENGINE: 2, ResourceType.GEAR: 30, ResourceType.PLATE: 30},
    EntityType.STONE_GENERATOR: {ResourceType.ENGINE: 3, ResourceType.GEAR: 50, ResourceType.PLATE: 50},
}

# cost to buy parts
SHOP_PRICES = {
    ResourceType.GEAR: 0.99,
    ResourceType.PLATE: 2.59,
    ResourceType.ENGINE: 14.99,
}