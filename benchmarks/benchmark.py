"""
benchmarks/benchmark.py — Reusable multi-run process-isolated benchmark engine.

Usage:
    from benchmarks.benchmark import Benchmark, BenchmarkEntry
    entries = [
        BenchmarkEntry(label="A* / 8-puzzle easy", algo_class=AStar, algo_kwargs={}, problem=p1),
        BenchmarkEntry(label="IDA* / 8-puzzle easy", algo_class=IDAStar, algo_kwargs={}, problem=p2),
    ]
    Benchmark(entries).run(csv_path="results/search_benchmark.csv", num_runs=30, timeout=10.0)
"""

import csv
import copy
import time
import math
import multiprocessing
from dataclasses import dataclass
from typing import Any, List, Optional

from core.result import Result


@dataclass
class BenchmarkEntry:
    label: str
    algo_class: type
    problem: Any
    algo_kwargs: dict = None   # extra kwargs forwarded to algo_class(problem, **kwargs)


@dataclass
class BenchmarkResult:
    label: str
    success: bool
    path_cost: float
    nodes_expanded: int
    nodes_generated: int
    runtime: float
    max_frontier_size: int
    runtime_std: float = 0.0
    runs_count: int = 1


_COLUMNS = [
    "Label", "Success", "Path Cost",
    "Nodes Expanded", "Nodes Generated",
    "Runtime (s)", "Runtime Std", "Max Frontier", "Runs"
]


def _worker_process_target(entry: BenchmarkEntry, queue: multiprocessing.Queue):
    """Worker process target that runs an algorithm instance isolated from main process."""
    try:
        p_copy = copy.deepcopy(entry.problem)
        kwargs = entry.algo_kwargs or {}
        t0 = time.perf_counter()
        algo = entry.algo_class(p_copy, **kwargs)
        res = algo.run()
        elapsed = time.perf_counter() - t0
        if res:
            res.runtime = elapsed
        queue.put((True, res, None))
    except Exception as ex:
        queue.put((False, None, str(ex)))


class Benchmark:
    def __init__(self, entries: List[BenchmarkEntry]):
        self.entries = entries
        self.results: List[BenchmarkResult] = []

    def run(self, csv_path: Optional[str] = None, num_runs: int = 1, timeout: float = 10.0, verbose: bool = True) -> List[BenchmarkResult]:
        self.results.clear()

        for entry in self.entries:
            kwargs = entry.algo_kwargs or {}
            runtimes = []
            last_result = None
            actual_executed_runs = 0

            actual_runs = num_runs

            for r in range(actual_runs):
                actual_executed_runs += 1
                queue = multiprocessing.Queue()
                proc = multiprocessing.Process(target=_worker_process_target, args=(entry, queue), daemon=True)
                
                t0 = time.perf_counter()
                proc.start()
                proc.join(timeout=timeout)
                elapsed = time.perf_counter() - t0

                if proc.is_alive():
                    # Process timed out: terminate forcefully to free RAM
                    proc.terminate()
                    proc.join(timeout=1.0)
                    if proc.is_alive():
                        proc.kill()
                    last_result = Result(success=False, runtime=timeout)
                    if verbose:
                        print(f"  TIMEOUT [{entry.label}] (>{timeout:.1f}s)")
                    break

                # Extract result from queue
                if not queue.empty():
                    success_flag, res, err_msg = queue.get()
                    if err_msg:
                        last_result = Result(success=False, runtime=elapsed)
                        if verbose and r == 0:
                            print(f"  ERROR [{entry.label}]: {err_msg}")
                        break
                    if res:
                        last_result = res
                        if res.success:
                            runtimes.append(res.runtime)
                else:
                    last_result = Result(success=False, runtime=elapsed)

                # Adaptive scaling for very fast vs slow runs to prevent long benchmark delays
                if r == 0 and elapsed > 1.0 and actual_runs > 3:
                    actual_runs = min(num_runs, 3)

            if not last_result:
                last_result = Result(success=False, runtime=0.0)

            mean_runtime = sum(runtimes) / len(runtimes) if runtimes else last_result.runtime
            std_runtime = math.sqrt(sum((x - mean_runtime)**2 for x in runtimes) / len(runtimes)) if len(runtimes) > 1 else 0.0

            br = BenchmarkResult(
                label=entry.label,
                success=last_result.success,
                path_cost=last_result.path_cost,
                nodes_expanded=last_result.nodes_expanded,
                nodes_generated=last_result.nodes_generated,
                runtime=mean_runtime,
                runtime_std=std_runtime,
                max_frontier_size=last_result.max_frontier_size,
                runs_count=actual_executed_runs
            )
            self.results.append(br)

        if verbose:
            self._print_table()

        if csv_path:
            self._save_csv(csv_path)

        return self.results

    def _print_table(self):
        if not self.results:
            return

        col_widths = [max(len(c), max((len(str(getattr(r, _field_for(c)))) for r in self.results), default=0))
                      for c in _COLUMNS]

        header = "  ".join(c.ljust(w) for c, w in zip(_COLUMNS, col_widths))
        separator = "  ".join("-" * w for w in col_widths)
        print("\n" + header)
        print(separator)

        for r in self.results:
            row = [
                r.label,
                str(r.success),
                f"{r.path_cost:.1f}",
                str(r.nodes_expanded),
                str(r.nodes_generated),
                f"{r.runtime:.5f}",
                f"{r.runtime_std:.5f}",
                str(r.max_frontier_size),
                str(r.runs_count)
            ]
            print("  ".join(v.ljust(w) for v, w in zip(row, col_widths)))
        print()

    def _save_csv(self, path: str):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(_COLUMNS)
            for r in self.results:
                writer.writerow([
                    r.label, r.success, r.path_cost,
                    r.nodes_expanded, r.nodes_generated,
                    round(r.runtime, 6), round(r.runtime_std, 6),
                    r.max_frontier_size, r.runs_count
                ])
        print(f"Saved -> {path}")


def _field_for(col: str) -> str:
    mapping = {
        "Label": "label",
        "Success": "success",
        "Path Cost": "path_cost",
        "Nodes Expanded": "nodes_expanded",
        "Nodes Generated": "nodes_generated",
        "Runtime (s)": "runtime",
        "Runtime Std": "runtime_std",
        "Max Frontier": "max_frontier_size",
        "Runs": "runs_count"
    }
    return mapping[col]

