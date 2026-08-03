from typing import List, Any
from games.GameState import GameState

ROWS = 6
COLS = 7

class ConnectFourState(GameState):
    """
    Connect Four Domain.
    Board is a 6x7 grid (rows x cols).
    Players are 1 and -1 (representing Red and Yellow).
    0 is empty.
    """
    def __init__(self, board: List[List[int]] = None, current_player: int = 1):
        if board is None:
            self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        else:
            self.board = [row[:] for row in board]
            
        self.current_player = current_player
        # Cache the terminal status and winner once calculated
        self._winner = None
        self._is_terminal = None
        
    def get_legal_actions(self) -> List[int]:
        """Returns a list of valid columns (0 to 6) where a piece can be dropped."""
        # A column is valid if its top row (row 0) is empty
        actions = []
        for c in range(COLS):
            if self.board[0][c] == 0:
                actions.append(c)
        return actions

    def apply_action(self, action: int) -> 'ConnectFourState':
        """Drops a piece into the specified column and returns the new state."""
        new_board = [row[:] for row in self.board]
        
        # Find the lowest empty row in this column
        for r in range(ROWS - 1, -1, -1):
            if new_board[r][action] == 0:
                new_board[r][action] = self.current_player
                break
                
        next_player = -self.current_player
        return ConnectFourState(new_board, next_player)

    def is_terminal(self) -> bool:
        if self._is_terminal is not None:
            return self._is_terminal
            
        winner = self._get_winner()
        if winner != 0:
            self._winner = winner
            self._is_terminal = True
            return True
            
        # Check for draw (top row full)
        for c in range(COLS):
            if self.board[0][c] == 0:
                self._is_terminal = False
                return False
                
        self._is_terminal = True
        return True

    def get_utility(self, player: int) -> float:
        winner = self._get_winner()
        if winner == 0:
            return 0.0 # Draw or incomplete
            
        # Win is +10000, Loss is -10000
        # This matches the scale of our evaluation function
        if winner == player:
            return 10000.0
        else:
            return -10000.0

    def get_current_player(self) -> int:
        return self.current_player

    def _get_winner(self) -> int:
        """Returns 1, -1, or 0 if no winner yet."""
        if self._winner is not None:
            return self._winner
            
        # Check horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                if self.board[r][c] != 0 and \
                   self.board[r][c] == self.board[r][c+1] == self.board[r][c+2] == self.board[r][c+3]:
                    return self.board[r][c]
                    
        # Check vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if self.board[r][c] != 0 and \
                   self.board[r][c] == self.board[r+1][c] == self.board[r+2][c] == self.board[r+3][c]:
                    return self.board[r][c]
                    
        # Check positive diagonal
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if self.board[r][c] != 0 and \
                   self.board[r][c] == self.board[r+1][c+1] == self.board[r+2][c+2] == self.board[r+3][c+3]:
                    return self.board[r][c]
                    
        # Check negative diagonal
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if self.board[r][c] != 0 and \
                   self.board[r][c] == self.board[r-1][c+1] == self.board[r-2][c+2] == self.board[r-3][c+3]:
                    return self.board[r][c]
                    
        return 0
        
    def __str__(self) -> str:
        s = ""
        symbols = {1: 'R', -1: 'Y', 0: '.'}
        for r in range(ROWS):
            s += " ".join(symbols[self.board[r][c]] for c in range(COLS)) + "\n"
        s += "0 1 2 3 4 5 6\n"
        return s
