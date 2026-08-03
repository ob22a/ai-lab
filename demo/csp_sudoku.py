import time
from domains.sudoku.Sudoku import SudokuCSP, SUDOKU_EASY, SUDOKU_HARD
from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default
from csp.heuristics.MRV import mrv
from csp.inference.ForwardChecking import forward_checking
from csp.inference.MAC import mac


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


def run_sudoku_solver(name, board, inference_engine):
    print(f"\n--- {name} ---")
    problem = SudokuCSP(board)
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=mrv,
        order_domain_values=order_domain_values_default,
        inference=inference_engine
    )
    
    start_time = time.time()
    solution = solver.solve()
    duration = time.time() - start_time
    
    if solver.status == "SUCCESS":
        print(f"Solution found in {duration:.4f} seconds!")
        print(f"Nodes expanded: {solver.nodes_expanded}")
        print_sudoku(solution)
    else:
        print("Failed to find a solution.")


def main():
    print("Solving Sudoku with MRV + Inference")
    
    print("\n[EASY BOARD]")
    run_sudoku_solver("MRV + Forward Checking", SUDOKU_EASY, forward_checking)
    run_sudoku_solver("MRV + MAC (AC-3)", SUDOKU_EASY, mac)
    
    print("\n[HARD BOARD]")
    print("Notice the massive difference in node expansions on the hard board!")
    run_sudoku_solver("MRV + Forward Checking", SUDOKU_HARD, forward_checking)
    run_sudoku_solver("MRV + MAC (AC-3)", SUDOKU_HARD, mac)


if __name__ == "__main__":
    main()
