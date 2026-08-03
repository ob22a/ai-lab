from typing import Any

class HistoryHeuristic:
    """
    History Heuristic.
    Maintains a global score for every possible action across the entire search tree.
    When a move causes a cutoff, its score is increased (often weighted by depth).
    Moves with higher history scores are evaluated first.
    """
    def __init__(self):
        # Maps action -> score
        self.table = {}
        
    def increment(self, action: Any, depth: int):
        """
        Increment the score of the action.
        A common weighting scheme is depth^2, giving much higher weight to cutoffs
        found near the root of the tree.
        """
        weight = depth * depth
        if action not in self.table:
            self.table[action] = 0
        self.table[action] += weight
        
    def get_score(self, action: Any) -> float:
        return self.table.get(action, 0.0)
