import random
from typing import List, Tuple, Any
from games.GameState import GameState

EMPTY = 0
P1_MAN = 1    # Player 1 (MAX) moves down (row index increases)
P1_KING = 2
P2_MAN = -1   # Player 2 (MIN) moves up (row index decreases)
P2_KING = -2

# Precompute Zobrist hashing tables
_ZOBRIST_TABLE = {}
_ZOBRIST_TURN = random.getrandbits(64)

for r in range(8):
    for c in range(8):
        if (r + c) % 2 == 1:
            for piece in [P1_MAN, P1_KING, P2_MAN, P2_KING]:
                _ZOBRIST_TABLE[(r, c, piece)] = random.getrandbits(64)

class CheckersState(GameState):
    """
    State representation for Checkers.
    Actions are represented as a list of coordinates forming a path:
    [(r_start, c_start), (r_next, c_next), ...]
    This elegantly handles both single moves and multi-jumps.
    """
    def __init__(self, board: List[List[int]] = None, current_player: int = 1, zobrist_hash: int = None):
        if board is None:
            self.board = self._create_initial_board()
            self.current_player = 1
            self.hash = self._compute_initial_hash()
        else:
            self.board = [row[:] for row in board]
            self.current_player = current_player
            self.hash = zobrist_hash

    def _create_initial_board(self) -> List[List[int]]:
        board = [[EMPTY for _ in range(8)] for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = P1_MAN
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = P2_MAN
        return board
        
    def _compute_initial_hash(self) -> int:
        h = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != EMPTY:
                    h ^= _ZOBRIST_TABLE[(r, c, piece)]
        if self.current_player == -1:
            h ^= _ZOBRIST_TURN
        return h
        
    def get_hash(self) -> int:
        return self.hash
        
    def get_current_player(self) -> int:
        return self.current_player
        
    def is_terminal(self) -> bool:
        return len(self.get_legal_actions()) == 0

    def get_utility(self, player: int) -> float:
        # Checkers is terminal when a player has no legal moves.
        # The player whose turn it is has no moves, meaning they lost.
        if self.current_player == player:
            return -1000.0
        else:
            return 1000.0

    def _get_move_directions(self, piece: int) -> List[Tuple[int, int]]:
        if piece == P1_MAN:
            return [(1, -1), (1, 1)]
        elif piece == P2_MAN:
            return [(-1, -1), (-1, 1)]
        elif piece in (P1_KING, P2_KING):
            return [(1, -1), (1, 1), (-1, -1), (-1, 1)]
        return []

    def get_legal_actions(self) -> List[Any]:
        jumps = []
        regular_moves = []
        
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                # Check if it's our piece
                if (self.current_player == 1 and piece > 0) or (self.current_player == -1 and piece < 0):
                    piece_jumps = self._get_jumps_for_piece(r, c, piece)
                    jumps.extend(piece_jumps)
                    
                    if not jumps: # Only calculate regular moves if we haven't found any jumps globally
                        piece_moves = self._get_regular_moves_for_piece(r, c, piece)
                        regular_moves.extend(piece_moves)
                        
        # Mandatory jump rule: if ANY jump is possible, you must take it
        if jumps:
            return [tuple(a) for a in jumps]
        return [tuple(a) for a in regular_moves]

    def _get_regular_moves_for_piece(self, r: int, c: int, piece: int) -> List[List[Tuple[int, int]]]:
        moves = []
        dirs = self._get_move_directions(piece)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == EMPTY:
                moves.append([(r, c), (nr, nc)])
        return moves

    def _get_jumps_for_piece(self, r: int, c: int, piece: int, current_path=None, current_board=None) -> List[List[Tuple[int, int]]]:
        """
        Recursively finds all valid jump sequences (multi-jumps) for a specific piece.
        """
        if current_path is None:
            current_path = [(r, c)]
        if current_board is None:
            current_board = [row[:] for row in self.board]
            
        jumps = []
        dirs = self._get_move_directions(piece)
        
        for dr, dc in dirs:
            mid_r, mid_c = r + dr, c + dc
            end_r, end_c = r + 2 * dr, c + 2 * dc
            
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                mid_piece = current_board[mid_r][mid_c]
                end_piece = current_board[end_r][end_c]
                
                # Check if we can jump an opponent piece and land on an empty square
                is_opponent = (self.current_player == 1 and mid_piece < 0) or (self.current_player == -1 and mid_piece > 0)
                if is_opponent and end_piece == EMPTY:
                    # Simulate the jump temporarily
                    new_board = [row[:] for row in current_board]
                    new_board[r][c] = EMPTY
                    new_board[mid_r][mid_c] = EMPTY
                    
                    # Handle king promotion during a jump sequence
                    promoted_piece = piece
                    if piece == P1_MAN and end_r == 7:
                        promoted_piece = P1_KING
                    elif piece == P2_MAN and end_r == 0:
                        promoted_piece = P2_KING
                        
                    new_board[end_r][end_c] = promoted_piece
                    
                    new_path = current_path + [(end_r, end_c)]
                    
                    # If we promoted to a king, the jump sequence ends immediately (standard US Checkers rule)
                    if promoted_piece != piece:
                        jumps.append(new_path)
                    else:
                        # Recursively check for multi-jumps
                        further_jumps = self._get_jumps_for_piece(end_r, end_c, promoted_piece, new_path, new_board)
                        if further_jumps:
                            jumps.extend(further_jumps)
                        else:
                            jumps.append(new_path)
                            
        return jumps

    def apply_action(self, action: Any) -> 'CheckersState':
        """
        Applies a move or jump sequence, updating the board and Zobrist hash incrementally.
        """
        new_board = [row[:] for row in self.board]
        new_hash = self.hash
        
        start_r, start_c = action[0]
        piece = new_board[start_r][start_c]
        
        # Remove piece from start
        new_board[start_r][start_c] = EMPTY
        new_hash ^= _ZOBRIST_TABLE[(start_r, start_c, piece)]
        
        # Process the path
        for i in range(1, len(action)):
            curr_r, curr_c = action[i]
            prev_r, prev_c = action[i-1]
            
            # If it was a jump, remove the captured piece
            if abs(curr_r - prev_r) == 2:
                mid_r = (curr_r + prev_r) // 2
                mid_c = (curr_c + prev_c) // 2
                captured = new_board[mid_r][mid_c]
                new_board[mid_r][mid_c] = EMPTY
                new_hash ^= _ZOBRIST_TABLE[(mid_r, mid_c, captured)]
                
        # Determine final position and promotion
        end_r, end_c = action[-1]
        if piece == P1_MAN and end_r == 7:
            piece = P1_KING
        elif piece == P2_MAN and end_r == 0:
            piece = P2_KING
            
        # Place piece at end
        new_board[end_r][end_c] = piece
        new_hash ^= _ZOBRIST_TABLE[(end_r, end_c, piece)]
        
        # Switch turn
        new_hash ^= _ZOBRIST_TURN
        
        return CheckersState(new_board, -self.current_player, new_hash)

    def __str__(self):
        symbols = {EMPTY: '.', P1_MAN: 'b', P1_KING: 'B', P2_MAN: 'w', P2_KING: 'W'}
        lines = ["  0 1 2 3 4 5 6 7"]
        for r in range(8):
            row_str = f"{r} "
            for c in range(8):
                row_str += symbols[self.board[r][c]] + " "
            lines.append(row_str)
        return "\n".join(lines)
