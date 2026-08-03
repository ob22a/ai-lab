from domains.checkers.Checkers import CheckersState
from domains.checkers.CheckersEval import checkers_evaluation
from games.RandomSolver import RandomSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver
from games.MCTS import MCTSSolver
from games.Tournament import Tournament

def create_checkers():
    return CheckersState()

def main():
    print("Initializing Checkers Agents...")
    
    agent_random = RandomSolver(name="Random")
    
    # Fast evaluation agent (Depth 4)
    agent_ab4 = AlphaBetaOrderedSolver(max_depth=4, evaluation_function=checkers_evaluation)
    agent_ab4.name = "AlphaBeta(d=4)"
    
    # Deep evaluation agent (Depth 6)
    agent_ab6 = AlphaBetaOrderedSolver(max_depth=6, evaluation_function=checkers_evaluation)
    agent_ab6.name = "AlphaBeta(d=6)"
    
    # MCTS agent
    # Checkers is highly tactical. MCTS might struggle against Alpha-Beta without domain knowledge,
    # but let's test it with 1000 simulations!
    agent_mcts = MCTSSolver(num_simulations=1000)
    agent_mcts.name = "MCTS(1000)"
    
    agents = [agent_random, agent_ab4, agent_ab6, agent_mcts]
    
    # Run a small tournament. 
    # Checkers games can easily last 50-80 moves, making this a rigorous test of engine efficiency!
    tournament = Tournament(create_checkers, agents)
    tournament.run_tournament(games_per_matchup=2)

if __name__ == "__main__":
    main()
