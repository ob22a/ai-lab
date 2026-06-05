from dataclasses import dataclass, field
from typing import Any

@dataclass
class Result:
    success: bool

    solution: Any = None

    runtime: float = 0.0

    nodes_expanded: int = 0
    nodes_generated: int = 0

    solution_depth: int = 0
    path_cost: float = 0

    max_frontier_size: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        return (
            f"\nSuccess: {self.success}\n"
            f"Runtime: {self.runtime:.5f}s\n"
            f"Nodes expanded: {self.nodes_expanded}\n"
            f"Nodes generated: {self.nodes_generated}\n"
            f"Solution depth: {self.solution_depth}\n"
            f"Path cost: {self.path_cost}\n"
            f"Max frontier size: {self.max_frontier_size}"
        )