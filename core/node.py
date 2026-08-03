from dataclasses import dataclass, field
from typing import Optional, Any
import itertools

_counter = itertools.count()


@dataclass
class Node:
    state: Any
    parent: Optional["Node"] = None
    action: Optional[Any] = None
    path_cost: float = 0.0
    depth: int = 0

    f_cost: float = 0

    actions: list = field(default_factory=list)
    actions_generated: bool = False
    successor_index: int = 0

    children: list["Node"] = field(default_factory=list)

    fully_expanded: bool = False
    forgotten_f: float = float("inf")
    expanded: bool = False

    forgotten_children: list = field(default_factory=list)

    def __post_init__(self):
        self._id = next(_counter)

        if self.parent is not None:
            self.depth = self.parent.depth + 1

    def __lt__(self, other):
        return (self.f_cost, -self.depth, self._id) < (
            other.f_cost,
            -other.depth,
            other._id
        )