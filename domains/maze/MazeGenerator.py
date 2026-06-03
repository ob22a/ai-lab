from abc import ABC, abstractmethod
from .Maze import Maze

class MazeGenerator(ABC):

    def __init__(self, rows: int, cols: int):
        self.maze = Maze(rows, cols)
        self.maze_generated = False

    @abstractmethod
    def generate(self):
        pass