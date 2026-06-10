from dataclasses import dataclass,field
from typing import Optional

@dataclass(order=True)
class Node:
    path_cost: float # This makes comparison based on path cost first 
    
    state: tuple[int, int] = field(compare=False)
    parent: Optional["Node"] = field(compare=False)
    action: Optional[object] = field(compare=False)
    
    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1