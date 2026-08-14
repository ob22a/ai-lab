"""
demo/csp_sudoku.py
Sudoku CSP Solver Demo (Backtracking + MRV + MAC/FC).

Usage:
  python -m demo.csp_sudoku [--vis] [--difficulty easy|hard] [--solver backtracking|minconflicts] [--inference mac|fc|none]
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Top-Level Imports for Easy Code Substitution ---
from domains.sudoku.Sudoku import SudokuCSP, SUDOKU_EASY, SUDOKU_HARD
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.MinConflicts import MinConflictsSolver
from csp.heuristics.MRV import mrv
from csp.heuristics.LCV import lcv
from csp.inference.ForwardChecking import forward_checking
from csp.inference.MAC import mac
from visualization.SudokuVisualizer import SudokuVisualizer


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


def main():
    parser = argparse.ArgumentParser(description="Sudoku CSP Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--difficulty", type=str, default="hard", choices=["easy", "hard"], help="Board difficulty")
    parser.add_argument("--solver", type=str, default="backtracking", choices=["backtracking", "minconflicts"], help="Solver class")
    parser.add_argument("--inference", type=str, default="mac", choices=["mac", "fc", "none"], help="Inference algorithm")
    args = parser.parse_args()

    print("=" * 65)
    print(f"            SUDOKU CSP SOLVER DEMO ({args.difficulty.upper()})")
    print("=" * 65)

    board = SUDOKU_EASY if args.difficulty == "easy" else SUDOKU_HARD
    problem = SudokuCSP(board)

    inference_fn = mac if args.inference == "mac" else (forward_checking if args.inference == "fc" else None)

    if args.solver == "minconflicts":
        solver = MinConflictsSolver(problem, max_steps=2000)
    else:
        solver = BacktrackingSolver(
            problem,
            select_unassigned_variable=mrv,
            order_domain_values=lcv,
            inference=inference_fn
        )

    t0 = time.time()
    solution = solver.solve()
    dur = time.time() - t0

    if solver.status == "SUCCESS" and solution:
        print(f"\nSolution Found in {dur:.4f}s! (Nodes expanded: {solver.nodes_expanded})\n")
        print_sudoku(solution)
    else:
        print(f"\nNo solution found for this Sudoku board configuration.")

    if args.vis:
        print("\nLaunching Pygame Sudoku Visualizer...")
        vis_problem = SudokuCSP(board)
        vis_solver = BacktrackingSolver(
            vis_problem,
            select_unassigned_variable=mrv,
            order_domain_values=lcv,
            inference=inference_fn
        ) if args.solver == "backtracking" else MinConflictsSolver(vis_problem, max_steps=2000)

        vis = SudokuVisualizer(problem=vis_problem, solver=vis_solver, delay_ms=10)
        vis.run()
    else:
        print("=" * 65)


if __name__ == "__main__":
    main()

