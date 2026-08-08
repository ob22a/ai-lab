import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.n_queens.NQueensProblem import NQueensProblem
from domains.n_queens.NQueensCSP import NQueensCSP
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm
from csp.Backtracking import BacktrackingSolver
from csp.SymmetricBacktracking import SymmetricBacktrackingSolver
from csp.heuristics.MRV import mrv
from csp.inference.MAC import mac
from visualization.NQueensVisualizer import NQueensVisualizer


def main():
    print("=" * 65)
    print("         N-QUEENS UNIFIED VISUALIZER DEMO")
    print("=" * 65)
    print("Supports both Local Search Optimizers and CSP Solvers!")
    print("1. CSP Solver (NQueensCSP + Backtracking / MAC / Symmetry Breaking)")
    print("2. Local Search (NQueensProblem + Simulated Annealing)")
    print("=" * 65)
    
    use_csp = True
    n = 12
    
    if use_csp:
        print(f"Launching NQueensCSP (n={n}) with MAC inference...")
        problem = NQueensCSP(n=n, break_symmetry=True)
        solver = SymmetricBacktrackingSolver(
            problem,
            select_unassigned_variable=mrv,
            inference=mac
        )
    else:
        print(f"Launching NQueensProblem (n={n}) with Simulated Annealing...")
        problem = NQueensProblem(n=n)
        solver = SimulatedAnnealing(problem)

    visualizer = NQueensVisualizer(
        problem=problem,
        solver=solver,
        cell_size=60,
        fps=8
    )
    visualizer.run()


if __name__ == "__main__":
    main()
