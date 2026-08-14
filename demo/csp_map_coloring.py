# =====================================================================
# TWEAKABLE CONFIGURATION - Modify these variables to test variations!
# =====================================================================
# Solvers available:   BacktrackingSolver, MinConflictsSolver
# Heuristics available: mrv, mrv_with_degree_heuristic, lcv, None
# Inferences available: mac, forward_checking, None
# =====================================================================

import sys
from domains.map_coloring.MapColoring import MapColoringCSP
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.MAC import mac
from csp.inference.ForwardChecking import forward_checking
from visualization.MapColoringVisualizer import MapColoringVisualizer

# ── User Configuration ────────────────────────────────────────────────
CHOSEN_SOLVER    = BacktrackingSolver
CHOSEN_HEURISTIC = mrv_with_degree_heuristic               # Options: mrv, mrv_with_degree_heuristic, None
CHOSEN_INFERENCE = forward_checking  # Options: mac, forward_checking, None
VISUALIZE        = True               # Set to False for text-only output


def main():
    visualize = VISUALIZE and ("--no-vis" not in sys.argv)
    print("--- Constraint Satisfaction Problem (CSP): Map Coloring ---")
    print("Solving Australia Map 3-Coloring...")
    
    problem = MapColoringCSP()
    solver = CHOSEN_SOLVER(
        problem,
        select_unassigned_variable=CHOSEN_HEURISTIC,
        order_domain_values=order_domain_values_default,
        inference=CHOSEN_INFERENCE
    )
    
    solution = solver.solve()
    
    if solver.status == "SUCCESS":
        print("\nSolution found!")
        for var, value in solution.items():
            print(f"  {var}: {value}")
    else:
        print("\nFailed to find a solution.")
        
    print(f"\nNodes expanded: {solver.nodes_expanded}")

    if visualize:
        print("\nLaunching Pygame Map Coloring Visualizer...")
        vis = MapColoringVisualizer(solver_class=CHOSEN_SOLVER)
        vis.run()


if __name__ == "__main__":
    main()
