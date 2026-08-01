from core.problem import SearchProblem
from .NPuzzle import NPuzzle
from .PatternDatabase import PatternDatabase
from domains.n_puzzle.PatternDatabase import combined_pdb_heuristic
from typing import List, Union, Literal

class NPuzzleProblem(SearchProblem):
    def __init__(self, start_state: str, puzzle: NPuzzle, heuristic_type: Literal["manhattan", "pattern_db", "misplaced_tile"] = "manhattan", pdbs: List[Union[PatternDatabase]] = None):
        super().__init__(start_state, puzzle.goal_state)
        self.puzzle = puzzle
        self.heuristic_type = heuristic_type
        
        self.loaded_pdbs = []
        if pdbs:
            print("Loading Pattern Databases for heuristic...")
            for pdb in pdbs:
                print(f"Loading PDB: {pdb.filename}...")
                self.loaded_pdbs.append(pdb)
            
            print(f"Loaded {len(self.loaded_pdbs)} Pattern Databases for heuristic.")

    def get_actions(self, state: str) -> list[int]:
        # The action is simply the index we are going to swap the '0' tile with!
        zero_index = state.index('0')
        return self.puzzle.moves_map[zero_index]

    def get_result(self, state: str, action: int) -> str:
        # String slicing / list joining is extremely fast in Python
        zero_index = state.index('0')
        state_list = list(state)
        state_list[zero_index], state_list[action] = state_list[action], state_list[zero_index]
        return "".join(state_list)

    def heuristic(self, state: str) -> float:
        if self.heuristic_type == "manhattan":
            return self._manhattan_distance(state)
        elif self.heuristic_type == "pattern_db":
            return self._pdb_heuristic(state)
        elif self.heuristic_type == "misplaced_tile":
            return float(sum(1 for i, char in enumerate(state) if char != '0' and char != self.puzzle.goal_state[i]))
        return 0.0
    def _pdb_heuristic(self, state: str) -> float:
        if not self.loaded_pdbs:
            return 0.0
            
        return float(combined_pdb_heuristic(state, self.loaded_pdbs))

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
