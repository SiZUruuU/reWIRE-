import pygame
from ...entity import MACHINE_RECIPES, SHOP_PRICES
from ...utils import get_scaled_mouse_pos, Fonts, Animation, EntityType

WORKSHOP_PANEL_SIZE = (576, 288)
WORKSHOP_SCREEN_PADDING = {"north": 80, "south": 32, "east": 32, "west": 32}

WORKSHOP_ICON_BG_COLOR = (91, 110, 225, 100)
WORKSHOP_ICON_SIZE = 64

WORKSHOP_CLOSE_BUTTON = (544, 8, 24, 24)

WORKSHOP_ARROW_LEFT = (40, 140, 28, 44)
WORKSHOP_ARROW_RIGHT = (508, 140, 28, 44)

WORKSHOP_ICON_POS = (110, 96, 64, 64)
WORKSHOP_LABEL_POS = (190, 98)
WORKSHOP_OWNED_POS = (190, 118)
WORKSHOP_MATS_START = (190, 140)
WORKSHOP_MATS_LINE_HEIGHT = 22
WORKSHOP_CRAFT_BUTTON = (190, 216, 90, 28)

WORKSHOP_DESC_POS = (328, 116)
WORKSHOP_DESC_MAX_WIDTH = 170
WORKSHOP_DESC_LINE_HEIGHT = 16

WORKSHOP_COLOR_LABEL = (255, 255, 255)
WORKSHOP_COLOR_OWNED = (100,190, 100)
WORKSHOP_COLOR_MATS = (180, 200, 200)
WORKSHOP_COLOR_CRAFT_BORDER = (255, 255, 255)
WORKSHOP_COLOR_CRAFT_TEXT = (255, 255, 255)
WORKSHOP_COLOR_CRAFT_DISABLED_BORDER = (70, 85, 195)
WORKSHOP_COLOR_CRAFT_DISABLED_TEXT = (70, 85, 155)
WORKSHOP_COLOR_CLOSE = (200, 60, 60)
WORKSHOP_COLOR_CLOSE_TEXT = (255, 255, 255)
WORKSHOP_COLOR_ARROW = (255, 255, 255)
WORKSHOP_COLOR_ARROW_DISABLED = (90, 90, 90)
WORKSHOP_COLOR_DESCRIPTION = (10, 50, 20)

MACHINE_DESCRIPTIONS = {
    EntityType.CONVEYOR: "Moves resources from one machine to another.",
    EntityType.BUZZSAW: "Cuts wood into boards, or breaks stone into blocks.",
    EntityType.CRUSHER: "Crushes stone into sand for glassmaking.",
    EntityType.FURNACE: "Smelts materials using fuel to produce metals and glass.",
    EntityType.WOOD_GENERATOR: "Automatically produces wood over time.",
    EntityType.STONE_GENERATOR: "Automatically produces stone, but needs charcoal fuel to run.",
}

