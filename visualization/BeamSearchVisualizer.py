import pygame
import time
from typing import List, Tuple, Dict, Any

from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class BeamSearchVisualizer(Visualizer):
    """
    Interactive Pygame visualizer for Local Beam Search (e.g. N-Queens optimization).
    Displays:
      1. Main Hero Board for the selected/best beam state with attacking pair visualizer.
      2. Multi-Beam Candidate fleet showing all k beam states side-by-side with mini-boards and metrics.
      3. Rich HUD with statistics, diversity, iterations, and step-by-step history scrubbing.
    """

    def __init__(
        self,
        problem,
        solver: SearchAlgorithm,
        cell_size: int = 50,
        fps: int = 10,
        auto_run: bool = False
    ):
        self.problem = problem
        self.solver = solver
        self.cell_size = cell_size
        self.fps = fps
        self.auto_run = auto_run

        self.n = getattr(self.problem, "n", 8)
        self.k = getattr(self.solver, "k", 5)

        # Layout geometry
        self.board_size = self.n * self.cell_size
        self.beam_panel_width = 320
        self.hud_width = 300
        
        self.width = self.board_size + self.beam_panel_width + self.hud_width
        self.height = max(self.board_size + 40, 520)

        # Theme & Color Palette
        self.COLORS = {
            "background": (26, 28, 35),
            "panel_bg": (32, 35, 45),
            "panel_border": (50, 55, 70),
            
            "black_square": (118, 150, 86),
            "white_square": (238, 238, 210),
            "queen": (30, 30, 30),
            "queen_outline": (255, 255, 255),
            
            "mini_black": (80, 100, 60),
            "mini_white": (180, 180, 160),
            "mini_queen": (230, 70, 70),

            "attack_line": (255, 75, 75, 180),
            "attack_glow": (255, 100, 100, 80),

            "hud": (22, 24, 30),
            "hud_line": (45, 50, 65),
            "hud_text": (210, 215, 230),
            "hud_muted": (140, 145, 165),
            "hud_title": (255, 195, 80),
            "accent": (80, 160, 255),
            "accent_subtle": (40, 70, 110),
            
            "success": (80, 220, 120),
            "warning": (255, 170, 60),
            "danger": (255, 85, 85),
            
            "card_bg": (38, 42, 54),
            "card_selected": (50, 70, 105),
            "card_border": (60, 68, 88),
            "card_border_selected": (100, 170, 255),
            "card_best": (50, 85, 65),
            "card_border_best": (80, 220, 120),
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab - Local Beam Search Visualizer")

        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("consolas", 12)
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_bold = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_queen = pygame.font.SysFont("segoe ui symbol", max(16, int(self.cell_size * 0.65)))

        self.running = True
        self.selected_beam_idx = 0  # Index within the current beam to view on hero board
        
        # History snapshot list
        self.history: List[Dict[str, Any]] = []
        self.history_index = 0

        self.restart()

    def _create_snapshot(self) -> Dict[str, Any]:
        """Creates a snapshot of the current solver state for history scrubbing."""
        beam = list(getattr(self.solver, "beam_states", [self.solver.current_state]))
        # Sort beam states descending by fitness
        scored_beam = []
        for s in beam:
            val = self.problem.value(s)
            scored_beam.append((val, s))
        scored_beam.sort(key=lambda x: x[0], reverse=True)
        sorted_states = [s for _, s in scored_beam]
        sorted_values = [v for v, _ in scored_beam]

        best_s = sorted_states[0] if sorted_states else self.solver.best_state
        best_v = sorted_values[0] if sorted_values else self.solver.best_value

        return {
            "beam_states": sorted_states,
            "beam_values": sorted_values,
            "best_state": best_s,
            "best_value": best_v,
            "status": self.solver.status,
            "num_iterations": self.solver.num_iterations,
            "nodes_expanded": self.solver.nodes_expanded,
            "nodes_generated": self.solver.nodes_generated,
        }

    def restart(self):
        self.solver.reset()
        self.history = [self._create_snapshot()]
        self.history_index = 0
        self.selected_beam_idx = 0
        self.auto_run = False

    def _get_attacking_pairs(self, state: Tuple[int, ...]) -> List[Tuple[int, int]]:
        """Finds all pairs of columns (i, j) where queens attack each other."""
        attacks = []
        n = len(state)
        for i in range(n):
            for j in range(i + 1, n):
                if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                    attacks.append((i, j))
        return attacks

    def draw_hero_board(self, state: Tuple[int, ...]):
        """Draws the main large chessboard with queens and attacking pair lines."""
        board_rect = pygame.Rect(0, 0, self.board_size, self.board_size)
        
        # Checkerboard tiles
        for r in range(self.n):
            for c in range(self.n):
                color = self.COLORS["white_square"] if (r + c) % 2 == 0 else self.COLORS["black_square"]
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)

        # Attacking lines & highlights
        attacks = self._get_attacking_pairs(state)
        attacked_cols = set()
        for i, j in attacks:
            attacked_cols.add(i)
            attacked_cols.add(j)

        # Draw attack connecting lines
        for i, j in attacks:
            p1 = (i * self.cell_size + self.cell_size // 2, state[i] * self.cell_size + self.cell_size // 2)
            p2 = (j * self.cell_size + self.cell_size // 2, state[j] * self.cell_size + self.cell_size // 2)
            pygame.draw.line(self.screen, (255, 80, 80), p1, p2, 2)

        # Draw Queens
        for c, r in enumerate(state):
            center = (c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2)
            is_attacked = c in attacked_cols
            
            # Subtle glow under attacked queen
            if is_attacked:
                pygame.draw.circle(self.screen, (255, 100, 100, 120), center, self.cell_size // 2 - 2)

            q_color = (180, 40, 40) if is_attacked else self.COLORS["queen"]
            pygame.draw.circle(self.screen, q_color, center, self.cell_size // 3)
            pygame.draw.circle(self.screen, self.COLORS["queen_outline"], center, self.cell_size // 3, 2)

            crown = self.font_queen.render("♕", True, self.COLORS["queen_outline"])
            crown_rect = crown.get_rect(center=center)
            crown_rect.y -= 2
            self.screen.blit(crown, crown_rect)

        # Bottom label bar under hero board
        bar_rect = pygame.Rect(0, self.board_size, self.board_size, self.height - self.board_size)
        pygame.draw.rect(self.screen, self.COLORS["panel_bg"], bar_rect)
        pygame.draw.line(self.screen, self.COLORS["panel_border"], (0, self.board_size), (self.board_size, self.board_size), 2)
        
        conflicts = len(attacks)
        val = self.problem.max_fitness - conflicts
        label = f"Hero View: Beam #{self.selected_beam_idx + 1} | Fitness: {val}/{self.problem.max_fitness} | Conflicts: {conflicts}"
        lbl_surf = self.font_bold.render(label, True, self.COLORS["success"] if conflicts == 0 else self.COLORS["hud_text"])
        self.screen.blit(lbl_surf, (15, self.board_size + 12))

    def draw_mini_board(self, surf: pygame.Surface, state: Tuple[int, ...], size: int):
        """Renders a compact mini-board onto a sub-surface."""
        mini_cell = size / self.n
        for r in range(self.n):
            for c in range(self.n):
                color = self.COLORS["mini_white"] if (r + c) % 2 == 0 else self.COLORS["mini_black"]
                rect = pygame.Rect(int(c * mini_cell), int(r * mini_cell), int(mini_cell) + 1, int(mini_cell) + 1)
                pygame.draw.rect(surf, color, rect)

        # Mini queens as dots
        for c, r in enumerate(state):
            cx = int(c * mini_cell + mini_cell / 2)
            cy = int(r * mini_cell + mini_cell / 2)
            rad = max(2, int(mini_cell * 0.35))
            pygame.draw.circle(surf, self.COLORS["mini_queen"], (cx, cy), rad)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), rad, 1)

    def draw_beam_panel(self, snap: Dict[str, Any]):
        """Renders the middle panel displaying cards for each of the k beam states."""
        panel_x = self.board_size
        panel_rect = pygame.Rect(panel_x, 0, self.beam_panel_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["panel_bg"], panel_rect)
        pygame.draw.line(self.screen, self.COLORS["panel_border"], (panel_x, 0), (panel_x, self.height), 2)

        # Header
        title = self.font_title.render("BEAM CANDIDATES", True, self.COLORS["hud_title"])
        self.screen.blit(title, (panel_x + 15, 15))
        sub = self.font_small.render(f"Top k={len(snap['beam_states'])} Parallel States", True, self.COLORS["hud_muted"])
        self.screen.blit(sub, (panel_x + 15, 38))

        # Render cards
        card_start_y = 65
        available_h = self.height - card_start_y - 15
        card_count = max(1, len(snap["beam_states"]))
        card_h = min(80, max(55, available_h // card_count - 8))
        mini_size = max(36, card_h - 14)

        for idx, state in enumerate(snap["beam_states"]):
            card_y = card_start_y + idx * (card_h + 8)
            card_rect = pygame.Rect(panel_x + 12, card_y, self.beam_panel_width - 24, card_h)

            is_selected = (idx == self.selected_beam_idx)
            is_best = (idx == 0)

            # Card background
            if is_selected:
                bg_col = self.COLORS["card_selected"]
                border_col = self.COLORS["card_border_selected"]
                border_w = 2
            elif is_best:
                bg_col = self.COLORS["card_best"]
                border_col = self.COLORS["card_border_best"]
                border_w = 2
            else:
                bg_col = self.COLORS["card_bg"]
                border_col = self.COLORS["card_border"]
                border_w = 1

            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_col, card_rect, border_w, border_radius=6)

            # Mini board
            mini_surf = pygame.Surface((mini_size, mini_size))
            self.draw_mini_board(mini_surf, state, mini_size)
            self.screen.blit(mini_surf, (card_rect.x + 8, card_rect.y + (card_h - mini_size) // 2))

            # Info text
            val = snap["beam_values"][idx] if idx < len(snap["beam_values"]) else self.problem.value(state)
            conflicts = self.problem.max_fitness - val
            
            badge_txt = f"#{idx+1} BEST" if is_best else f"#{idx+1}"
            badge_col = self.COLORS["success"] if is_best else self.COLORS["accent"]
            b_surf = self.font_bold.render(badge_txt, True, badge_col)
            self.screen.blit(b_surf, (card_rect.x + mini_size + 18, card_rect.y + 8))

            val_txt = f"Fitness: {val}/{self.problem.max_fitness}"
            v_surf = self.font_small.render(val_txt, True, self.COLORS["hud_text"])
            self.screen.blit(v_surf, (card_rect.x + mini_size + 18, card_rect.y + 28))

            c_txt = f"Conflicts: {conflicts}"
            c_col = self.COLORS["success"] if conflicts == 0 else self.COLORS["warning"]
            c_surf = self.font_small.render(c_txt, True, c_col)
            self.screen.blit(c_surf, (card_rect.x + mini_size + 18, card_rect.y + 44))

            # Shortcut key label
            if idx < 9:
                key_surf = self.font_small.render(f"[{idx+1}]", True, self.COLORS["hud_muted"])
                self.screen.blit(key_surf, (card_rect.right - 28, card_rect.y + 8))

    def draw_hud(self, snap: Dict[str, Any]):
        """Renders the right HUD panel with search statistics and control instructions."""
        hud_x = self.board_size + self.beam_panel_width
        hud_rect = pygame.Rect(hud_x, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud"], hud_rect)
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (hud_x, 0), (hud_x, self.height), 2)

        x = hud_x + 20
        y = 20

        def write(text, font=None, color=None, gap=6):
            nonlocal y
            f = font or self.font
            c = color or self.COLORS["hud_text"]
            surf = f.render(str(text), True, c)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + gap

        write("BEAM SEARCH OPTIMIZER", self.font_title, self.COLORS["hud_title"], 12)
        write(f"Domain: {self.n}-Queens Problem", color=self.COLORS["hud_muted"])
        write(f"Algorithm: Local Beam Search", color=self.COLORS["hud_muted"])
        
        status_name = snap["status"].name if hasattr(snap["status"], "name") else str(snap["status"])
        status_col = (
            self.COLORS["success"] if snap["best_value"] == self.problem.max_fitness
            else self.COLORS["warning"] if status_name == "SUCCESS"
            else self.COLORS["accent"]
        )
        write(f"Status: {status_name}", self.font_bold, status_col, 14)

        # Beam Metrics
        write("SEARCH METRICS", self.font_bold, self.COLORS["accent"], 8)
        write(f"Iteration: {snap['num_iterations']}")
        write(f"Beam Width (k): {self.k}")
        
        unique_states = len(set(snap["beam_states"]))
        diversity = f"{unique_states}/{len(snap['beam_states'])} ({int(unique_states / max(1, len(snap['beam_states'])) * 100)}%)"
        write(f"Beam Diversity: {diversity}")
        
        best_conflicts = self.problem.max_fitness - snap["best_value"]
        write(f"Best Fitness: {snap['best_value']} / {self.problem.max_fitness}")
        write(f"Min Conflicts: {best_conflicts}", color=self.COLORS["success"] if best_conflicts == 0 else self.COLORS["danger"])
        
        write(f"Nodes Expanded: {snap['nodes_expanded']}")
        write(f"Nodes Evaluated: {snap['nodes_generated']}", gap=14)

        # Playback & Controls
        write("CONTROLS", self.font_bold, self.COLORS["hud_title"], 8)
        write("[RIGHT] Step Forward")
        write("[LEFT]  Step Backward")
        write("[SPACE] Play / Pause")
        write("[A]     Toggle Auto-Run")
        write("[1..9]  Inspect Beam State")
        write("[R]     Restart")
        write("[UP/DN] Speed (FPS)", gap=14)

        # Live State
        state_txt = "AUTO-RUNNING" if self.auto_run else "PAUSED / MANUAL"
        state_col = self.COLORS["success"] if self.auto_run else self.COLORS["warning"]
        write(f"Mode: {state_txt}", color=state_col)
        write(f"Step: {self.history_index} / {len(self.history) - 1}")
        write(f"FPS: {self.fps}")

    def render(self):
        snap = self.history[self.history_index]
        
        # Ensure selected index is valid
        if self.selected_beam_idx >= len(snap["beam_states"]):
            self.selected_beam_idx = 0
            
        hero_state = snap["beam_states"][self.selected_beam_idx] if snap["beam_states"] else snap["best_state"]
        
        self.draw_hero_board(hero_state)
        self.draw_beam_panel(snap)
        self.draw_hud(snap)
        pygame.display.flip()

    def _step_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
        elif self.solver.status == SearchStatus.RUNNING:
            self.solver.search_step()
            snap = self._create_snapshot()
            self.history.append(snap)
            self.history_index = len(self.history) - 1

    def _step_backward(self):
        if self.history_index > 0:
            self.history_index -= 1

    def handle_mouse_click(self, pos: Tuple[int, int]):
        """Select a beam candidate card when clicked."""
        x, y = pos
        panel_x = self.board_size
        if panel_x <= x < panel_x + self.beam_panel_width:
            snap = self.history[self.history_index]
            card_start_y = 65
            available_h = self.height - card_start_y - 15
            card_count = max(1, len(snap["beam_states"]))
            card_h = min(80, max(55, available_h // card_count - 8))
            
            for idx in range(len(snap["beam_states"])):
                card_y = card_start_y + idx * (card_h + 8)
                if card_y <= y <= card_y + card_h:
                    self.selected_beam_idx = idx
                    break

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_SPACE:
                    self.auto_run = not self.auto_run
                elif event.key == pygame.K_a:
                    self.auto_run = not self.auto_run
                elif event.key == pygame.K_RIGHT:
                    self._step_forward()
                elif event.key == pygame.K_LEFT:
                    self._step_backward()
                elif event.key == pygame.K_UP:
                    self.fps = min(60, self.fps + 2)
                elif event.key == pygame.K_DOWN:
                    self.fps = max(1, self.fps - 2)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    snap = self.history[self.history_index]
                    if idx < len(snap["beam_states"]):
                        self.selected_beam_idx = idx

        if self.auto_run:
            if self.solver.status == SearchStatus.RUNNING or self.history_index < len(self.history) - 1:
                self._step_forward()
            else:
                self.auto_run = False

    def run(self):
        while self.running:
            self.update()
            self.render()
            self.clock.tick(self.fps)
        pygame.quit()
