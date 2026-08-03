from typing import Dict, Any, List
from csp.CSPProblem import CSPProblem

def forward_checking(csp: CSPProblem, var: Any, value: Any, assignment: Dict[Any, Any], current_domains: Dict[Any, List[Any]]) -> bool:
    """
    Forward Checking Inference.
    Whenever a variable X is assigned a value, Forward Checking looks at all 
    unassigned variables Y that are connected to X by a constraint. 
    It removes any values from Y's domain that are inconsistent with X's assignment.
    If Y's domain becomes empty, it returns False (failure).
    """
    for constraint in csp.constraints[var]:
        for neighbor in constraint.variables:
            if neighbor != var and neighbor not in assignment:
                # We need to filter the neighbor's domain
                valid_values = []
                
                # Check each remaining value in neighbor's domain
                for neighbor_val in current_domains[neighbor]:
                    assignment[neighbor] = neighbor_val
                    if constraint.is_satisfied(assignment):
                        valid_values.append(neighbor_val)
                    del assignment[neighbor]
                
                # Update neighbor's domain in-place
                current_domains[neighbor] = valid_values
                
                # If domain is empty, we hit a dead end, return failure immediately
                if not current_domains[neighbor]:
                    return False
                    
    return True
