"""
visualization/CycleCutsetVisualizer.py
State-of-the-Art Dual-Panel Pygame Visualizer for Cycle Cutset Conditioning & Tree Subproblem Solving.

Features:
  - Dual-Panel Architecture:
      Left Panel: Partitioned Constraint Graph displaying Cutset variables S (glowing Red/Gold) and Tree variables T (Electric Blue) with node value badges.
      Right Panel: Candidate Inspector displaying active cutset assignments to S and real-time domain pruning cards for T.
  - Step Inspector:
      Step 1: Greedy Cycle Cutset S Identification.
      Step 2: Candidate Cutset Assignment Testing.
      Step 3: Real-Time Domain Pruning on Conditioned Subproblem T.
      Step 4: Zero-Backtrack Tree Resolution & Merged Assignment Reconstruction.
  - Standardized Controls: [SPACE] Auto-Run | [LEFT/RIGHT] Step Navigation | [R] Restart | [ESC] Back.
"""

import sys
import os
import pygame
import time
import math
from typing import Dict, Any, List, Tuple

from csp.CycleCutset import CycleCutsetSolver
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
CUTSET_RED = (240, 80, 80)
TREE_BLUE = (80, 160, 245)
GREEN_SOLVED = (80, 220, 140)
PRUNED_RED = (200, 60, 60)
CARD_BG = (30, 38, 55)
ORANGE_SEP = (245, 150, 60)


