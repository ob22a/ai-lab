import pytest
from domains.tic_tac_toe.TicTacToe import TicTacToeState
from games.Minimax import MinimaxSolver
from games.AlphaBeta import AlphaBetaSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver
from games.Expectiminimax import ExpectiminimaxSolver
from games.MCTS import MCTSSolver
from games.IterativeDeepening import IterativeDeepeningSolver

def test_minimax_tictactoe():
    # X to move, one move away from winning:
    # X O X
    # O X O
    #   ' ' '
    board = [
        ['X', 'O', 'X'],
        ['O', 'X', 'O'],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(board, current_player='X')
    solver = MinimaxSolver()
    best_move = solver.get_best_action(state)
    # The only sensible move for X to win immediately is (2,2) on the diagonal
    assert best_move in [(2, 0), (2, 2)]

def test_alphabeta_tictactoe():
    board = [
        ['X', 'O', 'X'],
        ['O', 'X', 'O'],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(board, current_player='X')
    solver = AlphaBetaSolver()
    best_move = solver.get_best_action(state)
    assert best_move in [(2, 0), (2, 2)]

def test_alphabeta_ordered_tictactoe():
    board = [
        ['X', 'O', 'X'],
        ['O', 'X', 'O'],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(board, current_player='X')
    solver = AlphaBetaOrderedSolver(max_depth=3)
    best_move = solver.get_best_action(state)
    assert best_move in [(2, 0), (2, 2)]

def test_expectiminimax_tictactoe():
    board = [
        ['X', 'O', 'X'],
        ['O', 'X', 'O'],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(board, current_player='X')
    solver = ExpectiminimaxSolver(max_depth=3)
    best_move = solver.get_best_action(state)
    assert best_move in [(2, 0), (2, 2)]

def test_mcts_tictactoe():
    board = [
        ['X', 'O', 'X'],
        ['O', 'X', 'O'],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(board, current_player='X')
    solver = MCTSSolver(num_simulations=200)
    best_move = solver.get_best_action(state)
    assert best_move in [(2, 0), (2, 1), (2, 2)]

def test_iterative_deepening_tictactoe():
    board = [
        ['X', 'O', 'X'],
        ['O', 'X', 'O'],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(board, current_player='X')
    solver = IterativeDeepeningSolver(time_limit_seconds=0.5)
    best_move = solver.get_best_action(state)
    assert best_move in [(2, 0), (2, 2)]
