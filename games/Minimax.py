from typing import Any, Tuple
from games.GameState import GameState
from games.GameSolver import GameSolver

class MinimaxSolver(GameSolver):
    """
    Pure Minimax Algorithm.
    Assumes a zero-sum, two-player perfect-information game.
    Evaluates the entire game tree down to the terminal states.
    """
    
    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 0
        self.root_player = state.get_current_player()
        
        # We are at the root, so we act as the MAX player (maximizing root_player's utility)
        best_value = float('-inf')
        best_action = None
        
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            # The next turn will be MIN (the opponent) trying to minimize root_player's utility
            value = self._min_value(child_state)
            
            if value > best_value:
                best_value = value
                best_action = action
                
        return best_action
        
    def _max_value(self, state: GameState) -> float:
        self.nodes_expanded += 1
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
            
        value = float('-inf')
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = max(value, self._min_value(child_state))
            
        return value
        
    def _min_value(self, state: GameState) -> float:
        self.nodes_expanded += 1
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
            
        value = float('inf')
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = min(value, self._max_value(child_state))
            
        return value
