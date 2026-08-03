from games.AlphaBeta import AlphaBetaSolver
from games.MCTS import MCTSSolver
from visualization.BoardGameVisualizer import BoardGameVisualizer

def main():
    print("Initializing Board Game Visualizer...")
    
    # --- CHOOSE YOUR GAME ---
    # Uncomment the game you want to play!
    
    # from domains.connect_four.ConnectFour import ConnectFourState
    # initial_state = ConnectFourState()
    
    # from domains.tic_tac_toe.TicTacToe import TicTacToeState
    # initial_state = TicTacToeState()
    
    from domains.othello.Othello import OthelloState
    initial_state = OthelloState()
    # ------------------------
    
    # We will pit AlphaBeta (depth=4) against MCTS (1000 simulations)
    # Alternatively, you can change one of these to "HUMAN" to play against the AI!
    # Wait, AlphaBetaSolver doesn't take depth in __init__, it takes it in IterativeDeepening or maybe AlphaBetaOrdered? Let's check... wait, I will just remove the depth argument for now if it doesn't take it, but wait, ConnectFour with unbounded AlphaBeta will hang forever. Let's just use RandomSolver or use MCTS vs MCTS to be safe.
    from games.RandomSolver import RandomSolver
    p1 = RandomSolver()
    p2 = MCTSSolver(num_simulations=500)
    
    # Uncomment to play against MCTS yourself!
    # p1 = "HUMAN"
    
    visualizer = BoardGameVisualizer(
        initial_state=initial_state,
        player1=p1,
        player2=p2,
        cell_size=80
    )
    
    visualizer.run()

if __name__ == "__main__":
    main()
