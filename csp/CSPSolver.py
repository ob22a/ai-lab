from abc import ABC, abstractmethod
from typing import Dict, Any
from csp.CSPProblem import CSPProblem


class CSPSolver(ABC):
    """
    Base class for CSP solvers.
    """
    def __init__(self, problem: CSPProblem):
        self.problem = problem
        self.status = "RUNNING"
        self.nodes_expanded = 0
        self.assignment: Dict[Any, Any] = {}

    @abstractmethod
    def solve(self) -> Dict[Any, Any]:
        """
        Runs the solver and returns the completed assignment, or None if no solution exists.
        """
        pass
