from typing import Dict, List, Any
from csp.CSPProblem import CSPProblem, Constraint


class NotEqualConstraint(Constraint):
    """
    A binary constraint specifying that two variables must have different values.
    """
    def __init__(self, var1: Any, var2: Any):
        super().__init__([var1, var2])
        self.var1 = var1
        self.var2 = var2

    def is_satisfied(self, assignment: Dict[Any, Any]) -> bool:
        # If either variable is unassigned, the constraint is not yet violated
        if self.var1 not in assignment or self.var2 not in assignment:
            return True
        return assignment[self.var1] != assignment[self.var2]


class MapColoringCSP(CSPProblem):
    """
    Australia Map Coloring CSP.
    """
    def __init__(self):
        variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
        domains = {var: ['Red', 'Green', 'Blue'] for var in variables}
        super().__init__(variables, domains)
        
        # Add constraints for adjacent regions
        self.add_constraint(NotEqualConstraint('WA', 'NT'))
        self.add_constraint(NotEqualConstraint('WA', 'SA'))
        self.add_constraint(NotEqualConstraint('NT', 'SA'))
        self.add_constraint(NotEqualConstraint('NT', 'Q'))
        self.add_constraint(NotEqualConstraint('SA', 'Q'))
        self.add_constraint(NotEqualConstraint('SA', 'NSW'))
        self.add_constraint(NotEqualConstraint('SA', 'V'))
        self.add_constraint(NotEqualConstraint('Q', 'NSW'))
        self.add_constraint(NotEqualConstraint('NSW', 'V'))
        # Tasmania ('T') is an island, so it has no adjacent regions and thus no constraints!
