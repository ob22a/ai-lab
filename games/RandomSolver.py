import random
from typing import Any
from games.GameState import GameState
from games.GameSolver import GameSolver

class RandomSolver(GameSolver):
    """
    A baseline agent that chooses actions completely at random.
    Useful for benchmarking intelligent agents.
    """
    def __init__(self, name: str = "Random"):
        super().__init__()
        self.name = name
        
    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 1
        actions = state.get_legal_actions()
        if not actions:
            return None
        return random.choice(actions)
