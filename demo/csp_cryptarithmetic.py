# =====================================================================
# TWEAKABLE CONFIGURATION - Modify these variables to test variations!
# =====================================================================
# Solvers available:   BacktrackingSolver
# Heuristics available: mrv, mrv_with_degree_heuristic, lcv, None
# Inferences available: forward_checking, None
# =====================================================================

import sys
import time
from domains.cryptarithmetic.Cryptarithmetic import CryptarithmeticCSP
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.ForwardChecking import forward_checking
from visualization.CryptarithmeticVisualizer import CryptarithmeticVisualizer

# ── User Configuration ────────────────────────────────────────────────
PUZZLE_ADDENDS = ["SEND", "MORE"]
PUZZLE_RESULT  = "MONEY"
CHOSEN_SOLVER    = BacktrackingSolver
CHOSEN_HEURISTIC = mrv_with_degree_heuristic  # Options: mrv, mrv_with_degree_heuristic, None
CHOSEN_INFERENCE = forward_checking           # Options: forward_checking, None
VISUALIZE        = True                        # Set to False for text-only output


def solve_crypto(addends, result, visualize=True):
    puzzle_str = f"{' + '.join(addends)} = {result}"
    print(f"\n--- Cryptarithmetic CSP: {puzzle_str} ---")
    
    try:
        problem = CryptarithmeticCSP(addends, result)
    except ValueError as e:
        print(f"Error: {e}")
        return
        
    solver = CHOSEN_SOLVER(
        problem,
        select_unassigned_variable=CHOSEN_HEURISTIC,
        order_domain_values=order_domain_values_default,
        inference=CHOSEN_INFERENCE
    )
    
    start = time.time()
    solution = solver.solve()
    duration = time.time() - start
    
    if solver.status == "SUCCESS":
        print(f"Solution found in {duration:.4f} seconds! (Nodes expanded: {solver.nodes_expanded})")
        print("Assignment:")
        for char, digit in sorted(solution.items()):
            print(f"  {char} = {digit}")
            
        print("\nVerification:")
        for word in addends:
            val = "".join(str(solution[c]) for c in word)
            print(f"  {word:10} -> {val:10}")
        print("  " + "-"*20)
        res_val = "".join(str(solution[c]) for c in result)
        print(f"  {result:10} -> {res_val:10}")
    else:
        print(f"NO SOLUTION EXISTS. Searched in {duration:.4f} seconds. (Nodes expanded: {solver.nodes_expanded})")

    if visualize:
        print("\nLaunching Pygame Cryptarithmetic Visualizer...")
        vis = CryptarithmeticVisualizer(puzzle=puzzle_str, solver_class=CHOSEN_SOLVER)
        vis.run()


def main():
    visualize = VISUALIZE and ("--no-vis" not in sys.argv)
    clean_argv = [a for a in sys.argv if a != "--no-vis"]

    if len(clean_argv) > 2:
        args = clean_argv[1:]
        addends = [w.upper() for w in args[:-1]]
        result = args[-1].upper()
        solve_crypto(addends, result, visualize=visualize)
    else:
        solve_crypto(PUZZLE_ADDENDS, PUZZLE_RESULT, visualize=visualize)


if __name__ == "__main__":
    main()
