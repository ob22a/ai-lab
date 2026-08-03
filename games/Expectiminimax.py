from typing import Any
from games.GameState import GameState
from games.GameSolver import GameSolver

class ExpectiminimaxSolver(GameSolver):
    """
    Expectiminimax Algorithm for Stochastic Games.
    Handles three node types:
    - MAX: Maximizes utility (Player 1)
    - MIN: Minimizes utility (Player 2)
    - CHANCE: Calculates Expected Value (Weighted Average) of random outcomes
    """
    
    def __init__(self, max_depth: int = -1, evaluation_function=None):
        super().__init__()
        self.max_depth = max_depth
        self.evaluation_function = evaluation_function
        
    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 0
        self.root_player = state.get_current_player()
        
        best_value = float('-inf')
        best_action = None
        
        for action in state.get_legal_actions():
            child_state = state.apply_action(action)
            value = self._expectiminimax(child_state, depth=1)
            
            if value > best_value:
                best_value = value
                best_action = action
                
        return best_action
        
    def _expectiminimax(self, state: GameState, depth: int) -> float:
        self.nodes_expanded += 1
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
            
        if self.max_depth != -1 and depth >= self.max_depth:
            if self.evaluation_function:
                return self.evaluation_function(state, self.root_player)
            return state.get_utility(self.root_player)
            
        current_player = state.get_current_player()
        
        if current_player == 0:
            # CHANCE NODE
            # Calculate Expected Value
            expected_value = 0.0
            outcomes = state.get_chance_outcomes()
            
            if not outcomes:
                return 0.0
                
            for action, probability in outcomes:
                child_state = state.apply_action(action)
                # Recursively evaluate the child
                child_value = self._expectiminimax(child_state, depth + 1)
                expected_value += (probability * child_value)
                
            return expected_value
            
        elif current_player == self.root_player:
            # MAX NODE
            value = float('-inf')
            for action in state.get_legal_actions():
                child_state = state.apply_action(action)
                value = max(value, self._expectiminimax(child_state, depth + 1))
            return value
            
        else:
            # MIN NODE
            value = float('inf')
            for action in state.get_legal_actions():
                child_state = state.apply_action(action)
                value = min(value, self._expectiminimax(child_state, depth + 1))
            return value
