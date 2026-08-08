from typing import Dict, Any, List, Optional, Callable, Set
import copy

from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default, inference_default
from csp.CSPProblem import CSPProblem


class SymmetricBacktrackingSolver(BacktrackingSolver):
    """
    Backtracking Solver equipped with Symmetry Breaking.
    
    Supports:
    1. Value Symmetry Breaking: If multiple domain values have not yet been used in the 
       current partial assignment, branching on more than ONE unused value creates 
       isomorphic duplicate search subtrees. This solver prunes redundant unused values.
    2. Custom Symmetry Condition / Filter: A user-defined predicate (assignment, var, val) -> bool
       to enforce geometric/variable symmetry cuts (e.g., N-Queens reflection/rotation cuts).
    """
    def __init__(self, problem: CSPProblem,
                 select_unassigned_variable: Callable = unassigned_variable_default,
                 order_domain_values: Callable = order_domain_values_default,
                 inference: Callable = inference_default,
                 value_symmetry: bool = False,
                 symmetry_filter: Optional[Callable[[Dict[Any, Any], Any, Any], bool]] = None):
        super().__init__(problem, select_unassigned_variable, order_domain_values, inference)
        self.value_symmetry = value_symmetry
        self.symmetry_filter = symmetry_filter
        self.symmetric_branches_pruned = 0

    def backtrack(self, assignment: Dict[Any, Any], current_domains: Dict[Any, List[Any]]) -> Optional[Dict[Any, Any]]:
        if len(assignment) == len(self.problem.variables):
            return assignment

        var = self.select_unassigned_variable(assignment, self.problem, current_domains)
        
        # Track used values in current assignment for value symmetry breaking
        used_values = set(assignment.values()) if self.value_symmetry else set()
        seen_first_unused = False
        
        for value in self.order_domain_values(var, assignment, self.problem, current_domains):
            # 1. Check custom symmetry filter
            if self.symmetry_filter is not None:
                if not self.symmetry_filter(assignment, var, value):
                    self.symmetric_branches_pruned += 1
                    continue

            # 2. Check value symmetry: only try the first unassigned value
            if self.value_symmetry:
                if value not in used_values:
                    if seen_first_unused:
                        # Symmetric duplicate of an already tried unused value
                        self.symmetric_branches_pruned += 1
                        continue
                    seen_first_unused = True

            self.nodes_expanded += 1
            if self.problem.is_consistent(var, value, assignment):
                assignment[var] = value
                if self.on_assign:
                    self.on_assign(var, value, assignment)
                
                local_domains = copy.deepcopy(current_domains)
                local_domains[var] = [value]
                
                inferences_succeeded = self.inference(self.problem, var, value, assignment, local_domains)
                
                if inferences_succeeded:
                    result = self.backtrack(assignment, local_domains)
                    if result is not None:
                        return result
                
                del assignment[var]
                if self.on_unassign:
                    self.on_unassign(var, assignment)

        return None
