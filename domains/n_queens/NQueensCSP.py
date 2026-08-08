from typing import Dict, Any
from csp.CSPProblem import CSPProblem, Constraint

class NQueensConstraint(Constraint):
    """
    Constraint between two queens to ensure they do not attack each other.
    """
    def __init__(self, row1: int, row2: int):
        super().__init__([row1, row2])
        self.row1 = row1
        self.row2 = row2

    def is_satisfied(self, assignment: Dict[Any, Any]) -> bool:
        if self.row1 not in assignment or self.row2 not in assignment:
            return True
            
        col1 = assignment[self.row1]
        col2 = assignment[self.row2]
        
        # Check same column
        if col1 == col2:
            return False
            
        # Check diagonal
        if abs(self.row1 - self.row2) == abs(col1 - col2):
            return False
            
        return True


class NQueensCSP(CSPProblem):
    """
    N-Queens formulated as a Constraint Satisfaction Problem.
    Variables = rows (0 to N-1)
    Domains = columns (0 to N-1)
    Constraints = NQueensConstraint between all pairs of rows
    """
    def __init__(self, n: int, break_symmetry: bool = False):
        self.n = n
        variables = list(range(n))
        domains = {var: list(range(n)) for var in variables}
        
        # Symmetry breaking: restrict first row to left half of board (breaks vertical reflection symmetry)
        if break_symmetry and n > 0:
            domains[0] = list(range((n + 1) // 2))
            
        super().__init__(variables, domains)
        
        # Add binary constraints for all pairs of rows
        for i in range(n):
            for j in range(i + 1, n):
                self.add_constraint(NQueensConstraint(i, j))

    def count_conflicts(self, assignment: Dict[Any, Any]) -> int:
        """
        Counts the number of pairwise queen attacking conflicts in the given assignment.
        """
        conflicts = 0
        assigned_rows = [r for r in range(self.n) if r in assignment]
        for idx in range(len(assigned_rows)):
            for jdx in range(idx + 1, len(assigned_rows)):
                r1 = assigned_rows[idx]
                r2 = assigned_rows[jdx]
                c1 = assignment[r1]
                c2 = assignment[r2]
                if c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                    conflicts += 1
        return conflicts

