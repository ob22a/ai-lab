from csp.Backjumping import BackjumpingSolver
from csp.Backtracking import unassigned_variable_default, order_domain_values_default, inference_default
from csp.CSPProblem import CSPProblem
from typing import Dict, Any, List, Callable
import copy

class CBJSolver(BackjumpingSolver):
    """
    Conflict-Directed Backjumping (CBJ) Solver.
    When a variable fails and jumps back to a target variable, it merges its own 
    conflict set into the target variable's conflict set. This allows the target 
    variable to remember the reasons why future variables failed, preventing it 
    from making the same mistakes if it jumps back further.
    """
    def __init__(self, problem: CSPProblem,
                 select_unassigned_variable: Callable = unassigned_variable_default,
                 order_domain_values: Callable = order_domain_values_default,
                 inference: Callable = inference_default):
        super().__init__(problem, select_unassigned_variable, order_domain_values, inference)

    def solve_jump(self, assignment: Dict[Any, Any], current_domains: Dict[Any, List[Any]]) -> Any:
        # We override solve_jump to add the conflict set merging logic
        if len(assignment) == len(self.problem.variables):
            return assignment

        var = self.select_unassigned_variable(assignment, self.problem, current_domains)
        self.assignment_order.append(var)
        
        for value in self.order_domain_values(var, assignment, self.problem, current_domains):
            self.nodes_expanded += 1
            
            is_valid = True
            for constraint in self.problem.constraints[var]:
                assignment[var] = value
                if not constraint.is_satisfied(assignment):
                    is_valid = False
                    for neighbor in constraint.variables:
                        if neighbor != var and neighbor in assignment:
                            self.conflict_sets[var].add(neighbor)
                del assignment[var]
                
                if not is_valid:
                    break
            
            if is_valid:
                assignment[var] = value
                local_domains = copy.deepcopy(current_domains)
                local_domains[var] = [value]
                
                inferences_succeeded = self.inference(self.problem, var, value, assignment, local_domains)
                
                if inferences_succeeded:
                    result = self.solve_jump(assignment, local_domains)
                    
                    if isinstance(result, dict):
                        return result
                        
                    jump_target = result
                    
                    if jump_target is not None:
                        if jump_target != var:
                            # We are jumping OVER this variable!
                            del assignment[var]
                            self.assignment_order.pop()
                            return jump_target
                            
                        # If jump_target == var, we stop jumping.
                        # CBJ LOGIC: The child jumped back to us. Its conflict set was already 
                        # merged into ours when it failed (see below).
                else:
                    for neighbor in self.problem.constraints[var]:
                        for n in neighbor.variables:
                            if n != var and n in assignment:
                                self.conflict_sets[var].add(n)
                
                if var in assignment:
                    del assignment[var]

        self.assignment_order.pop()
        
        if not self.conflict_sets[var]:
            return None
            
        jump_target = None
        jump_index = -1
        
        for conflict_var in self.conflict_sets[var]:
            if conflict_var in self.assignment_order:
                idx = self.assignment_order.index(conflict_var)
                if idx > jump_index:
                    jump_index = idx
                    jump_target = conflict_var
                    
        # --- CBJ CORE LOGIC ---
        # Before returning jump_target, merge var's conflict_set into jump_target's conflict_set
        if jump_target is not None:
            self.conflict_sets[jump_target].update(self.conflict_sets[var])
            self.conflict_sets[jump_target].remove(jump_target) # Remove itself
            
        return jump_target
