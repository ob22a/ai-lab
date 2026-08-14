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

    def reset(self):
        """
        Resets the solver internal state for a clean re-run.
        """
        self.status = "RUNNING"
        self.nodes_expanded = 0
        self.assignment = {}

    def solve(self) -> Dict[Any, Any]:
        """
        Runs the solver and returns the completed assignment, or None if no solution exists.
        """
        import time
        t0 = time.time()
        assignment = self._solve_impl()
        dur = time.time() - t0
        try:
            from utils.auto_logger import auto_log_csp
            auto_log_csp(self, assignment, dur)
        except Exception:
            pass
        return assignment

    @abstractmethod
    def _solve_impl(self) -> Dict[Any, Any]:
        pass
