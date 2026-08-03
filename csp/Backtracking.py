from csp.CSPSolver import CSPSolver
from typing import Dict, Any


class BacktrackingSolver(CSPSolver):
    """
    Classic Depth-First Search Backtracking solver for CSPs.
    """
    def solve(self) -> Dict[Any, Any]:
        result = self.backtrack(self.assignment)
        if result is None:
            self.status = "FAILURE"
        else:
            self.status = "SUCCESS"
        return result

    def backtrack(self, assignment: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Recursive backtracking algorithm.
        """
        # If assignment is complete, return it
        if len(assignment) == len(self.problem.variables):
            return assignment

        # Select unassigned variable
        unassigned = [v for v in self.problem.variables if v not in assignment]
        var = unassigned[0] # Naive variable ordering

        for value in self.problem.domains[var]: # Naive value ordering
            self.nodes_expanded += 1
            if self.problem.is_consistent(var, value, assignment):
                assignment[var] = value
                
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                
                # Backtrack
                del assignment[var]

        return None
