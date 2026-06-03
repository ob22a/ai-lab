from dataclasses import dataclass

@dataclass
class Node:
    state: any
    parent: any
    action: any
    path_cost: float
    depth: int 