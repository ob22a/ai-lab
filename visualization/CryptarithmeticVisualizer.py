"""
CryptarithmeticVisualizer.py
Pygame visualizer for Cryptarithmetic CSP puzzles (e.g., SEND + MORE = MONEY).

Features:
  - Visual equation layout rendering with letter tiles
  - Real-time digit trial & backtracking assignment animation
  - Supports Backtracking, MRV, LCV, MAC, Forward Checking
"""

import pygame
import time
from domains.cryptarithmetic.Cryptarithmetic import CryptarithmeticCSP

# Colors
BG_COLOR = (18, 22, 34)
HUD_BG = (28, 33, 50)
HUD_LINE = (65, 75, 110)
TEXT_COLOR = (235, 240, 255)
TEXT_DIM = (130, 140, 170)
GOLD = (255, 205, 60)
TILE_BG = (45, 55, 85)
TILE_BORDER = (85, 105, 155)
DIGIT_COLOR = (80, 220, 140)
BACKTRACK_COLOR = (240, 90, 90)


class CryptarithmeticVisualizer:
    def __init__(self, puzzle: str = "SEND + MORE = MONEY", solver_class=None, fps: int = 30):
        self.puzzle_str = puzzle
        parts = puzzle.replace(" ", "").split("=")
        result_word = parts[-1]
        addends = parts[0].split("+")
        self.problem = CryptarithmeticCSP(addends, result_word)
        self.solver_class = solver_class
        self.fps = fps
        self.W, self.H = 950, 650
        self.HUD_W = 280

        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – Cryptarithmetic Visualizer")

        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_tile = pygame.font.SysFont("consolas", 26, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 12)

        self.running = True
        self.history_index = 0
        self.auto_run = True

        self._solve()

    def _solve(self):
        from csp.Backtracking import BacktrackingSolver
        cls = self.solver_class or BacktrackingSolver
        solver = cls(self.problem)

        self.steps = [{'assignment': {}, 'last_var': None, 'action': 'start'}]

        def _on_assign(var, val, assignment):
            self.steps.append({
                'assignment': dict(assignment),
                'last_var': var,
                'action': 'assign'
            })

        def _on_unassign(var, assignment):
            self.steps.append({
                'assignment': dict(assignment),
                'last_var': var,
                'action': 'unassign'
            })

        if hasattr(solver, 'on_assign'):
            solver.on_assign = _on_assign
            solver.on_unassign = _on_unassign

        solution = solver.solve()
        self.solution = solution or {}
        self.nodes_expanded = getattr(solver, 'nodes_expanded', 0)
        self.runtime = getattr(solver, 'runtime', 0.0)

        if not self.steps:
            self.steps = [{'assignment': self.solution, 'last_var': None, 'action': 'end'}]

    def render(self):
        self.screen.fill(BG_COLOR)
        canvas_w = self.W - self.HUD_W

        step = self.steps[min(self.history_index, len(self.steps)-1)] if self.steps else {'assignment': {}}
        assignment = step['assignment']
        last_var = step.get('last_var', None)
        action_type = step.get('action', 'assign')

        parts = self.puzzle_str.replace("=", "+").split("+")
        word1 = parts[0].strip() if len(parts) > 0 else "SEND"
        word2 = parts[1].strip() if len(parts) > 1 else "MORE"
        word3 = parts[2].strip() if len(parts) > 2 else "MONEY"

        tile_w = 44
        tile_h = 56
        gap = 8

        def render_word(word, y_pos):
            total_w = len(word) * (tile_w + gap) - gap
            start_x = canvas_w // 2 + 80 - total_w
            for idx, char in enumerate(word):
                x = start_x + idx * (tile_w + gap)
                r = pygame.Rect(x, y_pos, tile_w, tile_h)
                border_c = BACKTRACK_COLOR if (char == last_var and action_type == 'unassign') else (GOLD if char == last_var else TILE_BORDER)
                pygame.draw.rect(self.screen, TILE_BG, r, border_radius=8)
                pygame.draw.rect(self.screen, border_c, r, width=2, border_radius=8)

                ls = self.font_tile.render(char, True, TEXT_COLOR)
                self.screen.blit(ls, (r.centerx - ls.get_width()//2, y_pos + 4))

                d_val = assignment.get(char, "_")
                ds = self.font_md.render(str(d_val), True, DIGIT_COLOR if d_val != "_" else TEXT_DIM)
                self.screen.blit(ds, (r.centerx - ds.get_width()//2, y_pos + 32))

        render_word(word1, 100)
        plus_s = self.font_lg.render("+", True, GOLD)
        self.screen.blit(plus_s, (canvas_w // 2 - 140, 175))
        render_word(word2, 160)

        line_w = max(len(word1), len(word2), len(word3)) * (tile_w + gap) + 40
        pygame.draw.line(self.screen, GOLD, (canvas_w // 2 + 90 - line_w, 230), (canvas_w // 2 + 90, 230), 4)

        render_word(word3, 250)

        # Draw HUD
        hud_rect = pygame.Rect(canvas_w, 0, self.HUD_W, self.H)
        pygame.draw.rect(self.screen, HUD_BG, hud_rect)
        pygame.draw.line(self.screen, HUD_LINE, (canvas_w, 0), (canvas_w, self.H), 2)

        hx = canvas_w + 14
        hy = 16

        def txt(s, font=None, col=None, gap=6):
            nonlocal hy
            f = font or self.font_md
            c = col or TEXT_COLOR
            self.screen.blit(f.render(s, True, c), (hx, hy))
            hy += f.size(s)[1] + gap

        txt("CRYPTARITHMETIC CSP", self.font_lg, GOLD, 10)
        txt(f"Puzzle: {self.puzzle_str}")
        txt(f"Solver: {self.solver_class.__name__ if self.solver_class else 'Backtracking'}")
        hy += 10
        txt(f"Nodes Expanded: {self.nodes_expanded}")
        txt(f"Runtime:        {self.runtime:.4f}s")
        hy += 10
        txt(f"Step: {self.history_index+1} / {len(self.steps)}")
        if action_type == 'unassign':
            txt(f"Action: BACKTRACK ({last_var})", col=BACKTRACK_COLOR)
        elif action_type == 'assign':
            txt(f"Action: Assign {last_var}", col=GOLD)
        hy += 15
        txt("LETTER MAPPINGS:", col=GOLD)
        for var in sorted(self.problem.variables):
            val = assignment.get(var, "Unassigned")
            txt(f"  {var} = {val}", self.font_sm, DIGIT_COLOR if val != "Unassigned" else TEXT_DIM)

        hy += 15
        txt("CONTROLS:", col=TEXT_DIM)
        txt("[SPACE] Play / Pause", self.font_sm, TEXT_DIM)
        txt("[RIGHT] Step forward", self.font_sm, TEXT_DIM)
        txt("[LEFT]  Step backward", self.font_sm, TEXT_DIM)
        txt("[R]     Restart", self.font_sm, TEXT_DIM)
        txt("[B]     Back to Hub", self.font_sm, TEXT_DIM)

        pygame.display.flip()

    def run(self):
        last_step_time = time.time()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.W, self.H = event.w, event.h
                    self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.auto_run = not self.auto_run
                    elif event.key == pygame.K_RIGHT:
                        self.history_index = min(self.history_index + 1, len(self.steps) - 1)
                    elif event.key == pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)
                    elif event.key == pygame.K_r:
                        self.history_index = 0

            if self.auto_run and time.time() - last_step_time > 0.05:
                if self.history_index < len(self.steps) - 1:
                    self.history_index += 1
                last_step_time = time.time()

            self.render()
            self.clock.tick(self.fps)
