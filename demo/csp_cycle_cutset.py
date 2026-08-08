import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.map_coloring.MapColoring import MapColoringCSP
from csp.CycleCutset import CycleCutsetSolver, find_cycle_cutset
from csp.Backtracking import BacktrackingSolver


def main():
    print("=" * 65)
    print("         CYCLE CUTSET CONDITIONING DEMO")
    print("=" * 65)
    print("Cycle Cutset conditioning decomposes a general CSP into:")
    print("  1. A small cutset S of variables whose removal breaks all cycles.")
    print("  2. An acyclic tree subproblem on T = V \\ S solved in linear time.")
    print("Total complexity: O(d^|S| * (n - |S|) * d^2)\n")
    
    problem = MapColoringCSP()
    
    # 1. Automatic Cutset Detection
    auto_cutset = find_cycle_cutset(problem)
    print(f"Australia Map Coloring Graph:")
    print(f"  All Variables: {problem.variables}")
    print(f"  Detected Cutset S: {auto_cutset}")
    remaining_tree = [v for v in problem.variables if v not in auto_cutset]
    print(f"  Remaining Tree T:  {remaining_tree}\n")
    
    # 2. Solve with Cycle Cutset Conditioning
    cutset_solver = CycleCutsetSolver(problem, cutset=auto_cutset)
    solution = cutset_solver.solve()
    
    print(f"--- Cutset Solver Results ---")
    print(f"Status: {cutset_solver.status}")
    print(f"Nodes Evaluated: {cutset_solver.nodes_expanded}")
    print("Solution Assignment:")
    for var, color in solution.items():
        is_cutset_mark = " (Cutset Variable)" if var in auto_cutset else ""
        print(f"  {var:4s}: {color}{is_cutset_mark}")
        
    # 3. Compare with standard Backtracking
    bt_solver = BacktrackingSolver(MapColoringCSP())
    bt_solution = bt_solver.solve()
    print(f"\nStandard Backtracking Nodes: {bt_solver.nodes_expanded}")
    print("=" * 65)


if __name__ == "__main__":
    main()
