import pygame
from ...entity import SHOP_PRICES, MACHINE_RECIPES
from ...utils import get_scaled_mouse_pos, Fonts, Animation

SHOP_PANEL_SIZE = (576, 288)

SHOP_SCREEN_PADDING = {"north": 16, "south": 32, "east": 16, "west": 16}

SHOP_CLOSE_BUTTON = (544, 2, 20, 20)
SHOP_BUY_BUTTON   = (228, 260, 120, 24)

SHOP_CART_START = (384, 96)
SHOP_CART_LINE_HEIGHT = 26

# compact rows
# so the whole row reads as one unit instead of spanning the screen
SHOP_ROWS = [
    {
        "icon": (32, 40, 64, 64),
        "label_offset": (100, 42),
        "owned_offset": (100, 60),
        "dec":   (100, 80, 18, 18),
        "inc1":  (122, 80, 18, 18),
        "inc5":  (144, 80, 18, 18),
        "inc10": (166, 80, 18, 18),
    },
    {
        "icon": (32, 116, 64, 64),
        "label_offset": (100, 118),
        "owned_offset": (100, 136),
        "dec":   (100, 156, 18, 18),
        "inc1":  (122, 156, 18, 18),
        "inc5":  (144, 156, 18, 18),
        "inc10": (166, 156, 18, 18),
    },
    {
        "icon": (32, 192, 64, 64),
        "label_offset": (100, 194),
        "owned_offset": (100, 212),
        "dec":   (100, 232, 18, 18),
        "inc1":  (122, 232, 18, 18),
        "inc5":  (144, 232, 18, 18),
        "inc10": (166, 232, 18, 18),
    },
]


SHOP_COLOR_SCREEN_LABEL = (25, 30, 45)
SHOP_COLOR_SCREEN_OWNED = (70, 75, 95)
SHOP_COLOR_SCREEN_CASH  = (20, 90, 40)
SHOP_COLOR_SCREEN_CART_ITEM  = (25, 30, 45)
SHOP_COLOR_SCREEN_CART_EMPTY = (110, 115, 130)

SHOP_COLOR_DEC_BUTTON = (60, 60, 70)
SHOP_COLOR_INC_BUTTON = (60, 80, 60)
SHOP_COLOR_BUTTON_BORDER = (200, 200, 200)
SHOP_COLOR_BUTTON_ARROW = (255, 255, 255)
SHOP_COLOR_AMOUNT_LABEL = (200, 255, 200)

SHOP_COLOR_BEZEL_CLOSE = (200, 60, 60)
SHOP_COLOR_BEZEL_CLOSE_TEXT = (255, 255, 255)
SHOP_COLOR_BEZEL_BUY_ENABLED = (100, 200, 100)
SHOP_COLOR_BEZEL_BUY_DISABLED = (90, 90, 90)
SHOP_COLOR_BEZEL_BUY_TEXT = (20, 20, 20)

SHOP_COLOR_FALLBACK_ICON = (90, 90, 110)
SHOP_COLOR_FALLBACK_ICON_BORDER = (200, 200, 200)

SHOP_CASH_HEADER_POS = (32, 20)


