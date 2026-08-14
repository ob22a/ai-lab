"""
TSPVisualizer.py
Pygame visualizer for Traveling Salesperson Problem (TSP) Optimization.

Features:
  - Supports Hill Climbing, Simulated Annealing, Local Beam Search, Genetic Algorithm
  - Local Beam Search Mode: Displays k parallel candidate beam tour routes, beam selector tabs [1..k], and Best vs Avg Beam Distance curves.
  - Genetic Algorithm Mode: Displays top elite tour chromosomes per generation in HUD, interactive elite route selection, and Best vs Avg Population Distance curves.
  - Interactive speed controls (+/-), step navigation (LEFT/RIGHT), auto-run toggle (SPACE), and reset (R).
"""

import pygame
import time
import random
import math
from typing import List, Tuple, Dict, Any

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
AVG_TOUR_COLOR = (240, 160, 60)
GRAPH_BG = (20, 26, 42)
BUTTON_BG = (40, 50, 75)
BUTTON_ACTIVE = (70, 140, 230)


class TSPVisualizer:
    def __init__(self, num_cities: int = 20, solver_class=None, fps: int = 30):
        self.W, self.H = 1050, 700
        self.HUD_W = 320
        self.fps = fps

        random.seed(42)
        cities = [(random.uniform(0.05, 0.95), random.uniform(0.05, 0.95)) for _ in range(num_cities)]
        self.problem = TSPProblem(cities)
        self.solver_class = solver_class

        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – TSP Optimization & Population Visualizer")

        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 12)

        self.running = True
        self.history: List[Dict[str, Any]] = []
        self.history_index = 0
        self.selected_sub_idx = 0
        self.auto_run = True

        self._solve()

    def _solve(self):
        from search.local.SimulatedAnnealing import SimulatedAnnealing
        from search.local.LocalBeamSearch import LocalBeamSearch
        from search.local.GeneticAlgorithm import GeneticAlgorithm

        cls = self.solver_class or SimulatedAnnealing
        solver = cls(self.problem)
        solver.reset()

        t0 = time.time()
        self.history = []

        mode = "single"
        if isinstance(solver, LocalBeamSearch):
            mode = "beam"
        elif isinstance(solver, GeneticAlgorithm):
            mode = "ga"

        step_count = 0
        max_steps = 2000

        best_overall_st = self.problem.initial_state
        best_overall_dist = -self.problem.value(best_overall_st)

        no_change_count = 0
        while solver.status == SearchStatus.RUNNING and step_count < max_steps:
            solver.search_step()
            step_count += 1

            if mode == "beam":
                beams = getattr(solver, 'population', [getattr(solver, 'current_state', self.problem.initial_state)])
                beam_dists = [-self.problem.value(st) for st in beams]
                min_d = min(beam_dists)
                avg_d = sum(beam_dists) / len(beam_dists)
                best_st = beams[beam_dists.index(min_d)]

                if min_d < best_overall_dist:
                    best_overall_dist = min_d
                    best_overall_st = best_st

                self.history.append({
                    "mode": "beam",
                    "step": step_count,
                    "beams": beams,
                    "beam_dists": beam_dists,
                    "best_dist": min_d,
                    "avg_dist": avg_d,
                    "best_overall": best_overall_dist,
                    "best_state": best_st
                })

            elif mode == "ga":
                pop = getattr(solver, 'population', [getattr(solver, 'current_state', self.problem.initial_state)])
                pop_dists = [(-self.problem.value(st), st) for st in pop]
                pop_dists.sort(key=lambda x: x[0])

                best_d = pop_dists[0][0]
                avg_d = sum(d for d, _ in pop_dists) / len(pop_dists)
                best_st = pop_dists[0][1]

                if best_d < best_overall_dist:
                    best_overall_dist = best_d
                    best_overall_st = best_st

                # Top 6 elites
                top_elites = pop_dists[:6]

                self.history.append({
                    "mode": "ga",
                    "generation": getattr(solver, 'generation', step_count),
                    "elites": top_elites,
                    "best_dist": best_d,
                    "avg_dist": avg_d,
                    "best_overall": best_overall_dist,
                    "best_state": best_st
                })

            else:
                curr_st = getattr(solver, 'current_state', self.problem.initial_state)
                curr_d = -self.problem.value(curr_st)
                temp = getattr(solver, 'temperature', None)

                if curr_d < best_overall_dist - 1e-4:
                    best_overall_dist = curr_d
                    best_overall_st = curr_st
                    no_change_count = 0
                else:
                    no_change_count += 1

                self.history.append({
                    "mode": "single",
                    "step": step_count,
                    "state": curr_st,
                    "best_dist": curr_d,
                    "avg_dist": curr_d,
                    "best_overall": best_overall_dist,
                    "temp": temp,
                    "best_state": best_overall_st
                })

                # Dynamic convergence early stopping for SA / HC
                if no_change_count >= 150:
                    break

        self.runtime = time.time() - t0
        if not self.history:
            init_d = -self.problem.value(self.problem.initial_state)
            self.history = [{
                "mode": "single",
                "step": 0,
                "state": self.problem.initial_state,
                "best_dist": init_d,
                "avg_dist": init_d,
                "best_overall": init_d,
                "temp": None,
                "best_state": self.problem.initial_state
            }]

    def render(self):
        self.screen.fill(BG_COLOR)
        canvas_w = self.W - self.HUD_W

        idx = min(self.history_index, len(self.history) - 1)
        step_data = self.history[idx]
        mode = step_data["mode"]

        # Graph area at bottom of canvas
        graph_h = 140
        map_h = self.H - graph_h - 20

        def c2p(c):
            return int(c[0] * (canvas_w - 60) + 30), int(c[1] * (map_h - 60) + 30)

        # Determine active state to render on 2D map
        active_state = None
        if mode == "beam":
            beams = step_data["beams"]
            sub_idx = min(self.selected_sub_idx, len(beams) - 1)
            active_state = beams[sub_idx]
        elif mode == "ga":
            elites = step_data["elites"]
            sub_idx = min(self.selected_sub_idx, len(elites) - 1)
            active_state = elites[sub_idx][1]
        else:
            active_state = step_data["state"]

        # 1. Draw Tour Lines
        if active_state and len(active_state) > 1:
            for i in range(len(active_state)):
                p1 = c2p(self.problem.cities[active_state[i - 1]])
                p2 = c2p(self.problem.cities[active_state[i]])
                pygame.draw.line(self.screen, TOUR_COLOR, p1, p2, 2)

        # 2. Draw City Nodes
        for i, city in enumerate(self.problem.cities):
            pos = c2p(city)
            pygame.draw.circle(self.screen, CITY_COLOR, pos, 7)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 2)
            lbl = self.font_sm.render(str(i), True, TEXT_DIM)
            self.screen.blit(lbl, (pos[0] + 8, pos[1] - 8))

        # 3. Distance Progression Dual Curve Chart
        graph_rect = pygame.Rect(20, map_h + 10, canvas_w - 40, graph_h - 10)
        pygame.draw.rect(self.screen, GRAPH_BG, graph_rect, border_radius=8)
        pygame.draw.rect(self.screen, HUD_LINE, graph_rect, width=1, border_radius=8)

        best_dists = [h["best_dist"] for h in self.history]
        avg_dists = [h["avg_dist"] for h in self.history]

        if len(best_dists) > 1:
            max_d = max(max(best_dists), max(avg_dists))
            min_d = min(min(best_dists), min(avg_dists))
            d_range = max(1.0, max_d - min_d)

            best_pts = []
            avg_pts = []
            cur_limit = min(idx + 1, len(self.history))
            total_n = max(1, len(self.history) - 1)

            for i in range(cur_limit):
                gx = graph_rect.x + int((i / total_n) * graph_rect.width)
                by = graph_rect.bottom - 12 - int(((best_dists[i] - min_d) / d_range) * (graph_rect.height - 24))
                ay = graph_rect.bottom - 12 - int(((avg_dists[i] - min_d) / d_range) * (graph_rect.height - 24))
                best_pts.append((gx, by))
                avg_pts.append((gx, ay))

            if len(avg_pts) > 1 and mode in ("beam", "ga"):
                pygame.draw.lines(self.screen, AVG_TOUR_COLOR, False, avg_pts, 2)
            if len(best_pts) > 1:
                pygame.draw.lines(self.screen, BEST_TOUR_COLOR, False, best_pts, 2)

        title_label = "Best (Green) vs Avg (Orange) Distance Curve" if mode in ("beam", "ga") else "Distance Progression Curve"
        g_lbl = self.font_sm.render(title_label, True, TEXT_DIM)
        self.screen.blit(g_lbl, (graph_rect.x + 10, graph_rect.y + 6))

        # 4. HUD Panel
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

        solver_name = self.solver_class.__name__ if self.solver_class else "SimulatedAnnealing"
        txt("TSP OPTIMIZATION", self.font_lg, GOLD, 8)
        txt(f"Cities: {len(self.problem.cities)} | Solver: {solver_name}")
        txt(f"Simulation Speed: {self.fps} FPS", self.font_sm, CYAN, 6)
        hy += 4

        txt(f"Best Dist:    {step_data['best_dist']:.2f}", col=BEST_TOUR_COLOR)
        if mode in ("beam", "ga"):
            txt(f"Avg Dist:     {step_data['avg_dist']:.2f}", col=AVG_TOUR_COLOR)
        txt(f"Overall Best: {step_data['best_overall']:.2f}", col=GOLD)
        txt(f"Runtime:      {self.runtime:.4f}s")
        hy += 6

        # Mode-Specific Interactive Controls (Candidate Tabs / Elite Inspector)
        if mode == "beam":
            txt("BEAM CANDIDATES (k = %d):" % len(step_data["beams"]), col=TEXT_DIM)
            num_b = min(6, len(step_data["beams"]))
            tab_w = (self.HUD_W - 32) // max(1, num_b)
            for bi in range(num_b):
                bx = hx + bi * tab_w
                b_rect = pygame.Rect(bx, hy, tab_w - 3, 24)
                is_sel = bi == self.selected_sub_idx
                pygame.draw.rect(self.screen, BUTTON_ACTIVE if is_sel else BUTTON_BG, b_rect, border_radius=4)
                d_lbl = self.font_sm.render(f"B{bi+1}:{step_data['beam_dists'][bi]:.0f}", True, TEXT_COLOR)
                self.screen.blit(d_lbl, (bx + 2, hy + 4))
            hy += 30

        elif mode == "ga":
            txt("POPULATION ELITES (Gen %d):" % step_data["generation"], col=TEXT_DIM)
            for ei, (edist, estate) in enumerate(step_data["elites"]):
                e_rect = pygame.Rect(hx, hy, self.HUD_W - 28, 22)
                is_sel = ei == self.selected_sub_idx
                pygame.draw.rect(self.screen, BUTTON_ACTIVE if is_sel else BUTTON_BG, e_rect, border_radius=4)
                e_lbl = self.font_sm.render(f"  Elite #{ei+1}: Dist = {edist:.2f}", True, TEXT_COLOR)
                self.screen.blit(e_lbl, (hx + 4, hy + 3))
                hy += 26
            hy += 4

        elif step_data.get("temp") is not None:
            txt(f"Temperature:  {step_data['temp']:.2f}", col=TEXT_DIM)
            hy += 6

        txt(f"Step: {self.history_index+1} / {len(self.history)}")
        hy += 8

        txt("CONTROLS:", col=TEXT_DIM)
        txt("[SPACE] Play / Pause", self.font_sm, TEXT_DIM)
        txt("[+/-]   Increase / Decrease Speed", self.font_sm, CYAN)
        txt("[LEFT/RIGHT] Step backward / forward", self.font_sm, TEXT_DIM)
        txt("[1-6] Select Beam / Elite Candidate", self.font_sm, TEXT_DIM)
        txt("[R] Restart | [ESC] Back to Hub", self.font_sm, TEXT_DIM)

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
                    if event.key in (pygame.K_ESCAPE, pygame.K_b):
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.auto_run = not self.auto_run
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                        self.fps = min(120, self.fps + 10)
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.fps = max(5, self.fps - 10)
                    elif event.key == pygame.K_RIGHT:
                        self.history_index = min(self.history_index + 1, len(self.history) - 1)
                    elif event.key == pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)
                    elif event.key == pygame.K_r:
                        self.history_index = 0
                    elif pygame.K_1 <= event.key <= pygame.K_6:
                        self.selected_sub_idx = event.key - pygame.K_1

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    canvas_w = self.W - self.HUD_W
                    if mx > canvas_w:
                        # Clicked HUD candidate buttons
                        step_data = self.history[min(self.history_index, len(self.history) - 1)]
                        if step_data["mode"] == "beam":
                            num_b = min(6, len(step_data["beams"]))
                            tab_w = (self.HUD_W - 32) // max(1, num_b)
                            rel_x = mx - canvas_w - 14
                            if rel_x >= 0:
                                self.selected_sub_idx = min(num_b - 1, rel_x // tab_w)

            if self.auto_run and time.time() - last_step_time > (1.0 / max(1, self.fps)):
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                last_step_time = time.time()

            self.render()
            self.clock.tick(self.fps)

        pygame.quit()

