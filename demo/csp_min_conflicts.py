import time
from domains.n_queens.NQueensCSP import NQueensCSP
from csp.MinConflicts import MinConflictsSolver
from csp.Backtracking import BacktrackingSolver


def solve_nqueens(n, solver_class):
    print(f"\n--- {solver_class.__name__} on {n}-Queens ---")
    problem = NQueensCSP(n)
    solver = solver_class(problem)
    
    start_time = time.time()
    solution = solver.solve()
    duration = time.time() - start_time
    
    if solver.status == "SUCCESS":
        print(f"Solution found in {duration:.4f} seconds!")
        print(f"Steps/Nodes expanded: {solver.nodes_expanded}")
        if n <= 10:
            print("Assignment:", solution)
    else:
        print(f"Failed to find a solution in {duration:.4f} seconds.")


def main():
    print("Evaluating CSP Solvers on N-Queens")
    
    print("\n[8-Queens]")
    solve_nqueens(8, BacktrackingSolver)
    solve_nqueens(8, MinConflictsSolver)
    
    print("\n[50-Queens]")
    # Backtracking will struggle heavily here without heuristics/inference, 
    # but Min-Conflicts will blaze through it.
    solve_nqueens(50, MinConflictsSolver)
    
    print("\n[200-Queens]")
    print("Warning: Creating the 200-Queens constraint graph takes a moment...")
    # Min-Conflicts can solve 200-Queens very quickly after graph creation!
    solve_nqueens(200, MinConflictsSolver)


if __name__ == "__main__":
    main()