class WorkshopGUI:
    def __init__(self, level):
        self.level = level
        self.game = level.game
        self.machine_items = list(MACHINE_RECIPES.keys())
        self.selected_index = 0

    ## LAYOUT ##
    def get_layout(self):
        panel = pygame.Rect(
            self.game.GAME_WIDTH // 2 - WORKSHOP_PANEL_SIZE[0] // 2,
            self.game.GAME_HEIGHT // 2 - WORKSHOP_PANEL_SIZE[1] // 2,
            *WORKSHOP_PANEL_SIZE
        )

        def to_rect(offset):
            ox, oy, w, h = offset
            return pygame.Rect(panel.x + ox, panel.y + oy, w, h)

        def to_pos(offset):
            ox, oy = offset
            return (panel.x + ox, panel.y + oy)

        return {
            "panel": panel,
            "icon_rect": to_rect(WORKSHOP_ICON_POS),
            "label_pos": to_pos(WORKSHOP_LABEL_POS),
            "owned_pos": to_pos(WORKSHOP_OWNED_POS),
            "mats_start": to_pos(WORKSHOP_MATS_START),
            "craft_rect": to_rect(WORKSHOP_CRAFT_BUTTON),
            "arrow_left_rect": to_rect(WORKSHOP_ARROW_LEFT),
            "arrow_right_rect": to_rect(WORKSHOP_ARROW_RIGHT),
            "close_rect": to_rect(WORKSHOP_CLOSE_BUTTON),
            "desc_pos": to_pos(WORKSHOP_DESC_POS),
        }

    @property
    def selected_entity_type(self):
        return self.machine_items[self.selected_index]

    def handle_input(self, actions):
        if actions["key_r"] and actions["Lshift"]:
            self.cycle(-1)
            self.game.reset_key("key_r")
        elif actions["key_r"]:
            self.cycle(1)
            self.game.reset_key("key_r")

        self.handle_click(actions)

    def cycle(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.machine_items)

    def handle_click(self, actions):
        if not actions["LMB"]:
            return

        mx, my = get_scaled_mouse_pos(self.game)
        layout = self.get_layout()

        if layout["close_rect"].collidepoint(mx, my):
            self.level.workshop_open = False
            self.game.reset_key("LMB")
            return

        if layout["arrow_left_rect"].collidepoint(mx, my):
            self.cycle(-1)
            self.game.reset_key("LMB")
            return

        if layout["arrow_right_rect"].collidepoint(mx, my):
            self.cycle(1)
            self.game.reset_key("LMB")
            return

        if layout["craft_rect"].collidepoint(mx, my):
            self.try_craft(self.selected_entity_type)
            self.game.reset_key("LMB")
            return

    def try_craft(self, entity_type):
        recipe = MACHINE_RECIPES[entity_type]
        economy = self.level.economy
        if economy.spend_resources(recipe):
            self.level.machine_inventory.add(entity_type)

    def draw(self, display):
        layout = self.get_layout()
        panel = layout["panel"]
        font_head = self.game.assets[Fonts.HEADER]
        font_body = self.game.assets[Fonts.BODY]
        icons = self.game.assets.get(Animation.ICONS_BLUEPRINT, {})
        mat_icons = self.game.assets.get(Animation.RESOURCE_ICONS, {})
        economy = self.level.economy

        display.blit(self.game.assets[Animation.WORKSHOP_PANEL], panel.topleft)

        entity_type = self.selected_entity_type
        recipe = MACHINE_RECIPES[entity_type]

        # full-size icon with background
        pygame.draw.rect(display, WORKSHOP_ICON_BG_COLOR, layout["icon_rect"])
        icon = icons.get(entity_type)
        if icon is not None:
            display.blit(icon, layout["icon_rect"].topleft)

        label = font_head.render(entity_type.type.upper(), True, WORKSHOP_COLOR_LABEL)
        display.blit(label, layout["label_pos"])

        owned_count = self.level.machine_inventory.get_count(entity_type)
        owned = font_head.render(f"owned: {owned_count}", True, WORKSHOP_COLOR_OWNED)
        display.blit(owned, layout["owned_pos"])

        mat_x, mat_y = layout["mats_start"]
        for resource_type, amount in recipe.items():
            if amount <= 0:
                continue
            line_x = mat_x
            mat_icon = mat_icons.get(resource_type)
            if mat_icon is not None:
                display.blit(mat_icon, (line_x, mat_y - 2))
                line_x += mat_icon.get_width() + 6
            amt_text = font_head.render(f"{resource_type.value} x{amount}", True, WORKSHOP_COLOR_MATS)
            display.blit(amt_text, (line_x, mat_y))
            mat_y += WORKSHOP_MATS_LINE_HEIGHT

        # craft button
        can_craft = economy.can_afford(recipe)
        border_color = WORKSHOP_COLOR_CRAFT_BORDER if can_craft else WORKSHOP_COLOR_CRAFT_DISABLED_BORDER
        text_color = WORKSHOP_COLOR_CRAFT_TEXT if can_craft else WORKSHOP_COLOR_CRAFT_DISABLED_TEXT
        pygame.draw.rect(display, border_color, layout["craft_rect"], 2)
        craft_text = font_head.render("CRAFT", True, text_color)
        display.blit(craft_text, craft_text.get_rect(center=layout["craft_rect"].center))

        # description
        description = MACHINE_DESCRIPTIONS.get(entity_type, "")
        self.draw_wrapped_text(
            display, description, layout["desc_pos"],
            WORKSHOP_DESC_MAX_WIDTH, WORKSHOP_DESC_LINE_HEIGHT,
            WORKSHOP_COLOR_DESCRIPTION, font_body
        )

        # nav arrows
        self.draw_arrow(display, layout["arrow_left_rect"], "left")
        self.draw_arrow(display, layout["arrow_right_rect"], "right")

        # position indicator
        pos_text = font_head.render(f"{self.selected_index + 1} / {len(self.machine_items)}", True, WORKSHOP_COLOR_LABEL)
        display.blit(pos_text, pos_text.get_rect(midtop=(panel.centerx, panel.y + WORKSHOP_SCREEN_PADDING["north"] - 20)))

        # close button
        pygame.draw.rect(display, WORKSHOP_COLOR_CLOSE, layout["close_rect"])
        x_text = font_head.render("X", True, WORKSHOP_COLOR_CLOSE_TEXT)
        display.blit(x_text, x_text.get_rect(center=layout["close_rect"].center))

    def draw_arrow(self, display, rect, direction):
        pygame.draw.rect(display, WORKSHOP_COLOR_ARROW, rect, 2)
        cx, cy = rect.center
        size = 8
        if direction == "left":
            points = [(cx + size, cy - size), (cx + size, cy + size), (cx - size, cy)]
        else:
            points = [(cx - size, cy - size), (cx - size, cy + size), (cx + size, cy)]
        pygame.draw.polygon(display, WORKSHOP_COLOR_ARROW, points)

    def draw_wrapped_text(self, display, text, pos, max_width, line_height, color, font):
            words = text.split(" ")
            lines = []
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            x, y = pos
            for line in lines:
                rendered = font.render(line, True, color)
                display.blit(rendered, (x, y))
                y += line_height