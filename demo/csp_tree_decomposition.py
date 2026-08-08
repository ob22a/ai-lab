import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.map_coloring.MapColoring import MapColoringCSP
from csp.TreeDecomposition import TreeDecomposition, TreeDecompositionSolver, auto_tree_decomposition


def main():
    print("=" * 65)
    print("         TREE DECOMPOSITION (JUNCTION TREE) DEMO")
    print("=" * 65)
    print("Tree Decomposition transforms a general cyclic CSP into a meta Tree-CSP:")
    print("  1. Groups variables into overlapping clusters (megavariables).")
    print("  2. Solves each cluster's internal constraints to build compound domains.")
    print("  3. Enforces Separator Agreement on shared variables along tree edges.")
    print("  4. Solves the meta tree CSP via TreeCSPSolver in linear time with 0 backtracks!\n")
    
    problem = MapColoringCSP()
    
    # 1. Automatic Tree Decomposition
    decomp = auto_tree_decomposition(problem)
    is_valid, msg = decomp.validate(problem)
    
    print(f"Tree Decomposition Validation: {msg}")
    print("\nClusters (Megavariables):")
    for cid, vars_list in decomp.clusters.items():
        print(f"  {cid}: {vars_list}")
        
    print("\nCluster Tree Edges (Junction Tree):")
    for u, v in decomp.edges:
        shared = set(decomp.clusters[u]) & set(decomp.clusters[v])
        print(f"  {u} <---> {v}  [Separator: {list(shared)}]")
        
    # 2. Solve using TreeDecompositionSolver
    solver = TreeDecompositionSolver(problem, decomposition=decomp)
    solution = solver.solve()
    
    print(f"\nSolver Status: {solver.status}")
    print(f"Nodes / Subproblem evaluations: {solver.nodes_expanded}")
    print("\nReconstructed Original Solution:")
    for var, color in sorted(solution.items()):
        print(f"  {var:4s}: {color}")
    print("=" * 65)


if __name__ == "__main__":
    main()
