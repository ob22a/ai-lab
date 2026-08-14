"""
benchmarks/csp_benchmark.py — CSP solver benchmarks with raw per-run CSV output.
"""

import argparse
import copy
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from benchmarks.benchmark import append_result_to_csv
from core.result import Result

from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default, inference_default
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.heuristics.LCV import lcv
from csp.inference.ForwardChecking import forward_checking
from csp.inference.MAC import mac
from csp.MinConflicts import MinConflictsSolver
from csp.Backjumping import BackjumpingSolver
from csp.CBJ import CBJSolver
from csp.SymmetricBacktracking import SymmetricBacktrackingSolver

from domains.map_coloring.MapColoring import MapColoringCSP
from domains.n_queens.NQueensCSP import NQueensCSP
from domains.sudoku.Sudoku import SudokuCSP, SUDOKU_EASY, SUDOKU_HARD

CSP_TIMEOUT_S = 10.0


def _run_csp_solver(solver_factory, timeout: float) -> Result:
    t0 = time.perf_counter()
    try:
        solver = solver_factory()
        solver.solve()
        elapsed = time.perf_counter() - t0
        if elapsed > timeout:
            return Result(success=False, runtime=timeout, nodes_expanded=getattr(solver, "nodes_expanded", 0))
        success = getattr(solver, "status", "") == "SUCCESS"
        return Result(
            success=success,
            runtime=elapsed,
            nodes_expanded=getattr(solver, "nodes_expanded", 0),
            nodes_generated=getattr(solver, "nodes_generated", 0),
            path_cost=1.0 if success else 0.0,
        )
    except Exception:
        return Result(success=False, runtime=timeout)


def _solver_configs():
    return [
        ("BT (Naive)", lambda csp: BacktrackingSolver(copy.deepcopy(csp))),
        ("BT+MRV", lambda csp: BacktrackingSolver(copy.deepcopy(csp), select_unassigned_variable=mrv)),
        ("BT+FC", lambda csp: BacktrackingSolver(copy.deepcopy(csp), inference=forward_checking)),
        ("BT+MAC", lambda csp: BacktrackingSolver(copy.deepcopy(csp), inference=mac)),
        ("BT+MRV+FC", lambda csp: BacktrackingSolver(copy.deepcopy(csp), select_unassigned_variable=mrv, inference=forward_checking)),
        ("BT+MRV+MAC", lambda csp: BacktrackingSolver(copy.deepcopy(csp), select_unassigned_variable=mrv, inference=mac)),
        ("BT+Degree", lambda csp: BacktrackingSolver(copy.deepcopy(csp), select_unassigned_variable=mrv_with_degree_heuristic)),
        ("BT+LCV", lambda csp: BacktrackingSolver(copy.deepcopy(csp), order_domain_values=lcv)),
        ("Backjumping", lambda csp: BackjumpingSolver(copy.deepcopy(csp), select_unassigned_variable=mrv)),
        ("CBJ", lambda csp: CBJSolver(copy.deepcopy(csp))),
        ("Symmetric BT", lambda csp: SymmetricBacktrackingSolver(copy.deepcopy(csp))),
        ("Min-Conflicts", lambda csp: MinConflictsSolver(copy.deepcopy(csp))),
    ]


def _problem_configs():
    return [
        ("Map Coloring", lambda: MapColoringCSP()),
        ("8-Queens", lambda: NQueensCSP(8)),
        ("Sudoku Easy", lambda: SudokuCSP(SUDOKU_EASY)),
        ("Sudoku Hard", lambda: SudokuCSP(SUDOKU_HARD)),
    ]


SKIP_COMBOS = {
    ("BT (Naive)", "Sudoku Easy"),
    ("BT (Naive)", "Sudoku Hard"),
    ("BT+MRV", "Sudoku Hard"),
    ("Min-Conflicts", "Sudoku Easy"),
    ("Min-Conflicts", "Sudoku Hard"),
}


def main(num_runs=30, problem_filter=None, solver_filter=None, reset=False):
    csv_path = "results/csp_benchmarks.csv"
    configs = _solver_configs()
    problems = _problem_configs()

    if solver_filter:
        filt = {s.strip().lower() for s in solver_filter}
        configs = [(n, f) for n, f in configs if any(x in n.lower() for x in filt)]
    if problem_filter:
        filt = {p.strip().lower() for p in problem_filter}
        problems = [(n, f) for n, f in problems if any(x in n.lower() for x in filt)]

    print(f"\n=== Running CSP Benchmarks ({num_runs} runs per solver) ===")
    first_write = reset

    for prob_name, prob_factory in problems:
        print(f"  Domain: {prob_name}")
        for solver_name, solver_factory in configs:
            if (solver_name, prob_name) in SKIP_COMBOS:
                print(f"    SKIP {solver_name} on {prob_name} (known hang)")
                continue
            label = f"{solver_name} / {prob_name}"
            for run_idx in range(num_runs):
                csp = prob_factory()
                res = _run_csp_solver(lambda c=csp: solver_factory(c), CSP_TIMEOUT_S)
                append_result_to_csv(csv_path, label, run_idx + 1, res, reset=first_write)
                first_write = False
                if run_idx == 0 and not res.success:
                    print(f"    FAIL {label} ({res.runtime:.2f}s)")
                    break

    print(f"Saved raw CSP runs -> {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--domains", type=str, default="", help="Comma-separated CSP domains to run")
    parser.add_argument("--algos", type=str, default="", help="Comma-separated solver name filter")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    prob_list = [d.strip() for d in args.domains.split(",") if d.strip()] or None
    algo_list = [a.strip() for a in args.algos.split(",") if a.strip()] or None
    main(num_runs=args.runs, problem_filter=prob_list, solver_filter=algo_list, reset=args.reset)
