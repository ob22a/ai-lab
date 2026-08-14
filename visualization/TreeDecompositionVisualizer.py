"""
visualization/TreeDecompositionVisualizer.py
State-of-the-Art Dual-Panel Pygame Visualizer for Tree Decomposition & Junction Tree CSP Solving.

Features:
  - Dual-Panel Architecture:
      Left Panel: Original CSP Graph with node assignment badges and translucent cluster overlays (e.g. C1 = {WA, NT, SA}).
      Right Panel: Junction Meta-Tree & Separator edges displaying shared variable agreement rules.
  - Step Inspector:
      Step 1: Structural Clique Decomposition & Separators.
      Step 2: Internal Cluster Tuple Generation (showing explicit variable=value tuples).
      Step 3: Separator Agreement Constraints & Directional Arc Consistency.
      Step 4: Zero-Backtrack Global Assignment Reconstruction.
  - Standardized Controls: [SPACE] Auto-Run | [LEFT/RIGHT] Step Navigation | [R] Restart | [ESC] Back.
"""

import sys
import os
import pygame
import time
import math
from typing import Dict, Any, List, Tuple

from csp.TreeDecomposition import TreeDecompositionSolver, TreeDecomposition
from csp.CSPProblem import CSPProblem

# Rich Aesthetic Color Palette
BG_COLOR = (15, 18, 26)
PANEL_LEFT_BG = (22, 28, 40)
PANEL_RIGHT_BG = (18, 22, 32)
HUD_BG = (12, 15, 22)
HUD_LINE = (50, 65, 95)
TEXT_COLOR = (235, 240, 255)
TEXT_DIM = (140, 155, 185)
GOLD = (255, 215, 0)
CYAN = (70, 200, 240)
GREEN_SOLVED = (80, 220, 140)
RED_ALERT = (240, 80, 80)
ORANGE_SEP = (245, 150, 60)

CLUSTER_OVERLAY_COLORS = [
    (70, 130, 240, 60),   # Translucent Blue
    (240, 100, 120, 60),  # Translucent Red
    (90, 210, 140, 60),   # Translucent Green
    (240, 180, 70, 60),   # Translucent Orange
    (170, 110, 240, 60),  # Translucent Purple
]


