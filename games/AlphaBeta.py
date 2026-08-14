from typing import Any
from games.GameState import GameState
from games.GameSolver import GameSolver

class AlphaBetaSolver(GameSolver):
    """
    Alpha-Beta Pruning Algorithm.
    Guarantees the exact same result as Minimax, but prunes branches that 
    cannot possibly affect the final decision. Supports optional max_depth limit.
    """
    def __init__(self, max_depth: int = -1):
        super().__init__()
        self.max_depth = max_depth
    
    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 0
        self.root_player = state.get_current_player()
        
        best_value = float('-inf')
        best_action = None
        alpha = float('-inf')
        beta = float('inf')
        
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = self._min_value(child_state, alpha, beta, depth=1)
            
            if value > best_value:
                best_value = value
                best_action = action
                
            alpha = max(alpha, best_value)
            
        return best_action
        
    def _max_value(self, state: GameState, alpha: float, beta: float, depth: int = 0) -> float:
        self.nodes_expanded += 1
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
        if self.max_depth > 0 and depth >= self.max_depth:
            return state.get_utility(self.root_player)
            
        value = float('-inf')
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = max(value, self._min_value(child_state, alpha, beta, depth + 1))
            
            if value >= beta:
                return value
                
            alpha = max(alpha, value)
            
        return value
        
    def _min_value(self, state: GameState, alpha: float, beta: float, depth: int = 0) -> float:
        self.nodes_expanded += 1
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
        if self.max_depth > 0 and depth >= self.max_depth:
            return state.get_utility(self.root_player)
            
        value = float('inf')
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = min(value, self._max_value(child_state, alpha, beta, depth + 1))
            
            if value <= alpha:
                return value
                
            beta = min(beta, value)
            
        return value
