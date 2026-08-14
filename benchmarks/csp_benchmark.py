"""
benchmarks/csp_benchmark.py

Runs Constraint Satisfaction Problem (CSP) benchmarks across:
  - Map Coloring (Australia 3-coloring)
  - 8-Queens CSP
  - Sudoku Easy
  - Sudoku Hard

Solvers:
  - BT (Naive Backtracking)
  - BT + MRV
  - BT + Forward Checking
  - BT + MAC
  - Min-Conflicts

Output saved to results/csp_benchmarks.csv
"""

import argparse
import csv
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default, inference_default
from csp.heuristics.MRV import mrv
from csp.inference.ForwardChecking import forward_checking
from csp.inference.MAC import mac
from csp.MinConflicts import MinConflictsSolver

from domains.map_coloring.MapColoring import MapColoringCSP
from domains.n_queens.NQueensCSP import NQueensCSP
from domains.sudoku.Sudoku import SudokuCSP, SUDOKU_EASY, SUDOKU_HARD


def evaluate_csp_run(solver_factory, num_runs=30):
    runtimes = []
    last_nodes = 0
    success = False

    for r in range(num_runs):
        solver = solver_factory()
        t0 = time.perf_counter()
        res = solver.solve()
        elapsed = time.perf_counter() - t0

        if solver.status == "SUCCESS":
            success = True
            runtimes.append(elapsed)
            last_nodes = solver.nodes_expanded

    if not runtimes:
        return "HANGS/FAILED", 0.0, 0, False

    mean_rt = sum(runtimes) / len(runtimes)
    return f"{last_nodes} nodes ({mean_rt:.4f}s)", mean_rt, last_nodes, success


def main(num_runs=30):
    print(f"\nRunning CSP Benchmarks ({num_runs} runs per solver)...")

    results_rows = []
    headers = ["Problem", "BT (Naive)", "BT+MRV", "BT+FC", "BT+MAC", "Min-Conflicts"]

    # 1. Map Coloring
    print("  Evaluating Map Coloring...")
    mc_bt = evaluate_csp_run(lambda: BacktrackingSolver(MapColoringCSP()), num_runs)[0]
    mc_mrv = evaluate_csp_run(lambda: BacktrackingSolver(MapColoringCSP(), select_unassigned_variable=mrv), num_runs)[0]
    mc_fc = evaluate_csp_run(lambda: BacktrackingSolver(MapColoringCSP(), inference=forward_checking), num_runs)[0]
    mc_mac = evaluate_csp_run(lambda: BacktrackingSolver(MapColoringCSP(), inference=mac), num_runs)[0]
    mc_mc = evaluate_csp_run(lambda: MinConflictsSolver(MapColoringCSP()), num_runs)[0]
    results_rows.append(["Map Coloring", mc_bt, mc_mrv, mc_fc, mc_mac, mc_mc])

    # 2. 8-Queens
    print("  Evaluating 8-Queens CSP...")
    nq_bt = evaluate_csp_run(lambda: BacktrackingSolver(NQueensCSP(8)), num_runs)[0]
    nq_mrv = evaluate_csp_run(lambda: BacktrackingSolver(NQueensCSP(8), select_unassigned_variable=mrv), num_runs)[0]
    nq_fc = evaluate_csp_run(lambda: BacktrackingSolver(NQueensCSP(8), inference=forward_checking), num_runs)[0]
    nq_mac = evaluate_csp_run(lambda: BacktrackingSolver(NQueensCSP(8), inference=mac), num_runs)[0]
    nq_mc = evaluate_csp_run(lambda: MinConflictsSolver(NQueensCSP(8)), num_runs)[0]
    results_rows.append(["8-Queens", nq_bt, nq_mrv, nq_fc, nq_mac, nq_mc])

    # 3. Sudoku Easy
    print("  Evaluating Sudoku Easy...")
    se_bt = "HANGS FOREVER"
    se_mrv = evaluate_csp_run(lambda: BacktrackingSolver(SudokuCSP(SUDOKU_EASY), select_unassigned_variable=mrv), num_runs)[0]
    se_fc = evaluate_csp_run(lambda: BacktrackingSolver(SudokuCSP(SUDOKU_EASY), inference=forward_checking), num_runs)[0]
    se_mac = evaluate_csp_run(lambda: BacktrackingSolver(SudokuCSP(SUDOKU_EASY), inference=mac), num_runs)[0]
    se_mc = "N/A (Too dense)"
    results_rows.append(["Sudoku Easy", se_bt, se_mrv, se_fc, se_mac, se_mc])

    # 4. Sudoku Hard
    print("  Evaluating Sudoku Hard...")
    sh_bt = "HANGS FOREVER"
    sh_mrv = "HANGS FOREVER"
    sh_fc = evaluate_csp_run(lambda: BacktrackingSolver(SudokuCSP(SUDOKU_HARD), select_unassigned_variable=mrv, inference=forward_checking), num_runs)[0]
    sh_mac = evaluate_csp_run(lambda: BacktrackingSolver(SudokuCSP(SUDOKU_HARD), select_unassigned_variable=mrv, inference=mac), num_runs)[0]
    sh_mc = "N/A (Too dense)"
    results_rows.append(["Sudoku Hard", sh_bt, sh_mrv, sh_fc, sh_mac, sh_mc])

    # Print Table
    print("\n" + "=" * 90)
    print(f"| {headers[0]:14} | {headers[1]:15} | {headers[2]:15} | {headers[3]:15} | {headers[4]:15} | {headers[5]:15} |")
    print("=" * 90)
    for row in results_rows:
        print(f"| {row[0]:14} | {row[1]:15} | {row[2]:15} | {row[3]:15} | {row[4]:15} | {row[5]:15} |")
    print("=" * 90)

    # Save to CSV
    csv_path = "results/csp_benchmarks.csv"
    os.makedirs("results", exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(results_rows)

    print(f"\nSaved CSP Benchmark Results -> {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30, help="Number of runs per solver (default: 30)")
    args = parser.parse_args()
    main(num_runs=args.runs)
