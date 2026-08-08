from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict, deque
import itertools
import copy

from csp.CSPSolver import CSPSolver
from csp.CSPProblem import CSPProblem
from csp.TreeCSP import TreeCSPSolver, get_constraint_graph, is_tree_graph


def find_cycle_cutset(csp: CSPProblem) -> List[Any]:
    """
    Finds a cycle cutset S using a greedy heuristic (highest degree node in cyclic components).
    Returns list of variables in S.
    """
    adj = get_constraint_graph(csp)
    remaining_vars = list(csp.variables)
    cutset = []
    
    while not is_tree_graph(remaining_vars, adj):
        # Pick the variable with highest degree among remaining variables
        remaining_set = set(remaining_vars)
        best_var = max(
            remaining_vars,
            key=lambda v: len(adj[v] & remaining_set)
        )
        cutset.append(best_var)
        remaining_vars.remove(best_var)
        
    return cutset


class CycleCutsetSolver(CSPSolver):
    """
    Cycle Cutset Conditioning Solver for CSPs.
    
    1. Identifies (or receives) a cycle cutset S of variables whose removal renders 
       the remaining constraint graph an acyclic forest / tree T = V \\ S.
    2. Iterates over all consistent assignments to S.
    3. For each assignment to S:
       a. Conditions the remaining variables in T (pruning values inconsistent with S).
       b. Solves the conditioned subproblem on T using the linear-time TreeCSPSolver.
    4. If the subproblem has a solution, merges S and T assignments and terminates.
    """
    def __init__(self, problem: CSPProblem, cutset: Optional[List[Any]] = None):
        super().__init__(problem)
        self.adj = get_constraint_graph(self.problem)
        if cutset is not None:
            self.cutset = list(cutset)
            remaining = [v for v in self.problem.variables if v not in self.cutset]
            if not is_tree_graph(remaining, self.adj):
                raise ValueError(f"Provided cutset {cutset} does not make remaining graph acyclic.")
        else:
            self.cutset = find_cycle_cutset(self.problem)
            
        self.tree_vars = [v for v in self.problem.variables if v not in self.cutset]

    def _get_cutset_assignments(self) -> List[Dict[Any, Any]]:
        """
        Generates all consistent assignments for the cutset variables S.
        """
        if not self.cutset:
            return [{}]
            
        valid_assignments = []
        
        def backtrack_cutset(index: int, current_assign: Dict[Any, Any]):
            if index == len(self.cutset):
                valid_assignments.append(dict(current_assign))
                return
                
            var = self.cutset[index]
            for val in self.problem.domains[var]:
                self.nodes_expanded += 1
                if self.problem.is_consistent(var, val, current_assign):
                    current_assign[var] = val
                    backtrack_cutset(index + 1, current_assign)
                    del current_assign[var]
                    
        backtrack_cutset(0, {})
        return valid_assignments

    def solve(self) -> Optional[Dict[Any, Any]]:
        """
        Runs cutset conditioning. Returns completed assignment or None.
        """
        self.reset()
        cutset_assignments = self._get_cutset_assignments()
        
        # If no variables in tree, return first valid cutset assignment
        if not self.tree_vars:
            if cutset_assignments:
                self.assignment = cutset_assignments[0]
                self.status = "SUCCESS"
                return self.assignment
            self.status = "FAILURE"
            return None

        # For each consistent cutset assignment:
        for s_assign in cutset_assignments:
            # 1. Condition domains of variables in T with respect to s_assign
            conditioned_domains: Dict[Any, List[Any]] = {}
            possible = True
            
            for t_var in self.tree_vars:
                valid_vals = []
                for val in self.problem.domains[t_var]:
                    if self.problem.is_consistent(t_var, val, s_assign):
                        valid_vals.append(val)
                if not valid_vals:
                    possible = False
                    break
                conditioned_domains[t_var] = valid_vals
                
            if not possible:
                continue

            # 2. Build subproblem for T
            sub_problem = CSPProblem(self.tree_vars, conditioned_domains)
            # Add constraints between variables in T
            added_constraints = set()
            for t_var in self.tree_vars:
                for constraint in self.problem.constraints[t_var]:
                    # If all variables in this constraint belong to T
                    if all(v in self.tree_vars for v in constraint.variables):
                        constr_key = (id(constraint))
                        if constr_key not in added_constraints:
                            added_constraints.add(constr_key)
                            sub_problem.add_constraint(constraint)

            # 3. Solve conditioned tree subproblem with TreeCSPSolver
            tree_solver = TreeCSPSolver(sub_problem)
            t_solution = tree_solver.solve()
            self.nodes_expanded += tree_solver.nodes_expanded
            
            if t_solution is not None:
                # Merge assignments
                full_assignment = dict(s_assign)
                full_assignment.update(t_solution)
                self.assignment = full_assignment
                self.status = "SUCCESS"
                return full_assignment

        self.status = "FAILURE"
        return None
