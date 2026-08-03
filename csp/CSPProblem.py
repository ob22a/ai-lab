from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, List, Tuple

V = TypeVar('V') # Variable type
D = TypeVar('D') # Domain value type

class Constraint(Generic[V, D], ABC):
    """Base class for all constraints."""
    def __init__(self, variables: List[V]):
        self.variables = variables

    @abstractmethod
    def is_satisfied(self, assignment: Dict[V, D]) -> bool:
        """Check if the constraint is satisfied given the current assignment."""
        pass


class CSPProblem(Generic[V, D]):
    """
    A Constraint Satisfaction Problem.
    Consists of variables, domains for those variables, and constraints.
    """
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]):
        self.variables = variables
        self.domains = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        for v in self.variables:
            self.constraints[v] = []
            if v not in self.domains:
                raise ValueError("Every variable must have a domain assigned to it.")

    def add_constraint(self, constraint: Constraint[V, D]):
        for v in constraint.variables:
            if v not in self.variables:
                raise ValueError("Variable in constraint not in CSP")
            self.constraints[v].append(constraint)

    def is_consistent(self, var: V, value: D, assignment: Dict[V, D]) -> bool:
        """
        Check if assigning `value` to `var` is consistent with the current assignment.
        """
        for constraint in self.constraints[var]:
            # Temporarily assign the value to check constraint
            assignment[var] = value
            satisfied = constraint.is_satisfied(assignment)
            del assignment[var]
            if not satisfied:
                return False
        return True
