"""
demo/csp_cryptarithmetic.py
Cryptarithmetic Letter Math CSP Solver Demo (SEND + MORE = MONEY).

Usage:
  python -m demo.csp_cryptarithmetic [--vis] [--addends SEND MORE] [--result MONEY] [--solver backtracking|minconflicts]
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Top-Level Imports for Easy Code Substitution ---
from domains.cryptarithmetic.Cryptarithmetic import CryptarithmeticCSP
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.MinConflicts import MinConflictsSolver
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.ForwardChecking import forward_checking
from visualization.CryptarithmeticVisualizer import CryptarithmeticVisualizer


def main():
    parser = argparse.ArgumentParser(description="Cryptarithmetic Letter Math CSP Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--addends", nargs="+", default=["SEND", "MORE"], help="Addend words (e.g. SEND MORE)")
    parser.add_argument("--result", type=str, default="MONEY", help="Result word (e.g. MONEY)")
    parser.add_argument("--solver", type=str, default="backtracking", choices=["backtracking", "minconflicts"], help="Solver class")
    args = parser.parse_args()

    addends = [w.upper() for w in args.addends]
    result = args.result.upper()
    puzzle_str = f"{' + '.join(addends)} = {result}"

    print("=" * 65)
    print(f"      CRYPTARITHMETIC LETTER MATH DEMO ({puzzle_str})")
    print("=" * 65)

    try:
        problem = CryptarithmeticCSP(addends, result)
    except ValueError as e:
        print(f"Error initializing puzzle: {e}")
        return

    if args.solver == "minconflicts":
        solver = MinConflictsSolver(problem, max_steps=3000)
    else:
        solver = BacktrackingSolver(
            problem,
            select_unassigned_variable=mrv_with_degree_heuristic,
            order_domain_values=order_domain_values_default,
            inference=forward_checking
        )

    t0 = time.time()
    solution = solver.solve()
    dur = time.time() - t0

    if solver.status == "SUCCESS" and solution:
        print(f"\nSolution Found in {dur:.4f}s! (Nodes expanded: {solver.nodes_expanded})\n")
        print("Letter Assignment:")
        for char, digit in sorted(solution.items()):
            print(f"  {char} = {digit}")

        print("\nEquation Verification:")
        for word in addends:
            val = "".join(str(solution[c]) for c in word)
            print(f"  {word:10s} -> {val:10s}")
        print("  " + "-" * 24)
        res_val = "".join(str(solution[c]) for c in result)
        print(f"  {result:10s} -> {res_val:10s}")
    else:
        print(f"\nNo valid letter assignment exists for this puzzle.")

    if args.vis:
        print("\nLaunching Pygame Cryptarithmetic Visualizer...")
        vis = CryptarithmeticVisualizer(puzzle=puzzle_str, solver_class=BacktrackingSolver if args.solver == "backtracking" else MinConflictsSolver)
        vis.run()
    else:
        print("=" * 65)


if __name__ == "__main__":
    main()

