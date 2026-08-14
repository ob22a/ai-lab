import pygame
import time
from typing import Dict, Any, List, Union, Tuple, Optional, Set
from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus
from csp.CSPSolver import CSPSolver
from csp.CSPProblem import CSPProblem


class NQueensVisualizer(Visualizer):
    """
    Unified, high-fidelity N-Queens Visualizer supporting both:
    1. Constraint Satisfaction Problems (NQueensCSP + CSPSolver e.g. Backtracking, MAC, Symmetry Breaking, Min-Conflicts)
    2. Local Search Optimization Problems (NQueensProblem + SearchAlgorithm e.g. HillClimbing, SimulatedAnnealing, GeneticAlgorithm)
    """
    def __init__(self, problem: Any, solver: Any, cell_size: int = 60, fps: int = 8, auto_run: bool = False):
        self.problem = problem
        self.solver = solver
        self.cell_size = cell_size
        self.fps = fps
        self.auto_run = auto_run
        
        self.is_csp = isinstance(self.problem, CSPProblem) or isinstance(self.solver, CSPSolver)
        self.n = getattr(self.problem, "n", 8)
        self.max_fitness = (self.n * (self.n - 1)) // 2
        
        self.board_margin = 35
        self.board_pixel_size = self.n * self.cell_size
        self.hud_width = 340
        
        self.width = self.board_pixel_size + self.board_margin * 2 + self.hud_width
        self.height = max(self.board_pixel_size + self.board_margin * 2, 560)

        self.COLORS = {
            "bg": (28, 30, 36),
            "hud": (38, 42, 52),
            "hud_card": (48, 54, 66),
            "hud_line": (65, 73, 89),
            "hud_text": (220, 226, 235),
            "hud_dim": (145, 155, 170),
            "hud_title": (255, 204, 102),
            "hud_accent": (90, 200, 250),
            "status_running": (255, 200, 80),
            "status_success": (80, 220, 120),
            "status_failure": (255, 90, 90),
            "black_square": (118, 150, 86),
            "white_square": (238, 238, 210),
            "queen": (30, 30, 35),
            "queen_outline": (255, 255, 255),
            "queen_active": (70, 160, 245),
            "queen_conflict": (235, 65, 65),
            "backtracked_square": (255, 110, 110, 110),
            "conflict_line": (240, 70, 70),
            "progress_bar_bg": (60, 68, 84),
            "progress_bar_fill": (80, 200, 140)
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        title = "AI Lab - N-Queens CSP Visualizer" if self.is_csp else "AI Lab - N-Queens Local Search"
        pygame.display.set_caption(title)

        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("consolas", 12)
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_bold = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 19, bold=True)
        self.font_queen = pygame.font.SysFont("segoe ui symbol", int(self.cell_size * 0.7))

        self.running = True
        self.history: List[Dict[str, Any]] = []
        self.history_index = 0

        self.init_solver()

    def _state_to_queens(self, state: Any) -> List[Tuple[int, int]]:
        """
        Converts local search state (tuple where state[col] = row) to a list of (row, col) coordinates.
        Guarantees all N queens are preserved regardless of row collisions.
        """
        if isinstance(state, (tuple, list)):
            return [(state[col], col) for col in range(len(state))]
        elif isinstance(state, dict):
            return [(r, c) for r, c in state.items()]
        return []

    def _assignment_to_queens(self, assignment: Dict[Any, Any]) -> List[Tuple[int, int]]:
        """Converts CSP assignment dict {row: col} to list of (row, col) coordinates."""
        return [(r, c) for r, c in assignment.items() if r is not None and c is not None]

    def _get_attacking_pairs(self, queens: List[Tuple[int, int]]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Returns list of attacking queen coordinate pairs ((r1, c1), (r2, c2)).
        Checks row conflicts, column conflicts, and diagonal conflicts.
        """
        pairs = []
        for i in range(len(queens)):
            r1, c1 = queens[i]
            for j in range(i + 1, len(queens)):
                r2, c2 = queens[j]
                if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                    pairs.append(((r1, c1), (r2, c2)))
        return pairs

    def init_solver(self):
        """Initializes solver state and records search trajectory."""
        self.history = []
        self.history_index = 0
        
        if self.is_csp:
            self._record_csp_history()
        else:
            if hasattr(self.problem, "get_random_state"):
                self.problem.initial_state = self.problem.get_random_state()
            if hasattr(self.solver, "reset"):
                self.solver.reset()
            initial_state = getattr(self.solver, "current_state", tuple())
            queens = self._state_to_queens(initial_state)
            conflicts = len(self._get_attacking_pairs(queens))
            self.history.append({
                "queens": queens,
                "nodes_expanded": 0,
                "backtracks": 0,
                "conflicts": conflicts,
                "value": getattr(self.solver, "current_value", self.max_fitness - conflicts),
                "status": getattr(self.solver, "status", "RUNNING"),
                "action": "START",
                "active_queen": None,
                "backtracked_row": None,
                "temp": getattr(self.solver, "schedule", lambda t: 100)(0) if hasattr(self.solver, "schedule") else None
            })

    def _record_csp_history(self):
        """Executes CSP solver while recording every assignment and backtrack event."""
        recorded_steps: List[Dict[str, Any]] = []
        current_assign: Dict[Any, Any] = {}
        total_backtracks = 0
        
        recorded_steps.append({
            "queens": [],
            "nodes_expanded": 0,
            "backtracks": 0,
            "conflicts": 0,
            "value": 0,
            "status": "RUNNING",
            "action": "START",
            "active_queen": None,
            "backtracked_row": None,
            "temp": None
        })

        def handle_assign(var, val, assignment):
            current_assign[var] = val
            q_list = self._assignment_to_queens(current_assign)
            recorded_steps.append({
                "queens": q_list,
                "nodes_expanded": getattr(self.solver, "nodes_expanded", len(recorded_steps)),
                "backtracks": total_backtracks,
                "conflicts": len(self._get_attacking_pairs(q_list)),
                "value": len(q_list),
                "status": "RUNNING",
                "action": f"ASSIGN (Row {var} -> Col {val})",
                "active_queen": (var, val),
                "backtracked_row": None,
                "temp": None
            })

        def handle_unassign(var, assignment):
            nonlocal total_backtracks
            total_backtracks += 1
            if var in current_assign:
                del current_assign[var]
            q_list = self._assignment_to_queens(current_assign)
            recorded_steps.append({
                "queens": q_list,
                "nodes_expanded": getattr(self.solver, "nodes_expanded", len(recorded_steps)),
                "backtracks": total_backtracks,
                "conflicts": len(self._get_attacking_pairs(q_list)),
                "value": len(q_list),
                "status": "RUNNING",
                "action": f"BACKTRACK (Row {var})",
                "active_queen": None,
                "backtracked_row": var,
                "temp": None
            })

        if hasattr(self.solver, "on_assign"):
            self.solver.on_assign = handle_assign
            self.solver.on_unassign = handle_unassign

        solution = self.solver.solve()
        
        status_str = getattr(self.solver, "status", "SUCCESS" if solution is not None else "FAILURE")
        final_assign = solution if solution is not None else current_assign
        final_queens = self._assignment_to_queens(final_assign)
        
        recorded_steps.append({
            "queens": final_queens,
            "nodes_expanded": getattr(self.solver, "nodes_expanded", len(recorded_steps)),
            "backtracks": total_backtracks,
            "conflicts": len(self._get_attacking_pairs(final_queens)),
            "value": len(final_queens),
            "status": status_str,
            "action": "SEARCH COMPLETE",
            "active_queen": None,
            "backtracked_row": None,
            "temp": None
        })
        
        self.history = recorded_steps
        self.history_index = 0

    def restart(self):
        """Restarts the visualizer and search state."""
        self.auto_run = False
        if self.is_csp:
            self.history_index = 0
        else:
            self.init_solver()

    def draw_board(self, snapshot: Dict[str, Any]):
        queens = snapshot.get("queens", [])
        active_queen = snapshot.get("active_queen", None)
        backtracked_row = snapshot.get("backtracked_row", None)
        
        attacking_pairs = self._get_attacking_pairs(queens)
        conflicted_queens = set()
        for q1, q2 in attacking_pairs:
            conflicted_queens.add(q1)
            conflicted_queens.add(q2)

        ox = self.board_margin
        oy = self.board_margin

        # Draw coordinate headers
        for i in range(self.n):
            # Column headers (A, B, C...)
            col_label = chr(ord('A') + i) if self.n <= 26 else str(i)
            lbl = self.font_small.render(col_label, True, self.COLORS["hud_dim"])
            self.screen.blit(lbl, (ox + i * self.cell_size + self.cell_size // 2 - lbl.get_width() // 2, oy - 20))
            
            # Row headers (0, 1, 2...)
            row_label = str(i)
            lbl_r = self.font_small.render(row_label, True, self.COLORS["hud_dim"])
            self.screen.blit(lbl_r, (ox - 20, oy + i * self.cell_size + self.cell_size // 2 - lbl_r.get_height() // 2))

        # Draw checkered board
        for r in range(self.n):
            for c in range(self.n):
                sq_color = self.COLORS["white_square"] if (r + c) % 2 == 0 else self.COLORS["black_square"]
                rect = pygame.Rect(ox + c * self.cell_size, oy + r * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, sq_color, rect)
                
                # Highlight last backtracked row
                if backtracked_row is not None and r == backtracked_row:
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    s.fill(self.COLORS["backtracked_square"])
                    self.screen.blit(s, (ox + c * self.cell_size, oy + r * self.cell_size))

        # Board border
        board_rect = pygame.Rect(ox - 1, oy - 1, self.board_pixel_size + 2, self.board_pixel_size + 2)
        pygame.draw.rect(self.screen, self.COLORS["hud_line"], board_rect, 2)

        # Draw conflict lines between attacking pairs
        for q1, q2 in attacking_pairs:
            p1 = (ox + q1[1] * self.cell_size + self.cell_size // 2, oy + q1[0] * self.cell_size + self.cell_size // 2)
            p2 = (ox + q2[1] * self.cell_size + self.cell_size // 2, oy + q2[0] * self.cell_size + self.cell_size // 2)
            pygame.draw.line(self.screen, self.COLORS["conflict_line"], p1, p2, 3)

        # Draw Queens
        for (r, c) in queens:
            if r is None or c is None or r >= self.n or c >= self.n:
                continue
            center = (ox + c * self.cell_size + self.cell_size // 2, oy + r * self.cell_size + self.cell_size // 2)
            is_conflicted = (r, c) in conflicted_queens
            is_active = (active_queen is not None and (r, c) == active_queen)
            
            # Base circle
            if is_conflicted:
                queen_color = self.COLORS["queen_conflict"]
            elif is_active:
                queen_color = self.COLORS["queen_active"]
            else:
                queen_color = self.COLORS["queen"]

            pygame.draw.circle(self.screen, queen_color, center, self.cell_size // 3)
            pygame.draw.circle(self.screen, self.COLORS["queen_outline"], center, self.cell_size // 3, 2)
            
            # Crown symbol
            crown = self.font_queen.render("♕", True, self.COLORS["queen_outline"])
            crown_rect = crown.get_rect(center=center)
            crown_rect.y -= 2
            self.screen.blit(crown, crown_rect)

    def draw_hud(self, snapshot: Dict[str, Any]):
        hud_x = self.board_pixel_size + self.board_margin * 2
        hud_rect = pygame.Rect(hud_x, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud"], hud_rect)
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (hud_x, 0), (hud_x, self.height), 2)

        x = hud_x + 18
        y = 18

        def draw_text(text, font=None, color=None, dy=22):
            nonlocal y
            f = font or self.font
            c = color or self.COLORS["hud_text"]
            surf = f.render(str(text), True, c)
            self.screen.blit(surf, (x, y))
            y += dy

        def draw_card(height=80):
            card_rect = pygame.Rect(x - 6, y - 4, self.hud_width - 24, height)
            pygame.draw.rect(self.screen, self.COLORS["hud_card"], card_rect, border_radius=6)

        # 1. Header
        mode_badge = "CSP BACKTRACKING SEARCH" if self.is_csp else "LOCAL SEARCH OPTIMIZATION"
        draw_text("N-QUEENS LAB", self.font_title, self.COLORS["hud_title"], dy=20)
        draw_text(mode_badge, self.font_small, self.COLORS["hud_accent"], dy=16)
        draw_text(f"Solver: {self.solver.__class__.__name__}", self.font_bold, self.COLORS["hud_text"], dy=18)
        
        # Sub-heuristics info
        if hasattr(self.solver, "inference") and self.solver.inference:
            inf_name = getattr(self.solver.inference, "__name__", str(self.solver.inference))
            draw_text(f"Inference: {inf_name}", self.font_small, self.COLORS["hud_dim"], dy=16)

        y += 6
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (x - 6, y), (x + self.hud_width - 30, y), 1)
        y += 10

        # 2. Status & Progress Card
        draw_card(height=72)
        status_val = snapshot.get("status", getattr(self.solver, "status", "RUNNING"))
        status_str = status_val.name if hasattr(status_val, "name") else str(status_val)
        
        queens = snapshot.get("queens", [])
        conflicts = snapshot.get("conflicts", len(self._get_attacking_pairs(queens)))
        
        if status_str == "SUCCESS" or (not self.is_csp and len(queens) == self.n and conflicts == 0):
            st_color = self.COLORS["status_success"]
            st_text = "● STATUS: SOLVED (0 Conflicts)"
        elif status_str == "FAILURE":
            st_color = self.COLORS["status_failure"]
            st_text = "● STATUS: FAILED"
        else:
            st_color = self.COLORS["status_running"]
            st_text = "● STATUS: RUNNING"
            
        draw_text(st_text, self.font_bold, st_color, dy=18)
        
        total_steps = max(1, len(self.history) - 1)
        step_pct = (self.history_index / total_steps) * 100
        draw_text(f"Step: {self.history_index} / {total_steps}  ({step_pct:.1f}%)", self.font_small, self.COLORS["hud_text"], dy=16)
        
        # Progress Bar
        bar_w = self.hud_width - 36
        bar_h = 7
        bar_rect = pygame.Rect(x, y, bar_w, bar_h)
        pygame.draw.rect(self.screen, self.COLORS["progress_bar_bg"], bar_rect, border_radius=3)
        fill_w = int(bar_w * (self.history_index / total_steps))
        if fill_w > 0:
            fill_rect = pygame.Rect(x, y, fill_w, bar_h)
            pygame.draw.rect(self.screen, self.COLORS["progress_bar_fill"], fill_rect, border_radius=3)
        y += 18

        # 3. Live Search Metrics Card
        y += 6
        draw_card(height=125)
        action_text = snapshot.get("action", "IDLE")
        draw_text(f"Action: {action_text}", self.font_bold, self.COLORS["hud_accent"], dy=18)
        
        draw_text(f"Queens on Board: {len(queens)} / {self.n}", self.font, self.COLORS["hud_text"], dy=16)
        
        if self.is_csp:
            nodes = snapshot.get("nodes_expanded", getattr(self.solver, "nodes_expanded", 0))
            backtracks = snapshot.get("backtracks", 0)
            draw_text(f"Nodes Expanded:  {nodes}", self.font, self.COLORS["hud_text"], dy=16)
            draw_text(f"Backtracks:      {backtracks}", self.font, self.COLORS["hud_text"], dy=16)
            if hasattr(self.solver, "symmetric_branches_pruned"):
                draw_text(f"Symmetries Cut:  {self.solver.symmetric_branches_pruned}", self.font, self.COLORS["hud_accent"], dy=16)
        else:
            val = snapshot.get("value", getattr(self.solver, "current_value", self.max_fitness - conflicts))
            draw_text(f"Fitness (Non-Att): {val} / {self.max_fitness}", self.font, self.COLORS["hud_text"], dy=16)
            temp = snapshot.get("temp", None)
            if temp is not None:
                draw_text(f"Temperature (T):  {temp:.4f}", self.font, self.COLORS["hud_title"], dy=16)
            else:
                draw_text(f"Iterations:       {getattr(self.solver, 'num_iterations', len(self.history))}", self.font, self.COLORS["hud_text"], dy=16)

        c_col = (80, 220, 120) if conflicts == 0 else (255, 90, 90)
        draw_text(f"Attacking Pairs: {conflicts} conflicts", self.font, c_col, dy=18)

        # 4. Playback State
        y += 8
        pb_state = f"AUTO-RUN: ON ({self.fps} FPS)" if self.auto_run else "AUTO-RUN: PAUSED"
        pb_col = self.COLORS["status_success"] if self.auto_run else self.COLORS["hud_dim"]
        draw_text(pb_state, self.font_bold, pb_col, dy=16)

        # 5. Interactive Controls Legend
        y += 8
        draw_text("CONTROLS:", self.font_bold, self.COLORS["hud_title"], dy=16)
        draw_text("[SPACE]     Play / Pause Auto-Run", self.font_small, self.COLORS["hud_dim"], dy=14)
        draw_text("[RIGHT]     Step Forward", self.font_small, self.COLORS["hud_dim"], dy=14)
        draw_text("[LEFT]      Step Backward", self.font_small, self.COLORS["hud_dim"], dy=14)
        draw_text("[HOME]      Jump to Start (Step 0)", self.font_small, self.COLORS["hud_dim"], dy=14)
        draw_text("[END]       Jump to Latest Step", self.font_small, self.COLORS["hud_dim"], dy=14)
        draw_text("[R]         Restart (New Random State)", self.font_small, self.COLORS["hud_dim"], dy=14)
        draw_text("[UP / DN]   Speed (FPS)", self.font_small, self.COLORS["hud_dim"], dy=14)
        draw_text("[ESC]       Quit", self.font_small, self.COLORS["hud_dim"], dy=14)

    def render(self):
        self.screen.fill(self.COLORS["bg"])
        if not self.history:
            pygame.display.flip()
            return
        snapshot = self.history[self.history_index]
        self.draw_board(snapshot)
        self.draw_hud(snapshot)
        pygame.display.flip()

    def _step_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
        elif not self.is_csp and hasattr(self.solver, "status") and self.solver.status == SearchStatus.RUNNING:
            prev_state = getattr(self.solver, "current_state", None)
            self.solver.search_step()
            curr_state = getattr(self.solver, "current_state", None)
            
            # Detect which queen moved
            moved_queen = None
            if prev_state is not None and curr_state is not None:
                for col in range(min(len(prev_state), len(curr_state))):
                    if prev_state[col] != curr_state[col]:
                        moved_queen = (curr_state[col], col)
                        break
                        
            new_queens = self._state_to_queens(curr_state)
            conflicts = len(self._get_attacking_pairs(new_queens))
            val = getattr(self.solver, "current_value", self.max_fitness - conflicts)
            
            # Check for simulated annealing temperature
            temp_val = None
            if hasattr(self.solver, "schedule") and hasattr(self.solver, "num_iterations"):
                temp_val = self.solver.schedule(self.solver.num_iterations)
                
            action_desc = f"MOVE: Queen at Col {moved_queen[1]} -> Row {moved_queen[0]}" if moved_queen else "LOCAL SEARCH STEP"
            
            self.history.append({
                "queens": new_queens,
                "nodes_expanded": getattr(self.solver, "nodes_expanded", len(self.history)),
                "backtracks": 0,
                "conflicts": conflicts,
                "value": val,
                "status": self.solver.status,
                "action": action_desc,
                "active_queen": moved_queen,
                "backtracked_row": None,
                "temp": temp_val
            })
            self.history_index = len(self.history) - 1

    def _step_backward(self):
        if self.history_index > 0:
            self.history_index -= 1

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_SPACE:
                    self.auto_run = not self.auto_run
                elif event.key == pygame.K_RIGHT:
                    self._step_forward()
                elif event.key == pygame.K_LEFT:
                    self._step_backward()
                elif event.key == pygame.K_HOME:
                    self.history_index = 0
                elif event.key == pygame.K_END:
                    self.history_index = max(0, len(self.history) - 1)
                elif event.key == pygame.K_UP:
                    self.fps = min(60, self.fps + 2)
                elif event.key == pygame.K_DOWN:
                    self.fps = max(1, self.fps - 2)

        if self.auto_run:
            if self.history_index < len(self.history) - 1:
                self._step_forward()
            elif not self.is_csp and hasattr(self.solver, "status") and self.solver.status == SearchStatus.RUNNING:
                self._step_forward()
            else:
                self.auto_run = False

    def run(self):
        while self.running:
            self.update()
            self.render()
            self.clock.tick(self.fps)
            
        pygame.quit()
