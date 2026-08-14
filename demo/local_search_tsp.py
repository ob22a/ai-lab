"""
demo/local_search_tsp.py
Traveling Salesperson Problem (TSP) Optimization Demo.

Supports 4 Local Search & Continuous Optimization Solvers:
  1. SimulatedAnnealing  (Exponential cooling schedule)
  2. HillClimbing        (Steepest-ascent with random restarts)
  3. LocalBeamSearch     (k parallel beam candidate tours)
  4. GeneticAlgorithm    (OX1 crossover, 2-Opt mutation, population elites)

Usage:
  python -m demo.local_search_tsp [--vis] [--algo SimulatedAnnealing|HillClimbing|LocalBeamSearch|GeneticAlgorithm] [--cities 20]
"""

import sys
import os
import argparse
import random
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Top-Level Imports for Easy Code Substitution ---
from domains.tsp.TSPProblem import TSPProblem
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm
from visualization.TSPVisualizer import TSPVisualizer


def generate_random_cities(n, width=100, height=100):
    return [(random.uniform(0, width), random.uniform(0, height)) for _ in range(n)]


def main():
    parser = argparse.ArgumentParser(description="TSP Tour Optimization Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--algo", type=str, default="LocalBeamSearch",
                        choices=["SimulatedAnnealing", "HillClimbing", "LocalBeamSearch", "GeneticAlgorithm"],
                        help="Optimization algorithm class")
    parser.add_argument("--cities", type=int, default=20, help="Number of random cities (default: 20)")
    args = parser.parse_args()

    print("=" * 65)
    print(f"      TSP TOUR OPTIMIZATION DEMO ({args.cities} CITIES)")
    print("=" * 65)

    random.seed(42)
    cities = generate_random_cities(args.cities)
    problem = TSPProblem(cities)

    initial_dist = -problem.value(problem.initial_state)
    print(f"Initial Tour Distance: {initial_dist:.2f}")

    # Map CLI string to algorithm class
    solvers = {
        "SimulatedAnnealing": SimulatedAnnealing,
        "HillClimbing": HillClimbing,
        "LocalBeamSearch": LocalBeamSearch,
        "GeneticAlgorithm": GeneticAlgorithm
    }
    solver_cls = solvers.get(args.algo, SimulatedAnnealing)

    print(f"\nExecuting {solver_cls.__name__}...")
    solver = solver_cls(problem)

    t0 = time.time()
    res = solver.run()
    dur = time.time() - t0

    best_st = getattr(solver, 'best_state', None) or getattr(solver, 'solution_node', None).state
    best_dist = -problem.value(best_st)
    print(f"\nOptimization Complete:")
    print(f"  Final Best Tour Distance: {best_dist:.2f}")
    print(f"  Runtime:                {dur:.4f} seconds")

    if args.vis:
        print(f"\nLaunching Pygame TSP Visualizer with {solver_cls.__name__}...")
        vis = TSPVisualizer(num_cities=args.cities, solver_class=solver_cls)
        vis.run()
    else:
        print("=" * 65)


if __name__ == "__main__":
    main()

