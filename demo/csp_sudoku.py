# =====================================================================
# TWEAKABLE CONFIGURATION - Modify these variables to test variations!
# =====================================================================
# Solvers available:   BacktrackingSolver, MinConflictsSolver
# Heuristics available: mrv, mrv_with_degree_heuristic, lcv, None
# Inferences available: mac, forward_checking, None
# =====================================================================

import sys
import time
from domains.sudoku.Sudoku import SudokuCSP, SUDOKU_EASY, SUDOKU_HARD
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.heuristics.MRV import mrv
from csp.heuristics.LCV import lcv
from csp.inference.ForwardChecking import forward_checking
from csp.inference.MAC import mac
from visualization.SudokuVisualizer import SudokuVisualizer

# ── User Configuration ────────────────────────────────────────────────
CHOSEN_BOARD = SUDOKU_HARD       # Options: SUDOKU_EASY, SUDOKU_HARD
CHOSEN_SOLVER = BacktrackingSolver
CHOSEN_HEURISTIC = mrv          # Options: mrv, None
CHOSEN_ORDERING = lcv           # Options: lcv, order_domain_values_default
CHOSEN_INFERENCE = mac          # Options: mac, forward_checking, None
VISUALIZE = True                # Set to False to run text-only solver


def print_sudoku(assignment):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("- - - + - - - + - - -")
        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += "| "
            val = assignment.get((r, c), ".")
            row_str += f"{val} "
        print(row_str)
    print()


def run_sudoku_demo(visualize=True):
    print("\n--- Sudoku CSP Demo ---")
    problem = SudokuCSP(CHOSEN_BOARD)
    
    solver = CHOSEN_SOLVER(
        problem,
        select_unassigned_variable=CHOSEN_HEURISTIC,
        order_domain_values=CHOSEN_ORDERING,
        inference=CHOSEN_INFERENCE
    )
    
    start_time = time.time()
    solution = solver.solve()
    duration = time.time() - start_time
    
    if solver.status == "SUCCESS":
        print(f"Solution found in {duration:.4f} seconds! (Nodes expanded: {solver.nodes_expanded})")
        print_sudoku(solution)
    else:
        print("Failed to find a solution.")

    if visualize:
        print("\nLaunching Pygame Sudoku Visualizer...")
        vis_problem = SudokuCSP(CHOSEN_BOARD)
        vis_solver = CHOSEN_SOLVER(
            vis_problem,
            select_unassigned_variable=CHOSEN_HEURISTIC,
            order_domain_values=CHOSEN_ORDERING,
            inference=CHOSEN_INFERENCE
        )
        vis = SudokuVisualizer(problem=vis_problem, solver=vis_solver, delay_ms=10)
        vis.run()


def main():
    visualize = VISUALIZE and ("--no-vis" not in sys.argv)
    run_sudoku_demo(visualize=visualize)


if __name__ == "__main__":
    main()
