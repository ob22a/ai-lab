from typing import Any
from games.GameState import GameState
from games.GameSolver import GameSolver

class AlphaBetaSolver(GameSolver):
    """
    Alpha-Beta Pruning Algorithm.
    Guarantees the exact same result as Minimax, but prunes branches that 
    cannot possibly affect the final decision.
    """
    
    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 0
        self.root_player = state.get_current_player()
        
        best_value = float('-inf')
        best_action = None
        alpha = float('-inf')
        beta = float('inf')
        
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = self._min_value(child_state, alpha, beta)
            
            if value > best_value:
                best_value = value
                best_action = action
                
            alpha = max(alpha, best_value)
            
        return best_action
        
    def _max_value(self, state: GameState, alpha: float, beta: float) -> float:
        self.nodes_expanded += 1
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
            
        value = float('-inf')
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = max(value, self._min_value(child_state, alpha, beta))
            
            if value >= beta:
                # Beta Cutoff
                # The MIN player above us already has a guaranteed path that is better (lower)
                # than this value. They will never let us get here.
                return value
                
            alpha = max(alpha, value)
            
        return value
        
    def _min_value(self, state: GameState, alpha: float, beta: float) -> float:
        self.nodes_expanded += 1
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
            
        value = float('inf')
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = min(value, self._max_value(child_state, alpha, beta))
            
            if value <= alpha:
                # Alpha Cutoff
                # The MAX player above us already has a guaranteed path that is better (higher)
                # than this value. They will never let us get here.
                return value
                
            beta = min(beta, value)
            
        return value
