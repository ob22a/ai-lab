from .Cell import Cell

class Maze:

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols

        self.cells = [
            [Cell(r, c) for c in range(cols)]
            for r in range(rows)
        ]

    def get_cell(self, row: int, col: int):
        return self.cells[row][col]

    def remove_wall(self, cell_a: Cell, cell_b: Cell):

        dr = cell_b.row - cell_a.row
        dc = cell_b.col - cell_a.col

        if dr == 1:
            cell_a.bottom = False
            cell_b.top = False

        elif dr == -1:
            cell_a.top = False
            cell_b.bottom = False

        elif dc == 1:
            cell_a.right = False
            cell_b.left = False

        elif dc == -1:
            cell_a.left = False
            cell_b.right = False

    def printMaze(self):
      for row in self.cells:
          for cell in row:
              print("----" if cell.top else "    ", end="")
          print()  # newline after top walls

          for cell in row:
              print("|   " if cell.left else "    ", end="")
          print("|")  if row[-1].right else print(" ")  # newline after left walls and right wall of the last cell
      
      # bottom walls
      for cell in self.cells[-1]:
          print("----" if cell.bottom else "    ", end="")
      print()  # newline after bottom walls