import random
from .MazeGenerator import MazeGenerator
from .UnionFind import UnionFind

class RandomizedKruskalGenerator(MazeGenerator):

    def __init__(self, rows: int, cols: int):
        super().__init__(rows, cols)
        self.walls=[]
        self.uf = UnionFind()
        self.current_wall_index = 0

        # Initialize union-find and wall list
        for row in self.maze.cells:
            for cell in row:
                self.uf.make_set((cell.row, cell.col))
                
        for r in range(self.maze.rows):
            for c in range(self.maze.cols):

              current = self.maze.get_cell(r, c)

              if c + 1 < self.maze.cols:
                  right = self.maze.get_cell(r, c + 1)
                  self.walls.append((current, right))

              if r + 1 < self.maze.rows:
                  bottom = self.maze.get_cell(r + 1, c)
                  self.walls.append((current, bottom))

        random.shuffle(self.walls)

    def generate_step(self):
        while self.current_wall_index < len(self.walls):
            cell_a, cell_b = self.walls[self.current_wall_index]
            id_a = (cell_a.row, cell_a.col)
            id_b = (cell_b.row, cell_b.col)

            if self.uf.union(id_a, id_b):
                self.maze.remove_wall(cell_a, cell_b)

            self.current_wall_index += 1
            return True  
        else:
            self.maze_generated = True
            return False 

    def generate(self):
        while self.generate_step():
            pass

        return self.maze