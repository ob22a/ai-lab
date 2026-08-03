from abc import ABC, abstractmethod
from typing import Any
from games.GameState import GameState

class GameSolver(ABC):
    """
    Abstract Base Class for Game Solvers/Agents.
    """
    def __init__(self):
        self.nodes_expanded = 0
        
    @abstractmethod
    def get_best_action(self, state: GameState) -> Any:
        """
        Given the current GameState, computes and returns the best action 
        for the player whose turn it currently is.
        """
        pass
