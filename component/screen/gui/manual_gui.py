import pygame
from ...utils import get_scaled_mouse_pos, Fonts, Animation

MANUAL_EDGE_GAP = 2

MANUAL_COLOR_PAGE_NUM = (90, 80, 65)
MANUAL_COLOR_ARROW = (170, 160, 145)
MANUAL_COLOR_ARROW_DISABLED = (60, 45, 30)
MANUAL_COLOR_CLOSE = (150, 40, 40)
MANUAL_COLOR_CLOSE_TEXT = (255, 255, 255)


class ManualGUI:
    def __init__(self, world):
        self.world = world
        self.game = world.game
        self.is_open = False
        self.current_page = 0
        self.pages = self.game.assets[Animation.MANUAL_PANEL_PAGES]

    def toggle(self):
        self.is_open = not self.is_open

    def close(self):
        self.is_open = False

    def get_layout(self):
        page_image = self.pages[self.current_page]
        page_rect = page_image.get_rect(
            center=(self.game.GAME_WIDTH // 2, self.game.GAME_HEIGHT // 2)
        )

        arrow_size = (32, 48)
        close_size = (24, 24)

        arrow_left_rect = pygame.Rect(0, 0, *arrow_size)
        arrow_left_rect.midright = (page_rect.left - MANUAL_EDGE_GAP, page_rect.centery)

        arrow_right_rect = pygame.Rect(0, 0, *arrow_size)
        arrow_right_rect.midleft = (page_rect.right + MANUAL_EDGE_GAP, page_rect.centery)

        close_rect = pygame.Rect(0, 0, *close_size)
        close_rect.bottomleft = (page_rect.right-40, page_rect.top+20)

        return {
            "page_rect": page_rect,
            "arrow_left_rect": arrow_left_rect,
            "arrow_right_rect": arrow_right_rect,
            "close_rect": close_rect,
        }

    def handle_input(self, actions):
        if not self.is_open:
            return

        if actions["key_r"] and actions["Lshift"]:
            self.prev_page()
            self.game.reset_key("key_r")
        elif actions["key_r"]:
            self.next_page()
            self.game.reset_key("key_r")

        if actions["LMB"]:
            mx, my = get_scaled_mouse_pos(self.game)
            layout = self.get_layout()

            if layout["close_rect"].collidepoint(mx, my):
                self.close()
                self.game.reset_key("LMB")
                return
            if layout["arrow_left_rect"].collidepoint(mx, my):
                self.prev_page()
                self.game.reset_key("LMB")
                return
            if layout["arrow_right_rect"].collidepoint(mx, my):
                self.next_page()
                self.game.reset_key("LMB")
                return

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1

    def draw(self, display):
        if not self.is_open:
            return
        layout = self.get_layout()
        page_rect = layout["page_rect"]
        font_body = self.game.assets[Fonts.BODY]

        page_image = self.pages[self.current_page]
        display.blit(page_image, page_rect)

        page_num_text = font_body.render(f"{self.current_page + 1} / {len(self.pages)}", True, MANUAL_COLOR_PAGE_NUM)
        page_num_rect = page_num_text.get_rect(midbottom=(page_rect.centerx, page_rect.bottom - MANUAL_EDGE_GAP*15))
        display.blit(page_num_text, page_num_rect)

        self._draw_arrow(display, layout["arrow_left_rect"], "left", enabled=self.current_page > 0)
        self._draw_arrow(display, layout["arrow_right_rect"], "right", enabled=self.current_page < len(self.pages) - 1)

        pygame.draw.rect(display, MANUAL_COLOR_CLOSE, layout["close_rect"])
        x_text = font_body.render("X", True, MANUAL_COLOR_CLOSE_TEXT)
        display.blit(x_text, x_text.get_rect(center=layout["close_rect"].center))

    def _draw_arrow(self, display, rect, direction, enabled):
        color = MANUAL_COLOR_ARROW if enabled else MANUAL_COLOR_ARROW_DISABLED
        cx, cy = rect.center
        size = 10
        if direction == "left":
            points = [(cx + size, cy - size), (cx + size, cy + size), (cx - size, cy)]
        else:
            points = [(cx - size, cy - size), (cx - size, cy + size), (cx + size, cy)]
        pygame.draw.polygon(display, color, points)