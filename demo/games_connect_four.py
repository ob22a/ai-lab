import time
from domains.connect_four.ConnectFour import ConnectFourState
from domains.connect_four.ConnectFourEval import connect_four_evaluation
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver

def play_connect_four(depth: int):
    print(f"\n=== Connect Four: Alpha-Beta (Depth {depth}) ===")
    
    # Set up a board where Player 1 (Red) is about to get 4 in a row, 
    # and Player -1 (Yellow) must block it.
    
    # Empty board except for 3 Red pieces in a row at the bottom
    board = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0]
    ]
    
    state = ConnectFourState(board, current_player=-1) # Yellow's turn to play
    print("Initial State (Yellow to move):")
    print(state)
    
    solver = AlphaBetaOrderedSolver(max_depth=depth, evaluation_function=connect_four_evaluation)
    
    start = time.time()
    best_action = solver.get_best_action(state)
    duration = time.time() - start
    
    print(f"Yellow's best action: Drop piece in column {best_action}")
    print(f"Nodes expanded: {solver.nodes_expanded}")
    print(f"Time taken: {duration:.4f} seconds")
    
    next_state = state.apply_action(best_action)
    print("\nResulting State:")
    print(next_state)


def main():
    print("Evaluating Connect Four AI")
    
    # Test at increasing depths
    play_connect_four(depth=2)
    play_connect_four(depth=4)
    play_connect_four(depth=6)

if __name__ == "__main__":
    main()
