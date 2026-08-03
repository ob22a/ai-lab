from typing import Any, List
from core.online_problem import OnlineSearchEnvironment


class UnknownMazeEnvironment(OnlineSearchEnvironment):
    """
    An online version of a maze. The agent does not have access to the full map.
    It can only perceive its current location, and discovers walls by bumping into them.
    (If it tries to move into a wall, it stays in the same place).
    """
    def __init__(self, maze, start_pos, goal_pos):
        self.maze = maze
        self.agent_location = start_pos
        self.goal_pos = goal_pos
        self.start_pos = start_pos

    def get_percept(self) -> Any:
        return self.agent_location

    def execute_action(self, action: Any) -> Any:
        # Standard actions: 'Up', 'Down', 'Left', 'Right'
        row, col = self.agent_location
        new_row, new_col = row, col

        # Discovering walls: we look at the maze data.
        # Maze cells have boolean flags: top, bottom, left, right (True = wall)
        cell = self.maze.cells[row][col]
        
        if action == 'Up' and not cell.top:
            new_row -= 1
        elif action == 'Down' and not cell.bottom:
            new_row += 1
        elif action == 'Left' and not cell.left:
            new_col -= 1
        elif action == 'Right' and not cell.right:
            new_col += 1
            
        self.agent_location = (new_row, new_col)
        return self.agent_location
        
    def get_reverse_action(self, state, prev_state):
        # Used by OnlineDFS to backtrack
        r1, c1 = state
        r2, c2 = prev_state
        if r2 < r1: return 'Up'
        if r2 > r1: return 'Down'
        if c2 < c1: return 'Left'
        if c2 > c1: return 'Right'
        return None

    def is_goal(self, state: Any) -> bool:
        return state == self.goal_pos

    def get_actions(self, state: Any) -> List[Any]:
        # The agent can TRY any action, it doesn't know if there's a wall until it bumps into it.
        # But to be slightly nicer, we can say it observes walls in its CURRENT cell.
        # Let's say it can observe its current cell's walls before moving.
        row, col = state
        cell = self.maze.cells[row][col]
        actions = []
        if not cell.top: actions.append('Up')
        if not cell.bottom: actions.append('Down')
        if not cell.left: actions.append('Left')
        if not cell.right: actions.append('Right')
        return actions

    def get_cost(self, state: Any, action: Any, next_state: Any) -> float:
        return 1.0

    def reset(self):
        self.agent_location = self.start_pos
