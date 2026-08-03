from csp.CSPSolver import CSPSolver
from csp.CSPProblem import CSPProblem
from typing import Dict, Any, Callable, List
import copy


def unassigned_variable_default(assignment: Dict[Any, Any], csp: CSPProblem, current_domains: Dict[Any, List[Any]]) -> Any:
    """Default: pick the first unassigned variable."""
    unassigned = [v for v in csp.variables if v not in assignment]
    return unassigned[0] if unassigned else None

def order_domain_values_default(var: Any, assignment: Dict[Any, Any], csp: CSPProblem, current_domains: Dict[Any, List[Any]]) -> List[Any]:
    """Default: return the domain values in order."""
    return current_domains[var]

def inference_default(csp: CSPProblem, var: Any, value: Any, assignment: Dict[Any, Any], current_domains: Dict[Any, List[Any]]) -> bool:
    """Default: no inference, always return True (no failure)."""
    return True


class BacktrackingSolver(CSPSolver):
    """
    Depth-First Search Backtracking solver for CSPs, supporting extensible heuristics and inference.
    """
    def __init__(self, problem: CSPProblem, 
                 select_unassigned_variable: Callable = unassigned_variable_default,
                 order_domain_values: Callable = order_domain_values_default,
                 inference: Callable = inference_default):
        super().__init__(problem)
        self.select_unassigned_variable = select_unassigned_variable
        self.order_domain_values = order_domain_values
        self.inference = inference
        self.on_assign = None
        self.on_unassign = None

    def solve(self) -> Dict[Any, Any]:
        # Initialize current domains with full domains
        current_domains = {var: list(values) for var, values in self.problem.domains.items()}
        result = self.backtrack(self.assignment, current_domains)
        if result is None:
            self.status = "FAILURE"
        else:
            self.status = "SUCCESS"
        return result

    def backtrack(self, assignment: Dict[Any, Any], current_domains: Dict[Any, List[Any]]) -> Dict[Any, Any]:
        if len(assignment) == len(self.problem.variables):
            return assignment

        var = self.select_unassigned_variable(assignment, self.problem, current_domains)
        
        for value in self.order_domain_values(var, assignment, self.problem, current_domains):
            self.nodes_expanded += 1
            if self.problem.is_consistent(var, value, assignment):
                assignment[var] = value
                if self.on_assign:
                    self.on_assign(var, value, assignment)
                
                # We must clone current_domains because inference might prune it
                # We could track removals instead to be more memory efficient, but deepcopy is simple.
                local_domains = copy.deepcopy(current_domains)
                local_domains[var] = [value]
                
                # Run inference (e.g. Forward Checking)
                inferences_succeeded = self.inference(self.problem, var, value, assignment, local_domains)
                
                if inferences_succeeded:
                    result = self.backtrack(assignment, local_domains)
                    if result is not None:
                        return result
                
                # Backtrack
                del assignment[var]
                if self.on_unassign:
                    self.on_unassign(var, assignment)

        return None
