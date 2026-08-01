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

        self.margin = 20
        self.hud_width = 300

        self.board_size = window_size

        self.width = self.board_size + self.hud_width
        self.height = self.board_size

        self.cell_size = (
            self.board_size - self.margin * 2
        ) // self.puzzle_size

        self.COLORS = {

            "background": (44, 37, 30),

            "board": (65, 53, 42),

            "hud": (35, 35, 35),

            "hud_line": (80, 80, 80),

            "tile": (236, 224, 193),

            "tile_goal": (171, 225, 150),

            "tile_text": (40, 35, 30),

            "empty": (120, 94, 70),

            "shadow": (20, 20, 20),

            "text": (240, 240, 240),

            "highlight": (255, 195, 90),

            "loading": (0, 0, 0, 170)
        }

        pygame.init()

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption(
            "N-Puzzle Search Visualizer"
        )

        self.clock = pygame.time.Clock()

        tile_font_size = max(20, self.cell_size // 2)

        self.font = pygame.font.SysFont(
            "Arial",
            tile_font_size,
            bold=True
        )

        self.font_small = pygame.font.SysFont(
            "Arial",
            18
        )

        self.font_hud = pygame.font.SysFont(
            "Arial",
            22,
            bold=True
        )

        self.font_large = pygame.font.SysFont(
            "Arial",
            40,
            bold=True
        )

        self.running = True

        self.playback_mode = False

        self.solution_path: List[str] = []

        self.playback_index = 0

        self.last_playback_time = 0

        self.playback_delay = 0.35

        self.is_loading = not show_search_process

        self.goal_state = "".join(
            hex(i)[2:]
            for i in range(
                puzzle_size * puzzle_size
            )
        )

    def draw_board(self, state_str):

        self.screen.fill(self.COLORS["background"])

        board_rect = pygame.Rect(
            0,
            0,
            self.board_size,
            self.height
        )

        pygame.draw.rect(
            self.screen,
            self.COLORS["board"],
            board_rect
        )

        spacing = 8

        for i, value in enumerate(state_str):

            row = i // self.puzzle_size
            col = i % self.puzzle_size

            x = (
                self.margin
                + col * self.cell_size
                + spacing // 2
            )

            y = (
                self.margin
                + row * self.cell_size
                + spacing // 2
            )

            rect = pygame.Rect(
                x,
                y,
                self.cell_size - spacing,
                self.cell_size - spacing
            )

            shadow = rect.move(3, 3)

            pygame.draw.rect(
                self.screen,
                self.COLORS["shadow"],
                shadow,
                border_radius=12
            )

            if value == "0":

                pygame.draw.rect(
                    self.screen,
                    self.COLORS["empty"],
                    rect,
                    border_radius=12
                )

                continue

            if value == self.goal_state[i]:

                color = self.COLORS["tile_goal"]

            else:

                color = self.COLORS["tile"]

            pygame.draw.rect(
                self.screen,
                color,
                rect,
                border_radius=12
            )

            number = str(int(value, 16))

            text = self.font.render(
                number,
                True,
                self.COLORS["tile_text"]
            )

            self.screen.blit(
                text,
                text.get_rect(center=rect.center)
            )
    
        # ======================================================

    def draw_hud(self):

        hud_rect = pygame.Rect(
            self.board_size,
            0,
            self.hud_width,
            self.height
        )

        pygame.draw.rect(
            self.screen,
            self.COLORS["hud"],
            hud_rect
        )

        pygame.draw.line(
            self.screen,
            self.COLORS["hud_line"],
            (self.board_size, 0),
            (self.board_size, self.height),
            2
        )

        x = self.board_size + 20
        y = 20

        def draw(text,
                 font=None,
                 color=None,
                 gap=8):

            nonlocal y

            if font is None:
                font = self.font_small

            if color is None:
                color = self.COLORS["text"]

            surf = font.render(
                text,
                True,
                color
            )

            self.screen.blit(
                surf,
                (x, y)
            )

            y += surf.get_height() + gap

        draw(
            "SEARCH STATUS",
            self.font_hud,
            self.COLORS["highlight"],
            15
        )

        status_color = (
            self.COLORS["tile_goal"]
            if self.solver.status == SearchStatus.SUCCESS
            else self.COLORS["text"]
        )

        draw(
            f"Status : {self.solver.status.name}",
            color=status_color
        )

        y += 12

        draw(
            "STATISTICS",
            self.font_hud,
            self.COLORS["highlight"],
            12
        )

        draw(
            f"Expanded : {self.solver.nodes_expanded}"
        )

        draw(
            f"Generated : {self.solver.nodes_generated}"
        )

        if hasattr(self.solver, "frontier_states"):

            draw(
                f"Frontier : {len(self.solver.frontier_states)}"
            )

        if hasattr(self.solver, "max_frontier_size"):

            draw(
                f"Max Frontier : {self.solver.max_frontier_size}"
            )

        if hasattr(self.solver, "limit"):

            draw(
                f"Threshold : {self.solver.limit}"
            )

        if self.playback_mode:

            y += 12

            draw(
                "PLAYBACK",
                self.font_hud,
                self.COLORS["highlight"]
            )

            draw(
                f"Move : {self.playback_index}"
            )

            draw(
                f"Total : {len(self.solution_path)-1}"
            )

        y = self.height - 180

        draw(
            "CONTROLS",
            self.font_hud,
            self.COLORS["highlight"]
        )

        if self.show_search_process:

            draw("SPACE  Step Search")

            draw("A      Auto Search")

        else:

            draw("A      Auto Play")

        draw("LEFT   Previous Move")

        draw("RIGHT  Next Move")

        draw("R      Restart")

        draw("ESC    Quit")

    def render(self):

        if self.playback_mode and self.solution_path:

            state = self.solution_path[
                self.playback_index
            ]

        elif self.solver.current_node:

            state = self.solver.current_node.state

        else:

            state = self.solver.problem.start

        self.draw_board(state)

        self.draw_hud()

        if self.is_loading:

            overlay = pygame.Surface(
                (self.board_size, self.height),
                pygame.SRCALPHA
            )

            overlay.fill(
                self.COLORS["loading"]
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            text = self.font_large.render(
                "SOLVING...",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                text,
                text.get_rect(
                    center=(
                        self.board_size // 2,
                        self.height // 2
                    )
                )
            )

        pygame.display.flip()

    def check_solution(self):

        if (
            self.solver.status == SearchStatus.SUCCESS
            and not self.playback_mode
        ):

            self.playback_mode = True

            self.solution_path = reconstruct_path(
                self.solver.solution_node
            )

            self.playback_index = 0

            self.last_playback_time = time.time()

            self.auto_run = False

    def draw_hud(self):

        hud_rect = pygame.Rect(
            self.board_size,
            0,
            self.hud_width,
            self.height
        )

        pygame.draw.rect(
            self.screen,
            self.COLORS["hud"],
            hud_rect
        )

        pygame.draw.line(
            self.screen,
            self.COLORS["hud_line"],
            (self.board_size, 0),
            (self.board_size, self.height),
            2
        )

        x = self.board_size + 20
        y = 20

        def draw(text,
                 font=None,
                 color=None,
                 gap=8):

            nonlocal y

            if font is None:
                font = self.font_small

            if color is None:
                color = self.COLORS["text"]

            surf = font.render(
                text,
                True,
                color
            )

            self.screen.blit(
                surf,
                (x, y)
            )

            y += surf.get_height() + gap

        draw(
            "SEARCH STATUS",
            self.font_hud,
            self.COLORS["highlight"],
            15
        )

        status_color = (
            self.COLORS["tile_goal"]
            if self.solver.status == SearchStatus.SUCCESS
            else self.COLORS["text"]
        )

        draw(
            f"Status : {self.solver.status.name}",
            color=status_color
        )

        y += 12

        draw(
            "STATISTICS",
            self.font_hud,
            self.COLORS["highlight"],
            12
        )

        draw(
            f"Expanded : {self.solver.nodes_expanded}"
        )

        draw(
            f"Generated : {self.solver.nodes_generated}"
        )

        if hasattr(self.solver, "frontier_states"):

            draw(
                f"Frontier : {len(self.solver.frontier_states)}"
            )

        if hasattr(self.solver, "max_frontier_size"):

            draw(
                f"Max Frontier : {self.solver.max_frontier_size}"
            )

        if hasattr(self.solver, "limit"):

            draw(
                f"Threshold : {self.solver.limit}"
            )

        if self.playback_mode:

            y += 12

            draw(
                "PLAYBACK",
                self.font_hud,
                self.COLORS["highlight"]
            )

            draw(
                f"Move : {self.playback_index}"
            )

            draw(
                f"Total : {len(self.solution_path)-1}"
            )

        y = self.height - 180

        draw(
            "CONTROLS",
            self.font_hud,
            self.COLORS["highlight"]
        )

        if self.show_search_process:

            draw("SPACE  Step Search")

            draw("A      Auto Search")

        else:

            draw("A      Auto Play")

        draw("LEFT   Previous Move")

        draw("RIGHT  Next Move")

        draw("R      Restart")

        draw("ESC    Quit")

    def render(self):

        if self.playback_mode and self.solution_path:

            state = self.solution_path[
                self.playback_index
            ]

        elif self.solver.current_node:

            state = self.solver.current_node.state

        else:

            state = self.solver.problem.start

        self.draw_board(state)

        self.draw_hud()

        if self.is_loading:

            overlay = pygame.Surface(
                (self.board_size, self.height),
                pygame.SRCALPHA
            )

            overlay.fill(
                self.COLORS["loading"]
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            text = self.font_large.render(
                "SOLVING...",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                text,
                text.get_rect(
                    center=(
                        self.board_size // 2,
                        self.height // 2
                    )
                )
            )

        pygame.display.flip()

    def check_solution(self):

        if (
            self.solver.status == SearchStatus.SUCCESS
            and not self.playback_mode
        ):

            self.playback_mode = True

            self.solution_path = reconstruct_path(
                self.solver.solution_node
            )

            self.playback_index = 0

            self.last_playback_time = time.time()

            self.auto_run = False
    
    def update(self):
        """Handle input, search, and playback."""

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

                    # Step search manually
                    if (
                        self.show_search_process
                        and self.solver.status == SearchStatus.RUNNING
                    ):
                        self.solver.search_step()
                        self.check_solution()

                elif event.key == pygame.K_RIGHT:

                    if (
                        self.playback_mode
                        and self.playback_index < len(self.solution_path) - 1
                    ):
                        self.playback_index += 1

                elif event.key == pygame.K_LEFT:

                    if (
                        self.playback_mode
                        and self.playback_index > 0
                    ):
                        self.playback_index -= 1

        if (
            self.auto_run
            and self.show_search_process
            and self.solver.status == SearchStatus.RUNNING
        ):
            self.solver.search_step()
            self.check_solution()

        if (
            self.auto_run
            and self.playback_mode
            and len(self.solution_path) > 0
        ):

            now = time.time()

            if now - self.last_playback_time >= self.playback_delay:

                if self.playback_index < len(self.solution_path) - 1:
                    self.playback_index += 1

                self.last_playback_time = now
    
    def run(self):
        """Main application loop."""

        while self.running:

            self.update()

            # Solve immediately when search visualization is disabled
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
    
    def restart(self):
        """Reset the solver and visualizer."""

        self.solver.reset()

        self.playback_mode = False
        self.solution_path = []
        self.playback_index = 0
        self.last_playback_time = 0

        self.auto_run = False

        # Show loading screen again if solving instantly
        self.is_loading = not self.show_search_process

        # Make sure the initial state is displayed
        if hasattr(self.solver, "current_node"):
            self.solver.current_node = None

        if hasattr(self.solver, "solution_node"):
            self.solver.solution_node = None