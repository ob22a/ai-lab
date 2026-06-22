import random
from .NPuzzle import NPuzzle

class NPuzzleGenerator:
    def __init__(self, size: int):
        self.size = size
        self.puzzle = NPuzzle(size)

    def generate(self) -> str:
        """Generates a random, mathematically solvable N-puzzle state."""
        chars = list(self.puzzle.goal_state)
        random.shuffle(chars)
        
        # If the generated state is not solvable, we fix it by swapping 
        # two adjacent non-zero tiles. This perfectly flips the inversion parity!
        if not self.is_solvable(chars):
            # Find the first two non-zero tiles and swap them
            idx1, idx2 = 0, 1
            if chars[0] == '0':
                idx1, idx2 = 1, 2
            elif chars[1] == '0':
                idx1, idx2 = 0, 2
                
            chars[idx1], chars[idx2] = chars[idx2], chars[idx1]

        return "".join(chars)

    def is_solvable(self, state_list: list) -> bool:
        """
        Determines if a puzzle state is solvable based on Inversion Parity.
        An inversion is when a larger number appears before a smaller number 
        (ignoring the empty tile '0').
        """
        inversions = 0
        state_len = len(state_list)
        
        for i in range(state_len):
            if state_list[i] == '0':
                continue
            for j in range(i + 1, state_len):
                if state_list[j] == '0':
                    continue
                # Compare hexadecimal values
                val_i = int(state_list[i], 16)
                val_j = int(state_list[j], 16)
                if val_i > val_j:
                    inversions += 1

        # For odd-sized grids (e.g., 3x3), solvable if inversions is EVEN
        if self.size % 2 != 0:
            return inversions % 2 == 0
            
        # For even-sized grids (e.g., 4x4), solvability depends on both 
        # inversions parity AND the row the blank tile is on from the bottom.
        else:
            zero_index = state_list.index('0')
            # 1-indexed row from the bottom
            zero_row_from_bottom = self.size - (zero_index // self.size)
            
            if zero_row_from_bottom % 2 == 0:
                # Blank is on an EVEN row from the bottom -> inversions must be ODD
                return inversions % 2 != 0
            else:
                # Blank is on an ODD row from the bottom -> inversions must be EVEN
                return inversions % 2 == 0
