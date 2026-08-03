import pygame
import time
from typing import List

from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus

def reconstruct_node_path(node):
    path = []
    while node:
        path.append(node)
        node = node.parent
    return path[::-1]


class SokobanVisualizer(Visualizer):
    def __init__(
        self,
        problem,
        solver: SearchAlgorithm,
        cell_size=40,
        fps=60,
        auto_run=False,
        show_search_process=False
    ):
        self.problem = problem
        self.solver = solver

        self.cell_size = cell_size
        self.fps = fps

        self.auto_run = auto_run
        self.show_search_process = show_search_process

        self.hud_width = 300
        
        self.board_width = self.problem.width * self.cell_size
        self.board_height = self.problem.height * self.cell_size

        self.width = self.board_width + self.hud_width
        self.height = max(self.board_height, 400) # Minimum height for HUD

        self.COLORS = {
            "background": (30, 30, 30),
            "hud": (40, 40, 40),
            "hud_line": (100, 100, 100),
            "hud_text": (200, 200, 200),
            "hud_title": (255, 200, 100),
            
            "wall": (100, 100, 100),
            "floor": (50, 50, 50),
            "target": (200, 50, 50),
            "player": (50, 200, 50),
            "box": (200, 150, 50),
            "box_on_target": (50, 200, 200),
            "player_on_target": (150, 250, 150),
            
            "loading": (0, 0, 0, 180)
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AI Lab - Sokoban Solver")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_large = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)

        self.running = True
        self.playback_mode = False
        self.solution_path = []
        self.playback_index = 0
        self.playback_delay = 0.2
        self.last_playback_time = 0

        self.is_loading = not self.show_search_process

    def restart(self):
        self.solver.reset()
        self.playback_mode = False
        self.solution_path = []
        self.playback_index = 0
        self.is_loading = not self.show_search_process

    def draw_board(self, state):
        board_rect = pygame.Rect(0, 0, self.board_width, self.board_height)
        pygame.draw.rect(self.screen, self.COLORS["background"], board_rect)
        
        offset_x = (self.board_width - (self.problem.width * self.cell_size)) // 2
        offset_y = (self.board_height - (self.problem.height * self.cell_size)) // 2

        for r in range(self.problem.height):
            for c in range(self.problem.width):
                pos = (r, c)
                
                rect = pygame.Rect(
                    offset_x + c * self.cell_size,
                    offset_y + r * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Draw Base (Floor or Wall)
                if pos in self.problem.walls:
                    pygame.draw.rect(self.screen, self.COLORS["wall"], rect)
                    pygame.draw.rect(self.screen, (60,60,60), rect, 2) # Wall border
                else:
                    pygame.draw.rect(self.screen, self.COLORS["floor"], rect)
                    pygame.draw.rect(self.screen, (40,40,40), rect, 1) # Grid line
                    
                # Draw Target
                if pos in self.problem.targets:
                    pygame.draw.circle(
                        self.screen, 
                        self.COLORS["target"], 
                        rect.center, 
                        self.cell_size // 6
                    )

                # Draw Box
                if pos in state.boxes:
                    box_rect = rect.inflate(-self.cell_size//4, -self.cell_size//4)
                    color = self.COLORS["box_on_target"] if pos in self.problem.targets else self.COLORS["box"]
                    pygame.draw.rect(self.screen, color, box_rect, border_radius=4)
                    pygame.draw.rect(self.screen, (255,255,255), box_rect, 2, border_radius=4) # Box highlight

                # Draw Player
                if pos == state.player:
                    color = self.COLORS["player_on_target"] if pos in self.problem.targets else self.COLORS["player"]
                    pygame.draw.circle(
                        self.screen,
                        color,
                        rect.center,
                        self.cell_size // 3
                    )
                    pygame.draw.circle(
                        self.screen,
                        (255,255,255),
                        rect.center,
                        self.cell_size // 3,
                        2
                    )

    def draw_hud(self):
        hud_rect = pygame.Rect(self.board_width, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud"], hud_rect)
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (self.board_width, 0), (self.board_width, self.height), 2)

        x = self.board_width + 20
        y = 20

        def draw(text, font=None, color=None, gap=8):
            nonlocal y
            f = font or self.font
            c = color or self.COLORS["hud_text"]
            surface = f.render(str(text), True, c)
            self.screen.blit(surface, (x, y))
            y += surface.get_height() + gap

        draw("SOKOBAN SOLVER", self.font_title, self.COLORS["hud_title"], 20)
        draw(f"Algorithm: {self.solver.__class__.__name__}")
        draw(f"Status: {self.solver.status.name}")
        draw(f"Nodes Expanded: {self.solver.nodes_expanded}")
        draw(f"Nodes Generated: {self.solver.nodes_generated}")
        
        y += 20
        draw("CONTROLS:", self.font_title, self.COLORS["hud_title"])
        draw("[SPACE] Step / Playback")
        draw("[A] Toggle Auto-Run")
        draw("[R] Restart")
        draw("[Left/Right] Scrub Playback")
        
        y += 20
        draw(f"Auto-Run: {'ON' if self.auto_run else 'OFF'}")
        
        if self.playback_mode and self.solution_path:
            draw(f"Playback: {self.playback_index}/{len(self.solution_path)-1}")
            
            # Show the action taken
            current_node = self.solution_path[self.playback_index]
            if current_node.action:
                action_text = f"Action: {current_node.action}"
                if current_node.action.islower():
                    action_text += " (PUSH)"
                else:
                    action_text += " (MOVE)"
                draw(action_text, color=(100, 255, 100))

    def render(self):
        if self.playback_mode and self.solution_path:
            state = self.solution_path[self.playback_index].state
        elif self.solver.current_node:
            state = self.solver.current_node.state
        else:
            state = self.solver.problem.start

        self.draw_board(state)
        self.draw_hud()

        if self.is_loading:
            overlay = pygame.Surface((self.board_width, self.height), pygame.SRCALPHA)
            overlay.fill(self.COLORS["loading"])
            self.screen.blit(overlay, (0, 0))

            text = self.font_large.render("SOLVING...", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(self.board_width // 2, self.height // 2)))

        pygame.display.flip()

    def check_solution(self):
        if self.solver.status == SearchStatus.SUCCESS and not self.playback_mode:
            self.playback_mode = True
            self.solution_path = reconstruct_node_path(self.solver.solution_node)
            self.playback_index = 0
            self.last_playback_time = time.time()
            self.auto_run = False
            
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
                elif event.key == pygame.K_SPACE:
                    if self.show_search_process and self.solver.status == SearchStatus.RUNNING:
                        self.solver.search_step()
                        self.check_solution()
                elif event.key == pygame.K_RIGHT:
                    if self.playback_mode and self.playback_index < len(self.solution_path) - 1:
                        self.playback_index += 1
                elif event.key == pygame.K_LEFT:
                    if self.playback_mode and self.playback_index > 0:
                        self.playback_index -= 1

        if self.auto_run and self.show_search_process and self.solver.status == SearchStatus.RUNNING:
            self.solver.search_step()
            self.check_solution()

        if self.auto_run and self.playback_mode and len(self.solution_path) > 0:
            now = time.time()
            if now - self.last_playback_time >= self.playback_delay:
                if self.playback_index < len(self.solution_path) - 1:
                    self.playback_index += 1
                self.last_playback_time = now

    def run(self):
        while self.running:
            self.update()
            
            if self.is_loading:
                self.render()
                pygame.display.flip()
                pygame.event.pump()
                
                self.solver.run()
                self.check_solution()
                self.is_loading = False

            self.render()
            self.clock.tick(self.fps)

        pygame.quit()
