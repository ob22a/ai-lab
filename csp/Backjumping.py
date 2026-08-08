from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default, inference_default
from csp.CSPProblem import CSPProblem
from typing import Dict, Any, List, Callable
import copy

class BackjumpingSolver(BacktrackingSolver):
    """
    Backjumping Solver.
    Maintains a conflict set for each variable.
    When a variable fails (runs out of valid values), it jumps back to the most 
    recently assigned variable in its conflict set, skipping innocent variables.
    """
    def __init__(self, problem: CSPProblem,
                 select_unassigned_variable: Callable = unassigned_variable_default,
                 order_domain_values: Callable = order_domain_values_default,
                 inference: Callable = inference_default):
        super().__init__(problem, select_unassigned_variable, order_domain_values, inference)
        # conflict_sets maps var -> set of previously assigned vars that conflicted with it
        self.conflict_sets: Dict[Any, set] = {v: set() for v in problem.variables}
        # To know which variable was "most recently assigned", we track the assignment sequence
        self.assignment_order: List[Any] = []

    def solve(self) -> Dict[Any, Any]:
        self.reset()
        self.conflict_sets = {v: set() for v in self.problem.variables}
        self.assignment_order = []
        current_domains = {var: list(values) for var, values in self.problem.domains.items()}
        
        # solve_jump returns either the solution dict, or a variable to jump back to (or None for failure)
        result = self.solve_jump(self.assignment, current_domains)
        if isinstance(result, dict):
            self.status = "SUCCESS"
            self.assignment = result
            return result
        else:
            self.status = "FAILURE"
            return None

    def solve_jump(self, assignment: Dict[Any, Any], current_domains: Dict[Any, List[Any]]) -> Any:
        if len(assignment) == len(self.problem.variables):
            return assignment

        var = self.select_unassigned_variable(assignment, self.problem, current_domains)
        self.assignment_order.append(var)
        
        # We must track conflicts for `var`
        # A conflict occurs when we try a value and it fails a constraint against a previous variable.
        # We'll build the conflict set dynamically.
        
        for value in self.order_domain_values(var, assignment, self.problem, current_domains):
            self.nodes_expanded += 1
            
            # Check constraints. If it fails, add the conflicting variable to var's conflict set.
            is_valid = True
            for constraint in self.problem.constraints[var]:
                # Temporarily assign to check
                assignment[var] = value
                if not constraint.is_satisfied(assignment):
                    is_valid = False
                    # Add all assigned variables in this constraint to our conflict set
                    for neighbor in constraint.variables:
                        if neighbor != var and neighbor in assignment:
                            self.conflict_sets[var].add(neighbor)
                del assignment[var]
                
                if not is_valid:
                    break # Failed, try next value
            
            if is_valid:
                assignment[var] = value
                
                local_domains = copy.deepcopy(current_domains)
                local_domains[var] = [value]
                
                inferences_succeeded = self.inference(self.problem, var, value, assignment, local_domains)
                
                if inferences_succeeded:
                    result = self.solve_jump(assignment, local_domains)
                    
                    if isinstance(result, dict):
                        return result # Solution found!
                        
                    # If it returned a variable to jump to...
                    jump_target = result
                    
                    if jump_target is not None:
                        if jump_target != var:
                            # We are jumping OVER this variable!
                            del assignment[var]
                            self.assignment_order.pop()
                            # Do NOT try other values for var, keep jumping up!
                            return jump_target
                            
                        # If jump_target == var, we stop jumping and just try the next value in the loop
                        # (We don't need to do anything, just let the loop continue)
                        
                else:
                    # Inference failed. Technically forward checking adds to conflicts, 
                    # but for basic backjumping we often just add all previously assigned neighbors.
                    for neighbor in self.problem.constraints[var]:
                        for n in neighbor.variables:
                            if n != var and n in assignment:
                                self.conflict_sets[var].add(n)
                
                # Backtrack assignment to try next value
                if var in assignment:
                    del assignment[var]

        # If we exhausted all values and failed, we must initiate a jump back!
        self.assignment_order.pop()
        
        if not self.conflict_sets[var]:
            return None # Nowhere to jump, complete failure
            
        # Find the most recently assigned variable in var's conflict set
        jump_target = None
        jump_index = -1
        
        for conflict_var in self.conflict_sets[var]:
            if conflict_var in self.assignment_order:
                idx = self.assignment_order.index(conflict_var)
                if idx > jump_index:
                    jump_index = idx
                    jump_target = conflict_var
                    
        return jump_target
