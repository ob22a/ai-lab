import time
from domains.tic_tac_toe.TicTacToe import TicTacToeState
from games.Minimax import MinimaxSolver
from games.AlphaBeta import AlphaBetaSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver

def compare_solvers():
    print("=== Tic-Tac-Toe Game Tree Complexity ===")
    print("Evaluating the entire game tree from an empty board.\n")
    
    empty_board = [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(empty_board, 'X')
    
    # 1. Pure Minimax
    print("1. Pure Minimax")
    minimax = MinimaxSolver()
    start = time.time()
    minimax.get_best_action(state)
    print(f"Nodes expanded: {minimax.nodes_expanded}")
    print(f"Time: {time.time() - start:.4f}s\n")
    
    # 2. Alpha-Beta Pruning
    print("2. Alpha-Beta Pruning")
    ab = AlphaBetaSolver()
    start = time.time()
    ab.get_best_action(state)
    print(f"Nodes expanded: {ab.nodes_expanded}")
    print(f"Time: {time.time() - start:.4f}s\n")
    
    # 3. Alpha-Beta Pruning (with Move Ordering)
    print("3. Alpha-Beta Pruning (Killer Moves + History)")
    ab_ordered = AlphaBetaOrderedSolver()
    start = time.time()
    ab_ordered.get_best_action(state)
    print(f"Nodes expanded: {ab_ordered.nodes_expanded}")
    print(f"Time: {time.time() - start:.4f}s\n")
    
    print("Note: For tiny state spaces like Tic-Tac-Toe, move ordering overhead")
    print("can sometimes increase wall-clock time despite exploring fewer nodes.")
    print("However, for massive games like Chess, node reduction is exponential!")

def main():
    compare_solvers()

if __name__ == "__main__":
    main()
