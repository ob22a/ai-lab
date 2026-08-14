"""
demo/csp_map_coloring.py
Australia Map Coloring CSP Solver Demo.

Usage:
  python -m demo.csp_map_coloring [--vis] [--solver backtracking|minconflicts] [--inference mac|fc|none]
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Top-Level Imports for Easy Code Substitution ---
from domains.map_coloring.MapColoring import MapColoringCSP
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.MinConflicts import MinConflictsSolver
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.MAC import mac
from csp.inference.ForwardChecking import forward_checking
from visualization.MapColoringVisualizer import MapColoringVisualizer


def main():
    parser = argparse.ArgumentParser(description="Map Coloring CSP Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--solver", type=str, default="backtracking", choices=["backtracking", "minconflicts"], help="Solver class")
    parser.add_argument("--inference", type=str, default="fc", choices=["mac", "fc", "none"], help="Inference algorithm")
    args = parser.parse_args()

    print("=" * 65)
    print("         AUSTRALIA MAP COLORING CSP DEMO (3 COLORS)")
    print("=" * 65)

    problem = MapColoringCSP()
    inference_fn = mac if args.inference == "mac" else (forward_checking if args.inference == "fc" else None)

    if args.solver == "minconflicts":
        solver = MinConflictsSolver(problem, max_steps=1000)
    else:
        solver = BacktrackingSolver(
            problem,
            select_unassigned_variable=mrv_with_degree_heuristic,
            order_domain_values=order_domain_values_default,
            inference=inference_fn
        )

    t0 = time.time()
    solution = solver.solve()
    dur = time.time() - t0


    if solver.status == "SUCCESS" and solution:
        print(f"\nSolution Found in {dur:.4f}s! (Nodes expanded: {solver.nodes_expanded})")
        print("\nTerritory Colors:")
        for var, color in sorted(solution.items()):
            print(f"  {var:6s}: {color}")
    else:
        print("\nFailed to find a valid map coloring.")

    if args.vis:
        print("\nLaunching Pygame Map Coloring Visualizer...")
        vis = MapColoringVisualizer(solver_class=BacktrackingSolver if args.solver == "backtracking" else MinConflictsSolver)
        vis.run()
    else:
        print("=" * 65)


if __name__ == "__main__":
    main()

