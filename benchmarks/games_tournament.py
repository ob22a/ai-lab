from domains.connect_four.ConnectFour import ConnectFourState
from domains.connect_four.ConnectFourEval import connect_four_evaluation
from games.RandomSolver import RandomSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver
from games.MCTS import MCTSSolver
from games.Tournament import Tournament

def create_connect_four():
    return ConnectFourState()

def main():
    print("Initializing Agents...")
    
    # 1. Random Agent
    agent_random = RandomSolver(name="RandomAgent")
    
    # 2. Alpha-Beta Pruning (Depth 6)
    # Using our fast evaluation heuristic
    agent_ab = AlphaBetaOrderedSolver(max_depth=6, evaluation_function=connect_four_evaluation)
    agent_ab.name = "AlphaBeta(d=6)"
    
    # 3. Monte Carlo Tree Search (500 simulations)
    agent_mcts = MCTSSolver(num_simulations=500)
    agent_mcts.name = "MCTS(500)"
    
    agents = [agent_random, agent_ab, agent_mcts]
    
    # Run the tournament
    tournament = Tournament(create_connect_four, agents)
    
    # NOTE: We are running 2 games per matchup to keep the benchmark fast.
    # To test in-depth and get statistically significant results (like a 95% win rate vs Random), 
    # increase games_per_matchup to 10 or 100.
    tournament.run_tournament(games_per_matchup=2)

if __name__ == "__main__":
    main()