class ShopGUI:
    def __init__(self, world):
        self.world = world
        self.game = world.game
        self.shop_items = list(SHOP_PRICES.keys())
        self.cart = {}

    def get_shop_layout(self):
        panel = pygame.Rect(
            self.game.GAME_WIDTH // 2 - SHOP_PANEL_SIZE[0] // 2,
            self.game.GAME_HEIGHT // 2 - SHOP_PANEL_SIZE[1] // 2,
            *SHOP_PANEL_SIZE
        )

        def to_rect(offset):
            ox, oy, w, h = offset
            return pygame.Rect(panel.x + ox, panel.y + oy, w, h)

        def to_pos(offset):
            ox, oy = offset
            return (panel.x + ox, panel.y + oy)

        rows = []
        for i, resource_type in enumerate(self.shop_items):
            cfg = SHOP_ROWS[i]
            rows.append({
                "resource_type": resource_type,
                "icon_rect": to_rect(cfg["icon"]),
                "dec_rect": to_rect(cfg["dec"]),
                "inc1_rect": to_rect(cfg["inc1"]),
                "inc5_rect": to_rect(cfg["inc5"]),
                "inc10_rect": to_rect(cfg["inc10"]),
                "label_pos": to_pos(cfg["label_offset"]),
                "owned_pos": to_pos(cfg["owned_offset"]),
            })

        return {
            "panel": panel,
            "rows": rows,
            "buy_rect": to_rect(SHOP_BUY_BUTTON),
            "close_rect": to_rect(SHOP_CLOSE_BUTTON),
            "cart_start": to_pos(SHOP_CART_START),
        }

    ## INPUT ##
    def handle_shop_click(self, actions):
        if not actions["LMB"]:
            return

        mx, my = get_scaled_mouse_pos(self.game)
        layout = self.get_shop_layout()

        if layout["close_rect"].collidepoint(mx, my):
            self.world.desk_open = False
            self.cart = {}
            self.game.reset_key("LMB")
            return

        if layout["buy_rect"].collidepoint(mx, my):
            self.try_buy_cart()
            self.game.reset_key("LMB")
            return

        for row in layout["rows"]:
            rt = row["resource_type"]
            if row["dec_rect"].collidepoint(mx, my):
                self.adjust_cart(rt, -1)
            elif row["inc1_rect"].collidepoint(mx, my):
                self.adjust_cart(rt, 1)
            elif row["inc5_rect"].collidepoint(mx, my):
                self.adjust_cart(rt, 5)
            elif row["inc10_rect"].collidepoint(mx, my):
                self.adjust_cart(rt, 10)
            else:
                continue
            self.game.reset_key("LMB")
            return

    def adjust_cart(self, resource_type, amount):
        current = self.cart.get(resource_type, 0)
        new_amount = max(0, current + amount)
        if new_amount == 0:
            self.cart.pop(resource_type, None)
        else:
            self.cart[resource_type] = new_amount

    def try_buy_cart(self):
        total_cost = sum(SHOP_PRICES[rt] * amt for rt, amt in self.cart.items())
        if self.world.economy.spend_cash(total_cost):
            for rt, amt in self.cart.items():
                self.world.economy.add_resource(rt, amt)
            self.cart = {}

    def clear_cart(self):
        self.cart = {}

    ## DRAW ##
    def draw_shop_gui(self, display):
        layout = self.get_shop_layout()
        panel = layout["panel"]
        font = self.game.assets[Fonts.BODY]
        icons = self.game.assets.get(Animation.RESOURCE_ICONS, {}) 
        economy = self.world.economy

        display.blit(self.game.assets[Animation.SHOP_PANEL], panel.topleft)

        for row in layout["rows"]:
            rt = row["resource_type"]
            icon = icons.get(rt)
            if icon is not None:
                display.blit(icon, row["icon_rect"].topleft)
            else:
                pygame.draw.rect(display, SHOP_COLOR_FALLBACK_ICON, row["icon_rect"])
                pygame.draw.rect(display, SHOP_COLOR_FALLBACK_ICON_BORDER, row["icon_rect"], 1)

            label = font.render(f"{rt.name} (${SHOP_PRICES[rt]})", True, SHOP_COLOR_SCREEN_LABEL)
            display.blit(label, row["label_pos"])

            owned = font.render(f"owned: {economy.get_resource_count(rt)}", True, SHOP_COLOR_SCREEN_OWNED)
            display.blit(owned, row["owned_pos"])

            self._draw_triangle_button(display, row["dec_rect"], "left")
            self._draw_amount_button(display, row["inc1_rect"], "1")
            self._draw_amount_button(display, row["inc5_rect"], "5")
            self._draw_amount_button(display, row["inc10_rect"], "10")

        cash_text = font.render(f"Cash: ${economy.cash}", True, SHOP_COLOR_SCREEN_CASH)
        display.blit(cash_text, (panel.x + SHOP_CASH_HEADER_POS[0], panel.y + SHOP_CASH_HEADER_POS[1]))

        cart_x, cart_y = layout["cart_start"]
        if not self.cart:
            empty_text = font.render("(empty)", True, SHOP_COLOR_SCREEN_CART_EMPTY)
            display.blit(empty_text, (cart_x, cart_y))
        else:
            for rt, amt in self.cart.items():
                line = font.render(f"{rt.name}   x{amt}", True, SHOP_COLOR_SCREEN_CART_ITEM)
                display.blit(line, (cart_x, cart_y))
                cart_y += SHOP_CART_LINE_HEIGHT

        pygame.draw.rect(display, SHOP_COLOR_BEZEL_CLOSE, layout["close_rect"])
        x_text = font.render("X", True, SHOP_COLOR_BEZEL_CLOSE_TEXT)
        display.blit(x_text, x_text.get_rect(center=layout["close_rect"].center))

        total_cost = sum(SHOP_PRICES[rt] * amt for rt, amt in self.cart.items())
        can_buy = total_cost > 0 and economy.cash >= total_cost
        buy_color = SHOP_COLOR_BEZEL_BUY_ENABLED if can_buy else SHOP_COLOR_BEZEL_BUY_DISABLED
        pygame.draw.rect(display, buy_color, layout["buy_rect"])
        buy_text = font.render(f"BUY (${total_cost})", True, SHOP_COLOR_BEZEL_BUY_TEXT)
        display.blit(buy_text, buy_text.get_rect(center=layout["buy_rect"].center))

    def _draw_triangle_button(self, display, rect, direction):
        pygame.draw.rect(display, SHOP_COLOR_DEC_BUTTON, rect)
        pygame.draw.rect(display, SHOP_COLOR_BUTTON_BORDER, rect, 1)
        cx, cy = rect.center
        size = rect.width // 3
        if direction == "left":
            points = [(cx + size, cy - size), (cx + size, cy + size), (cx - size, cy)]
        else:
            points = [(cx - size, cy - size), (cx - size, cy + size), (cx + size, cy)]
        pygame.draw.polygon(display, SHOP_COLOR_BUTTON_ARROW, points)

    def _draw_amount_button(self, display, rect, label):
        pygame.draw.rect(display, SHOP_COLOR_INC_BUTTON, rect)
        pygame.draw.rect(display, SHOP_COLOR_BUTTON_BORDER, rect, 1)
        cx, cy = rect.center
        size = max(rect.width // 4, 3)
        points = [(cx - size, cy - size), (cx - size, cy + size), (cx + size, cy)]
        pygame.draw.polygon(display, SHOP_COLOR_BUTTON_ARROW, points)