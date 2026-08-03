from typing import Any, Dict, List
import math

class MCTSNode:
    def __init__(self, state: Any, parent: 'MCTSNode' = None, action_taken: Any = None):
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        
        self.children: Dict[Any, 'MCTSNode'] = {}
        self.visits = 0
        self.wins = 0.0
        
        # Untried actions are initialized upon node creation
        self.untried_actions: List[Any] = state.get_legal_actions()
        
    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0
        
    def is_terminal(self) -> bool:
        return self.state.is_terminal()
        
    def get_best_child(self, exploration_constant: float = math.sqrt(2)) -> 'MCTSNode':
        """Selects the child with the highest Upper Confidence Bound (UCT)."""
        best_child = None
        best_score = float('-inf')
        
        for child in self.children.values():
            # UCT Formula: (wins / visits) + C * sqrt(ln(parent_visits) / visits)
            exploitation = child.wins / child.visits
            exploration = exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
            uct_score = exploitation + exploration
            
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
                
        return best_child
