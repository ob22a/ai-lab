"""
visualization/CycleCutsetVisualizer.py
Pygame visualizer for Cycle Cutset Conditioning & Tree Subproblem Solving.
"""

import sys
import os
import pygame
import math
from typing import Dict, Any, List, Tuple

from csp.CycleCutset import CycleCutsetSolver
from csp.CSPProblem import CSPProblem
from csp.TreeCSP import get_constraint_graph

# Colors
BG_COLOR = (24, 28, 36)
TEXT_COLOR = (235, 240, 245)
TITLE_COLOR = (255, 215, 0)
CUTSET_COLOR = (235, 80, 80)
TREE_COLOR = (70, 160, 240)
SOLVED_COLOR = (80, 200, 120)
EDGE_COLOR = (90, 105, 125)
HUD_BG = (18, 22, 30)


class CycleCutsetVisualizer:
    def __init__(self, problem: CSPProblem, solver: CycleCutsetSolver, fps: int = 2):
        pygame.init()
        self.W, self.H = 950, 680
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("Cycle Cutset Conditioning Visualizer")
        self.clock = pygame.time.Clock()
        self.fps = fps

        self.problem = problem
        self.solver = solver
        self.cutset = set(solver.cutset)
        self.tree_vars = set(solver.tree_vars)
        self.adj = solver.adj

        self.font_lg = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 13)

        # Compute variable node layout positions
        self.var_pos = {}
        all_vars = list(problem.variables)
        n = len(all_vars)
        cx, cy = self.W // 2, self.H // 2 - 30
        radius = min(self.W, self.H) // 3.0

        for i, var in enumerate(all_vars):
            angle = (2 * math.pi * i / n) - (math.pi / 2)
            px = int(cx + radius * math.cos(angle))
            py = int(cy + radius * math.sin(angle))
            self.var_pos[var] = (px, py)

        self.history = []
        self._build_history()
        self.history_index = 0
        self.auto_run = True

    def _build_history(self):
        # Step 1: Cutset identified
        self.history.append({
            "stage": "Cycle Cutset Identification",
            "desc": f"Identified Cutset S = {list(self.cutset)}. Remaining subproblem T is an acyclic tree forest.",
            "assign": None
        })

        # Step 2: Solution found
        sol = self.solver.solve()
        self.history.append({
            "stage": "Subproblem Conditioning & Resolution Complete",
            "desc": "Conditioned tree subproblem domains and solved tree CSP with zero backtracks.",
            "assign": sol
        })

    def run(self):
        running = True
        while running:
            self.W, self.H = self.screen.get_size()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.auto_run = not self.auto_run
                    elif event.key == pygame.K_RIGHT:
                        self.history_index = min(len(self.history) - 1, self.history_index + 1)
                    elif event.key == pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)

            if self.auto_run and self.history_index < len(self.history) - 1:
                self.history_index += 1

            self.render()
            self.clock.tick(self.fps)

        pygame.quit()

    def render(self):
        self.screen.fill(BG_COLOR)
        step = self.history[self.history_index]

        # Draw Graph Edges
        drawn_edges = set()
        for u in self.adj:
            for v in self.adj[u]:
                edge = tuple(sorted([str(u), str(v)]))
                if edge not in drawn_edges and u in self.var_pos and v in self.var_pos:
                    drawn_edges.add(edge)
                    pygame.draw.line(self.screen, EDGE_COLOR, self.var_pos[u], self.var_pos[v], 3)

        # Draw Variable Nodes
        for var, (px, py) in self.var_pos.items():
            is_cutset = var in self.cutset
            col = CUTSET_COLOR if is_cutset else TREE_COLOR

            val_str = ""
            if step["assign"] and var in step["assign"]:
                val_str = f"={step['assign'][var]}"

            lbl = f"{var}{val_str}"
            txt = self.font_md.render(lbl, True, TEXT_COLOR)

            radius = 28
            pygame.draw.circle(self.screen, BG_COLOR, (px, py), radius)
            pygame.draw.circle(self.screen, col, (px, py), radius, width=4)
            self.screen.blit(txt, (px - txt.get_width() // 2, py - txt.get_height() // 2))

        # HUD Overlay
        hud_rect = pygame.Rect(0, self.H - 120, self.W, 120)
        pygame.draw.rect(self.screen, HUD_BG, hud_rect)
        pygame.draw.line(self.screen, TITLE_COLOR, (0, self.H - 120), (self.W, self.H - 120), 2)

        title = self.font_lg.render(f"Step {self.history_index + 1}/{len(self.history)}: {step['stage']}", True, TITLE_COLOR)
        self.screen.blit(title, (20, self.H - 110))

        desc = self.font_md.render(step['desc'], True, TEXT_COLOR)
        self.screen.blit(desc, (20, self.H - 80))

        if step["assign"]:
            sol_str = "Final Assignment: " + ", ".join(f"{k}:{v}" for k, v in sorted(step["assign"].items()))
            sol_txt = self.font_sm.render(sol_str, True, SOLVED_COLOR)
            self.screen.blit(sol_txt, (20, self.H - 50))

        ctrl_txt = self.font_sm.render("Legend: RED = Cutset S | BLUE = Tree T | [SPACE] Auto-Run | [LEFT/RIGHT] Step | [ESC] Exit", True, TITLE_COLOR)
        self.screen.blit(ctrl_txt, (20, self.H - 25))

        pygame.display.flip()
