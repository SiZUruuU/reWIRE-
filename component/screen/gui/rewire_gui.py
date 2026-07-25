import pygame
import random
from ...utils import get_scaled_mouse_pos, Fonts, EntityType

REWIRE_COLOR_POOL = [
    (220, 60, 60), # red
    (60, 200, 90), # green
    (60, 120, 220), # blue
    (230, 200, 60), # yellow
    (200, 90, 220), # magenta
    (60, 200, 200), # cyan
    (240, 140, 40), # orange
    (140, 90, 220), # purple
    (150, 220, 60), # lime
    (220, 60, 140), # pink
    (100, 100, 100), # grey
    (255, 255, 255), # white
]

REWIRE_NODE_COUNTS = {
    EntityType.CONVEYOR: 3,
    EntityType.BUZZSAW: 3,
    EntityType.CRUSHER: 5,
    EntityType.FURNACE: 6,
    EntityType.WOOD_GENERATOR: 8,
    EntityType.STONE_GENERATOR: 10,
}

REWIRE_PANEL_SIZE = (300, 220)
REWIRE_TERMINAL_RADIUS = 10
REWIRE_LEFT_X = 60
REWIRE_RIGHT_X = 240
REWIRE_TOP_Y = 50
REWIRE_SPACING = 40


REWIRE_PANEL_SIZE = (340, 400)
REWIRE_TERMINAL_RADIUS = 9
REWIRE_LEFT_X = 60
REWIRE_RIGHT_X = 280
REWIRE_TOP_Y = 60
# spacing is automatic ;3
REWIRE_SPACING = 26


class RewireGUI:
    def __init__(self, world):
        self.world = world
        self.game = world.game
        self.active_machine = None
        self.node_count = 0
        self.right_order = []
        self.connected = set()

        # drag state
        self.dragging_from = None # index of left node being dragged, or None
        self.drag_pos = None # current mouse pos while dragging

    @property
    def is_open(self):
        return self.active_machine is not None

    def open(self, machine):
        self.active_machine = machine
        self.node_count = REWIRE_NODE_COUNTS.get(machine.entity_type, 6)
        self.right_order = list(range(self.node_count))
        random.shuffle(self.right_order)
        self.connected = set()
        self.dragging_from = None
        self.drag_pos = None

    def close(self):
        self.active_machine = None

    def get_layout(self):
        panel = pygame.Rect(
            self.game.GAME_WIDTH // 2 - REWIRE_PANEL_SIZE[0] // 2,
            self.game.GAME_HEIGHT // 2 - REWIRE_PANEL_SIZE[1] // 2,
            *REWIRE_PANEL_SIZE
        )

        # fit spacing to available vertical room based on node count
        available_height = REWIRE_PANEL_SIZE[1] - REWIRE_TOP_Y - 40
        spacing = min(REWIRE_SPACING, available_height / max(self.node_count - 1, 1))

        left_points, right_points = [], []
        for i in range(self.node_count):
            ly = panel.y + REWIRE_TOP_Y + i * spacing
            left_points.append((panel.x + REWIRE_LEFT_X, ly))
            right_points.append((panel.x + REWIRE_RIGHT_X, ly))
        return panel, left_points, right_points

    # drag to connect minigame input
    def handle_input(self, actions):
        if not self.is_open:
            return

        mx, my = get_scaled_mouse_pos(self.game)
        panel, left_points, right_points = self.get_layout()

        mouse_down = actions["LMB"]

        if self.dragging_from is None:
            if mouse_down:
                for i, (lx, ly) in enumerate(left_points):
                    if i in self.connected:
                        continue
                    if (mx - lx) ** 2 + (my - ly) ** 2 <= REWIRE_TERMINAL_RADIUS ** 2:
                        self.dragging_from = i
                        self.drag_pos = (mx, my)
                        return
        else:
            self.drag_pos = (mx, my)
            if not mouse_down:
                # check if on top of a valid node
                for slot_index, (rx, ry) in enumerate(right_points):
                    color_index = self.right_order[slot_index]
                    if color_index in self.connected:
                        continue
                    if (mx - rx) ** 2 + (my - ry) ** 2 <= REWIRE_TERMINAL_RADIUS ** 2:
                        if color_index == self.dragging_from:
                            self.connected.add(color_index)
                            if len(self.connected) == self.node_count:
                                self.complete_rewire()
                        break
                self.dragging_from = None
                self.drag_pos = None

    def complete_rewire(self):
        if self.active_machine is not None and hasattr(self.active_machine, "breakdown"):
            self.active_machine.breakdown.repair()
        self.close()

    ## DRAW ##
    def draw(self, display):
        if not self.is_open:
            return
        panel, left_points, right_points = self.get_layout()
        font = self.game.assets[Fonts.BODY]

        bg = pygame.Surface(panel.size, pygame.SRCALPHA)
        bg.fill((20, 20, 30, 235))
        display.blit(bg, panel.topleft)
        pygame.draw.rect(display, (255, 255, 255), panel, 1)

        title = font.render(f"REWIRE ({len(self.connected)}/{self.node_count})", True, (255, 255, 255))
        display.blit(title, (panel.x + 16, panel.y + 16))

        for i, (lx, ly) in enumerate(left_points):
            color = REWIRE_COLOR_POOL[i]
            pygame.draw.circle(display, color, (lx, ly), REWIRE_TERMINAL_RADIUS)
            if i in self.connected:
                pygame.draw.circle(display, (255, 255, 255), (lx, ly), REWIRE_TERMINAL_RADIUS, 2)

        for slot_index, (rx, ry) in enumerate(right_points):
            color_index = self.right_order[slot_index]
            color = REWIRE_COLOR_POOL[color_index]
            pygame.draw.circle(display, color, (rx, ry), REWIRE_TERMINAL_RADIUS)
            if color_index in self.connected:
                pygame.draw.circle(display, (255, 255, 255), (rx, ry), REWIRE_TERMINAL_RADIUS, 2)

        # completed wires
        for color_index in self.connected:
            left_pos = left_points[color_index]
            right_slot = self.right_order.index(color_index)
            right_pos = right_points[right_slot]
            pygame.draw.line(display, REWIRE_COLOR_POOL[color_index], left_pos, right_pos, 3)

        # drag line following the cursor
        if self.dragging_from is not None and self.drag_pos is not None:
            pygame.draw.line(
                display, REWIRE_COLOR_POOL[self.dragging_from],
                left_points[self.dragging_from], self.drag_pos, 3
            )

        if len(self.connected) == self.node_count:
            done_text = font.render("FIXED!", True, (100, 255, 100))
            display.blit(done_text, (panel.centerx - done_text.get_width() // 2, panel.bottom - 30))