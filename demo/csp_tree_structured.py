import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from csp.CSPProblem import CSPProblem
from domains.map_coloring.MapColoring import NotEqualConstraint
from csp.TreeCSP import TreeCSPSolver


def main():
    print("=" * 65)
    print("         TREE-STRUCTURED CSP SOLVER DEMO")
    print("=" * 65)
    print("A Tree-Structured CSP has an acyclic constraint graph.")
    print("It is solved in O(n * d^2) time with ZERO backtracking:\n"
          "  1. Directional Arc Consistency (DAC) bottom-up from leaves to root.\n"
          "  2. Greedy consistent assignment top-down from root to leaves.\n")
    
    # We construct a tree constraint graph:
    # Root: WA -> Children: NT, SA
    # NT -> Child: Q
    # Q -> Child: NSW
    # NSW -> Child: V
    # Island: T
    variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
    domains = {var: ['Red', 'Green', 'Blue'] for var in variables}
    
    tree_csp = CSPProblem(variables, domains)
    tree_csp.add_constraint(NotEqualConstraint('WA', 'NT'))
    tree_csp.add_constraint(NotEqualConstraint('WA', 'SA'))
    tree_csp.add_constraint(NotEqualConstraint('NT', 'Q'))
    tree_csp.add_constraint(NotEqualConstraint('Q', 'NSW'))
    tree_csp.add_constraint(NotEqualConstraint('NSW', 'V'))
    
    print("Constraint Graph Edges: (WA-NT), (WA-SA), (NT-Q), (Q-NSW), (NSW-V), (T isolated)")
    print(f"Variables: {variables}")
    print(f"Colors available: {domains['WA']}\n")
    
    solver = TreeCSPSolver(tree_csp, root='WA')
    solution = solver.solve()
    
    print(f"Topological Order: {' -> '.join(solver.topological_order)}")
    print(f"Solver Status: {solver.status}")
    print(f"Nodes / Operations: {solver.nodes_expanded}")
    print("\nSolution Assignment:")
    for var in solver.topological_order:
        print(f"  {var:4s}: {solution[var]}")
    print("=" * 65)


if __name__ == "__main__":
    main()
