"""
MapColoringVisualizer.py
Pygame visualizer for the Australia Map Coloring CSP domain.

Features:
  - Graph node & region visualization for Australia states
  - Full real-time backtracking animation with assign & unassign steps
  - Color assignments (Red, Green, Blue)
  - Supports Backtracking, MRV, LCV, Forward Checking, MAC, Min-Conflicts
"""

import pygame
import time
from domains.map_coloring.MapColoring import MapColoringCSP

COLOR_MAP = {
    'Red': (240, 80, 80),
    'Green': (80, 200, 100),
    'Blue': (80, 140, 240),
    'UNASSIGNED': (100, 110, 140)
}

REGION_POS = {
    'WA': (140, 240),
    'NT': (290, 160),
    'SA': (300, 320),
    'Q':  (440, 200),
    'NSW': (480, 340),
    'V':   (430, 440),
    'T':   (450, 520)
}

ADJACENCY = [
    ('WA', 'NT'), ('WA', 'SA'),
    ('NT', 'SA'), ('NT', 'Q'),
    ('SA', 'Q'),  ('SA', 'NSW'), ('SA', 'V'),
    ('Q', 'NSW'),
    ('NSW', 'V')
]

# Colors
BG_COLOR = (18, 22, 34)
HUD_BG = (28, 33, 50)
HUD_LINE = (65, 75, 110)
TEXT_COLOR = (235, 240, 255)
TEXT_DIM = (130, 140, 170)
GOLD = (255, 205, 60)
BACKTRACK_COLOR = (240, 90, 90)


class MapColoringVisualizer:
    def __init__(self, solver_class=None, fps: int = 30):
        self.problem = MapColoringCSP()
        self.solver_class = solver_class
        self.fps = fps
        self.W, self.H = 950, 650
        self.HUD_W = 280

        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – Map Coloring CSP Visualizer")

        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("consolas", 22, bold=True)
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
        curr_assignment = step['assignment']
        last_var = step.get('last_var', None)
        action_type = step.get('action', 'assign')

        # Scale coordinates
        scale_x = (canvas_w - 60) / 560.0
        scale_y = (self.H - 60) / 540.0

        def pos(region):
            ox, oy = REGION_POS[region]
            return int(ox * scale_x + 30), int(oy * scale_y + 30)

        # Draw Adjacency Edges
        for r1, r2 in ADJACENCY:
            p1, p2 = pos(r1), pos(r2)
            pygame.draw.line(self.screen, (70, 80, 110), p1, p2, 3)

        # Draw Region Nodes
        for region in REGION_POS:
            p = pos(region)
            c_name = curr_assignment.get(region, 'UNASSIGNED')
            col = COLOR_MAP.get(c_name, COLOR_MAP['UNASSIGNED'])

            # Highlight last modified region
            border_col = BACKTRACK_COLOR if (region == last_var and action_type == 'unassign') else ((255, 255, 255) if region == last_var else (180, 190, 220))
            border_w = 4 if region == last_var else 2

            pygame.draw.circle(self.screen, col, p, 32)
            pygame.draw.circle(self.screen, border_col, p, 32, width=border_w)

            lbl = self.font_lg.render(region, True, (20, 20, 20) if c_name != 'UNASSIGNED' else TEXT_COLOR)
            self.screen.blit(lbl, (p[0] - lbl.get_width()//2, p[1] - lbl.get_height()//2))

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

        txt("MAP COLORING CSP", self.font_lg, GOLD, 10)
        txt(f"Regions: {len(REGION_POS)}")
        txt(f"Colors:  Red, Green, Blue")
        txt(f"Solver:  {self.solver_class.__name__ if self.solver_class else 'Backtracking'}")
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
        txt("ASSIGNMENTS:", col=GOLD)
        for r in REGION_POS:
            assigned = curr_assignment.get(r, 'Unassigned')
            txt(f"  {r}: {assigned}", self.font_sm, COLOR_MAP.get(assigned, TEXT_DIM))

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

            if self.auto_run and time.time() - last_step_time > 0.4:
                if self.history_index < len(self.steps) - 1:
                    self.history_index += 1
                last_step_time = time.time()

            self.render()
            self.clock.tick(self.fps)
