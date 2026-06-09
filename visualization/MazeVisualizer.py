import pygame
import copy
from typing import Deque

from visualization.Visualizer import Visualizer
from search.SearchAlgorithm import SearchStatus
from core.node import Node
from core.utils import reconstruct_path

from search.SearchAlgorithm import SearchAlgorithm


class MazeSearchVisualizer(Visualizer):

    def __init__(
        self,
        maze,
        solver:SearchAlgorithm,
        cell_size=30,
        fps=60,
        auto_run=False
    ):
        self.maze = maze
        self.solver = solver

        self.cell_size = cell_size
        self.fps = fps
        self.auto_run = auto_run

        self.width = maze.cols * cell_size
        self.height = maze.rows * cell_size

        self.COLORS = {
            "background": (255, 255, 255),

            "explored": (200, 200, 200),
            "frontier": (100, 150, 255),

            "current": (255, 100, 100),

            "solution": (100, 255, 100),

            "start": (255, 255, 0),
            "goal": (255, 0, 255),

            "wall": (0, 0, 0),

            "text": (0, 0, 0)
        }

        self.show_frontier = True
        self.show_explored = True
        self.show_solution = True
        self.show_current = True

        pygame.init()

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption(
            "Maze Search Visualizer"
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            None,
            24
        )

        self.running = True

    def draw_cell(self, row, col, color,padding=4):

        x = col * self.cell_size
        y = row * self.cell_size

        padded_size = self.cell_size - (padding * 2)

        pygame.draw.rect(
            self.screen,
            color,
            (
                x+padding,
                y+padding,
                padded_size,
                padded_size
            )
        )

    def draw_walls(self):

        for row in self.maze.cells:

            for cell in row:

                x = cell.col * self.cell_size
                y = cell.row * self.cell_size

                if cell.top:
                    pygame.draw.line(
                        self.screen,
                        self.COLORS["wall"],
                        (x, y),
                        (x + self.cell_size, y),
                        2
                    )

                if cell.right:
                    pygame.draw.line(
                        self.screen,
                        self.COLORS["wall"],
                        (x + self.cell_size, y),
                        (
                            x + self.cell_size,
                            y + self.cell_size
                        ),
                        2
                    )

                if cell.bottom:
                    pygame.draw.line(
                        self.screen,
                        self.COLORS["wall"],
                        (
                            x,
                            y + self.cell_size
                        ),
                        (
                            x + self.cell_size,
                            y + self.cell_size
                        ),
                        2
                    )

                if cell.left:
                    pygame.draw.line(
                        self.screen,
                        self.COLORS["wall"],
                        (x, y),
                        (
                            x,
                            y + self.cell_size
                        ),
                        2
                    )

    def render(self):

        self.screen.fill(
            self.COLORS["background"]
        )

        if self.show_explored:

            for state in self.solver.explored:

                self.draw_cell(
                    state[0],
                    state[1],
                    self.COLORS["explored"]
                )

        if self.show_frontier:

            for state in self.solver.frontier_states:

                self.draw_cell(
                    state[0],
                    state[1],
                    self.COLORS["frontier"]
                )

        if (
            self.show_solution
            and self.solver.solution_node
        ):

            path = reconstruct_path(
                self.solver.solution_node
            )

            for row, col in path:

                self.draw_cell(
                    row,
                    col,
                    self.COLORS["solution"]
                )

        start_row, start_col = (
            self.solver.problem.start
        )

        goal_row, goal_col = (
            self.solver.problem.goal
        )

        self.draw_cell(
            start_row,
            start_col,
            self.COLORS["start"]
        )

        self.draw_cell(
            goal_row,
            goal_col,
            self.COLORS["goal"]
        )

        if (
            self.show_current
            and self.solver.current_node
        ):

            row, col = (
                self.solver.current_node.state
            )

            self.draw_cell(
                row,
                col,
                self.COLORS["current"]
            )

        self.draw_walls()

       

        pygame.display.flip()

    def update(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif self.solver.status == SearchStatus.SUCCESS:
                    self.restart()

                elif event.key == pygame.K_SPACE:

                    if (
                        self.solver.status
                        == SearchStatus.RUNNING
                    ):
                        self.solver.search_step()

                elif event.key == pygame.K_a:

                    self.auto_run = (
                        not self.auto_run
                    )

        if (
            self.auto_run
            and self.solver.status
            == SearchStatus.RUNNING
        ):
            self.solver.search_step()

    def restart(self):
        self.solver.reset()
    
    def run(self):

        while self.running:

            self.update()

            self.render()

            self.clock.tick(
                self.fps
            )

        pygame.quit()