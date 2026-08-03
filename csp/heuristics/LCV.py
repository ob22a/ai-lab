from typing import Dict, Any, List
from csp.CSPProblem import CSPProblem

def lcv(var: Any, assignment: Dict[Any, Any], csp: CSPProblem, current_domains: Dict[Any, List[Any]]) -> List[Any]:
    """
    Least Constraining Value (LCV) heuristic.
    Orders the domain values for the selected variable by evaluating how many options 
    they eliminate for neighboring unassigned variables.
    Prefers values that eliminate the fewest options.
    """
    def count_eliminated(value):
        eliminated = 0
        # Temporarily assign to see the impact
        assignment[var] = value
        
        for constraint in csp.constraints[var]:
            for neighbor in constraint.variables:
                if neighbor != var and neighbor not in assignment:
                    # Check how many values in neighbor's domain would be eliminated
                    for neighbor_value in current_domains[neighbor]:
                        assignment[neighbor] = neighbor_value
                        if not constraint.is_satisfied(assignment):
                            eliminated += 1
                        del assignment[neighbor]
                        
        del assignment[var]
        return eliminated

    # Sort the values based on how many options they eliminate (ascending)
    return sorted(current_domains[var], key=count_eliminated)
