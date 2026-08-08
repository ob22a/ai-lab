from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict, deque
import copy

from csp.CSPSolver import CSPSolver
from csp.CSPProblem import CSPProblem
from csp.inference.AC3 import revise


def get_constraint_graph(csp: CSPProblem) -> Dict[Any, Set[Any]]:
    """
    Extracts the undirected binary constraint graph from a CSPProblem.
    """
    adj = defaultdict(set)
    for var in csp.variables:
        for constraint in csp.constraints[var]:
            for other in constraint.variables:
                if other != var and other in csp.variables:
                    adj[var].add(other)
                    adj[other].add(var)
    # Ensure all variables are in adj
    for var in csp.variables:
        if var not in adj:
            adj[var] = set()
    return adj


def is_tree_graph(variables: List[Any], adj: Dict[Any, Set[Any]]) -> bool:
    """
    Checks if the constraint graph induced by variables is a forest (collection of trees, i.e., acyclic).
    """
    visited = set()
    
    for var in variables:
        if var not in visited:
            queue = deque([(var, None)])
            visited.add(var)
            while queue:
                curr, parent = queue.popleft()
                for neighbor in adj[curr]:
                    if neighbor not in variables:
                        continue
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, curr))
                    elif neighbor != parent:
                        return False # Cycle detected!
    return True


class TreeCSPSolver(CSPSolver):
    """
    Tree-Structured CSP Solver.
    
    Solves any CSP whose constraint graph is a tree (or forest) in O(n * d^2) time:
    1. Directs the tree from an arbitrary root and orders variables topologically X1..Xn.
    2. Applies Directional Arc Consistency (DAC) bottom-up from Xn down to X2:
       Domain(Parent(Xj)) is revised with respect to Xj.
    3. If any domain becomes empty, problem is unsolvable.
    4. Greedily assigns values top-down from X1 to Xn with ZERO backtracking.
    """
    def __init__(self, problem: CSPProblem, root: Optional[Any] = None):
        super().__init__(problem)
        self.root = root
        self.adj = get_constraint_graph(self.problem)
        self.parents: Dict[Any, Any] = {}
        self.topological_order: List[Any] = []
        self.components: List[List[Any]] = []

    def _build_tree_order(self) -> bool:
        """
        Builds directed trees / forests and topological ordering.
        Returns False if graph contains a cycle.
        """
        self.parents = {}
        self.topological_order = []
        self.components = []
        visited = set()
        
        var_pool = list(self.problem.variables)
        if self.root is not None and self.root in var_pool:
            var_pool.remove(self.root)
            var_pool.insert(0, self.root)
            
        for start_var in var_pool:
            if start_var not in visited:
                component_order = []
                queue = deque([(start_var, None)])
                visited.add(start_var)
                self.parents[start_var] = None
                
                while queue:
                    curr, parent = queue.popleft()
                    component_order.append(curr)
                    
                    for neighbor in self.adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            self.parents[neighbor] = curr
                            queue.append((neighbor, curr))
                        elif neighbor != parent:
                            # Cycle detected!
                            return False
                            
                self.components.append(component_order)
                self.topological_order.extend(component_order)
                
        return True

    def solve(self) -> Optional[Dict[Any, Any]]:
        """
        Runs the tree-structured CSP solver.
        Returns consistent assignment dict or None on failure.
        """
        self.reset()
        if not self._build_tree_order():
            raise ValueError("Constraint graph contains cycles and is not tree-structured.")

        current_domains = {var: list(values) for var, values in self.problem.domains.items()}
        n = len(self.topological_order)
        if n == 0:
            self.status = "SUCCESS"
            return {}
            
        # Step 1: Bottom-up Directional Arc Consistency (DAC)
        # For j = n down to 2: Revise(Parent(Xj), Xj)
        for j in range(n - 1, 0, -1):
            var_j = self.topological_order[j]
            parent_j = self.parents.get(var_j)
            
            if parent_j is not None:
                self.nodes_expanded += 1
                revised = revise(self.problem, parent_j, var_j, current_domains)
                if not current_domains[parent_j]:
                    self.status = "FAILURE"
                    return None
                    
        # Step 2: Top-down greedy assignment
        assignment: Dict[Any, Any] = {}
        for var in self.topological_order:
            parent = self.parents.get(var)
            assigned_value = None
            
            if parent is None:
                if not current_domains[var]:
                    self.status = "FAILURE"
                    return None
                assigned_value = current_domains[var][0]
            else:
                for val in current_domains[var]:
                    if self.problem.is_consistent(var, val, assignment):
                        assigned_value = val
                        break
                        
            if assigned_value is None:
                self.status = "FAILURE"
                return None
                
            assignment[var] = assigned_value
            self.nodes_expanded += 1

        self.assignment = assignment
        self.status = "SUCCESS"
        return assignment
