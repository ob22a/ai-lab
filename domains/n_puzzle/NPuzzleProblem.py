from core.problem import SearchProblem
from .NPuzzle import NPuzzle
from typing import Literal

class NPuzzleProblem(SearchProblem):
    def __init__(self, start_state: str, puzzle: NPuzzle, heuristic_type: str = "manhattan"):
        super().__init__(start_state, puzzle.goal_state)
        self.puzzle = puzzle
        self.heuristic_type = heuristic_type

    def get_actions(self, state: str) -> list:
        # The action is simply the index we are going to swap the '0' tile with!
        zero_index = state.index('0')
        return self.puzzle.moves_map[zero_index]

    def get_result(self, state: str, action: int) -> str:
        # String slicing / list joining is extremely fast in Python
        zero_index = state.index('0')
        state_list = list(state)
        state_list[zero_index], state_list[action] = state_list[action], state_list[zero_index]
        return "".join(state_list)

    def heuristic(self, state: Literal['misplaced_tile','manhattan']) -> float:
        if self.heuristic_type == "manhattan":
            return self._manhattan_distance(state)
        
        elif self.heuristic_type == "misplaced_tile":
            return self._misplaced_tiles(state)

        return 0.0
    
    def _misplaced_tiles(self,state:str)->float:
        cost = 0

        for idx, c in enumerate(state):
            if self.puzzle.goal_state[idx]!=c:
                cost+=1

        return cost

    def _manhattan_distance(self, state: str) -> float:
        dist = 0
        for i, char in enumerate(state):
            if char == '0':
                continue
            
            # Find where this tile SHOULD be
            target_index = self.puzzle.goal_state.index(char)
            
            # Calculate grid coordinates
            current_row, current_col = i // self.puzzle.size, i % self.puzzle.size
            target_row, target_col = target_index // self.puzzle.size, target_index % self.puzzle.size
            
            # Manhattan distance formula
            dist += abs(current_row - target_row) + abs(current_col - target_col)
            
        return float(dist)
