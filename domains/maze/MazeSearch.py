from core.problem import SearchProblem
from enum import Enum, auto
from typing import Tuple

class Moves(Enum):
  UP = auto()
  DOWN =auto()
  LEFT = auto()
  RIGHT = auto()


class MazeSearchProblem(SearchProblem):
  def __init__(self, maze, start:Tuple[int,int], goal:Tuple[int,int]):
    super().__init__(start, goal)
    self.size = (
      maze.rows,
      maze.cols
    )
    self.maze = maze
  
  def get_actions(self, state:Tuple[int,int]) -> list[Moves]:
    # All the moves from this cell
    dir = [(0,1),(1,0),(-1,0),(0,-1)]
    actions = []

    cell = self.maze.cells[state[0]][state[1]]

    for dx,dy in dir:
      nx,ny=state[0]+dx,state[1]+dy
      
      if 0<=nx<self.size[0] and 0<=ny<self.size[1]:
        if (nx-state[0]==1 and not cell.bottom):
          actions.append(Moves.DOWN)
        elif nx-state[0]==-1 and not cell.top:
          actions.append(Moves.UP)
        elif ny-state[1]==1 and not cell.right:
          actions.append(Moves.RIGHT)
        elif ny-state[1]==-1 and not cell.left:
          actions.append(Moves.LEFT)
    
    return actions
  
  def get_result(self, state:Tuple[int,int], action:Moves) -> Tuple[int,int]:
    match action:
      case Moves.UP:
        if state[0]==0:
          raise IndexError('Can not perform up at the first row')
        return (state[0]-1,state[1])
      case Moves.DOWN:
        if state[0]==self.size[0]-1:
          raise IndexError('Can not perform dowm at the last row')
        return (state[0]+1,state[1])
      case Moves.LEFT:
        if state[1]==0:
          raise IndexError('Can not move left at the first column')
        return (state[0],state[1]-1)
      case Moves.RIGHT:
        if state[1]==self.size[1]-1:
          raise IndexError('Can not move right at the last column')
        return (state[0],state[1]+1)
  