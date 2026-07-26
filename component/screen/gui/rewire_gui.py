import pygame
import random
from ...utils import get_scaled_mouse_pos, Fonts, EntityType, Animation

REWIRE_NODE_COUNTS = {
    EntityType.CONVEYOR: 3,
    EntityType.BUZZSAW: 4,
    EntityType.CRUSHER: 4,
    EntityType.FURNACE: 5,
    EntityType.WOOD_GENERATOR: 6,
    EntityType.STONE_GENERATOR: 8,
}

REWIRE_COLOR_POOL = [
    (220, 60, 60), 
    (60, 200, 90), 
    (60, 120, 220), 
    (230, 200, 60),
    (200, 90, 220), 
    (60, 200, 200), 
    (240, 140, 40), 
    (140, 90, 220),
    (150, 220, 60), 
    (220, 60, 140), 
    (100, 100, 100), 
    (255, 255, 255),
]

REWIRE_PANEL_SIZE = (400, 300)
REWIRE_BATCH_SIZE = 6
REWIRE_NODE_RADIUS = 7

# hard coded area based off of my calculation
# no one speaks about this
REWIRE_NODE_A_AREA = (112, 80, 16, 144)
REWIRE_NODE_B_AREA = (284, 96, 16, 120)

REWIRE_BATCH_ADVANCE_DELAY = 0.5


class RewireGUI:
    def __init__(self, level):
        self.level = level
        self.game = level.game
        self.active_machine = None
        self.node_count = 0
        # batches are the list of colors
        self.batches = []
        self.current_batch_index = 0 # current color
        self.right_order = []        
        self.connected = set()
        self.advance_timer = 0.0

        self.dragging_from = None
        self.drag_pos = None

    @property
    def is_open(self):
        return self.active_machine is not None

    def open(self, machine):
        self.active_machine = machine
        self.node_count = REWIRE_NODE_COUNTS.get(machine.entity_type, 6)

        all_indices = list(range(self.node_count))
        self.batches = [
            all_indices[i:i + REWIRE_BATCH_SIZE]
            for i in range(0, self.node_count, REWIRE_BATCH_SIZE)
        ]
        self.current_batch_index = 0
        self.connected = set()
        self.advance_timer = 0.0
        self._start_batch()

    def _start_batch(self):
        current = self.batches[self.current_batch_index]
        self.right_order = list(current)
        random.shuffle(self.right_order)
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

        current = self.batches[self.current_batch_index]
        n = len(current)

        ax, ay, aw, ah = REWIRE_NODE_A_AREA
        bx, by, bw, bh = REWIRE_NODE_B_AREA

        a_spacing = ah / max(n - 1, 1)
        b_spacing = bh / max(n - 1, 1)

        left_points = {}
        right_points = {}
        for i, color_index in enumerate(current):
            left_points[color_index] = (panel.x + ax + aw // 2, panel.y + ay + i * a_spacing)
        for slot_index, color_index in enumerate(self.right_order):
            right_points[color_index] = (panel.x + bx + bw // 2, panel.y + by + slot_index * b_spacing)

        return panel, left_points, right_points

    ## hold and drag logic
    def handle_input(self, actions, delta_time=0.0):
        if not self.is_open:
            return

        if self.advance_timer > 0:
            self.advance_timer -= delta_time
            if self.advance_timer <= 0:
                self._advance_or_finish()
            return

        mx, my = get_scaled_mouse_pos(self.game)
        panel, left_points, right_points = self.get_layout()
        mouse_down = actions["LMB"]

        if self.dragging_from is None:
            if mouse_down:
                for color_index, (lx, ly) in left_points.items():
                    if color_index in self.connected:
                        continue
                    if (mx - lx) ** 2 + (my - ly) ** 2 <= REWIRE_NODE_RADIUS ** 2:
                        self.dragging_from = color_index
                        self.drag_pos = (mx, my)
                        return
        else:
            self.drag_pos = (mx, my)
            if not mouse_down:
                for color_index, (rx, ry) in right_points.items():
                    if color_index in self.connected:
                        continue
                    if (mx - rx) ** 2 + (my - ry) ** 2 <= REWIRE_NODE_RADIUS ** 2:
                        if color_index == self.dragging_from:
                            self.connected.add(color_index)
                            current = self.batches[self.current_batch_index]
                            if all(c in self.connected for c in current):
                                self.advance_timer = REWIRE_BATCH_ADVANCE_DELAY
                        break
                self.dragging_from = None
                self.drag_pos = None

    def _advance_or_finish(self):
        if self.current_batch_index + 1 < len(self.batches):
            self.current_batch_index += 1
            self._start_batch()
        else:
            self.complete_rewire()

    def complete_rewire(self):
        if self.active_machine is not None and hasattr(self.active_machine, "breakdown"):
            self.active_machine.breakdown.repair()
        self.close()

    ## draw method
    def draw(self, display):
        if not self.is_open:
            return
        panel, left_points, right_points = self.get_layout()
        font = self.game.assets[Fonts.BODY]

        display.blit(self.game.assets[Animation.REWIRE_BOX_PANEL], panel.topleft)
        pygame.draw.rect(display, (255, 255, 255), panel, 1)

        batch_label = f"Batch {self.current_batch_index + 1}/{len(self.batches)}  ({len(self.connected)}/{self.node_count})"
        text = font.render(batch_label, True, (255, 255, 255))
        display.blit(text, (panel.x + 8, panel.y + 6))

        current = self.batches[self.current_batch_index]

        for color_index in current:
            lx, ly = left_points[color_index]
            color = REWIRE_COLOR_POOL[color_index]
            pygame.draw.circle(display, color, (lx, ly), REWIRE_NODE_RADIUS)
            if color_index in self.connected:
                pygame.draw.circle(display, (255, 255, 255), (lx, ly), REWIRE_NODE_RADIUS, 2)

        for color_index in current:
            rx, ry = right_points[color_index]
            color = REWIRE_COLOR_POOL[color_index]
            pygame.draw.circle(display, color, (rx, ry), REWIRE_NODE_RADIUS)
            if color_index in self.connected:
                pygame.draw.circle(display, (255, 255, 255), (rx, ry), REWIRE_NODE_RADIUS, 2)

        for color_index in current:
            if color_index in self.connected:
                pygame.draw.line(display, REWIRE_COLOR_POOL[color_index], left_points[color_index], right_points[color_index], 3)

        if self.dragging_from is not None and self.drag_pos is not None:
            pygame.draw.line(display, REWIRE_COLOR_POOL[self.dragging_from], left_points[self.dragging_from], self.drag_pos, 3)

        if self.advance_timer > 0 and len(self.connected) == self.node_count:
            done_text = font.render("FIXED!", True, (100, 255, 100))
            display.blit(done_text, (panel.centerx - done_text.get_width() // 2, panel.bottom - 20))