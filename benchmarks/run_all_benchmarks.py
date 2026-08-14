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

# Hide pygame prompt from spamming during multiprocessing runs
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import benchmarks.search_benchmark as sb
import benchmarks.local_search_benchmark as lsb
import benchmarks.csp_benchmark as cb
import benchmarks.game_benchmark as gb


import glob

def main():
    parser = argparse.ArgumentParser(description="Run all AI Lab benchmarks and populate CSV results.")
    parser.add_argument("--runs", type=int, default=30, help="Number of benchmark iterations per algorithm/pairing (default: 30)")
    parser.add_argument("--reset", action="store_true", help="Delete existing CSVs in results/ before running")
    args = parser.parse_args()

    num_runs = args.runs
    
    if args.reset and os.path.exists("results"):
        print("Cleaning old results...")
        for f in glob.glob("results/*.csv"):
            os.remove(f)
            
    print("=" * 80)
    print(f"AI Lab - FULL BENCHMARK SUITE ({num_runs} RUNS PER DOMAIN/ALGORITHM)")
    print("=" * 80)

    search_runs = num_runs
    csp_game_runs = min(num_runs, 10)  # Use 10 or less for deterministic suites

    # 1. Search Algorithms (8-Puzzle, 15-Puzzle, Maze)
    print(f"\n[1/5] Running Search Algorithm Benchmarks ({search_runs} runs)...")
    sb.main(num_runs=search_runs)

    # 2. Local Search & Optimization (TSP, N-Queens)
    print(f"\n[2/5] Running Local Search & Optimization Benchmarks ({search_runs} runs)...")
    lsb.main(num_runs=search_runs)

    # 3. CSP Solvers
    print(f"\n[3/5] Running Constraint Satisfaction Problem (CSP) Benchmarks ({csp_game_runs} runs)...")
    cb.main(num_runs=csp_game_runs)

    # 4. Adversarial Game Tournament
    print(f"\n[4/5] Running Adversarial Game Tournament Benchmarks ({csp_game_runs} runs)...")
    gb.run_game_tournament(num_runs=csp_game_runs)
    
    # 5. Online Search
    print("\n[5/5] Running Online Search (LRTA*) Benchmark...")
    os.system(f"{sys.executable} -m benchmarks.online_search_benchmark")

    print("\n" + "=" * 80)
    print("ALL BENCHMARK CSVs SUCCESSFULLY CREATED & POPULATED IN results/")
    print("Run 'python benchmarks/generate_report.py' to generate all report diagrams!")
    print("=" * 80)


if __name__ == "__main__":
    main()

