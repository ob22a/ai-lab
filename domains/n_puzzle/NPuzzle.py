class NPuzzle:
    """
    Representation of an N-Puzzle domain (e.g. 3x3 for 8-Puzzle, 4x4 for 15-Puzzle).
    Tile numbering: '0' is the empty tile. 
    For 8-puzzle, tiles are '0'-'8'.
    For 15-puzzle, tiles are '0'-'9' and 'a'-'f' (hexadecimal).
    """
    def __init__(self, size: int):
        self.size = size # The N in NxN grid
        self.total_tiles = size * size
        self.moves_map = self._precompute_moves()
        self.goal_state = self._generate_goal_state()

    def _generate_goal_state(self) -> str:
        # e.g., for 3x3: "012345678"
        # for 4x4: "0123456789abcdef"
        return "".join(hex(i)[2:] for i in range(self.total_tiles))

    def _precompute_moves(self) -> dict:
        """
        Performance Optimization: 
        Precomputes valid swap indices for every possible index of the empty tile '0'.
        This completely eliminates 2D grid math during search loops.
        """
        moves_map = {}
        for i in range(self.total_tiles):
            row = i // self.size
            col = i % self.size
            valid_moves = []
            if row > 0:
                valid_moves.append(i - self.size) # Up
            if row < self.size - 1:
                valid_moves.append(i + self.size) # Down
            if col > 0:
                valid_moves.append(i - 1)         # Left
            if col < self.size - 1:
                valid_moves.append(i + 1)         # Right
            moves_map[i] = valid_moves
        return moves_map
