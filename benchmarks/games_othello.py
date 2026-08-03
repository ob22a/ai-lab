from domains.othello.Othello import OthelloState
from domains.othello.OthelloEval import othello_evaluation
from games.RandomSolver import RandomSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver
from games.MCTS import MCTSSolver
from games.Tournament import Tournament

def create_othello():
    return OthelloState()

def main():
    print("Initializing Othello Agents...")
    
    agent_random = RandomSolver(name="Random")
    
    agent_ab4 = AlphaBetaOrderedSolver(max_depth=4, evaluation_function=othello_evaluation)
    agent_ab4.name = "AlphaBeta(d=4)"
    
    # Othello branching factor is manageable, so depth 6 is reasonable
    agent_ab6 = AlphaBetaOrderedSolver(max_depth=6, evaluation_function=othello_evaluation)
    agent_ab6.name = "AlphaBeta(d=6)"
    
    # MCTS using pure random simulations without heuristics often struggles in Othello 
    # because random playouts tend to flip huge swaths of the board randomly,
    # destroying the concept of positional "stability" that humans and heuristics use.
    agent_mcts = MCTSSolver(num_simulations=1000)
    agent_mcts.name = "MCTS(1000)"
    
    agents = [agent_random, agent_ab4, agent_ab6, agent_mcts]
    
    # Run a small tournament. 
    tournament = Tournament(create_othello, agents)
    tournament.run_tournament(games_per_matchup=2)

if __name__ == "__main__":
    main()
