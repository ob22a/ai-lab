import pygame
import copy
import time
from typing import Deque, Dict, Any, List, Tuple, Optional

from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus
from core.node import Node
from core.utils import reconstruct_path


class MazeSearchVisualizer(Visualizer):
    """
    Interactive Pygame visualizer for Maze Search algorithms.
    Supports:
      1. Offline Search Solvers (A*, IDA*, GBFS, IGBFS, BFS, DFS, Bidirectional, etc.)
         - Displays explored set, frontier set, current node, and final reconstructed solution.
      2. Online Search Agents (LRTA*, Online DFS, etc.)
         - In-cell dynamic heuristic overlay (H(s) rendered directly inside/above each cell).
         - Real-time heat-map coloring for learned heuristic values and dead-end updates.
         - Step and iteration counters tracking current trial and cumulative steps.
         - Multi-trial LRTA* learning progression with trial history and convergence tracking.
    """

    def __init__(
        self,
        maze,
        solver: SearchAlgorithm,
        cell_size: int = 30,
        fps: int = 30,
        auto_run: bool = False,
        show_heuristics: bool = True
    ):
        self.maze = maze
        self.solver = solver

        self.cell_size = cell_size
        self.fps = fps
        self.auto_run = auto_run
        self.show_heuristics = show_heuristics

        self.maze_width = maze.cols * cell_size
        self.maze_height = maze.rows * cell_size
        self.hud_width = 310

        self.width = self.maze_width + self.hud_width
        self.height = max(self.maze_height, 480)

        # Palette & Styles
        self.COLORS = {
            "background": (24, 26, 33),
            "maze_bg": (255, 255, 255),
            
            "explored": (220, 228, 240),
            "frontier": (120, 175, 255),
            "current": (255, 90, 90),
            "solution": (80, 220, 120),
            
            "start": (255, 210, 60),
            "goal": (225, 80, 225),
            "wall": (35, 40, 50),
            
            "agent": (50, 150, 255),
            "agent_glow": (100, 200, 255, 120),
            "trail": (180, 210, 245),
            
            "h_cell_tint": (235, 242, 255),
            "h_cell_updated": (255, 220, 140),
            "h_text": (30, 45, 75),
            "h_text_updated": (180, 60, 20),

            "hud": (20, 22, 28),
            "hud_line": (45, 50, 65),
            "hud_text": (210, 215, 230),
            "hud_muted": (140, 145, 165),
            "hud_title": (255, 195, 80),
            "accent": (80, 160, 255),
            "success": (80, 220, 120),
            "warning": (255, 170, 60),
            "danger": (255, 85, 85),
            "card_bg": (32, 35, 46),
        }

        self.show_frontier = True
        self.show_explored = True
        self.show_solution = True
        self.show_current = True

        # Online search & trial state
        self.is_online = hasattr(self.solver, "env") or hasattr(self.solver, "H")
        self.trial_number = 1
        self.current_trial_steps = 0
        self.total_steps = 0
        self.trial_history: List[Tuple[int, int, bool]] = []  # (trial_num, steps, reached_goal)
        self.agent_trail: List[Tuple[int, int]] = []
        self.last_updated_cell: Optional[Tuple[int, int]] = None
        self.last_h_diff: float = 0.0

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        solver_name = self.solver.__class__.__name__
        pygame.display.set_caption(f"AI Framework - Maze Visualizer ({solver_name})")

        self.clock = pygame.time.Clock()
        
        # Adaptive font sizes
        h_font_size = max(10, min(16, int(self.cell_size * 0.42)))
        self.font_h = pygame.font.SysFont("consolas", h_font_size, bold=True)
        self.font_tiny = pygame.font.SysFont("consolas", 11)
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_bold = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 18, bold=True)

        self.running = True
        self.restart()

    def draw_cell(self, row: int, col: int, color: Tuple[int, int, int], padding: int = 1):
        x = col * self.cell_size
        y = row * self.cell_size
        padded_size = self.cell_size - (padding * 2)

        pygame.draw.rect(
            self.screen,
            color,
            (x + padding, y + padding, padded_size, padded_size)
        )

    def draw_walls(self):
        for row in self.maze.cells:
            for cell in row:
                x = cell.col * self.cell_size
                y = cell.row * self.cell_size

                if cell.top:
                    pygame.draw.line(self.screen, self.COLORS["wall"], (x, y), (x + self.cell_size, y), 2)
                if cell.right:
                    pygame.draw.line(self.screen, self.COLORS["wall"], (x + self.cell_size, y), (x + self.cell_size, y + self.cell_size), 2)
                if cell.bottom:
                    pygame.draw.line(self.screen, self.COLORS["wall"], (x, y + self.cell_size), (x + self.cell_size, y + self.cell_size), 2)
                if cell.left:
                    pygame.draw.line(self.screen, self.COLORS["wall"], (x, y), (x, y + self.cell_size), 2)

    def draw_online_heuristics(self, cur_state=None):
        """Draws dynamic in-cell heuristic numbers H(s) and learned cost heat-map tints."""
        if not hasattr(self.solver, "H") and not hasattr(self.solver, "get_H"):
            return

        h_table = getattr(self.solver, "H", {})
        if not h_table:
            return

        max_h = max(h_table.values()) if h_table else 1.0
        min_h = min(h_table.values()) if h_table else 0.0
        h_range = max(1.0, max_h - min_h)

        # 1. Draw Heat-map background tints for visited/perceived states
        for (r, c), h_val in h_table.items():
            if r >= self.maze.rows or c >= self.maze.cols:
                continue

            x = c * self.cell_size
            y = r * self.cell_size

            # Tint based on H value magnitude
            is_updated = (self.last_updated_cell == (r, c))
            if is_updated:
                tint = self.COLORS["h_cell_updated"]
            else:
                ratio = min(1.0, max(0.0, (h_val - min_h) / h_range))
                r_col = int(220 + 35 * ratio)
                g_col = int(235 - 35 * ratio)
                b_col = int(255 - 40 * ratio)
                tint = (r_col, g_col, b_col)

            pygame.draw.rect(self.screen, tint, (x + 2, y + 2, self.cell_size - 4, self.cell_size - 4))

    def draw_heuristic_numbers(self, cur_state=None):
        """Draws heuristic text numbers H(s) on top of all cell layers, ensuring maximum visibility."""
        if not self.show_heuristics or self.cell_size < 16:
            return

        if not hasattr(self.solver, "H") and not hasattr(self.solver, "get_H"):
            return

        h_table = getattr(self.solver, "H", {})
        if not h_table:
            return

        for (r, c), h_val in h_table.items():
            if r >= self.maze.rows or c >= self.maze.cols:
                continue

            x = c * self.cell_size
            y = r * self.cell_size

            is_updated = (self.last_updated_cell == (r, c))
            is_agent_here = (cur_state == (r, c))

            txt = f"{int(h_val)}" if isinstance(h_val, (int, float)) and h_val == int(h_val) else f"{h_val:.1f}"

            if is_agent_here:
                # Agent is on this cell (e.g. at Start node) - draw a floating badge on top of the agent
                surf = self.font_h.render(txt, True, (255, 255, 255))
                badge_w = surf.get_width() + 8
                badge_h = surf.get_height() + 4
                badge_rect = pygame.Rect(
                    x + (self.cell_size - badge_w) // 2,
                    y + (self.cell_size - badge_h) // 2,
                    badge_w,
                    badge_h
                )
                pygame.draw.rect(self.screen, (20, 30, 50), badge_rect, border_radius=4)
                pygame.draw.rect(self.screen, (100, 200, 255), badge_rect, 1, border_radius=4)
                self.screen.blit(surf, surf.get_rect(center=badge_rect.center))
            else:
                # Text rendered with subtle dark shadow for crystal clarity
                text_col = self.COLORS["h_text_updated"] if is_updated else self.COLORS["h_text"]
                surf = self.font_h.render(txt, True, text_col)
                rect = surf.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                self.screen.blit(surf, rect)

    def draw_hud(self):
        hud_x = self.maze_width
        hud_rect = pygame.Rect(hud_x, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud"], hud_rect)
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (hud_x, 0), (hud_x, self.height), 2)

        x = hud_x + 18
        y = 18

        def write(text, font=None, color=None, gap=5):
            nonlocal y
            f = font or self.font
            c = color or self.COLORS["hud_text"]
            surf = f.render(str(text), True, c)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + gap

        solver_name = self.solver.__class__.__name__
        write("MAZE SEARCH VISUALIZER", self.font_title, self.COLORS["hud_title"], 8)
        write(f"Solver: {solver_name}", self.font_bold, self.COLORS["hud_text"], 4)
        
        status_name = self.solver.status.name if hasattr(self.solver.status, "name") else str(self.solver.status)
        is_success = (status_name == "SUCCESS")
        status_col = self.COLORS["success"] if is_success else self.COLORS["accent"]
        write(f"Status: {status_name}", self.font_bold, status_col, 12)

        if self.is_online:
            # Online Search & LRTA* Metrics
            write("ONLINE SEARCH METRICS", self.font_bold, self.COLORS["accent"], 6)
            write(f"Current Trial: #{self.trial_number}")
            write(f"Trial Steps:   {self.current_trial_steps}")
            write(f"Total Steps:   {self.total_steps}")
            
            # Agent coordinate & H info
            agent_loc = None
            if hasattr(self.solver, "env") and hasattr(self.solver.env, "agent_location"):
                agent_loc = self.solver.env.agent_location
            elif hasattr(self.solver, "current_node") and self.solver.current_node:
                agent_loc = self.solver.current_node.state

            if agent_loc:
                write(f"Agent Pos: {agent_loc}")

            if hasattr(self.solver, "H"):
                h_table = self.solver.H
                h_start = h_table.get(getattr(self.solver.env, "start_pos", (0, 0)), 0.0) if hasattr(self.solver, "env") else 0.0
                h_curr = h_table.get(agent_loc, 0.0) if agent_loc else 0.0
                write(f"H[Start]:   {h_start:.1f}")
                write(f"H[Current]: {h_curr:.1f}")
                write(f"Learned States: {len(h_table)} / {self.maze.rows * self.maze.cols}")
                
                if self.last_updated_cell:
                    write(f"Last H Update: {self.last_updated_cell} (+{self.last_h_diff:.1f})", color=self.COLORS["warning"])

            # Trial History Log
            y += 8
            write("TRIAL HISTORY", self.font_bold, self.COLORS["hud_title"], 6)
            if not self.trial_history:
                write("Trial #1 in progress...", font=self.font_small, color=self.COLORS["hud_muted"])
            else:
                for t_num, t_steps, t_ok in self.trial_history[-4:]:
                    tag = "GOAL" if t_ok else "STOP"
                    col = self.COLORS["success"] if t_ok else self.COLORS["danger"]
                    write(f"Trial {t_num:2d}: {t_steps:4d} steps [{tag}]", font=self.font_small, color=col)

            # Online Controls
            y += 12
            write("CONTROLS", self.font_bold, self.COLORS["hud_title"], 6)
            write("[SPACE] Step Agent")
            write("[A]     Toggle Auto-Run")
            write("[T]     Next Trial (Keep H)")
            write("[R]     Full Reset (Clear H)")
            write("[H]     Toggle H Overlay")
            write("[UP/DN] Adjust Speed (FPS)")

        else:
            # Offline Search Metrics
            write("SEARCH STATISTICS", self.font_bold, self.COLORS["accent"], 6)
            write(f"Nodes Expanded:  {self.solver.nodes_expanded}")
            write(f"Nodes Generated: {self.solver.nodes_generated}")
            
            if hasattr(self.solver, "frontier_states"):
                write(f"Frontier Size:   {len(self.solver.frontier_states)}")
            if hasattr(self.solver, "max_frontier_size"):
                write(f"Max Frontier:    {self.solver.max_frontier_size}")
            if self.solver.solution_node:
                path = reconstruct_path(self.solver.solution_node)
                write(f"Solution Length: {len(path) - 1}", color=self.COLORS["success"])

            y += 14
            write("CONTROLS", self.font_bold, self.COLORS["hud_title"], 6)
            write("[SPACE] Step Search")
            write("[A]     Toggle Auto-Run")
            write("[R]     Restart Solver")
            write("[UP/DN] Adjust Speed (FPS)")

        y += 14
        state_txt = "AUTO-RUNNING" if self.auto_run else "PAUSED / MANUAL"
        state_col = self.COLORS["success"] if self.auto_run else self.COLORS["warning"]
        write(f"Mode: {state_txt}", color=state_col)
        write(f"FPS:  {self.fps}")

    def render(self):
        self.screen.fill(self.COLORS["background"])

        # Maze Background fill
        maze_rect = pygame.Rect(0, 0, self.maze_width, self.maze_height)
        pygame.draw.rect(self.screen, self.COLORS["maze_bg"], maze_rect)

        # 1. Offline search overlays (explored, frontier, solution)
        if not self.is_online:
            if self.show_explored and hasattr(self.solver, "explored"):
                for state in self.solver.explored:
                    if isinstance(state, tuple) and len(state) == 2:
                        self.draw_cell(state[0], state[1], self.COLORS["explored"])

            if self.show_frontier and hasattr(self.solver, "frontier_states"):
                for state in self.solver.frontier_states:
                    if isinstance(state, tuple) and len(state) == 2:
                        self.draw_cell(state[0], state[1], self.COLORS["frontier"])

            if self.show_solution and self.solver.solution_node:
                path = reconstruct_path(self.solver.solution_node)
                for row, col in path:
                    self.draw_cell(row, col, self.COLORS["solution"])

        # 2. Online search overlays (trail & heat-map background tints)
        if self.is_online:
            # Draw agent trail
            for r, c in self.agent_trail:
                self.draw_cell(r, c, self.COLORS["trail"], padding=3)

            # Draw in-cell heat-map background tints
            self.draw_online_heuristics()

        # 3. Draw Start & Goal positions (soft tint + border + badges)
        start_pos, goal_pos = None, None
        if hasattr(self.solver, "problem"):
            start_pos = getattr(self.solver.problem, "start", (0, 0))
            goal_pos = getattr(self.solver.problem, "goal", (self.maze.rows - 1, self.maze.cols - 1))
        elif hasattr(self.solver, "env"):
            start_pos = getattr(self.solver.env, "start_pos", (0, 0))
            goal_pos = getattr(self.solver.env, "goal_pos", (self.maze.rows - 1, self.maze.cols - 1))

        if start_pos:
            sx = start_pos[1] * self.cell_size
            sy = start_pos[0] * self.cell_size
            # Soft start tint + border
            pygame.draw.rect(self.screen, (255, 242, 180), (sx + 2, sy + 2, self.cell_size - 4, self.cell_size - 4))
            pygame.draw.rect(self.screen, (240, 180, 40), (sx + 2, sy + 2, self.cell_size - 4, self.cell_size - 4), 2)
            # "S" badge in top-left
            s_label = self.font_tiny.render("S", True, (160, 100, 10))
            self.screen.blit(s_label, (sx + 4, sy + 3))

        if goal_pos:
            gx = goal_pos[1] * self.cell_size
            gy = goal_pos[0] * self.cell_size
            # Soft goal tint + border
            pygame.draw.rect(self.screen, (250, 220, 250), (gx + 2, gy + 2, self.cell_size - 4, self.cell_size - 4))
            pygame.draw.rect(self.screen, (210, 80, 210), (gx + 2, gy + 2, self.cell_size - 4, self.cell_size - 4), 2)
            # "G" badge in top-left
            g_label = self.font_tiny.render("G", True, (150, 30, 150))
            self.screen.blit(g_label, (gx + 4, gy + 3))

        # 4. Current Node / Agent Position
        cur_state = None
        if hasattr(self.solver, "env") and hasattr(self.solver.env, "agent_location"):
            cur_state = self.solver.env.agent_location
        elif self.solver.current_node:
            cur_state = self.solver.current_node.state

        if cur_state and isinstance(cur_state, tuple) and len(cur_state) == 2:
            r, c = cur_state
            cx = c * self.cell_size + self.cell_size // 2
            cy = r * self.cell_size + self.cell_size // 2
            rad = max(4, self.cell_size // 3)
            
            # Agent glow
            pygame.draw.circle(self.screen, (100, 200, 255), (cx, cy), rad + 3)
            pygame.draw.circle(self.screen, self.COLORS["agent"], (cx, cy), rad)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), max(2, rad // 2))

        # 5. In-Cell Dynamic Heuristic Overlay (ALWAYS ON TOP of Start, Goal, and Agent!)
        if self.is_online:
            self.draw_heuristic_numbers(cur_state=cur_state)

        # 6. Draw Walls & HUD
        self.draw_walls()
        self.draw_hud()

        pygame.display.flip()

    def _step_solver(self):
        if self.is_online:
            # Online Search Agent step
            env = self.solver.env
            if not hasattr(self.solver, "percept") or self.solver.percept is None:
                self.solver.percept = env.get_percept()

            cur_loc = env.get_percept()
            
            # Check if heuristic table exists to detect updates
            h_before = dict(self.solver.H) if hasattr(self.solver, "H") else {}

            action = self.solver.search_step(self.solver.percept)
            
            if action is None:
                self.solver.status = SearchStatus.SUCCESS
                # Record trial success
                if not self.trial_history or self.trial_history[-1][0] != self.trial_number:
                    self.trial_history.append((self.trial_number, self.current_trial_steps, True))
            else:
                new_loc = env.execute_action(action)
                self.solver.percept = new_loc
                self.current_trial_steps += 1
                self.total_steps += 1
                self.agent_trail.append(new_loc)

                # Check which cell's H changed
                if hasattr(self.solver, "H"):
                    for s, val in self.solver.H.items():
                        if val != h_before.get(s, 0.0):
                            self.last_updated_cell = s
                            self.last_h_diff = val - h_before.get(s, 0.0)
                            break

                self.solver.current_node = Node(new_loc, parent=None, action=action, path_cost=self.current_trial_steps)
                
                # If agent reached goal
                if hasattr(env, "is_goal") and env.is_goal(new_loc):
                    self.solver.status = SearchStatus.SUCCESS
                    if not self.trial_history or self.trial_history[-1][0] != self.trial_number:
                        self.trial_history.append((self.trial_number, self.current_trial_steps, True))
        else:
            # Standard Offline Search Algorithm step
            self.solver.search_step()

    def next_trial(self):
        """Starts a new learning trial: resets agent to start position while preserving learned heuristic table H."""
        if not self.is_online:
            self.restart()
            return

        if not self.trial_history or self.trial_history[-1][0] != self.trial_number:
            is_goal = hasattr(self.solver, "status") and (self.solver.status == SearchStatus.SUCCESS or self.solver.status == "SUCCESS")
            self.trial_history.append((self.trial_number, self.current_trial_steps, is_goal))

        self.trial_number += 1
        self.current_trial_steps = 0
        self.last_updated_cell = None

        if hasattr(self.solver, "reset"):
            self.solver.reset()
        if hasattr(self.solver, "env") and hasattr(self.solver.env, "reset"):
            self.solver.env.reset()

        if hasattr(self.solver, "env"):
            self.solver.percept = self.solver.env.get_percept()
            start_pos = self.solver.env.agent_location
            self.agent_trail = [start_pos]
            self.solver.current_node = Node(start_pos, parent=None, action=None, path_cost=0)

            # Ensure start node has its heuristic initialized
            if hasattr(self.solver, "H") and start_pos is not None:
                if start_pos not in self.solver.H:
                    if hasattr(self.solver, "h"):
                        self.solver.H[start_pos] = self.solver.h(start_pos)
                    elif hasattr(self.solver, "heuristic_func"):
                        self.solver.H[start_pos] = self.solver.heuristic_func(start_pos)

        self.solver.status = SearchStatus.RUNNING

    def restart(self):
        """Full reset: resets solver and trial history."""
        self.trial_number = 1
        self.current_trial_steps = 0
        self.total_steps = 0
        self.trial_history = []
        self.last_updated_cell = None
        self.auto_run = False

        if hasattr(self.solver, "H"):
            self.solver.H.clear()

        self.solver.reset()

        if hasattr(self.solver, "env"):
            if hasattr(self.solver.env, "reset"):
                self.solver.env.reset()
            self.solver.percept = self.solver.env.get_percept()
            start_pos = self.solver.env.agent_location
            self.agent_trail = [start_pos]
            self.solver.current_node = Node(start_pos, parent=None, action=None, path_cost=0)

            # Ensure start node has its initial heuristic initialized immediately
            if hasattr(self.solver, "H") and start_pos is not None:
                if start_pos not in self.solver.H:
                    if hasattr(self.solver, "h"):
                        self.solver.H[start_pos] = self.solver.h(start_pos)
                    elif hasattr(self.solver, "heuristic_func"):
                        self.solver.H[start_pos] = self.solver.heuristic_func(start_pos)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_r:
                    self.restart()

                elif event.key == pygame.K_t:
                    self.next_trial()

                elif event.key == pygame.K_h:
                    self.show_heuristics = not self.show_heuristics

                elif event.key == pygame.K_a:
                    self.auto_run = not self.auto_run

                elif event.key == pygame.K_UP:
                    self.fps = min(120, self.fps + 5)

                elif event.key == pygame.K_DOWN:
                    self.fps = max(1, self.fps - 5)

                elif event.key == pygame.K_SPACE:
                    status_name = self.solver.status.name if hasattr(self.solver.status, "name") else str(self.solver.status)
                    if status_name == "SUCCESS" and self.is_online:
                        self.next_trial()
                    elif status_name in ("RUNNING", "DEPTH_EXCEEDED"):
                        self._step_solver()

        status_name = self.solver.status.name if hasattr(self.solver.status, "name") else str(self.solver.status)
        if self.auto_run and status_name in ("RUNNING", "DEPTH_EXCEEDED"):
            self._step_solver()

    def run(self):
        while self.running:
            self.update()
            self.render()
            self.clock.tick(self.fps)

        pygame.quit()