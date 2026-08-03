from typing import Dict, Any, List, Set
from csp.CSPProblem import CSPProblem, Constraint
from domains.map_coloring.MapColoring import NotEqualConstraint


class EquationConstraint(Constraint):
    """
    Global constraint that enforces sum(addends) == result.
    It only evaluates to False if ALL variables in the constraint have been assigned
    and the equation does not hold. Otherwise, it returns True (allowing search to proceed).
    """
    def __init__(self, addends: List[str], result: str, variables: List[str]):
        super().__init__(variables)
        self.addends = addends
        self.result = result

    def is_satisfied(self, assignment: Dict[Any, Any]) -> bool:
        # Check if all variables in the equation are assigned
        for var in self.variables:
            if var not in assignment:
                return True # Can't evaluate yet, assume valid for now
                
        def word_to_int(word: str) -> int:
            value = 0
            for char in word:
                value = value * 10 + assignment[char]
            return value
            
        sum_addends = sum(word_to_int(word) for word in self.addends)
        return sum_addends == word_to_int(self.result)


class CryptarithmeticCSP(CSPProblem):
    """
    A generic Cryptarithmetic CSP solver.
    Takes a list of addend words and a result word.
    Example: SEND + MORE = MONEY
    """
    def __init__(self, addends: List[str], result: str):
        self.addends = addends
        self.result = result
        
        # 1. Identify all unique variables (letters)
        unique_chars: Set[str] = set()
        for word in addends:
            for char in word:
                unique_chars.add(char)
        for char in result:
            unique_chars.add(char)
            
        variables = list(unique_chars)
        
        if len(variables) > 10:
            raise ValueError(f"Too many unique characters ({len(variables)}). Max 10 for digits 0-9.")
            
        # 2. Identify leading characters (cannot be zero)
        leading_chars: Set[str] = set()
        for word in addends:
            if len(word) > 1:
                leading_chars.add(word[0])
        if len(result) > 1:
            leading_chars.add(result[0])
            
        # 3. Setup domains
        domains = {}
        for var in variables:
            if var in leading_chars:
                domains[var] = list(range(1, 10))
            else:
                domains[var] = list(range(10))
                
        super().__init__(variables, domains)
        
        # 4. Add Constraints
        
        # 4a. AllDiff: Every letter must map to a unique digit
        # We decompose this into binary NotEqualConstraints
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                self.add_constraint(NotEqualConstraint(variables[i], variables[j]))
                
        # 4b. Global Equation Constraint
        self.add_constraint(EquationConstraint(addends, result, variables))
