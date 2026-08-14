"""
benchmarks/local_search_benchmark.py

Runs Local Search & Optimization algorithms on TSP and N-Queens domains.
Outputs: results/local_search_tsp.csv, results/local_search_nqueens.csv
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from benchmarks.benchmark import Benchmark, BenchmarkEntry

from domains.tsp.TSPProblem import TSPProblem
from domains.n_queens.NQueensProblem import NQueensProblem

from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm

LOCAL_TIMEOUT_S = 10.0

ALL_ALGOS = [
    ("Hill Climbing", HillClimbing, {}),
    ("Simulated Annealing", SimulatedAnnealing, {}),
    ("Local Beam (k=5)", LocalBeamSearch, {"k": 5}),
    ("Genetic Algorithm", GeneticAlgorithm, {"pop_size": 50, "max_generations": 300}),
]


def make_tsp_problem(num_cities=20):
    random.seed(42)
    cities = [(random.uniform(0.05, 0.95), random.uniform(0.05, 0.95)) for _ in range(num_cities)]
    return TSPProblem(cities)


def make_nqueens_problem(n=8):
    return NQueensProblem(n=n)


def _filter_algos(algo_filter):
    if not algo_filter:
        return ALL_ALGOS
    filt = {a.strip().lower() for a in algo_filter}
    return [(n, c, k) for n, c, k in ALL_ALGOS if any(f in n.lower() for f in filt)]


def main(num_runs=30, domains=None, algo_filter=None, reset=False):
    domains = domains or ["tsp", "nqueens"]
    algos = _filter_algos(algo_filter)

    if "tsp" in domains:
        print(f"\n=== Running TSP Optimization Benchmark ({num_runs} runs) ===")
        tsp_prob = make_tsp_problem(20)
        tsp_entries = [
            BenchmarkEntry(label=f"{name} / TSP (20 Cities)", algo_class=cls, problem=tsp_prob, algo_kwargs=kw)
            for name, cls, kw in algos
        ]
        Benchmark(tsp_entries).run(
            csv_path="results/local_search_tsp.csv",
            num_runs=num_runs,
            timeout=LOCAL_TIMEOUT_S,
            verbose=True,
            reset=reset,
        )

    if "nqueens" in domains:
        print(f"\n=== Running N-Queens Local Search Benchmark ({num_runs} runs) ===")
        nq_prob = make_nqueens_problem(8)
        nq_entries = [
            BenchmarkEntry(label=f"{name} / 8-Queens", algo_class=cls, problem=nq_prob, algo_kwargs=kw)
            for name, cls, kw in algos
        ]
        Benchmark(nq_entries).run(
            csv_path="results/local_search_nqueens.csv",
            num_runs=num_runs,
            timeout=LOCAL_TIMEOUT_S,
            verbose=True,
            reset=reset,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--domains", type=str, default="tsp,nqueens")
    parser.add_argument("--algos", type=str, default="")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    domain_list = [d.strip() for d in args.domains.split(",") if d.strip()]
    algo_list = [a.strip() for a in args.algos.split(",") if a.strip()] or None
    main(num_runs=args.runs, domains=domain_list, algo_filter=algo_list, reset=args.reset)
