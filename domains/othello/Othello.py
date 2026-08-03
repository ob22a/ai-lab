from typing import List, Tuple, Any
from games.GameState import GameState

EMPTY = 0
BLACK = 1  # Player 1 (MAX)
WHITE = -1 # Player 2 (MIN)

# 8 Directions for Othello flipping
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]

class OthelloState(GameState):
    """
    State representation for Othello/Reversi.
    """
    def __init__(self, board: List[List[int]] = None, current_player: int = BLACK, passed_last_turn: bool = False):
        if board is None:
            self.board = [[EMPTY for _ in range(8)] for _ in range(8)]
            self.board[3][3] = WHITE
            self.board[4][4] = WHITE
            self.board[3][4] = BLACK
            self.board[4][3] = BLACK
            self.current_player = BLACK
        else:
            self.board = [row[:] for row in board]
            self.current_player = current_player
            
        self.passed_last_turn = passed_last_turn
        
    def get_current_player(self) -> int:
        return self.current_player
        
    def is_terminal(self) -> bool:
        # Game is over if both players have to pass sequentially
        if self.passed_last_turn and len(self.get_legal_actions()) == 1 and self.get_legal_actions()[0] == "PASS":
            return True
            
        # Or if the board is completely full
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == EMPTY:
                    return False
        return True

    def get_utility(self, player: int) -> float:
        black_count = 0
        white_count = 0
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == BLACK:
                    black_count += 1
                elif self.board[r][c] == WHITE:
                    white_count += 1
                    
        # Win: +1000, Loss: -1000, Tie: 0
        if player == BLACK:
            if black_count > white_count: return 1000.0
            elif black_count < white_count: return -1000.0
            else: return 0.0
        else:
            if white_count > black_count: return 1000.0
            elif white_count < black_count: return -1000.0
            else: return 0.0

    def _get_flips(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Returns a list of opponent pieces that would be flipped if the current player plays at (r, c)."""
        if self.board[r][c] != EMPTY:
            return []
            
        flips = []
        for dr, dc in DIRECTIONS:
            curr_r, curr_c = r + dr, c + dc
            path = []
            
            # Walk in this direction as long as we see opponent pieces
            while 0 <= curr_r < 8 and 0 <= curr_c < 8 and self.board[curr_r][curr_c] == -self.current_player:
                path.append((curr_r, curr_c))
                curr_r += dr
                curr_c += dc
                
            # If we walked past at least one opponent piece and landed on our own piece, it's a valid flip sequence
            if path and 0 <= curr_r < 8 and 0 <= curr_c < 8 and self.board[curr_r][curr_c] == self.current_player:
                flips.extend(path)
                
        return flips

    def get_legal_actions(self) -> List[Any]:
        actions = []
        for r in range(8):
            for c in range(8):
                if self._get_flips(r, c):
                    actions.append((r, c))
                    
        if not actions:
            return ["PASS"]
            
        return actions

    def apply_action(self, action: Any) -> 'OthelloState':
        if action == "PASS":
            return OthelloState(self.board, -self.current_player, passed_last_turn=True)
            
        r, c = action
        flips = self._get_flips(r, c)
        
        new_board = [row[:] for row in self.board]
        new_board[r][c] = self.current_player
        
        for flip_r, flip_c in flips:
            new_board[flip_r][flip_c] = self.current_player
            
        return OthelloState(new_board, -self.current_player, passed_last_turn=False)

    def __str__(self):
        symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W'}
        lines = ["  0 1 2 3 4 5 6 7"]
        for r in range(8):
            row_str = f"{r} "
            for c in range(8):
                row_str += symbols[self.board[r][c]] + " "
            lines.append(row_str)
        return "\n".join(lines)
