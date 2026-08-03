from domains.tic_tac_toe.TicTacToe import TicTacToeState
from games.Minimax import MinimaxSolver

def test_scenario(name, board, current_player):
    print(f"\n=== {name} ===")
    state = TicTacToeState(board, current_player)
    print("Initial State:")
    print(state)
    
    solver = MinimaxSolver()
    best_action = solver.get_best_action(state)
    
    print(f"{current_player}'s best action is: {best_action}")
    print(f"Nodes expanded: {solver.nodes_expanded}")
    
    next_state = state.apply_action(best_action)
    print("\nResulting State:")
    print(next_state)


def main():
    print("Evaluating Minimax on Tic-Tac-Toe")
    
    # Scenario 1: X can win immediately
    win_board = [
        ['X', 'X', ' '],
        ['O', 'O', ' '],
        [' ', ' ', ' ']
    ]
    test_scenario("Scenario 1: X to win", win_board, 'X')
    
    # Scenario 2: X must block O
    block_board = [
        ['X', ' ', ' '],
        [' ', 'X', ' '],
        ['O', 'O', ' ']
    ]
    test_scenario("Scenario 2: X to block O", block_board, 'X')
    
    # Scenario 3: Empty board
    print("\n=== Scenario 3: Empty Board (Full Game Tree) ===")
    empty_board = [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' ']
    ]
    state = TicTacToeState(empty_board, 'X')
    solver = MinimaxSolver()
    best_action = solver.get_best_action(state)
    print(f"X's best starting action is: {best_action}")
    print(f"Nodes expanded: {solver.nodes_expanded}")


if __name__ == "__main__":
    main()
