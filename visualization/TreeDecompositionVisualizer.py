"""
visualization/TreeDecompositionVisualizer.py
Pygame visualizer for Tree Decomposition & Junction Tree CSP Solving.
"""

import sys
import os
import pygame
import math
from typing import Dict, Any, List, Tuple

from csp.TreeDecomposition import TreeDecompositionSolver, TreeDecomposition
from csp.CSPProblem import CSPProblem

# Colors
BG_COLOR = (24, 28, 36)
TEXT_COLOR = (235, 240, 245)
TITLE_COLOR = (255, 215, 0)
CLUSTER_BG = (45, 55, 75)
CLUSTER_BORDER = (80, 160, 240)
SEPARATOR_COLOR = (220, 120, 50)
NODE_FILL = (35, 40, 55)
NODE_BORDER = (120, 130, 150)
SOLVED_COLOR = (80, 200, 120)
ACCENT_BLUE = (70, 150, 235)
HUD_BG = (18, 22, 30)


class TreeDecompositionVisualizer:
    def __init__(self, problem: CSPProblem, solver: TreeDecompositionSolver, fps: int = 2):
        pygame.init()
        self.W, self.H = 1000, 700
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("Tree Decomposition & Junction Tree Visualizer")
        self.clock = pygame.time.Clock()
        self.fps = fps

        self.problem = problem
        self.solver = solver
        self.decomp = solver.decomposition

        self.font_lg = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 13)

        # Compute cluster positions in a circle/tree layout
        self.cluster_pos = {}
        cids = list(self.decomp.clusters.keys())
        n = len(cids)
        cx, cy = self.W // 2, self.H // 2 - 20
        radius = min(self.W, self.H) // 3.2

        for i, cid in enumerate(cids):
            angle = (2 * math.pi * i / n) - (math.pi / 2)
            px = int(cx + radius * math.cos(angle))
            py = int(cy + radius * math.sin(angle))
            self.cluster_pos[cid] = (px, py)

        # Precompute step history
        self.history = []
        self._build_history()
        self.history_index = 0
        self.auto_run = True

    def _build_history(self):
        # Step 1: Initial clusters
        self.history.append({
            "stage": "Tree Decomposition Structure",
            "desc": "Formed clusters (megavariables) & Junction Tree structure.",
            "sol": None
        })

        # Step 2: Internal domains generated
        cluster_domains = self.solver._generate_cluster_domains()
        self.history.append({
            "stage": "Internal Cluster Domain Generation",
            "desc": f"Generated valid internal tuples for each cluster.",
            "domains": cluster_domains,
            "sol": None
        })

        # Step 3: Meta-tree solving
        sol = self.solver.solve()
        self.history.append({
            "stage": "Zero-Backtrack Meta-Tree Solving Complete",
            "desc": "Solved Meta-Tree CSP via directional arc consistency & reconstructed full assignment.",
            "sol": sol
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

        # Draw Junction Tree edges
        for u, v in self.decomp.edges:
            p1 = self.cluster_pos[u]
            p2 = self.cluster_pos[v]
            pygame.draw.line(self.screen, ACCENT_BLUE, p1, p2, 4)
            # Shared separator label
            sep_vars = [var for var in self.decomp.clusters[u] if var in self.decomp.clusters[v]]
            if sep_vars:
                mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
                lbl = f"Sep: {','.join(map(str, sep_vars))}"
                txt = self.font_sm.render(lbl, True, SEPARATOR_COLOR)
                self.screen.blit(txt, (mx - txt.get_width() // 2, my - 12))

        # Draw Clusters
        for cid, (px, py) in self.cluster_pos.items():
            cvars = self.decomp.clusters[cid]
            lbl = f"{cid}: [{', '.join(map(str, cvars))}]"
            txt_surf = self.font_md.render(lbl, True, TEXT_COLOR)
            w, h = txt_surf.get_width() + 30, txt_surf.get_height() + 20
            rect = pygame.Rect(px - w // 2, py - h // 2, w, h)

            border_col = SOLVED_COLOR if step["sol"] else CLUSTER_BORDER
            pygame.draw.rect(self.screen, CLUSTER_BG, rect, border_radius=10)
            pygame.draw.rect(self.screen, border_col, rect, width=3, border_radius=10)
            self.screen.blit(txt_surf, (px - txt_surf.get_width() // 2, py - txt_surf.get_height() // 2))

        # HUD Overlay
        hud_rect = pygame.Rect(0, self.H - 120, self.W, 120)
        pygame.draw.rect(self.screen, HUD_BG, hud_rect)
        pygame.draw.line(self.screen, TITLE_COLOR, (0, self.H - 120), (self.W, self.H - 120), 2)

        title = self.font_lg.render(f"Step {self.history_index + 1}/{len(self.history)}: {step['stage']}", True, TITLE_COLOR)
        self.screen.blit(title, (20, self.H - 110))

        desc = self.font_md.render(step['desc'], True, TEXT_COLOR)
        self.screen.blit(desc, (20, self.H - 80))

        if step["sol"]:
            sol_str = "Solution: " + ", ".join(f"{k}:{v}" for k, v in sorted(step["sol"].items()))
            if len(sol_str) > 90:
                sol_str = sol_str[:90] + "..."
            sol_txt = self.font_sm.render(sol_str, True, SOLVED_COLOR)
            self.screen.blit(sol_txt, (20, self.H - 50))

        ctrl_txt = self.font_sm.render("Controls: [SPACE] Toggle Auto-Run | [LEFT/RIGHT] Step Navigation | [ESC] Exit", True, ACCENT_BLUE)
        self.screen.blit(ctrl_txt, (20, self.H - 25))

        pygame.display.flip()
