from typing import List, Any, Tuple
from games.GameState import GameState
import copy

class TicTacToeState(GameState):
    """
    State representation for a game of Tic-Tac-Toe.
    Board is a 3x3 list of characters: 'X', 'O', or ' ' (empty).
    'X' always goes first.
    """
    def __init__(self, board: List[List[str]] = None, current_player: str = 'X'):
        if board is None:
            self.board = [[' ' for _ in range(3)] for _ in range(3)]
        else:
            # Deep copy the board to ensure immutability of parent states
            self.board = [row[:] for row in board]
            
        self.current_player = current_player

    def get_legal_actions(self) -> List[Tuple[int, int]]:
        """Returns a list of (row, col) tuples representing empty cells."""
        actions = []
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == ' ':
                    actions.append((r, c))
        return actions

    def apply_action(self, action: Tuple[int, int]) -> 'TicTacToeState':
        """Applies the action (row, col) and returns a NEW state."""
        r, c = action
        if self.board[r][c] != ' ':
            raise ValueError(f"Invalid move: cell {r},{c} is already occupied.")
            
        # Determine the next player
        next_player = 'O' if self.current_player == 'X' else 'X'
        
        # Create a new state
        new_state = TicTacToeState(self.board, next_player)
        
        # Apply the move to the new state
        new_state.board[r][c] = self.current_player
        
        return new_state

    def is_terminal(self) -> bool:
        """The game is over if someone has won, or the board is full (draw)."""
        winner = self._get_winner()
        if winner is not None:
            return True
            
        # Check for draw (no empty cells left)
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == ' ':
                    return False
        return True

    def get_utility(self, player: str) -> float:
        """Returns +1 if the player won, -1 if they lost, 0 for a draw/incomplete."""
        winner = self._get_winner()
        if winner is None:
            return 0.0
        elif winner == player:
            return 1.0
        else:
            return -1.0

    def get_current_player(self) -> str:
        return self.current_player
        
    def _get_winner(self) -> str:
        """Helper to check if 'X' or 'O' has won. Returns None if no winner."""
        # Check rows and columns
        for i in range(3):
            if self.board[i][0] != ' ' and self.board[i][0] == self.board[i][1] == self.board[i][2]:
                return self.board[i][0]
            if self.board[0][i] != ' ' and self.board[0][i] == self.board[1][i] == self.board[2][i]:
                return self.board[0][i]
                
        # Check diagonals
        if self.board[0][0] != ' ' and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.board[0][0]
        if self.board[0][2] != ' ' and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.board[0][2]
            
        return None
        
    def __str__(self) -> str:
        s = ""
        for r in range(3):
            s += " | ".join(self.board[r]) + "\n"
            if r < 2:
                s += "---------\n"
        return s
