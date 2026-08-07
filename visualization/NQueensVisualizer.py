import pygame
import time
from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus

class NQueensVisualizer(Visualizer):
    def __init__(self, problem, solver: SearchAlgorithm, cell_size=60, fps=10, auto_run=False):
        self.problem = problem
        self.solver = solver
        self.solver.reset() # Initialize current_state
        self.cell_size = cell_size
        self.fps = fps
        self.auto_run = auto_run

        self.n = self.problem.n
        self.board_size = self.n * self.cell_size
        self.hud_width = 300
        
        self.width = self.board_size + self.hud_width
        self.height = max(self.board_size, 400)

        self.COLORS = {
            "hud": (40, 40, 40),
            "hud_line": (100, 100, 100),
            "hud_text": (200, 200, 200),
            "hud_title": (255, 200, 100),
            "black_square": (118, 150, 86),
            "white_square": (238, 238, 210),
            "queen": (40, 40, 40),
            "queen_outline": (255, 255, 255),
            "highlight": (255, 100, 100, 100) # Transparent red for attacking queens
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AI Framework - N-Queens Local Search")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_queen = pygame.font.SysFont("segoe ui symbol", int(self.cell_size * 0.7))

        self.running = True
        
        self.history = [self.solver.current_state]
        self.history_index = 0

    def restart(self):
        self.solver.reset()
        self.history = [self.solver.current_state]
        self.history_index = 0
        self.auto_run = False

    def draw_board(self, state):
        # Draw checkered board
        for r in range(self.n):
            for c in range(self.n):
                color = self.COLORS["white_square"] if (r + c) % 2 == 0 else self.COLORS["black_square"]
                rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
                
        # Draw Queens
        for c, r in enumerate(state):
            center = (c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2)
            pygame.draw.circle(self.screen, self.COLORS["queen"], center, self.cell_size // 3)
            pygame.draw.circle(self.screen, self.COLORS["queen_outline"], center, self.cell_size // 3, 2)
            
            # Simple crown symbol inside
            crown = self.font_queen.render("♕", True, self.COLORS["queen_outline"])
            crown_rect = crown.get_rect(center=center)
            # Offset slightly as some fonts render the crown a bit weirdly
            crown_rect.y -= 2
            self.screen.blit(crown, crown_rect)

    def draw_hud(self, state):
        hud_rect = pygame.Rect(self.board_size, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud"], hud_rect)
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (self.board_size, 0), (self.board_size, self.height), 2)

        x = self.board_size + 20
        y = 20

        def draw(text, font=None, color=None, gap=8):
            nonlocal y
            f = font or self.font
            c = color or self.COLORS["hud_text"]
            surface = f.render(str(text), True, c)
            self.screen.blit(surface, (x, y))
            y += surface.get_height() + gap

        status_name = self.solver.status.name if hasattr(self.solver.status, "name") else str(self.solver.status)
        draw("N-QUEENS OPTIMIZER", self.font_title, self.COLORS["hud_title"], 20)
        draw(f"Solver: {self.solver.__class__.__name__}")
        draw(f"Status: {status_name}")
        draw(f"Iterations: {self.solver.num_iterations}")
        draw(f"Nodes Evaluated: {self.solver.nodes_generated}")
        
        y += 10
        current_val = self.problem.value(state)
        max_val = self.problem.max_fitness
        conflicts = max_val - current_val
        draw(f"Conflicts: {conflicts}", color=(255, 100, 100) if conflicts > 0 else (100, 255, 100))
        
        y += 20
        draw("CONTROLS:", self.font_title, self.COLORS["hud_title"])
        draw("[RIGHT] Step Forward")
        draw("[LEFT]  Step Backward")
        draw("[SPACE] Play / Pause")
        draw("[R]     Restart")
        draw("[UP/DN] Speed (FPS)")
        
        y += 20
        draw(f"Auto-Run: {'ON' if self.auto_run else 'OFF'}")
        draw(f"Step: {self.history_index} / {len(self.history)-1}")
        draw(f"FPS: {self.fps}")

    def render(self):
        # We always render the state at history_index
        state_to_draw = self.history[self.history_index]
        self.draw_board(state_to_draw)
        self.draw_hud(state_to_draw)
        pygame.display.flip()

    def _step_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
        elif self.solver.status == SearchStatus.RUNNING:
            self.solver.search_step()
            if self.solver.current_state != self.history[-1]:
                self.history.append(self.solver.current_state)
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
                elif event.key == pygame.K_UP:
                    self.fps = min(60, self.fps + 2)
                elif event.key == pygame.K_DOWN:
                    self.fps = max(1, self.fps - 2)

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
