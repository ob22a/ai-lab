from typing import Dict, Any, List
from collections import deque
from csp.CSPProblem import CSPProblem
from csp.inference.AC3 import ac3


def mac(csp: CSPProblem, var: Any, value: Any, assignment: Dict[Any, Any], current_domains: Dict[Any, List[Any]]) -> bool:
    """
    Maintaining Arc Consistency (MAC) inference.
    After a variable `var` is assigned `value`, we initialize the AC-3 queue with
    all arcs (Y, var) where Y is an unassigned neighbor of `var`.
    Then we run AC-3 to propagate constraints.
    Returns False if an inconsistency is found, True otherwise.
    """
    queue = deque()
    
    # Add arcs (Y, var) where Y is an unassigned neighbor of var
    for constraint in csp.constraints[var]:
        # MAC also assumes strictly binary constraints for standard AC-3 to work properly
        if len(constraint.variables) != 2:
            raise ValueError(f"MAC requires strictly binary constraints. Found constraint with {len(constraint.variables)} variables: {constraint.variables}")
            
        neighbor = constraint.variables[0] if constraint.variables[1] == var else constraint.variables[1]
        
        if neighbor not in assignment:
            queue.append((neighbor, var))
            
    # Run AC-3 with the initialized queue
    return ac3(csp, current_domains, queue=queue)
