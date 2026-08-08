import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.n_queens.NQueensCSP import NQueensCSP
from csp.Backtracking import BacktrackingSolver
from csp.SymmetricBacktracking import SymmetricBacktrackingSolver
from csp.heuristics.MRV import mrv
from csp.inference.MAC import mac
from csp.inference.ForwardChecking import forward_checking
from visualization.NQueensVisualizer import NQueensVisualizer


def main():
    print("=" * 65)
    print("      N-QUEENS CSP PYGAME INTERACTIVE VISUALIZER")
    print("=" * 65)
    print("This demo runs NQueensCSP with Backtracking / MAC / Symmetry Breaking")
    print("in the unified Pygame NQueensVisualizer window.\n"
          "Controls:\n"
          "  [SPACE]     Play / Pause auto-run\n"
          "  [RIGHT]     Step forward (Queen assignment / prune)\n"
          "  [LEFT]      Step backward (Inspect previous assignments/backtracks)\n"
          "  [R]         Restart search\n"
          "  [UP / DOWN] Increase / Decrease animation speed\n")
    
    n = 8
    # Create NQueens CSP with optional symmetry breaking
    problem = NQueensCSP(n=n, break_symmetry=True)
    
    # Choose solver: Backtracking, MAC, FC, or SymmetricBacktracking
    solver = SymmetricBacktrackingSolver(
        problem,
        select_unassigned_variable=mrv,
        inference=mac,
        value_symmetry=False
    )
    
    visualizer = NQueensVisualizer(
        problem=problem,
        solver=solver,
        cell_size=60,
        fps=8,
        auto_run=False
    )
    
    visualizer.run()


if __name__ == "__main__":
    main()
