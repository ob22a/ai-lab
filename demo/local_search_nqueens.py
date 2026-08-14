"""
demo/local_search_nqueens.py
N-Queens Local Search & Continuous Optimization Demo.

Supports 4 Local Search & Continuous Optimization Solvers:
  1. HillClimbing        (Steepest-ascent with random restarts)
  2. SimulatedAnnealing  (Exponential cooling schedule)
  3. LocalBeamSearch     (k parallel beam candidate queens)
  4. GeneticAlgorithm    (OX1 crossover, 2-Opt mutation, population elites)

Usage:
  python -m demo.local_search_nqueens [--vis] [--algo HillClimbing|SimulatedAnnealing|LocalBeamSearch|GeneticAlgorithm] [--n 8]
"""

import sys
import os
import argparse
import random
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Top-Level Imports for Easy Code Substitution ---
from domains.n_queens.NQueensProblem import NQueensProblem
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm

from visualization.NQueensVisualizer import NQueensVisualizer
from visualization.BeamSearchVisualizer import BeamSearchVisualizer
from visualization.GeneticAlgorithmVisualizer import GeneticAlgorithmVisualizer


def print_board(state):
    n = len(state)
    for row in range(n):
        line = []
        for col in range(n):
            if state[col] == row:
                line.append("Q")
            else:
                line.append(".")
        print(" ".join(line))
    print()


def main():
    parser = argparse.ArgumentParser(description="N-Queens Local Search Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--algo", type=str, default="HillClimbing",
                        choices=["HillClimbing", "SimulatedAnnealing", "LocalBeamSearch", "GeneticAlgorithm"],
                        help="Optimization algorithm class")
    parser.add_argument("--n", type=int, default=8, help="Number of queens (board size)")
    args = parser.parse_args()

    print("=" * 65)
    print(f"         N-QUEENS LOCAL SEARCH DEMO ({args.n}-QUEENS)")
    print("=" * 65)

    random.seed(42)
    problem = NQueensProblem(args.n)

    solvers = {
        "HillClimbing": HillClimbing,
        "SimulatedAnnealing": SimulatedAnnealing,
        "LocalBeamSearch": LocalBeamSearch,
        "GeneticAlgorithm": GeneticAlgorithm
    }
    solver_cls = solvers.get(args.algo, HillClimbing)

    print(f"Executing {solver_cls.__name__}...")
    if solver_cls == LocalBeamSearch:
        solver = solver_cls(problem, k=5)
    elif solver_cls == GeneticAlgorithm:
        solver = solver_cls(problem, pop_size=50, max_generations=200)
    else:
        solver = solver_cls(problem)

    t0 = time.time()
    res = solver.run()
    dur = time.time() - t0

    sol_node = getattr(solver, 'best_state', None) or getattr(solver, 'solution_node', None).state
    val = problem.value(sol_node)

    print(f"\nOptimization Complete in {dur:.4f}s:")
    print(f"  Final Non-Attacking Queens: {val} / {problem.max_fitness} (Optimal? {val == problem.max_fitness})")
    print(f"  Nodes Expanded:           {solver.nodes_expanded}")

    if val == problem.max_fitness:
        print("\nOptimal Board Layout Found:")
        print_board(sol_node)

    if args.vis:
        print(f"\nLaunching Pygame Visualizer for {solver_cls.__name__}...")
        if solver_cls == LocalBeamSearch:
            vis = BeamSearchVisualizer(problem, solver, cell_size=50, fps=30)
        elif solver_cls == GeneticAlgorithm:
            vis = GeneticAlgorithmVisualizer(problem, solver, cell_size=50, fps=30)
        else:
            vis = NQueensVisualizer(problem, solver, cell_size=50, fps=30)
        vis.run()
    else:
        print("=" * 65)


if __name__ == "__main__":
    main()

