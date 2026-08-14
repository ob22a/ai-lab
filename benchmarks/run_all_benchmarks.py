"""
benchmarks/run_all_benchmarks.py

Unified benchmark execution script. Runs 30-iteration (or --runs N) benchmarks
across all AI Lab domains and generates separate CSV files in results/:

  - results/search_8puzzle.csv
  - results/search_15puzzle.csv
  - results/search_maze.csv
  - results/local_search_tsp.csv
  - results/local_search_nqueens.csv
  - results/csp_benchmarks.csv
  - results/game_tournament.csv

Usage:
  python benchmarks/run_all_benchmarks.py --runs 30
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import benchmarks.search_benchmark as sb
import benchmarks.local_search_benchmark as lsb
import benchmarks.csp_benchmark as cb
import benchmarks.game_benchmark as gb


def main():
    parser = argparse.ArgumentParser(description="Run all AI Lab benchmarks and populate CSV results.")
    parser.add_argument("--runs", type=int, default=30, help="Number of benchmark iterations per algorithm/pairing (default: 30)")
    args = parser.parse_args()

    num_runs = args.runs
    print("=" * 80)
    print(f"AI Lab - FULL BENCHMARK SUITE ({num_runs} RUNS PER DOMAIN/ALGORITHM)")
    print("=" * 80)

    # 1. Search Algorithms (8-Puzzle, 15-Puzzle, Maze)
    print("\n[1/4] Running Search Algorithm Benchmarks...")
    sb.main(num_runs=num_runs)

    # 2. Local Search & Optimization (TSP, N-Queens)
    print("\n[2/4] Running Local Search & Optimization Benchmarks...")
    lsb.main(num_runs=num_runs)

    # 3. CSP Solvers
    print("\n[3/4] Running Constraint Satisfaction Problem (CSP) Benchmarks...")
    cb.main(num_runs=num_runs)

    # 4. Adversarial Game Tournament
    print("\n[4/4] Running Adversarial Game Tournament Benchmarks...")
    gb.run_game_tournament(num_runs=num_runs)

    print("\n" + "=" * 80)
    print("ALL BENCHMARK CSVs SUCCESSFULLY CREATED & POPULATED IN results/")
    print("Run 'python benchmarks/generate_report.py' to generate all report diagrams!")
    print("=" * 80)


if __name__ == "__main__":
    main()

