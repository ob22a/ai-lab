from typing import Dict, Any, List
from csp.CSPProblem import CSPProblem

def mrv(assignment: Dict[Any, Any], csp: CSPProblem, current_domains: Dict[Any, List[Any]]) -> Any:
    """
    Minimum Remaining Values (MRV) heuristic.
    Selects the unassigned variable with the fewest legal values in its current domain.
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    
    if not unassigned:
        return None
        
    # Find variable with min domain size
    return min(unassigned, key=lambda v: len(current_domains[v]))