class CycleCutsetVisualizer:
    def __init__(self, problem: CSPProblem, solver: CycleCutsetSolver, fps: int = 30):
        pygame.init()
        self.W, self.H = 1100, 720
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – Cycle Cutset Conditioning Visualizer")
        self.clock = pygame.time.Clock()
        self.fps = fps

        self.problem = problem
        self.solver = solver
        self.cutset = set(solver.cutset)
        self.tree_vars = set(solver.tree_vars)
        self.adj = solver.adj

        self.font_lg = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 12)

        self._compute_layout()

        self.history = []
        self._build_history()
        self.history_index = 0
        self.auto_run = True
        self.running = True

    def _compute_layout(self):
        panel_w = self.W // 2
        center_y = self.H // 2 - 30

        # Left Panel layout: Constraint graph variables in a circle
        self.var_pos = {}
        all_vars = list(self.problem.variables)
        n = len(all_vars)
        cx = panel_w // 2
        radius = min(panel_w, self.H) // 3.2

        for i, var in enumerate(all_vars):
            angle = (2 * math.pi * i / max(1, n)) - (math.pi / 2)
            px = int(cx + radius * math.cos(angle))
            py = int(center_y + radius * math.sin(angle))
            self.var_pos[var] = (px, py)

    def _build_history(self):
        # Step 1: Cutset Identification
        self.history.append({
            "stage": "1. Greedy Cycle Cutset S Identification",
            "desc": f"Identified Cutset S = {list(self.cutset)}. Remaining subproblem T = {list(self.tree_vars)} is an acyclic tree forest.",
            "s_assign": None,
            "pruned_domains": None,
            "sol": None
        })

        # Step 2: Cutset Candidate Assignment
        cutset_assigns = self.solver._get_cutset_assignments()
        candidate = cutset_assigns[0] if cutset_assigns else {}

        self.history.append({
            "stage": "2. Testing Cutset Candidate Assignment",
            "desc": f"Instantiating Cutset S with consistent assignment: {candidate}",
            "s_assign": candidate,
            "pruned_domains": None,
            "sol": None
        })

        # Step 3: Domain Conditioning on T
        conditioned_domains = {}
        for t_var in self.tree_vars:
            valid_vals = [val for val in self.problem.domains[t_var] if self.problem.is_consistent(t_var, val, dict(candidate))]
            conditioned_domains[t_var] = valid_vals

        self.history.append({
            "stage": "3. Real-Time Domain Conditioning on Tree T",
            "desc": f"Pruned values in tree variables T inconsistent with candidate cutset assignment S.",
            "s_assign": candidate,
            "pruned_domains": conditioned_domains,
            "sol": None
        })

        # Step 4: Solved Full Assignment
        sol = self.solver.solve()
        self.history.append({
            "stage": "4. Zero-Backtrack Tree Resolution & Global Reconstruction",
            "desc": "Solved conditioned tree subproblem T with 0 backtracks and merged with S.",
            "s_assign": candidate,
            "pruned_domains": conditioned_domains,
            "sol": sol
        })

    def render(self):
        self.screen.fill(BG_COLOR)
        panel_w = self.W // 2
        step = self.history[self.history_index]

        # Draw Left Panel (Partitioned Graph)
        left_rect = pygame.Rect(0, 0, panel_w, self.H - 130)
        pygame.draw.rect(self.screen, PANEL_LEFT_BG, left_rect)
        pygame.draw.line(self.screen, HUD_LINE, (panel_w, 0), (panel_w, self.H - 130), 2)

        # Draw Right Panel (Domain Inspector)
        right_rect = pygame.Rect(panel_w, 0, panel_w, self.H - 130)
        pygame.draw.rect(self.screen, PANEL_RIGHT_BG, right_rect)

        # --- LEFT PANEL RENDERING ---
        hide_cutset = (self.history_index > 0)
        panel_title = "CONDITIONED SUBPROBLEM T (ACYCLIC TREE)" if hide_cutset else "FULL CONSTRAINT GRAPH (S + T)"
        lbl_left = self.font_lg.render(panel_title, True, GOLD)
        self.screen.blit(lbl_left, (20, 15))

        if hide_cutset:
            sub_lbl = self.font_sm.render(f"[Cutset S={list(self.cutset)} Removed -> Remaining Subproblem is a Tree]", True, ORANGE_SEP)
            self.screen.blit(sub_lbl, (20, 42))

        # Constraint Graph Edges
        drawn_edges = set()
        for u in self.adj:
            if hide_cutset and u in self.cutset:
                continue
            for v in self.adj[u]:
                if hide_cutset and v in self.cutset:
                    continue
                edge = tuple(sorted([str(u), str(v)]))
                if edge not in drawn_edges and u in self.var_pos and v in self.var_pos:
                    drawn_edges.add(edge)
                    pygame.draw.line(self.screen, CYAN if hide_cutset else HUD_LINE, self.var_pos[u], self.var_pos[v], 3 if hide_cutset else 2)

        # Variable Nodes
        for var, (px, py) in self.var_pos.items():
            is_cutset = var in self.cutset
            if hide_cutset and is_cutset:
                # Cutset variable is removed from graph view when conditioned
                continue

            col = CUTSET_RED if is_cutset else TREE_BLUE

            val_str = ""
            if step["sol"] and var in step["sol"]:
                val_str = f"={step['sol'][var]}"
            elif step["s_assign"] and var in step["s_assign"]:
                val_str = f"={step['s_assign'][var]}"

            lbl = f"{var}{val_str}"
            txt_s = self.font_md.render(lbl, True, TEXT_COLOR)

            pygame.draw.circle(self.screen, BG_COLOR, (px, py), 26)
            pygame.draw.circle(self.screen, col, (px, py), 26, width=3)
            self.screen.blit(txt_s, (px - txt_s.get_width() // 2, py - txt_s.get_height() // 2))

            # Cutset Badge (when visible in step 0)
            if is_cutset and not hide_cutset:
                c_txt = self.font_sm.render("[S]", True, GOLD)
                self.screen.blit(c_txt, (px - c_txt.get_width() // 2, py - 38))

        # --- RIGHT PANEL RENDERING ---
        lbl_right = self.font_lg.render("CANDIDATE & DOMAIN PRUNING INSPECTOR", True, GOLD)
        self.screen.blit(lbl_right, (panel_w + 20, 15))

        rx = panel_w + 20
        ry = 50

        # Cutset Candidate Card
        c_card = pygame.Rect(rx, ry, panel_w - 40, 70)
        pygame.draw.rect(self.screen, CARD_BG, c_card, border_radius=8)
        pygame.draw.rect(self.screen, CUTSET_RED, c_card, width=2, border_radius=8)

        self.screen.blit(self.font_md.render("Cutset Candidate S Assignment:", True, GOLD), (rx + 12, ry + 10))
        if step["s_assign"]:
            s_info = ", ".join(f"{k} = {v}" for k, v in step["s_assign"].items())
            self.screen.blit(self.font_md.render(s_info, True, TEXT_COLOR), (rx + 12, ry + 36))
        else:
            self.screen.blit(self.font_sm.render("(Evaluating Cutset partitioning...)", True, TEXT_DIM), (rx + 12, ry + 36))

        ry += 85
        self.screen.blit(self.font_md.render("Conditioned Domains for Tree Variables T:", True, CYAN), (rx, ry))
        ry += 24

        # Tree Variables Domain Cards
        for t_var in sorted(list(self.tree_vars), key=lambda x: str(x)):
            d_card = pygame.Rect(rx, ry, panel_w - 40, 50)
            pygame.draw.rect(self.screen, CARD_BG, d_card, border_radius=6)
            pygame.draw.rect(self.screen, TREE_BLUE, d_card, width=1, border_radius=6)

            all_vals = self.problem.domains[t_var]
            valid_vals = step["pruned_domains"][t_var] if step["pruned_domains"] and t_var in step["pruned_domains"] else all_vals

            v_title = self.font_md.render(f"Variable {t_var}:", True, TEXT_COLOR)
            self.screen.blit(v_title, (rx + 10, ry + 14))

            vx = rx + 120
            for val in all_vals:
                is_valid = val in valid_vals
                col = GREEN_SOLVED if is_valid else PRUNED_RED
                txt_v = self.font_sm.render(str(val), True, col)
                self.screen.blit(txt_v, (vx, ry + 15))
                if not is_valid:
                    # Strike-through line
                    pygame.draw.line(self.screen, PRUNED_RED, (vx, ry + 22), (vx + txt_v.get_width(), ry + 22), 2)
                vx += txt_v.get_width() + 14

            ry += 58

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

        ctrl_txt = self.font_sm.render("Legend: RED = Cutset S | BLUE = Tree T | [SPACE] Auto-Run | [LEFT/RIGHT] Step | [R] Restart | [ESC] Back", True, CYAN)
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
                    self._compute_layout()
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
