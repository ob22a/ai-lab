from typing import Any

class KillerMoves:
    """
    Killer Move Heuristic.
    Stores the move that recently caused a cutoff at a specific depth in the search tree.
    When exploring a new node at that same depth, we evaluate the killer move first,
    hoping it causes another cutoff.
    """
    def __init__(self, num_killers_per_depth: int = 2):
        self.num_killers = num_killers_per_depth
        # Dictionary mapping depth -> list of killer actions
        self.table = {}
        
    def store_killer(self, depth: int, action: Any):
        if depth not in self.table:
            self.table[depth] = []
            
        killers = self.table[depth]
        
        # Avoid duplicates
        if action in killers:
            return
            
        # Add to the front (most recent killer)
        killers.insert(0, action)
        
        # Keep only the top N killers
        if len(killers) > self.num_killers:
            killers.pop()
            
    def get_killers(self, depth: int) -> list:
        return self.table.get(depth, [])
