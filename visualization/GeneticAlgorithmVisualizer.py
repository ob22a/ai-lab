import pygame
import time
from typing import List, Tuple, Dict, Any

from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class GeneticAlgorithmVisualizer(Visualizer):
    """
    Interactive Pygame visualizer for Genetic Algorithm (e.g. N-Queens optimization).
    Displays:
      1. Main Hero Board for the generation's best individual with conflict highlighting & chromosome.
      2. Real-time Fitness Evolution Curve chart plotting Best and Average population fitness over generations.
      3. Elite Showcase displaying the top individuals of the current generation.
      4. Rich HUD with population analytics, diversity, generation counter, and history scrubbing.
    """

    def __init__(
        self,
        problem,
        solver: SearchAlgorithm,
        cell_size: int = 50,
        fps: int = 15,
        auto_run: bool = False
    ):
        self.problem = problem
        self.solver = solver
        self.cell_size = cell_size
        self.fps = fps
        self.auto_run = auto_run

        self.n = getattr(self.problem, "n", 8)
        self.pop_size = getattr(self.solver, "pop_size", 50)
        self.mutation_rate = getattr(self.solver, "mutation_rate", 0.1)
        self.max_generations = getattr(self.solver, "max_generations", 500)

        # Layout geometry
        self.board_size = self.n * self.cell_size
        self.middle_panel_width = 340
        self.hud_width = 300
        
        self.width = self.board_size + self.middle_panel_width + self.hud_width
        self.height = max(self.board_size + 40, 540)

        # Theme & Color Palette
        self.COLORS = {
            "background": (24, 26, 33),
            "panel_bg": (30, 33, 44),
            "panel_border": (48, 53, 68),
            
            "black_square": (118, 150, 86),
            "white_square": (238, 238, 210),
            "queen": (30, 30, 30),
            "queen_outline": (255, 255, 255),
            
            "mini_black": (75, 95, 60),
            "mini_white": (175, 175, 155),
            "mini_queen": (230, 70, 70),

            "attack_line": (255, 75, 75, 180),

            "hud": (20, 22, 28),
            "hud_line": (42, 46, 60),
            "hud_text": (210, 215, 230),
            "hud_muted": (140, 145, 165),
            "hud_title": (255, 195, 80),
            "accent": (80, 160, 255),
            
            "success": (80, 220, 120),
            "warning": (255, 170, 60),
            "danger": (255, 85, 85),
            
            "chart_bg": (22, 24, 32),
            "chart_grid": (40, 44, 58),
            "chart_best": (80, 220, 120),
            "chart_avg": (80, 190, 255),
            "chart_opt": (255, 205, 70),
            
            "card_bg": (36, 40, 52),
            "card_selected": (48, 68, 100),
            "card_border": (55, 62, 80),
            "card_border_selected": (90, 160, 250),
            "card_best": (40, 75, 55),
            "card_border_best": (75, 200, 110),
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AI Lab - Genetic Algorithm Evolution Visualizer")

        self.clock = pygame.time.Clock()
        self.font_tiny = pygame.font.SysFont("consolas", 10)
        self.font_small = pygame.font.SysFont("consolas", 12)
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_bold = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_queen = pygame.font.SysFont("segoe ui symbol", max(16, int(self.cell_size * 0.65)))

        self.running = True
        self.selected_elite_idx = 0
        
        self.history: List[Dict[str, Any]] = []
        self.history_index = 0

        self.restart()

    def _create_snapshot(self) -> Dict[str, Any]:
        """Creates a snapshot of the current GA generation for history scrubbing."""
        pop = list(getattr(self.solver, "population", [self.solver.current_state]))
        
        # Score each individual in the population
        scored = []
        for s in pop:
            val = self.problem.value(s)
            scored.append((val, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        
        values = [v for v, _ in scored]
        best_val = values[0] if values else self.problem.value(self.solver.best_state)
        avg_val = sum(values) / max(1, len(values))
        worst_val = values[-1] if values else best_val
        
        # Extract top 4 elites
        top_elites = [s for _, s in scored[:4]]
        top_elite_vals = values[:4]

        unique_genotypes = len(set(pop))
        diversity_pct = (unique_genotypes / max(1, len(pop))) * 100.0

        return {
            "generation": self.solver.num_iterations,
            "best_state": scored[0][1] if scored else self.solver.best_state,
            "best_value": best_val,
            "avg_value": avg_val,
            "worst_value": worst_val,
            "top_elites": top_elites,
            "top_elite_vals": top_elite_vals,
            "diversity_pct": diversity_pct,
            "unique_count": unique_genotypes,
            "status": self.solver.status,
            "nodes_expanded": self.solver.nodes_expanded,
            "nodes_generated": self.solver.nodes_generated,
        }

    def restart(self):
        self.solver.reset()
        self.history = [self._create_snapshot()]
        self.history_index = 0
        self.selected_elite_idx = 0
        self.auto_run = False

    def _get_attacking_pairs(self, state: Tuple[int, ...]) -> List[Tuple[int, int]]:
        attacks = []
        n = len(state)
        for i in range(n):
            for j in range(i + 1, n):
                if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                    attacks.append((i, j))
        return attacks

    def draw_hero_board(self, state: Tuple[int, ...]):
        """Draws the primary chessboard with queens and attacking pair lines."""
        # Checkerboard tiles
        for r in range(self.n):
            for c in range(self.n):
                color = self.COLORS["white_square"] if (r + c) % 2 == 0 else self.COLORS["black_square"]
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)

        # Attacking pairs
        attacks = self._get_attacking_pairs(state)
        attacked_cols = set()
        for i, j in attacks:
            attacked_cols.add(i)
            attacked_cols.add(j)

        # Attack lines
        for i, j in attacks:
            p1 = (i * self.cell_size + self.cell_size // 2, state[i] * self.cell_size + self.cell_size // 2)
            p2 = (j * self.cell_size + self.cell_size // 2, state[j] * self.cell_size + self.cell_size // 2)
            pygame.draw.line(self.screen, (255, 80, 80), p1, p2, 2)

        # Draw Queens
        for c, r in enumerate(state):
            center = (c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2)
            is_attacked = c in attacked_cols
            
            if is_attacked:
                pygame.draw.circle(self.screen, (255, 100, 100, 120), center, self.cell_size // 2 - 2)

            q_color = (180, 40, 40) if is_attacked else self.COLORS["queen"]
            pygame.draw.circle(self.screen, q_color, center, self.cell_size // 3)
            pygame.draw.circle(self.screen, self.COLORS["queen_outline"], center, self.cell_size // 3, 2)

            crown = self.font_queen.render("♕", True, self.COLORS["queen_outline"])
            crown_rect = crown.get_rect(center=center)
            crown_rect.y -= 2
            self.screen.blit(crown, crown_rect)

        # Bottom label bar with chromosome representation
        bar_rect = pygame.Rect(0, self.board_size, self.board_size, self.height - self.board_size)
        pygame.draw.rect(self.screen, self.COLORS["panel_bg"], bar_rect)
        pygame.draw.line(self.screen, self.COLORS["panel_border"], (0, self.board_size), (self.board_size, self.board_size), 2)
        
        conflicts = len(attacks)
        val = self.problem.max_fitness - conflicts
        chrom_str = str(list(state))
        lbl_surf = self.font_bold.render(f"Chromosome: {chrom_str}", True, self.COLORS["accent"])
        self.screen.blit(lbl_surf, (12, self.board_size + 8))
        
        stat_surf = self.font_small.render(f"Fitness: {val}/{self.problem.max_fitness} | Conflicts: {conflicts}", True, self.COLORS["success"] if conflicts == 0 else self.COLORS["hud_text"])
        self.screen.blit(stat_surf, (12, self.board_size + 24))

    def draw_mini_board(self, surf: pygame.Surface, state: Tuple[int, ...], size: int):
        mini_cell = size / self.n
        for r in range(self.n):
            for c in range(self.n):
                color = self.COLORS["mini_white"] if (r + c) % 2 == 0 else self.COLORS["mini_black"]
                rect = pygame.Rect(int(c * mini_cell), int(r * mini_cell), int(mini_cell) + 1, int(mini_cell) + 1)
                pygame.draw.rect(surf, color, rect)

        for c, r in enumerate(state):
            cx = int(c * mini_cell + mini_cell / 2)
            cy = int(r * mini_cell + mini_cell / 2)
            rad = max(2, int(mini_cell * 0.35))
            pygame.draw.circle(surf, self.COLORS["mini_queen"], (cx, cy), rad)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), rad, 1)

    def draw_fitness_chart(self, rect: pygame.Rect):
        """Draws a live line chart plotting Best & Average Fitness across all generations up to history_index."""
        pygame.draw.rect(self.screen, self.COLORS["chart_bg"], rect, border_radius=6)
        pygame.draw.rect(self.screen, self.COLORS["chart_grid"], rect, 1, border_radius=6)

        # Title and legend
        t_surf = self.font_bold.render("FITNESS PROGRESSION", True, self.COLORS["hud_title"])
        self.screen.blit(t_surf, (rect.x + 10, rect.y + 8))

        # Legend dots
        pygame.draw.circle(self.screen, self.COLORS["chart_best"], (rect.right - 140, rect.y + 16), 4)
        self.screen.blit(self.font_tiny.render("Best", True, self.COLORS["hud_text"]), (rect.right - 132, rect.y + 10))

        pygame.draw.circle(self.screen, self.COLORS["chart_avg"], (rect.right - 80, rect.y + 16), 4)
        self.screen.blit(self.font_tiny.render("Avg", True, self.COLORS["hud_text"]), (rect.right - 72, rect.y + 10))

        # Plot area
        pad_l, pad_r, pad_t, pad_b = 35, 15, 32, 22
        plot_w = rect.width - pad_l - pad_r
        plot_h = rect.height - pad_t - pad_b
        ox = rect.x + pad_l
        oy = rect.y + pad_t

        # Y-axis gridlines & labels
        max_fit = self.problem.max_fitness
        y_ticks = [0, max_fit // 2, max_fit]
        for val in y_ticks:
            py = int(oy + plot_h - (val / max(1, max_fit)) * plot_h)
            pygame.draw.line(self.screen, self.COLORS["chart_grid"], (ox, py), (ox + plot_w, py), 1)
            lbl = self.font_tiny.render(str(val), True, self.COLORS["hud_muted"])
            self.screen.blit(lbl, (rect.x + 8, py - 6))

        # Optimal ceiling line
        opt_y = int(oy + plot_h - (max_fit / max_fit) * plot_h)
        pygame.draw.line(self.screen, self.COLORS["chart_opt"], (ox, opt_y), (ox + plot_w, opt_y), 1)

        # History points up to current history_index
        history_slice = self.history[: self.history_index + 1]
        num_pts = len(history_slice)
        if num_pts < 2:
            return

        best_pts = []
        avg_pts = []
        for i, snap in enumerate(history_slice):
            px = int(ox + (i / (num_pts - 1)) * plot_w)
            by = int(oy + plot_h - (snap["best_value"] / max_fit) * plot_h)
            ay = int(oy + plot_h - (snap["avg_value"] / max_fit) * plot_h)
            best_pts.append((px, by))
            avg_pts.append((px, ay))

        # Draw curves
        pygame.draw.lines(self.screen, self.COLORS["chart_avg"], False, avg_pts, 2)
        pygame.draw.lines(self.screen, self.COLORS["chart_best"], False, best_pts, 2)

        # Current generation point marker
        cur_px, cur_by = best_pts[-1]
        pygame.draw.circle(self.screen, (255, 255, 255), (cur_px, cur_by), 4)
        pygame.draw.circle(self.screen, self.COLORS["chart_best"], (cur_px, cur_by), 2)

    def draw_middle_panel(self, snap: Dict[str, Any]):
        """Renders the middle panel with the fitness evolution chart and elite candidate showcase."""
        panel_x = self.board_size
        panel_rect = pygame.Rect(panel_x, 0, self.middle_panel_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["panel_bg"], panel_rect)
        pygame.draw.line(self.screen, self.COLORS["panel_border"], (panel_x, 0), (panel_x, self.height), 2)

        # 1. Top Section: Fitness Progression Chart
        chart_h = 160
        chart_rect = pygame.Rect(panel_x + 12, 12, self.middle_panel_width - 24, chart_h)
        self.draw_fitness_chart(chart_rect)

        # 2. Bottom Section: Elite Pool Showcase
        elites_y = chart_h + 24
        title = self.font_bold.render("ELITE GENOTYPE SHOWCASE", True, self.COLORS["hud_title"])
        self.screen.blit(title, (panel_x + 15, elites_y))

        card_start_y = elites_y + 24
        card_h = 62
        mini_size = 46

        for idx, state in enumerate(snap["top_elites"]):
            card_y = card_start_y + idx * (card_h + 8)
            if card_y + card_h > self.height - 10:
                break

            card_rect = pygame.Rect(panel_x + 12, card_y, self.middle_panel_width - 24, card_h)
            is_selected = (idx == self.selected_elite_idx)
            is_best = (idx == 0)

            if is_selected:
                bg_col = self.COLORS["card_selected"]
                border_col = self.COLORS["card_border_selected"]
                border_w = 2
            elif is_best:
                bg_col = self.COLORS["card_best"]
                border_col = self.COLORS["card_border_best"]
                border_w = 2
            else:
                bg_col = self.COLORS["card_bg"]
                border_col = self.COLORS["card_border"]
                border_w = 1

            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_col, card_rect, border_w, border_radius=6)

            # Mini Board
            mini_surf = pygame.Surface((mini_size, mini_size))
            self.draw_mini_board(mini_surf, state, mini_size)
            self.screen.blit(mini_surf, (card_rect.x + 8, card_rect.y + (card_h - mini_size) // 2))

            # Details
            val = snap["top_elite_vals"][idx]
            conflicts = self.problem.max_fitness - val
            badge_txt = f"#{idx+1} TOP ELITE" if is_best else f"#{idx+1} ELITE"
            badge_col = self.COLORS["success"] if is_best else self.COLORS["accent"]
            
            self.screen.blit(self.font_bold.render(badge_txt, True, badge_col), (card_rect.x + mini_size + 16, card_rect.y + 6))
            
            fit_txt = f"Fit: {val}/{self.problem.max_fitness} | Conflicts: {conflicts}"
            self.screen.blit(self.font_small.render(fit_txt, True, self.COLORS["hud_text"]), (card_rect.x + mini_size + 16, card_rect.y + 24))

            chrom_preview = str(list(state)[:4])[:-1] + ", ...]" if len(state) > 4 else str(list(state))
            self.screen.blit(self.font_tiny.render(f"Genes: {chrom_preview}", True, self.COLORS["hud_muted"]), (card_rect.x + mini_size + 16, card_rect.y + 42))

            # Key label
            self.screen.blit(self.font_small.render(f"[{idx+1}]", True, self.COLORS["hud_muted"]), (card_rect.right - 28, card_rect.y + 6))

    def draw_hud(self, snap: Dict[str, Any]):
        """Renders the right HUD panel with search statistics and control instructions."""
        hud_x = self.board_size + self.middle_panel_width
        hud_rect = pygame.Rect(hud_x, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud"], hud_rect)
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (hud_x, 0), (hud_x, self.height), 2)

        x = hud_x + 20
        y = 20

        def write(text, font=None, color=None, gap=5):
            nonlocal y
            f = font or self.font
            c = color or self.COLORS["hud_text"]
            surf = f.render(str(text), True, c)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + gap

        write("GENETIC ALGORITHM", self.font_title, self.COLORS["hud_title"], 10)
        write(f"Domain: {self.n}-Queens Problem", color=self.COLORS["hud_muted"])
        
        status_name = snap["status"].name if hasattr(snap["status"], "name") else str(snap["status"])
        status_col = (
            self.COLORS["success"] if snap["best_value"] == self.problem.max_fitness
            else self.COLORS["warning"] if status_name == "SUCCESS"
            else self.COLORS["accent"]
        )
        write(f"Status: {status_name}", self.font_bold, status_col, 12)

        # Generation & Population Analytics
        write("POPULATION METRICS", self.font_bold, self.COLORS["accent"], 6)
        write(f"Generation: {snap['generation']} / {self.max_generations}")
        write(f"Population Size: {self.pop_size}")
        write(f"Mutation Rate: {self.mutation_rate:.2f}")
        write(f"Diversity: {snap['unique_count']}/{self.pop_size} ({snap['diversity_pct']:.1f}%)")
        
        best_conf = self.problem.max_fitness - snap["best_value"]
        write(f"Best Fitness: {snap['best_value']} / {self.problem.max_fitness}")
        write(f"Avg Fitness:  {snap['avg_value']:.2f}")
        write(f"Worst Fitness:{snap['worst_value']}")
        write(f"Min Conflicts:{best_conf}", color=self.COLORS["success"] if best_conf == 0 else self.COLORS["danger"])
        
        write(f"Crossovers: {snap['nodes_expanded']}")
        write(f"Nodes Evaluated: {snap['nodes_generated']}", gap=12)

        # Playback & Controls
        write("CONTROLS", self.font_bold, self.COLORS["hud_title"], 6)
        write("[RIGHT] Step Generation")
        write("[LEFT]  Step Backward")
        write("[SPACE] Play / Pause")
        write("[A]     Toggle Auto-Run")
        write("[1..4]  Inspect Elite State")
        write("[R]     Restart Evolution")
        write("[UP/DN] Speed (FPS)", gap=12)

        # Live State
        state_txt = "EVOLVING..." if self.auto_run else "PAUSED / STEPPING"
        state_col = self.COLORS["success"] if self.auto_run else self.COLORS["warning"]
        write(f"Mode: {state_txt}", color=state_col)
        write(f"Step: {self.history_index} / {len(self.history) - 1}")
        write(f"FPS: {self.fps}")

    def render(self):
        snap = self.history[self.history_index]
        
        if self.selected_elite_idx >= len(snap["top_elites"]):
            self.selected_elite_idx = 0
            
        hero_state = snap["top_elites"][self.selected_elite_idx] if snap["top_elites"] else snap["best_state"]
        
        self.draw_hero_board(hero_state)
        self.draw_middle_panel(snap)
        self.draw_hud(snap)
        pygame.display.flip()

    def _step_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
        elif self.solver.status == SearchStatus.RUNNING:
            self.solver.search_step()
            snap = self._create_snapshot()
            self.history.append(snap)
            self.history_index = len(self.history) - 1

    def _step_backward(self):
        if self.history_index > 0:
            self.history_index -= 1

    def handle_mouse_click(self, pos: Tuple[int, int]):
        x, y = pos
        panel_x = self.board_size
        if panel_x <= x < panel_x + self.middle_panel_width:
            chart_h = 160
            elites_y = chart_h + 24
            card_start_y = elites_y + 24
            card_h = 62
            
            snap = self.history[self.history_index]
            for idx in range(len(snap["top_elites"])):
                card_y = card_start_y + idx * (card_h + 8)
                if card_y <= y <= card_y + card_h:
                    self.selected_elite_idx = idx
                    break

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_SPACE:
                    self.auto_run = not self.auto_run
                elif event.key == pygame.K_a:
                    self.auto_run = not self.auto_run
                elif event.key == pygame.K_RIGHT:
                    self._step_forward()
                elif event.key == pygame.K_LEFT:
                    self._step_backward()
                elif event.key == pygame.K_UP:
                    self.fps = min(60, self.fps + 5)
                elif event.key == pygame.K_DOWN:
                    self.fps = max(1, self.fps - 5)
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    idx = event.key - pygame.K_1
                    snap = self.history[self.history_index]
                    if idx < len(snap["top_elites"]):
                        self.selected_elite_idx = idx

        if self.auto_run:
            if self.solver.status == SearchStatus.RUNNING or self.history_index < len(self.history) - 1:
                self._step_forward()
            else:
                self.auto_run = False

    def run(self):
        while self.running:
            self.update()
            self.render()
            self.clock.tick(self.fps)
        pygame.quit()
