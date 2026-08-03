import time
from typing import List, Callable, Dict
from games.GameState import GameState
from games.GameSolver import GameSolver

class Tournament:
    """
    Runs a Round-Robin tournament between a list of agents.
    """
    def __init__(self, game_state_factory: Callable[[], GameState], agents: List[GameSolver]):
        """
        :param game_state_factory: A function that returns a fresh starting GameState
        :param agents: A list of configured GameSolvers
        """
        self.game_state_factory = game_state_factory
        self.agents = agents
        
    def play_match(self, agent1: GameSolver, agent2: GameSolver, num_games: int) -> Dict[str, float]:
        """
        Plays num_games between agent1 and agent2.
        They swap who goes first exactly halfway through.
        """
        a1_wins = 0
        a2_wins = 0
        draws = 0
        a1_time = 0.0
        a2_time = 0.0
        
        for i in range(num_games):
            state = self.game_state_factory()
            
            # Swap who plays player 1 (MAX) vs player 2 (MIN)
            if i < num_games // 2:
                p1_agent = agent1
                p2_agent = agent2
                a1_plays_p1 = True
            else:
                p1_agent = agent2
                p2_agent = agent1
                a1_plays_p1 = False
                
            while not state.is_terminal():
                current_player = state.get_current_player()
                if current_player == 1:
                    start_time = time.time()
                    action = p1_agent.get_best_action(state)
                    elapsed = time.time() - start_time
                    if a1_plays_p1:
                        a1_time += elapsed
                    else:
                        a2_time += elapsed
                else:
                    start_time = time.time()
                    action = p2_agent.get_best_action(state)
                    elapsed = time.time() - start_time
                    if a1_plays_p1:
                        a2_time += elapsed
                    else:
                        a1_time += elapsed
                        
                state = state.apply_action(action)
                
            # Determine winner based on Player 1's utility
            # For standard games: > 0 means P1 won, < 0 means P2 won, == 0 means draw
            u = state.get_utility(player=1)
            if u > 0:
                if a1_plays_p1:
                    a1_wins += 1
                else:
                    a2_wins += 1
            elif u < 0:
                if a1_plays_p1:
                    a2_wins += 1
                else:
                    a1_wins += 1
            else:
                draws += 1
                
        # Calculate stats
        total = max(1, num_games)
        return {
            "a1_win_rate": (a1_wins / total) * 100,
            "a2_win_rate": (a2_wins / total) * 100,
            "draw_rate": (draws / total) * 100,
            "a1_avg_time": (a1_time / total),
            "a2_avg_time": (a2_time / total)
        }

    def run_tournament(self, games_per_matchup: int = 2):
        print(f"=== Running Tournament ({len(self.agents)} Agents) ===")
        print(f"Games per matchup: {games_per_matchup}\n")
        
        for i in range(len(self.agents)):
            for j in range(i + 1, len(self.agents)):
                a1 = self.agents[i]
                a2 = self.agents[j]
                
                # Give agents names if they don't have one
                name1 = getattr(a1, 'name', a1.__class__.__name__)
                name2 = getattr(a2, 'name', a2.__class__.__name__)
                
                print(f"Match: {name1} vs {name2}")
                results = self.play_match(a1, a2, games_per_matchup)
                
                print(f"  {name1} Win Rate: {results['a1_win_rate']:.1f}%")
                print(f"  {name2} Win Rate: {results['a2_win_rate']:.1f}%")
                print(f"  Draw Rate: {results['draw_rate']:.1f}%")
                print(f"  {name1} Avg Move Time: {results['a1_avg_time']:.4f}s")
                print(f"  {name2} Avg Move Time: {results['a2_avg_time']:.4f}s\n")
