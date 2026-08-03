from domains.sudoku.Sudoku import SudokuCSP
from csp.Backtracking import BacktrackingSolver
from csp.heuristics.MRV import mrv
from csp.heuristics.LCV import lcv
from csp.inference.ForwardChecking import forward_checking
from visualization.SudokuVisualizer import SudokuVisualizer

def main():
    print("Initializing Sudoku CSP Visualizer...")
    
    # A standard difficult Sudoku puzzle (0 means empty)
    grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    problem = SudokuCSP(grid)
    
    # We will use Backtracking with MRV (Minimum Remaining Values) and Forward Checking
    # This makes the solver extremely smart and fast!
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=mrv,
        order_domain_values=lcv,
        inference=forward_checking
    )
    
    visualizer = SudokuVisualizer(
        problem=problem,
        solver=solver,
        cell_size=60,
        delay_ms=20 # 20ms delay per step so we can watch it think
    )
    
    visualizer.run()

if __name__ == "__main__":
    main()