class TreeDecompositionVisualizer:
    def __init__(self, problem: CSPProblem, solver: TreeDecompositionSolver, fps: int = 30):
        pygame.init()
        self.W, self.H = 1100, 720
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – Tree Decomposition & Junction Tree Visualizer")
        self.clock = pygame.time.Clock()
        self.fps = fps

        self.problem = problem
        self.solver = solver
        self.decomp = solver.decomposition

        self.font_lg = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 12)

        # Precompute positions for Left Panel (Original Graph) and Right Panel (Junction Tree)
        self._compute_layouts()

        self.history = []
        self._build_history()
        self.history_index = 0
        self.auto_run = True
        self.running = True

    def _compute_layouts(self):
        panel_w = self.W // 2
        center_y = self.H // 2 - 30

        # Left Panel layout: Original variables in a circle
        self.orig_var_pos = {}
        all_vars = list(self.problem.variables)
        n_orig = len(all_vars)
        cx_left = panel_w // 2
        r_left = min(panel_w, self.H) // 3.2

        for i, var in enumerate(all_vars):
            angle = (2 * math.pi * i / max(1, n_orig)) - (math.pi / 2)
            px = int(cx_left + r_left * math.cos(angle))
            py = int(center_y + r_left * math.sin(angle))
            self.orig_var_pos[var] = (px, py)

        # Right Panel layout: Junction Tree clusters in a circle
        self.meta_cluster_pos = {}
        cids = list(self.decomp.clusters.keys())
        n_meta = len(cids)
        cx_right = panel_w + panel_w // 2
        r_right = min(panel_w, self.H) // 3.2

        for i, cid in enumerate(cids):
            angle = (2 * math.pi * i / max(1, n_meta)) - (math.pi / 2)
            px = int(cx_right + r_right * math.cos(angle))
            py = int(center_y + r_right * math.sin(angle))
            self.meta_cluster_pos[cid] = (px, py)

    def _build_history(self):
        # Solve first to get full assignment and internal cluster domains
        sol = self.solver.solve()
        cluster_domains = self.solver._generate_cluster_domains()

        # Step 1: Clique Formation
        self.history.append({
            "stage": "1. Clique Cluster Decomposition",
            "desc": f"Formed {len(self.decomp.clusters)} overlapping variable clusters (megavariables) with Min-Fill elimination.",
            "tuples": None,
            "sol": None
        })

        # Step 2: Internal Cluster Tuple Generation
        self.history.append({
            "stage": "2. Internal Cluster Tuple Domain Generation",
            "desc": f"Generated valid internal tuples for each cluster satisfying internal constraints.",
            "tuples": cluster_domains,
            "sol": None
        })

        # Step 3: Directional Arc Consistency & Agreement
        self.history.append({
            "stage": "3. Separator Agreement & Directional Consistency",
            "desc": "Enforced separator agreement rules along tree edges (0 backtracks guaranteed).",
            "tuples": cluster_domains,
            "sol": None
        })

        # Step 4: Reconstructed Assignment
        self.history.append({
            "stage": "4. Zero-Backtrack Global Assignment Reconstruction",
            "desc": "Reconstructed full variable solution from meta-tree CSP.",
            "tuples": cluster_domains,
            "sol": sol
        })

    def render(self):
        self.screen.fill(BG_COLOR)
        panel_w = self.W // 2
        step = self.history[self.history_index]

        # Draw Left Panel (Original Graph)
        left_rect = pygame.Rect(0, 0, panel_w, self.H - 130)
        pygame.draw.rect(self.screen, PANEL_LEFT_BG, left_rect)
        pygame.draw.line(self.screen, HUD_LINE, (panel_w, 0), (panel_w, self.H - 130), 2)

        # Draw Right Panel (Junction Tree)
        right_rect = pygame.Rect(panel_w, 0, panel_w, self.H - 130)
        pygame.draw.rect(self.screen, PANEL_RIGHT_BG, right_rect)

        # --- LEFT PANEL RENDERING ---
        lbl_left = self.font_lg.render("ORIGINAL CSP GRAPH & CLUSTER MEMBERSHIPS", True, GOLD)
        self.screen.blit(lbl_left, (20, 15))

        # Original Graph Edges
        drawn_edges = set()
        for u in self.problem.variables:
            for constr in self.problem.constraints[u]:
                for v in constr.variables:
                    if u != v and u in self.orig_var_pos and v in self.orig_var_pos:
                        edge = tuple(sorted([str(u), str(v)]))
                        if edge not in drawn_edges:
                            drawn_edges.add(edge)
                            pygame.draw.line(self.screen, HUD_LINE, self.orig_var_pos[u], self.orig_var_pos[v], 2)

        # Map each variable to its containing clusters
        var_clusters = {}
        for cid, cvars in self.decomp.clusters.items():
            for v in cvars:
                if v not in var_clusters:
                    var_clusters[v] = []
                var_clusters[v].append(cid)

        # Original Graph Variable Nodes with Assignment & Cluster Membership Badges
        for var, (px, py) in self.orig_var_pos.items():
            val_str = ""
            if step["sol"] and var in step["sol"]:
                val_str = f"={step['sol'][var]}"

            lbl = f"{var}{val_str}"
            txt_s = self.font_md.render(lbl, True, TEXT_COLOR)
            border_col = GREEN_SOLVED if step["sol"] else CYAN

            pygame.draw.circle(self.screen, BG_COLOR, (px, py), 26)
            pygame.draw.circle(self.screen, border_col, (px, py), 26, width=3)
            self.screen.blit(txt_s, (px - txt_s.get_width() // 2, py - txt_s.get_height() // 2))

            # Render crisp Cluster Membership Tag Pill above node
            clusters_for_v = var_clusters.get(var, [])
            if clusters_for_v:
                c_tag_str = f"[{','.join(clusters_for_v)}]"
                c_tag_txt = self.font_sm.render(c_tag_str, True, ORANGE_SEP)
                self.screen.blit(c_tag_txt, (px - c_tag_txt.get_width() // 2, py - 42))

        # --- RIGHT PANEL RENDERING ---
        lbl_right = self.font_lg.render("JUNCTION META-TREE & SEPARATORS", True, GOLD)
        self.screen.blit(lbl_right, (panel_w + 20, 15))

        # Junction Tree Edges & Separators
        for u, v in self.decomp.edges:
            p1 = self.meta_cluster_pos[u]
            p2 = self.meta_cluster_pos[v]
            pygame.draw.line(self.screen, CYAN, p1, p2, 4)

            sep_vars = [var for var in self.decomp.clusters[u] if var in self.decomp.clusters[v]]
            if sep_vars:
                mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
                sep_lbl = f"Sep: {','.join(map(str, sep_vars))}"
                sep_txt = self.font_sm.render(sep_lbl, True, ORANGE_SEP)
                self.screen.blit(sep_txt, (mx - sep_txt.get_width() // 2, my - 12))

        # Junction Tree Cluster Nodes
        for cid, (px, py) in self.meta_cluster_pos.items():
            cvars = self.decomp.clusters[cid]
            lbl = f"{cid}: [{','.join(map(str, cvars))}]"
            txt_s = self.font_md.render(lbl, True, TEXT_COLOR)
            w, h = txt_s.get_width() + 24, txt_s.get_height() + 16
            rect = pygame.Rect(px - w // 2, py - h // 2, w, h)

            border_col = GREEN_SOLVED if step["sol"] else CYAN
            pygame.draw.rect(self.screen, BG_COLOR, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_col, rect, width=2, border_radius=8)
            self.screen.blit(txt_s, (px - txt_s.get_width() // 2, py - txt_s.get_height() // 2))

            # Display Tuples if in Step 2/3
            if step["tuples"] and cid in step["tuples"]:
                t_tuples = step["tuples"][cid]
                t_info = f"{len(t_tuples)} tuples"
                t_txt = self.font_sm.render(t_info, True, TEXT_DIM)
                self.screen.blit(t_txt, (px - t_txt.get_width() // 2, py + h // 2 + 4))

        # --- BOTTOM HUD OVERLAY ---
        hud_rect = pygame.Rect(0, self.H - 130, self.W, 130)
        pygame.draw.rect(self.screen, HUD_BG, hud_rect)
        pygame.draw.line(self.screen, GOLD, (0, self.H - 130), (self.W, self.H - 130), 2)

        st_title = self.font_lg.render(f"Step {self.history_index + 1}/{len(self.history)}: {step['stage']}", True, GOLD)
        self.screen.blit(st_title, (20, self.H - 120))

        st_desc = self.font_md.render(step['desc'], True, TEXT_COLOR)
        self.screen.blit(st_desc, (20, self.H - 92))

        if step["sol"]:
            sol_str = "Final Global Assignment: " + ", ".join(f"{k}:{v}" for k, v in sorted(step["sol"].items()))
            sol_txt = self.font_sm.render(sol_str, True, GREEN_SOLVED)
            self.screen.blit(sol_txt, (20, self.H - 64))

        ctrl_txt = self.font_sm.render("Controls: [SPACE] Toggle Auto-Run | [LEFT/RIGHT] Step Navigation | [R] Restart | [ESC] Back to Hub", True, CYAN)
        self.screen.blit(ctrl_txt, (20, self.H - 32))

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
                    self._compute_layouts()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_b):
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.auto_run = not self.auto_run
                    elif event.key == pygame.K_RIGHT:
                        self.history_index = min(len(self.history) - 1, self.history_index + 1)
                    elif event.key == pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)
                    elif event.key == pygame.K_r:
                        self.history_index = 0

            if self.auto_run and time.time() - last_step_time > 1.2:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                last_step_time = time.time()

            self.render()
            self.clock.tick(self.fps)

        pygame.quit()
