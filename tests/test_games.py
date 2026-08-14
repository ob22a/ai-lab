import pytest
from domains.tic_tac_toe.TicTacToe import TicTacToeState
from domains.connect_four.ConnectFour import ConnectFourState
from games.Minimax import MinimaxSolver
from games.AlphaBeta import AlphaBetaSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver
from games.Expectiminimax import ExpectiminimaxSolver
from games.MCTS import MCTSSolver
from games.IterativeDeepening import IterativeDeepeningSolver

# Shared board: X to move with a guaranteed diagonal win at (2,0) or (2,2).
# X O X
# O X O
# _ _ _
_WINNING_BOARD = [
    ['X', 'O', 'X'],
    ['O', 'X', 'O'],
    [' ', ' ', ' ']
]
_WINNING_MOVES = [(2, 0), (2, 2)]


def test_minimax_tictactoe():
    state = TicTacToeState(_WINNING_BOARD, current_player='X')
    solver = MinimaxSolver()
    best_move = solver.get_best_action(state)
    assert best_move in _WINNING_MOVES


def test_alphabeta_tictactoe():
    state = TicTacToeState(_WINNING_BOARD, current_player='X')
    solver = AlphaBetaSolver()
    best_move = solver.get_best_action(state)
    assert best_move in _WINNING_MOVES


def test_alphabeta_ordered_tictactoe():
    state = TicTacToeState(_WINNING_BOARD, current_player='X')
    solver = AlphaBetaOrderedSolver(max_depth=3)
    best_move = solver.get_best_action(state)
    assert best_move in _WINNING_MOVES


def test_expectiminimax_tictactoe():
    state = TicTacToeState(_WINNING_BOARD, current_player='X')
    solver = ExpectiminimaxSolver(max_depth=3)
    best_move = solver.get_best_action(state)
    assert best_move in _WINNING_MOVES


def test_mcts_tictactoe():
    """MCTS should prefer an immediate winning move over a non-winning one."""
    # Custom board where X must play (0, 2) to win, otherwise O can win on the next turn.
    # X X _
    # O O _
    # _ _ _
    mcts_board = [
        ['X', 'X', ' '],
        ['O', 'O', ' '],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(mcts_board, current_player='X')
    solver = MCTSSolver(num_simulations=500)
    best_move = solver.get_best_action(state)
    assert best_move == (0, 2)


def test_iterative_deepening_tictactoe():
    """Time-limited ID should finish quickly and pick a winning move."""
    state = TicTacToeState(_WINNING_BOARD, current_player='X')
    solver = IterativeDeepeningSolver(time_limit_seconds=0.5)
    best_move = solver.get_best_action(state)
    assert best_move in _WINNING_MOVES


def test_alphabeta_tictactoe_blocks_opponent():
    """O must block X from completing the top row."""
    board = [
        ['X', 'X', ' '],
        [' ', 'O', ' '],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(board, current_player='O')
    solver = AlphaBetaSolver()
    best_move = solver.get_best_action(state)
    assert best_move == (0, 2)


def test_alphabeta_connect_four():
    """Alpha-beta should return a legal move on a fresh Connect Four board."""
    state = ConnectFourState()
    solver = AlphaBetaSolver(max_depth=3)
    best_move = solver.get_best_action(state)
    assert best_move in state.get_legal_actions()
