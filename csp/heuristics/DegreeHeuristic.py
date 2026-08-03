from typing import Dict, Any, List
from csp.CSPProblem import CSPProblem

def mrv_with_degree_heuristic(assignment: Dict[Any, Any], csp: CSPProblem, current_domains: Dict[Any, List[Any]]) -> Any:
    """
    MRV heuristic with Degree Heuristic as a tie-breaker.
    Selects the unassigned variable with the fewest legal values in its current domain.
    If there is a tie, selects the variable involved in the most constraints with other unassigned variables.
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    
    if not unassigned:
        return None
        
    # Find the minimum domain size
    min_size = min(len(current_domains[v]) for v in unassigned)
    
    # Get all variables that have this minimum domain size
    mrv_candidates = [v for v in unassigned if len(current_domains[v]) == min_size]
    
    if len(mrv_candidates) == 1:
        return mrv_candidates[0]
        
    # Tie-breaker: Degree Heuristic
    # Count how many constraints each candidate is involved in with OTHER unassigned variables.
    def calculate_degree(var):
        degree = 0
        for constraint in csp.constraints[var]:
            for other_var in constraint.variables:
                if other_var != var and other_var in unassigned:
                    degree += 1
        return degree
        
    # We want to MAXIMIZE the degree to break ties
    return max(mrv_candidates, key=calculate_degree)
