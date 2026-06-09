from dataclasses import dataclass
from typing import Optional

@dataclass(order=True)
class Node:
    state: tuple[int, int]
    parent: Optional["Node"]
    action: Optional[object]
    path_cost: float
    
    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1