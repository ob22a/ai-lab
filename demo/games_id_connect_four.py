import time
from domains.connect_four.ConnectFour import ConnectFourState
from domains.connect_four.ConnectFourEval import connect_four_evaluation
from games.IterativeDeepening import IterativeDeepeningSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver

def test_iterative_deepening():
    print("=== Connect Four: Iterative Deepening (2.0s limit) ===\n")
    
    # Yellow is in trouble, but with enough depth they might find a block
    board = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0]
    ]
    
    state = ConnectFourState(board, current_player=-1) # Yellow's turn to play
    
    # 1. Run the ID solver
    id_solver = IterativeDeepeningSolver(time_limit_seconds=2.0, evaluation_function=connect_four_evaluation)
    
    start = time.time()
    best_action = id_solver.get_best_action(state)
    duration = time.time() - start
    
    print(f"Time Taken: {duration:.4f} seconds")
    print(f"Max Depth Fully Completed: {id_solver.max_depth_reached}")
    print(f"Nodes Expanded (Total across all depths): {id_solver.nodes_expanded}")
    print(f"Best Action Found: Drop piece in column {best_action}")
    
    print("\nResulting State:")
    print(state.apply_action(best_action))
    
def test_transposition_table():
    print("\n=== Transposition Table Efficacy (Depth 6) ===\n")
    
    # Empty board to maximize transpositions
    state = ConnectFourState() 
    
    ab = AlphaBetaOrderedSolver(max_depth=6, evaluation_function=connect_four_evaluation)
    
    start = time.time()
    ab.get_best_action(state)
    duration = time.time() - start
    
    tt = ab.transposition_table
    hit_rate = (tt.hits / tt.lookups) * 100 if tt.lookups > 0 else 0
    
    print(f"Time Taken: {duration:.4f} seconds")
    print(f"Nodes Expanded: {ab.nodes_expanded}")
    print(f"TT Lookups: {tt.lookups}")
    print(f"TT Cache Hits: {tt.hits}")
    print(f"Hit Rate: {hit_rate:.2f}%")

def main():
    test_iterative_deepening()
    test_transposition_table()

if __name__ == "__main__":
    main()
