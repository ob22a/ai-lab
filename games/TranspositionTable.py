from enum import Enum
from typing import Tuple, Any

class TTFlag(Enum):
    EXACT = 0
    LOWER_BOUND = 1 # Beta cutoff (value is at least X)
    UPPER_BOUND = 2 # Alpha cutoff (value is at most X)

class TranspositionTable:
    """
    Stores previously evaluated board states to avoid redundant search.
    """
    def __init__(self):
        # Maps zobrist_hash -> (depth, score, flag)
        self.table = {}
        self.hits = 0
        self.lookups = 0
        
    def lookup(self, state_hash: int, depth: int, alpha: float, beta: float) -> Tuple[bool, float]:
        """
        Looks up a state in the table.
        Returns (True, score) if a valid cached score can be used.
        Returns (False, 0.0) otherwise.
        """
        self.lookups += 1
        if state_hash in self.table:
            cached_depth, score, flag = self.table[state_hash]
            
            # We can only use the cached score if the cached search was at least
            # as deep as our current required search depth.
            if cached_depth >= depth:
                if flag == TTFlag.EXACT:
                    self.hits += 1
                    return True, score
                elif flag == TTFlag.LOWER_BOUND and score >= beta:
                    self.hits += 1
                    return True, score
                elif flag == TTFlag.UPPER_BOUND and score <= alpha:
                    self.hits += 1
                    return True, score
                    
        return False, 0.0
        
    def store(self, state_hash: int, depth: int, score: float, flag: TTFlag):
        """
        Stores a state in the table. Overwrites existing entries if the new
        search is deeper (more accurate).
        """
        if state_hash not in self.table or self.table[state_hash][0] <= depth:
            self.table[state_hash] = (depth, score, flag)
            
    def clear(self):
        self.table.clear()
        self.hits = 0
        self.lookups = 0
