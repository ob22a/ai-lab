import random
from .NPuzzle import NPuzzle

class NPuzzleGenerator:
    def __init__(self, size: int):
        self.size = size
        self.puzzle = NPuzzle(size)

    def generate(self, moves: int = 1000) -> str:
        grid = list(self.puzzle.goal_state)
        
        # Cache moves_map lookup for micro-optimization
        moves_map = self.puzzle.moves_map 

        for _ in range(moves):
            # Find current position of the empty tile '0'
            zero_idx = grid.index('0')
            
            # Retrieve the precomputed valid moves for this index
            valid_swaps = moves_map[zero_idx]

            # Select a random valid swap index
            swap_idx = random.choice(valid_swaps)
            
            # Execute the swap
            grid[zero_idx], grid[swap_idx] = grid[swap_idx], grid[zero_idx]

        return "".join(grid)