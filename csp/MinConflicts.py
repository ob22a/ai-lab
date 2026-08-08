from csp.CSPSolver import CSPSolver
from csp.CSPProblem import CSPProblem
from typing import Dict, Any, List, Optional
import random


class MinConflictsSolver(CSPSolver):
    """
    Min-Conflicts Local Search algorithm for CSPs.
    Starts with a complete, random (and likely inconsistent) assignment.
    Iteratively repairs the assignment by selecting a conflicted variable and
    assigning it the value that minimizes the number of conflicts.
    """
    def __init__(self, problem: CSPProblem, max_steps: int = 100000):
        super().__init__(problem)
        self.max_steps = max_steps
        self.on_assign = None
        self.on_unassign = None

    def solve(self) -> Optional[Dict[Any, Any]]:
        self.reset()
        
        # 1. Generate an initial complete random assignment
        for var in self.problem.variables:
            val = random.choice(self.problem.domains[var])
            self.assignment[var] = val
            if self.on_assign:
                self.on_assign(var, val, self.assignment)
            
        for step in range(self.max_steps):
            self.nodes_expanded += 1
            
            # 2. Find all conflicted variables
            conflicted_vars = []
            for var in self.problem.variables:
                if self._count_conflicts(var, self.assignment[var], self.assignment) > 0:
                    conflicted_vars.append(var)
                    
            if not conflicted_vars:
                # No conflicts! We found a solution.
                self.status = "SUCCESS"
                return self.assignment
                
            # 3. Pick a random conflicted variable
            var = random.choice(conflicted_vars)
            
            # 4. Find the value that minimizes conflicts
            min_conflicts = float('inf')
            best_values = []
            
            for value in self.problem.domains[var]:
                conflicts = self._count_conflicts(var, value, self.assignment)
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_values = [value]
                elif conflicts == min_conflicts:
                    best_values.append(value)
                    
            # Break ties randomly
            best_val = random.choice(best_values)
            self.assignment[var] = best_val
            if self.on_assign:
                self.on_assign(var, best_val, self.assignment)
            
        self.status = "FAILURE"
        return None
        
    def _count_conflicts(self, var: Any, value: Any, assignment: Dict[Any, Any]) -> int:
        """Counts how many constraints are violated if `var` is assigned `value`."""
        conflicts = 0
        
        # Temporarily assign to test
        original_val = assignment.get(var)
        assignment[var] = value
        
        for constraint in self.problem.constraints[var]:
            if not constraint.is_satisfied(assignment):
                conflicts += 1
                
        # Restore
        if original_val is not None:
            assignment[var] = original_val
        else:
            del assignment[var]
            
        return conflicts
