import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.map_coloring.MapColoring import MapColoringCSP
from csp.CycleCutset import CycleCutsetSolver, find_cycle_cutset
from csp.Backtracking import BacktrackingSolver


def main():
    parser = argparse.ArgumentParser(description="Cycle Cutset CSP Demo")
    parser.add_argument("--vis", action="store_true", help="Run with visual step-by-step trace")
    args = parser.parse_args()

    print("=" * 70)
    print("           CYCLE CUTSET CONDITIONING CSP DEMO")
    print("=" * 70)
    print("Cycle Cutset conditioning decomposes a general CSP into:")
    print("  Step 1: Identify a small cutset S of variables whose removal breaks all cycles.")
    print("  Step 2: Instantiating S conditions remaining variables into an acyclic tree T = V \\ S.")
    print("  Step 3: Solve conditioned tree subproblem T in linear time (0 backtracks!).")
    print("Complexity: O(d^|S| * (n - |S|) * d^2)\n")
    
    problem = MapColoringCSP()
    
    # 1. Cutset Detection
    print(">>> STEP 1: Automatic Cutset Detection (Greedy Degree Heuristic)...")
    auto_cutset = find_cycle_cutset(problem)
    remaining_tree = [v for v in problem.variables if v not in auto_cutset]

    print(f"  Constraint Graph Variables : {problem.variables}")
    print(f"  Identified Cutset S        : {auto_cutset}  (Cycle Breaking Variables)")
    print(f"  Conditioned Tree Subproblem: {remaining_tree}  (Acyclic Forest)")
    
    # 2. Solve with Cycle Cutset Conditioning
    print("\n>>> STEP 2 & 3: Conditioning & Tree Subproblem Resolution...")
    cutset_solver = CycleCutsetSolver(problem, cutset=auto_cutset)

    # Trace cutset assignments
    cutset_assigns = cutset_solver._get_cutset_assignments()
    print(f"  Valid Cutset Assignments S to test: {len(cutset_assigns)}")
    for idx, s_assign in enumerate(cutset_assigns[:3], 1):
        print(f"    [Candidate {idx}]: {s_assign}")

    solution = cutset_solver.solve()
    
    print("\n--- Cutset Solver Results ---")
    print(f"Status          : {cutset_solver.status}")
    print(f"Nodes Evaluated : {cutset_solver.nodes_expanded}")
    print("\nSolution Assignment:")
    for var, color in solution.items():
        tag = " <=== Cutset Variable S" if var in auto_cutset else " (Conditioned Tree T)"
        print(f"  {var:4s}: {color:6s}{tag}")
        
    # 3. Compare with standard Backtracking
    bt_solver = BacktrackingSolver(MapColoringCSP())
    bt_solver.solve()
    print(f"\nStandard Backtracking Nodes: {bt_solver.nodes_expanded}")
    print("=" * 70)

    if args.vis:
        print("\nLaunching Interactive Pygame Cycle Cutset Visualizer...")
        from visualization.CycleCutsetVisualizer import CycleCutsetVisualizer
        vis = CycleCutsetVisualizer(problem, cutset_solver)
        vis.run()


if __name__ == "__main__":
    main()


