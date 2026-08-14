# =====================================================================
# TWEAKABLE CONFIGURATION - Modify these variables to test variations!
# =====================================================================
# Solvers available:   SimulatedAnnealing, HillClimbing, LocalBeamSearch, GeneticAlgorithm
# Number of Cities:    10, 15, 20, 30, 50
# =====================================================================

import sys
import random
from domains.tsp.TSPProblem import TSPProblem
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm
from visualization.TSPVisualizer import TSPVisualizer

# ── User Configuration ────────────────────────────────────────────────
N_CITIES      = 20
CHOSEN_SOLVER = LocalBeamSearch  # Options: SimulatedAnnealing, HillClimbing, LocalBeamSearch, GeneticAlgorithm
VISUALIZE     = True                # Set to False for text-only output


def generate_random_cities(n, width=100, height=100):
    return [(random.uniform(0, width), random.uniform(0, height)) for _ in range(n)]


def main():
    visualize = VISUALIZE and ("--no-vis" not in sys.argv)
    print(f"--- TSP Local Search Demo ({N_CITIES} cities) ---")
    
    cities = generate_random_cities(N_CITIES)
    problem = TSPProblem(cities)
    
    initial_dist = -problem.value(problem.initial_state)
    print(f"Initial Distance: {initial_dist:.2f}")

    print(f"\nRunning {CHOSEN_SOLVER.__name__}...")
    solver = CHOSEN_SOLVER(problem)
    res = solver.run()
    best_st = getattr(solver, 'best_state', None) or getattr(solver, 'solution_node', None).state
    best_dist = -problem.value(best_st)
    print(f"   Final Best Distance: {best_dist:.2f} (Runtime: {res.runtime:.4f}s)")

    if visualize:
        print(f"\nLaunching Pygame TSP Optimization Visualizer ({CHOSEN_SOLVER.__name__})...")
        vis = TSPVisualizer(num_cities=N_CITIES, solver_class=CHOSEN_SOLVER)
        vis.run()


if __name__ == "__main__":
    random.seed(42)
    main()
