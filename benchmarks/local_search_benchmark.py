"""
benchmarks/local_search_benchmark.py

Runs Local Search & Optimization algorithms:
  - Hill Climbing
  - Simulated Annealing
  - Local Beam Search (k=5)
  - Genetic Algorithm

Across domains:
  - TSP (20 Cities)
  - 8-Queens (Local Search formulation)

Outputs saved to separate CSV files:
  - results/local_search_tsp.csv
  - results/local_search_nqueens.csv
"""

import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from benchmarks.benchmark import Benchmark, BenchmarkEntry, BenchmarkResult
import csv

from domains.tsp.TSPProblem import TSPProblem
from domains.n_queens.NQueensProblem import NQueensProblem

from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm

_COLUMNS = [
    "Label", "Success", "Best Objective / Tour Distance",
    "Nodes Expanded", "Nodes Generated",
    "Runtime (s)", "Runtime Std", "Max Frontier", "Runs"
]


def make_tsp_problem(num_cities=20):
    random.seed(42)
    cities = [(random.uniform(0.05, 0.95), random.uniform(0.05, 0.95)) for _ in range(num_cities)]
    return TSPProblem(cities)


def make_nqueens_problem(n=8):
    return NQueensProblem(n=n)


def run_local_benchmark(entries, num_runs=30):
    results = []
    for entry in entries:
        runtimes = []
        best_values = []
        last_nodes_exp = 0
        last_nodes_gen = 0
        last_success = False

        for r in range(num_runs):
            prob = entry.problem
            solver = entry.algo_class(prob, **(entry.algo_kwargs or {}))
            t0 = time.perf_counter()
            res = solver.run()
            elapsed = time.perf_counter() - t0

            runtimes.append(elapsed)
            val = getattr(solver, 'best_value', None) or getattr(solver, 'current_value', 0)
            best_values.append(val)
            last_nodes_exp = getattr(solver, 'nodes_expanded', 0)
            last_nodes_gen = getattr(solver, 'nodes_generated', 0)
            last_success = res.success

        avg_runtime = sum(runtimes) / len(runtimes)
        import math
        std_runtime = math.sqrt(sum((x - avg_runtime)**2 for x in runtimes) / len(runtimes)) if len(runtimes) > 1 else 0.0
        avg_val = sum(best_values) / len(best_values)

        # For TSP, objective value is negative distance, so invert to positive distance
        if "TSP" in entry.label:
            score = abs(avg_val)
        else:
            score = avg_val

        results.append(BenchmarkResult(
            label=entry.label,
            success=last_success,
            path_cost=score,
            nodes_expanded=last_nodes_exp,
            nodes_generated=last_nodes_gen,
            runtime=avg_runtime,
            runtime_std=std_runtime,
            max_frontier_size=1,
            runs_count=num_runs
        ))
    return results


def save_csv(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(_COLUMNS)
        for r in results:
            writer.writerow([
                r.label, r.success, round(r.path_cost, 2),
                r.nodes_expanded, r.nodes_generated,
                round(r.runtime, 6), round(r.runtime_std, 6),
                r.max_frontier_size, r.runs_count
            ])
    print(f"Saved -> {path}")


def main(num_runs=30):
    algos = [
        ("Hill Climbing", HillClimbing, {}),
        ("Simulated Annealing", SimulatedAnnealing, {}),
        ("Local Beam (k=5)", LocalBeamSearch, {"k": 5}),
        ("Genetic Algorithm", GeneticAlgorithm, {"pop_size": 50, "max_generations": 300}),
    ]

    # 1. TSP Benchmark
    print(f"\n=== Running TSP Optimization Benchmark ({num_runs} runs) ===")
    tsp_prob = make_tsp_problem(20)
    tsp_entries = [BenchmarkEntry(label=f"{name} / TSP (20 Cities)", algo_class=cls, problem=tsp_prob, algo_kwargs=kw) for name, cls, kw in algos]
    tsp_res = run_local_benchmark(tsp_entries, num_runs=num_runs)
    save_csv(tsp_res, "results/local_search_tsp.csv")

    # 2. N-Queens Benchmark
    print(f"\n=== Running N-Queens Local Search Benchmark ({num_runs} runs) ===")
    nq_prob = make_nqueens_problem(8)
    nq_entries = [BenchmarkEntry(label=f"{name} / 8-Queens", algo_class=cls, problem=nq_prob, algo_kwargs=kw) for name, cls, kw in algos]
    nq_res = run_local_benchmark(nq_entries, num_runs=num_runs)
    save_csv(nq_res, "results/local_search_nqueens.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30, help="Number of runs per algorithm (default: 30)")
    args = parser.parse_args()
    main(num_runs=args.runs)
