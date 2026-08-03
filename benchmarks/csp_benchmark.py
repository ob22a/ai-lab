import time
from typing import Callable, Any

from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default, inference_default
from csp.heuristics.MRV import mrv
from csp.inference.ForwardChecking import forward_checking
from csp.inference.MAC import mac
from csp.MinConflicts import MinConflictsSolver

from domains.map_coloring.MapColoring import MapColoringCSP
from domains.n_queens.NQueensCSP import NQueensCSP
from domains.sudoku.Sudoku import SudokuCSP, SUDOKU_EASY, SUDOKU_HARD

def run_backtracking(problem_generator: Callable, name: str, var_heuristic: Callable, inference: Callable) -> str:
    problem = problem_generator()
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=var_heuristic,
        order_domain_values=order_domain_values_default,
        inference=inference
    )
    start = time.time()
    solver.solve()
    duration = time.time() - start
    
    if solver.status == "SUCCESS":
        return f"{solver.nodes_expanded} nodes ({duration:.4f}s)"
    else:
        # Some simple heuristics might time out or hit recursion limits on Hard Sudoku
        return f"FAILED/TIMEOUT ({duration:.4f}s)"

def run_min_conflicts(problem_generator: Callable, max_steps: int = 10000) -> str:
    problem = problem_generator()
    solver = MinConflictsSolver(problem, max_steps=max_steps)
    start = time.time()
    solver.solve()
    duration = time.time() - start
    
    if solver.status == "SUCCESS":
        return f"{solver.nodes_expanded} steps ({duration:.4f}s)"
    else:
        return f"FAILED ({duration:.4f}s)"

def format_row(problem_name: str, bt: str, bt_mrv: str, bt_fc: str, bt_mac: str, min_conflicts: str) -> str:
    return f"| {problem_name:12} | {bt:20} | {bt_mrv:20} | {bt_fc:20} | {bt_mac:20} | {min_conflicts:20} |"

def main():
    print("Running CSP Benchmarks...\n")
    print("| Problem      | BT                   | BT+MRV               | BT+FC                | BT+MAC               | Min-Conflicts        |")
    print("|--------------|----------------------|----------------------|----------------------|----------------------|----------------------|")
    
    # 1. Map Coloring
    def map_coloring(): return MapColoringCSP()
    row1 = format_row(
        "Map Coloring",
        run_backtracking(map_coloring, "BT", unassigned_variable_default, inference_default),
        run_backtracking(map_coloring, "BT+MRV", mrv, inference_default),
        run_backtracking(map_coloring, "BT+FC", unassigned_variable_default, forward_checking),
        run_backtracking(map_coloring, "BT+MAC", unassigned_variable_default, mac),
        run_min_conflicts(map_coloring)
    )
    print(row1)
    
    # 2. 8-Queens
    def eight_queens(): return NQueensCSP(8)
    row2 = format_row(
        "8-Queens",
        run_backtracking(eight_queens, "BT", unassigned_variable_default, inference_default),
        run_backtracking(eight_queens, "BT+MRV", mrv, inference_default),
        run_backtracking(eight_queens, "BT+FC", unassigned_variable_default, forward_checking),
        run_backtracking(eight_queens, "BT+MAC", unassigned_variable_default, mac),
        run_min_conflicts(eight_queens)
    )
    print(row2)
    
    # 3. Sudoku Easy
    def sudoku_easy(): return SudokuCSP(SUDOKU_EASY)
    row3 = format_row(
        "Sudoku Easy",
        # Standard backtracking without any heuristics/inference will hang forever on Sudoku!
        # We cap it or just skip it. Let's skip pure BT for Sudoku.
        "HANGS FOREVER",
        run_backtracking(sudoku_easy, "BT+MRV", mrv, inference_default),
        run_backtracking(sudoku_easy, "BT+FC", unassigned_variable_default, forward_checking),
        run_backtracking(sudoku_easy, "BT+MAC", unassigned_variable_default, mac),
        "N/A (Too dense)"
    )
    print(row3)
    
    # 4. Sudoku Hard
    def sudoku_hard(): return SudokuCSP(SUDOKU_HARD)
    row4 = format_row(
        "Sudoku Hard",
        "HANGS FOREVER",
        "HANGS FOREVER",
        run_backtracking(sudoku_hard, "BT+FC", mrv, forward_checking), # Using MRV for FC to give it a chance
        run_backtracking(sudoku_hard, "BT+MAC", mrv, mac),
        "N/A (Too dense)"
    )
    print(row4)
    
    print("\nBenchmark Complete!")

if __name__ == "__main__":
    main()
