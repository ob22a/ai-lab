import pygame
import time
from typing import List

from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus
from core.utils import reconstruct_path

class NPuzzleVisualizer(Visualizer):
    def __init__(
        self,
        puzzle_size: int,
        solver: SearchAlgorithm,
        window_size=600,
        fps=60,
        auto_run=False,
        show_search_process=False
    ):
        self.puzzle_size = puzzle_size
        self.solver = solver
        
        self.window_size = window_size
        self.fps = fps
        self.auto_run = auto_run
        self.show_search_process = show_search_process
        
        # Dimensions
        self.hud_width = 300
        self.width = window_size + self.hud_width
        self.height = window_size
        
        self.cell_size = window_size // puzzle_size
        
        self.COLORS = {
            "background": (30, 30, 30),
            "hud_bg": (45, 45, 45),
            "tile": (100, 150, 255),
            "tile_goal": (100, 255, 100),
            "tile_text": (255, 255, 255),
            "empty": (20, 20, 20),
            "text": (200, 200, 200),
            "highlight": (255, 100, 100)
        }
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("N-Puzzle Search Visualizer")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.SysFont("Inter", self.cell_size // 2, bold=True)
        # Fallback if Inter isn't installed
        if "Inter" not in pygame.font.get_fonts():
            self.font_large = pygame.font.SysFont("Arial", self.cell_size // 2, bold=True)
            
        self.font_medium = pygame.font.SysFont("Arial", 28)
        self.font_small = pygame.font.SysFont("Arial", 20)
        
        self.running = True
        
        # Playback variables
        self.playback_mode = False
        self.solution_path: List[str] = []
        self.playback_index = 0
        self.last_playback_time = 0
        self.playback_delay = 0.2 # seconds between moves in playback
        
        # Determine the goal state to highlight tiles that are in the correct position
        self.goal_state = "".join(hex(i)[2:] for i in range(puzzle_size * puzzle_size))
        
        self.is_loading = False
        if not self.show_search_process:
            self.is_loading = True

    def draw_hud(self):
        # Draw HUD background
        hud_rect = pygame.Rect(self.window_size, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud_bg"], hud_rect)
        pygame.draw.line(self.screen, (60, 60, 60), (self.window_size, 0), (self.window_size, self.height), 2)
        
        y_offset = 30
        x_offset = self.window_size + 20
        
        def render_text(text, font, color, y):
            surface = font.render(text, True, color)
            self.screen.blit(surface, (x_offset, y))
            return y + surface.get_height() + 10
            
        # Status
        status_text = "Status: " + self.solver.status.name
        color = self.COLORS["tile_goal"] if self.solver.status == SearchStatus.SUCCESS else self.COLORS["text"]
        y_offset = render_text(status_text, self.font_medium, color, y_offset)
        
        y_offset += 20
        y_offset = render_text(f"Nodes Expanded: {self.solver.nodes_expanded}", self.font_small, self.COLORS["text"], y_offset)
        y_offset = render_text(f"Nodes Generated: {self.solver.nodes_generated}", self.font_small, self.COLORS["text"], y_offset)
        y_offset = render_text(f"Max Frontier: {self.solver.max_frontier_size}", self.font_small, self.COLORS["text"], y_offset)
        
        if self.playback_mode:
            y_offset += 30
            y_offset = render_text("--- PLAYBACK MODE ---", self.font_small, self.COLORS["highlight"], y_offset)
            y_offset = render_text(f"Move: {self.playback_index} / {len(self.solution_path)-1}", self.font_small, self.COLORS["text"], y_offset)
            
        # Controls
        y_offset = self.height - 150
        y_offset = render_text("Controls:", self.font_medium, self.COLORS["text"], y_offset)
        y_offset = render_text("[LEFT/RIGHT] Trace Solution", self.font_small, self.COLORS["text"], y_offset)
        if self.show_search_process:
            y_offset = render_text("[A] Toggle Auto-Run Search", self.font_small, self.COLORS["text"], y_offset)
            y_offset = render_text("[SPACE] Step Search", self.font_small, self.COLORS["text"], y_offset)
        else:
            y_offset = render_text("[A] Auto-Play Solution", self.font_small, self.COLORS["text"], y_offset)
        y_offset = render_text("[R] Restart Search", self.font_small, self.COLORS["text"], y_offset)

    def draw_board(self, state_str: str):
        self.screen.fill(self.COLORS["background"], pygame.Rect(0, 0, self.window_size, self.height))
        
        padding = 5
        
        for i, char in enumerate(state_str):
            row = i // self.puzzle_size
            col = i % self.puzzle_size
            
            x = col * self.cell_size + padding
            y = row * self.cell_size + padding
            size = self.cell_size - (padding * 2)
            
            rect = pygame.Rect(x, y, size, size)
            
            if char == '0':
                pygame.draw.rect(self.screen, self.COLORS["empty"], rect, border_radius=10)
            else:
                # Highlight if it's in the correct position
                if state_str[i] == self.goal_state[i]:
                    color = self.COLORS["tile_goal"]
                else:
                    color = self.COLORS["tile"]
                    
                pygame.draw.rect(self.screen, color, rect, border_radius=10)
                
                # Draw text
                # Convert hex to decimal for display (e.g., 'a' -> '10')
                display_text = str(int(char, 16))
                text_surf = self.font_large.render(display_text, True, self.COLORS["tile_text"])
                text_rect = text_surf.get_rect(center=rect.center)
                self.screen.blit(text_surf, text_rect)

    def render(self):
        # Determine which state to draw
        state_to_draw = ""
        if self.playback_mode and self.solution_path:
            state_to_draw = self.solution_path[self.playback_index]
        elif self.solver.current_node:
            state_to_draw = self.solver.current_node.state
        else:
            state_to_draw = self.solver.problem.start
            
        self.draw_board(state_to_draw)
        self.draw_hud()
        
        if getattr(self, 'is_loading', False):
            overlay = pygame.Surface((self.window_size, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            loading_surf = self.font_large.render("SOLVING...", True, (255, 255, 255))
            loading_rect = loading_surf.get_rect(center=(self.window_size // 2, self.height // 2))
            self.screen.blit(loading_surf, loading_rect)
            
        pygame.display.flip()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_a:
                    self.auto_run = not self.auto_run
                elif event.key == pygame.K_RIGHT:
                    if self.playback_mode and self.playback_index < len(self.solution_path) - 1:
                        self.playback_index += 1
                elif event.key == pygame.K_LEFT:
                    if self.playback_mode and self.playback_index > 0:
                        self.playback_index -= 1
                elif event.key == pygame.K_SPACE:
                    if self.playback_mode:
                        if self.playback_index < len(self.solution_path) - 1:
                            self.playback_index += 1
                    elif self.solver.status == SearchStatus.RUNNING:
                        self.solver.search_step()
                        self.check_solution()

        # Handle Auto-Run
        if self.auto_run:
            if self.playback_mode:
                current_time = time.time()
                if current_time - self.last_playback_time > self.playback_delay:
                    if self.playback_index < len(self.solution_path) - 1:
                        self.playback_index += 1
                        self.last_playback_time = current_time
            elif self.solver.status == SearchStatus.RUNNING:
                # Do a step
                self.solver.search_step()
                self.check_solution()

    def check_solution(self):
        if self.solver.status == SearchStatus.SUCCESS and not self.playback_mode:
            self.playback_mode = True
            self.solution_path = reconstruct_path(self.solver.solution_node)
            self.playback_index = 0
            self.last_playback_time = time.time()
            self.auto_run = False # Stop auto-playing right after search finishes!
            

    def restart(self):
        self.solver.reset()
        self.playback_mode = False
        self.solution_path = []
        self.playback_index = 0
        if not self.show_search_process:
            self.is_loading = True

    def run(self):
        while self.running:
            self.update()
            self.render()
            
            if getattr(self, 'is_loading', False):
                # We rendered the loading screen, now we block the loop for a split second to solve
                self.solver.run()
                self.check_solution()
                self.is_loading = False
                
            self.clock.tick(self.fps)
        pygame.quit()
