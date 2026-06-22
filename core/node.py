from dataclasses import dataclass
from typing import Optional, Any
import itertools

_counter = itertools.count()

@dataclass
class Node:
    state: Any
    parent: Optional["Node"] = None
    action: Optional[Any] = None
    path_cost: float = 0.0
    
    def __post_init__(self):
        self._id = next(_counter)
        
    def __lt__(self, other):
        return self._id < other._id
    
    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1