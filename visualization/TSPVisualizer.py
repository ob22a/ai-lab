"""
TSPVisualizer.py
Pygame visualizer for Traveling Salesperson Problem (TSP) Optimization.

Features:
  - Animated step-by-step tour optimization trajectory
  - Real-time candidate tour morphing and distance progression graph
  - Highlights current tour vs overall best tour found
  - Supports Hill Climbing, Simulated Annealing, Local Beam Search, Genetic Algorithm
"""

import pygame
import time
import random
from domains.tsp.TSPProblem import TSPProblem
from search.SearchAlgorithm import SearchStatus

# Colors
BG_COLOR = (15, 20, 30)
HUD_BG = (25, 30, 48)
HUD_LINE = (60, 70, 100)
TEXT_COLOR = (230, 235, 255)
TEXT_DIM = (130, 140, 170)
GOLD = (255, 200, 60)
CITY_COLOR = (240, 80, 80)
TOUR_COLOR = (80, 200, 240)
BEST_TOUR_COLOR = (80, 240, 140)
GRAPH_BG = (20, 26, 42)


class TSPVisualizer:
    def __init__(self, num_cities: int = 20, solver_class=None, fps: int = 60):
        self.W, self.H = 1000, 650
        self.HUD_W = 280
        self.fps = fps

        random.seed(42)
        cities = [(random.uniform(0.05, 0.95), random.uniform(0.05, 0.95)) for _ in range(num_cities)]
        self.problem = TSPProblem(cities)
        self.solver_class = solver_class

        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – TSP Optimization Visualizer")

        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 12)

        self.running = True
        self.history = []
        self.distances = []
        self.best_distances = []
        self.history_index = 0
        self.auto_run = True

        self._solve()

    def _solve(self):
        from search.local.SimulatedAnnealing import SimulatedAnnealing
        cls = self.solver_class or SimulatedAnnealing
        solver = cls(self.problem)

        solver.reset()
        t0 = time.time()

        initial_st = solver.current_state if hasattr(solver, 'current_state') else self.problem.initial_state
        self.history = [initial_st]
        self.best_state = initial_st
        self.best_value = self.problem.value(initial_st)
        
        self.distances = [-self.best_value]
        self.best_distances = [-self.best_value]

        # Step through solver and record trajectory
        step_count = 0
        max_steps = 1500

        while solver.status == SearchStatus.RUNNING and step_count < max_steps:
            solver.search_step()
            step_count += 1
            curr_st = getattr(solver, 'current_state', None)
            if curr_st is not None:
                val = self.problem.value(curr_st)
                if val > self.best_value:
                    self.best_value = val
                    self.best_state = curr_st
                
                # Sample state history
                if step_count % 2 == 0 or curr_st != self.history[-1]:
                    self.history.append(curr_st)
                    self.distances.append(-val)
                    self.best_distances.append(-self.best_value)

        self.runtime = time.time() - t0
        if not self.history:
            self.history = [self.problem.initial_state]
            self.distances = [-self.problem.value(self.problem.initial_state)]
            self.best_distances = [self.distances[0]]

    def render(self):
        self.screen.fill(BG_COLOR)
        canvas_w = self.W - self.HUD_W

        idx = min(self.history_index, len(self.history) - 1)
        state = self.history[idx] if self.history else self.problem.initial_state
        curr_dist = self.distances[idx] if idx < len(self.distances) else -self.problem.value(state)
        best_dist = self.best_distances[idx] if idx < len(self.best_distances) else -self.best_value

        # Graph area at bottom of canvas
        graph_h = 130
        map_h = self.H - graph_h - 20

        # Scale coordinates for 2D map
        def c2p(c):
            return int(c[0] * (canvas_w - 60) + 30), int(c[1] * (map_h - 60) + 30)

        # 1. Draw Current Tour Lines
        if state and len(state) > 1:
            for i in range(len(state)):
                p1 = c2p(self.problem.cities[state[i-1]])
                p2 = c2p(self.problem.cities[state[i]])
                pygame.draw.line(self.screen, TOUR_COLOR, p1, p2, 2)

        # 2. Draw City Nodes
        for i, city in enumerate(self.problem.cities):
            pos = c2p(city)
            pygame.draw.circle(self.screen, CITY_COLOR, pos, 7)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 2)
            lbl = self.font_sm.render(str(i), True, TEXT_DIM)
            self.screen.blit(lbl, (pos[0] + 8, pos[1] - 8))

        # 3. Distance Drop Graph at Bottom
        graph_rect = pygame.Rect(20, map_h + 10, canvas_w - 40, graph_h - 10)
        pygame.draw.rect(self.screen, GRAPH_BG, graph_rect, border_radius=8)
        pygame.draw.rect(self.screen, HUD_LINE, graph_rect, width=1, border_radius=8)

        # Draw Distance curve
        if len(self.distances) > 1:
            max_d = max(self.distances)
            min_d = min(self.best_distances)
            d_range = max(1.0, max_d - min_d)

            pts = []
            for i in range(min(idx + 1, len(self.distances))):
                gx = graph_rect.x + int((i / max(1, len(self.distances) - 1)) * graph_rect.width)
                gy = graph_rect.bottom - 10 - int(((self.distances[i] - min_d) / d_range) * (graph_rect.height - 20))
                pts.append((gx, gy))

            if len(pts) > 1:
                pygame.draw.lines(self.screen, BEST_TOUR_COLOR, False, pts, 2)

        g_lbl = self.font_sm.render("Distance Progression Curve", True, TEXT_DIM)
        self.screen.blit(g_lbl, (graph_rect.x + 10, graph_rect.y + 6))

        # 4. Draw HUD
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

        txt("TSP OPTIMIZATION", self.font_lg, GOLD, 10)
        txt(f"Cities: {len(self.problem.cities)}")
        txt(f"Solver: {self.solver_class.__name__ if self.solver_class else 'SimulatedAnnealing'}")
        hy += 10
        txt(f"Current Dist: {curr_dist:.2f}", col=TOUR_COLOR)
        txt(f"Best Dist:    {best_dist:.2f}", col=BEST_TOUR_COLOR)
        txt(f"Runtime:      {self.runtime:.4f}s")
        hy += 10
        txt(f"Step: {self.history_index+1} / {len(self.history)}")
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
                        self.history_index = min(self.history_index + 1, len(self.history) - 1)
                    elif event.key == pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)
                    elif event.key == pygame.K_r:
                        self.history_index = 0

            if self.auto_run and time.time() - last_step_time > 0.04:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                last_step_time = time.time()

            self.render()
            self.clock.tick(self.fps)
