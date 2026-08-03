import pygame
import time

class SudokuVisualizer:
    def __init__(self, problem, solver, cell_size=60, delay_ms=10):
        self.problem = problem
        self.solver = solver
        self.cell_size = cell_size
        self.delay_ms = delay_ms
        
        self.grid_size = 9
        self.board_size = self.grid_size * self.cell_size
        self.hud_width = 300
        
        self.width = self.board_size + self.hud_width
        self.height = self.board_size

        self.COLORS = {
            "background": (255, 255, 255),
            "hud": (40, 40, 40),
            "hud_line": (100, 100, 100),
            "hud_text": (200, 200, 200),
            "hud_title": (255, 200, 100),
            "grid_lines": (200, 200, 200),
            "grid_lines_thick": (0, 0, 0),
            "text_initial": (0, 0, 0),       # Given puzzle numbers
            "text_assigned": (0, 100, 255),  # AI guesses
            "highlight": (255, 255, 150),    # Cell being currently modified
            "unassigned": (255, 200, 200)    # Cell that just backtracked
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AI Framework - Sudoku CSP Solver")

        self.font = pygame.font.SysFont("consolas", 16)
        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_numbers = pygame.font.SysFont("consolas", 32, bold=True)

        self.running = True
        self.paused = True
        self.auto_run = False
        
        # State tracking
        self.initial_assignment = {var: vals[0] for var, vals in self.problem.domains.items() if len(vals) == 1}
        self.current_assignment = dict(self.initial_assignment)
        self.last_modified_var = None
        self.backtracked_vars = set()
        
        self.nodes_expanded = 0

        # Hook into solver
        if hasattr(self.solver, "on_assign"):
            self.solver.on_assign = self._handle_assign
            self.solver.on_unassign = self._handle_unassign

    def _handle_assign(self, var, value, assignment):
        self.current_assignment[var] = value
        self.last_modified_var = var
        if var in self.backtracked_vars:
            self.backtracked_vars.remove(var)
        self.nodes_expanded += 1
        self._step_frame()

    def _handle_unassign(self, var, assignment):
        if var in self.current_assignment:
            del self.current_assignment[var]
        self.last_modified_var = var
        self.backtracked_vars.add(var)
        self._step_frame()

    def draw_grid(self):
        self.screen.fill(self.COLORS["background"], (0, 0, self.board_size, self.height))
        
        # Draw highlights
        if self.last_modified_var:
            r, c = self.last_modified_var
            rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
            if self.last_modified_var in self.backtracked_vars:
                pygame.draw.rect(self.screen, self.COLORS["unassigned"], rect)
            else:
                pygame.draw.rect(self.screen, self.COLORS["highlight"], rect)

        # Draw lines
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            color = self.COLORS["grid_lines_thick"] if i % 3 == 0 else self.COLORS["grid_lines"]
            
            # Horizontal
            pygame.draw.line(self.screen, color, (0, i * self.cell_size), (self.board_size, i * self.cell_size), thickness)
            # Vertical
            pygame.draw.line(self.screen, color, (i * self.cell_size, 0), (i * self.cell_size, self.board_size), thickness)

        # Draw numbers
        for (r, c), val in self.current_assignment.items():
            color = self.COLORS["text_initial"] if (r, c) in self.initial_assignment else self.COLORS["text_assigned"]
            text = self.font_numbers.render(str(val), True, color)
            rect = text.get_rect(center=(c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2))
            self.screen.blit(text, rect)

    def draw_hud(self):
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

        draw("SUDOKU CSP SOLVER", self.font_title, self.COLORS["hud_title"], 20)
        draw(f"Solver: {self.solver.__class__.__name__}")
        draw(f"Status: {self.solver.status if hasattr(self.solver, 'status') else 'RUNNING'}")
        draw(f"Assignments: {self.nodes_expanded}")
        draw(f"Vars Assigned: {len(self.current_assignment)} / 81")
        
        y += 20
        draw("CONTROLS:", self.font_title, self.COLORS["hud_title"])
        draw("[SPACE] Play / Pause")
        draw("[UP/DOWN] Change Speed")
        
        y += 20
        state = "PAUSED" if self.paused else "PLAYING"
        draw(f"State: {state}", color=(255, 100, 100) if self.paused else (100, 255, 100))
        draw(f"Delay: {self.delay_ms} ms")

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_UP:
                    self.delay_ms = max(0, self.delay_ms - 10)
                elif event.key == pygame.K_DOWN:
                    self.delay_ms += 10
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _step_frame(self):
        if not self.running:
            raise InterruptedError("Visualizer closed by user.")
            
        self._process_events()
        
        while self.paused and self.running:
            self._process_events()
            self.draw_grid()
            self.draw_hud()
            pygame.display.flip()
            time.sleep(0.05)
            
        if not self.running:
            raise InterruptedError("Visualizer closed by user.")

        self.draw_grid()
        self.draw_hud()
        pygame.display.flip()
        
        if self.delay_ms > 0:
            time.sleep(self.delay_ms / 1000.0)

    def run(self):
        # Draw initial state and wait for unpause
        self.draw_grid()
        self.draw_hud()
        pygame.display.flip()
        
        print("Sudoku Visualizer ready. Press SPACE to start solving.")
        
        try:
            while self.paused and self.running:
                self._process_events()
                self.draw_grid()
                self.draw_hud()
                pygame.display.flip()
                time.sleep(0.05)
                
            if self.running:
                self.solver.solve()
                
            # Done solving, keep window open until closed
            self.last_modified_var = None
            while self.running:
                self._process_events()
                self.draw_grid()
                self.draw_hud()
                pygame.display.flip()
                time.sleep(0.1)
                
        except InterruptedError:
            pass
            
        pygame.quit()
