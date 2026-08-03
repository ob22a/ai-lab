from typing import Dict, Any, List, Tuple
from csp.CSPProblem import CSPProblem
from collections import deque

def revise(csp: CSPProblem, Xi: Any, Xj: Any, current_domains: Dict[Any, List[Any]]) -> bool:
    """
    Makes Xi arc-consistent with Xj.
    Returns True if current_domains[Xi] was revised (a value was removed), False otherwise.
    """
    revised = False
    
    # We need to find constraints between Xi and Xj
    constraints_between = []
    for constraint in csp.constraints[Xi]:
        if len(constraint.variables) != 2:
            raise ValueError(f"AC-3 requires strictly binary constraints. Found constraint with {len(constraint.variables)} variables: {constraint.variables}")
        if Xj in constraint.variables:
            constraints_between.append(constraint)
            
    if not constraints_between:
        return False # No direct constraint between Xi and Xj
        
    valid_values = []
    for x in current_domains[Xi]:
        # Does there exist some y in current_domains[Xj] that satisfies all constraints_between?
        exists_valid_y = False
        for y in current_domains[Xj]:
            # Temporarily assign x and y to check consistency
            assignment = {Xi: x, Xj: y}
            
            # Check all constraints between them
            all_satisfied = True
            for constraint in constraints_between:
                if not constraint.is_satisfied(assignment):
                    all_satisfied = False
                    break
                    
            if all_satisfied:
                exists_valid_y = True
                break
                
        if exists_valid_y:
            valid_values.append(x)
        else:
            revised = True
            
    if revised:
        current_domains[Xi] = valid_values
        
    return revised


def ac3(csp: CSPProblem, current_domains: Dict[Any, List[Any]], queue: deque = None) -> bool:
    """
    Arc Consistency Algorithm #3.
    If queue is None, initializes with all arcs in the CSP.
    Returns False if an inconsistency is found (a domain becomes empty), True otherwise.
    """
    if queue is None:
        queue = deque()
        for var in csp.variables:
            for constraint in csp.constraints[var]:
                if len(constraint.variables) != 2:
                    raise ValueError(f"AC-3 requires strictly binary constraints. Found constraint with {len(constraint.variables)} variables: {constraint.variables}")
                
                # Get the other variable in the binary constraint
                other_var = constraint.variables[0] if constraint.variables[1] == var else constraint.variables[1]
                # Add both directed arcs (var, other_var) and (other_var, var)
                # But since we iterate over all vars and their constraints, we just add (var, other_var)
                queue.append((var, other_var))
                
    while queue:
        Xi, Xj = queue.popleft()
        if revise(csp, Xi, Xj, current_domains):
            if not current_domains[Xi]:
                return False # Domain is empty, inconsistency found
                
            # If Xi was revised, we must re-evaluate all arcs (Xk, Xi) where Xk is a neighbor of Xi (excluding Xj)
            for constraint in csp.constraints[Xi]:
                other_var = constraint.variables[0] if constraint.variables[1] == Xi else constraint.variables[1]
                if other_var != Xj:
                    queue.append((other_var, Xi))
                    
    return True
