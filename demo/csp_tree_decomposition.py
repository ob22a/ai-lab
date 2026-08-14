import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.map_coloring.MapColoring import MapColoringCSP
from csp.TreeDecomposition import TreeDecomposition, TreeDecompositionSolver, auto_tree_decomposition


def main():
    parser = argparse.ArgumentParser(description="Tree Decomposition CSP Demo")
    parser.add_argument("--vis", action="store_true", help="Run with visual step-by-step trace")
    args = parser.parse_args()

    print("=" * 70)
    print("      TREE DECOMPOSITION (JUNCTION TREE META-CSP) DEMO")
    print("=" * 70)
    print("Tree Decomposition transforms a cyclic CSP into an acyclic Meta-Tree:")
    print("  Step 1: Group variables into overlapping clusters (megavariables).")
    print("  Step 2: Solve internal constraints for each cluster to build compound domains.")
    print("  Step 3: Enforce Separator Agreement along tree edges.")
    print("  Step 4: Solve the meta-tree CSP in linear time with 0 backtracks!\n")
    
    problem = MapColoringCSP()
    
    # 1. Automatic Tree Decomposition
    print(">>> STEP 1: Constructing Tree Decomposition (Min-Fill Elimination)...")
    decomp = auto_tree_decomposition(problem)
    is_valid, msg = decomp.validate(problem)
    
    print(f"Validation: {msg}")
    print("\n[Clusters / Megavariables]:")
    for cid, vars_list in decomp.clusters.items():
        print(f"  {cid:4s} = {vars_list}")
        
    print("\n[Junction Tree Edges (Separators)]:")
    for u, v in decomp.edges:
        shared = sorted(list(set(decomp.clusters[u]) & set(decomp.clusters[v])))
        print(f"  {u:4s} <==== Separator: {shared} ====> {v:4s}")

    # 2. Solve using TreeDecompositionSolver
    print("\n>>> STEP 2 & 3: Building Cluster Compound Domains & Agreement Constraints...")
    solver = TreeDecompositionSolver(problem, decomposition=decomp)
    
    cluster_domains = solver._generate_cluster_domains()
    if cluster_domains:
        for cid, tuples in cluster_domains.items():
            print(f"  Cluster {cid} Domain: {len(tuples)} valid tuple assignments (satisfying internal constraints)")

    print("\n>>> STEP 4: Solving Meta-Tree CSP via TreeCSPSolver (Zero Backtracks)...")
    solution = solver.solve()
    
    print(f"\nSolver Status: {solver.status}")
    print(f"Subproblem Evaluations: {solver.nodes_expanded}")
    print("\nReconstructed Variable Solution:")
    for var, color in sorted(solution.items()):
        print(f"  {var:4s}: {color}")
    if args.vis:
        print("\nLaunching Interactive Pygame Tree Decomposition Visualizer...")
        from visualization.TreeDecompositionVisualizer import TreeDecompositionVisualizer
        vis = TreeDecompositionVisualizer(problem, solver)
        vis.run()


if __name__ == "__main__":
    main()


