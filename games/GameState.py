from abc import ABC, abstractmethod
from typing import List, Any

class GameState(ABC):
    """
    Abstract Base Class for Adversarial Game States.
    Unlike standard Search and CSPs where we often mutate a single state object,
    Game Trees frequently branch deeply and simultaneously. 
    It is standard practice for apply_action() to return a *new* GameState object.
    """
    
    @abstractmethod
    def get_legal_actions(self) -> List[Any]:
        """Returns a list of legal actions available to the current player."""
        pass
        
    @abstractmethod
    def apply_action(self, action: Any) -> 'GameState':
        """
        Applies the action to the current state and returns a NEW GameState object
        representing the state of the game after the action.
        """
        pass
        
    @abstractmethod
    def is_terminal(self) -> bool:
        """Returns True if the game is over, False otherwise."""
        pass
        
    @abstractmethod
    def get_utility(self, player: Any) -> float:
        """
        Returns the utility of this state from the perspective of the specified player.
        Usually called only on terminal states (e.g., +1 for win, -1 for loss, 0 for draw).
        """
        pass
        
    @abstractmethod
    def get_current_player(self) -> Any:
        """Returns the player whose turn it is to move."""
        pass
