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
    def __init__(self, n: int):
        variables = list(range(n))
        domains = {var: list(range(n)) for var in variables}
        super().__init__(variables, domains)
        
        # Add binary constraints for all pairs of rows
        for i in range(n):
            for j in range(i + 1, n):
                self.add_constraint(NQueensConstraint(i, j))
