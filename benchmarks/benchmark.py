"""
benchmarks/benchmark.py — Reusable multi-run process-isolated benchmark engine.

Usage:
    from benchmarks.benchmark import Benchmark, BenchmarkEntry, append_result_to_csv
    entries = [
        BenchmarkEntry(label="A* / 8-puzzle easy", algo_class=AStar, algo_kwargs={}, problem=p1),
    ]
    Benchmark(entries).run(csv_path="results/search_8puzzle.csv", num_runs=30, timeout=20.0)
"""

import csv
import copy
import math
import multiprocessing
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from core.result import Result

# Increase recursion limit to allow pickling very deep Node paths (e.g. 50x50 mazes)
sys.setrecursionlimit(10000)

RAW_COLUMNS = [
    "Label", "Run#", "Success", "Path Cost",
    "Nodes Expanded", "Nodes Generated",
    "Runtime (s)", "Max Frontier", "Timestamp",
]

# Backward-compatible alias used by some benchmark scripts
_COLUMNS = RAW_COLUMNS


@dataclass
class BenchmarkEntry:
    label: str
    algo_class: type
    problem: Any
    algo_kwargs: dict = field(default_factory=dict)


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


def _worker(algo_class: type, problem: Any, algo_kwargs: dict, result_queue: multiprocessing.Queue):
    """Run one algorithm instance inside an isolated child process."""
    import sys

    sys.setrecursionlimit(20000)
    try:
        p_copy = copy.deepcopy(problem)
        kwargs = algo_kwargs or {}
        t0 = time.perf_counter()
        algo = algo_class(p_copy, **kwargs)
        res = algo.run()
        elapsed = time.perf_counter() - t0
        if res:
            res.runtime = elapsed
            res.solution = None  # Prevent RecursionError when pickling deep Node chains
        result_queue.put(("ok", res))
    except Exception as exc:
        result_queue.put(("error", str(exc)))


def _run_single_entry(algo_class: type, problem: Any, algo_kwargs: dict, timeout: float) -> Tuple[Optional[Result], float]:
    """Run one benchmark entry in a child process with a hard timeout."""
    ctx = multiprocessing.get_context("spawn")
    result_queue: multiprocessing.Queue = ctx.Queue()
    process = ctx.Process(
        target=_worker,
        args=(algo_class, problem, algo_kwargs or {}, result_queue),
    )
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join(1.0)
        if process.is_alive():
            process.kill()
            process.join(1.0)
        return None, timeout

    if result_queue.empty():
        return None, timeout

    status, payload = result_queue.get_nowait()
    if status == "error":
        return Result(success=False, runtime=timeout), timeout
    return payload, getattr(payload, "runtime", timeout) if payload else timeout


def append_result_to_csv(
    csv_path: str,
    label: str,
    run_num: int,
    result: Optional[Result],
    *,
    reset: bool = False,
) -> None:
    """Append a single raw run row to a benchmark CSV."""
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    write_header = reset or not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    mode = "w" if reset else "a"

    if result is None:
        row = [label, run_num, False, 0.0, 0, 0, 0.0, 0, _timestamp()]
    else:
        row = [
            label,
            run_num,
            result.success,
            result.path_cost,
            result.nodes_expanded,
            result.nodes_generated,
            round(result.runtime, 6),
            result.max_frontier_size,
            _timestamp(),
        ]

    with open(csv_path, mode, newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(RAW_COLUMNS)
        writer.writerow(row)

def append_game_result_to_csv(csv_path: str, game_name: str, p1_name: str, p2_name: str, p1_wins: int, p2_wins: int, draws: int, avg_time: float, reset: bool = False) -> None:
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    write_header = reset or not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    mode = "w" if reset else "a"
    with open(csv_path, mode, newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Game", "Agent 1", "Agent 2", "Agent 1 Wins", "Agent 2 Wins", "Draws", "Avg Game Time (s)"])
        writer.writerow([game_name, p1_name, p2_name, p1_wins, p2_wins, draws, round(avg_time, 6)])


def aggregate_raw_rows(rows: List[List[str]]) -> List[BenchmarkResult]:
    """Aggregate per-run CSV rows into summary BenchmarkResult objects."""
    groups: Dict[str, List[List[str]]] = defaultdict(list)
    for row in rows:
        if row:
            groups[row[0]].append(row)

    summaries: List[BenchmarkResult] = []
    for label, group in sorted(groups.items()):
        successes = [r[2].strip().lower() in ("true", "1") for r in group]
        runtimes = [float(r[6]) for r in group if r[2].strip().lower() in ("true", "1")]
        mean_runtime = sum(runtimes) / len(runtimes) if runtimes else float(group[-1][6])
        std_runtime = (
            math.sqrt(sum((x - mean_runtime) ** 2 for x in runtimes) / len(runtimes))
            if len(runtimes) > 1
            else 0.0
        )
        last = group[-1]
        summaries.append(
            BenchmarkResult(
                label=label,
                success=any(successes),
                path_cost=float(last[3]),
                nodes_expanded=int(float(last[4])),
                nodes_generated=int(float(last[5])),
                runtime=mean_runtime,
                runtime_std=std_runtime,
                max_frontier_size=int(float(last[7])),
                runs_count=len(group),
            )
        )
    return summaries


def read_raw_csv(filepath: str) -> List[List[str]]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        return [r for r in reader if r]


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Benchmark:
    def __init__(self, entries: List[BenchmarkEntry]):
        self.entries = entries
        self.results: List[BenchmarkResult] = []

    def run(
        self,
        csv_path: Optional[str] = None,
        num_runs: int = 1,
        timeout: float = 10.0,
        verbose: bool = True,
        reset: bool = False,
        algo_filter: Optional[List[str]] = None,
    ) -> List[BenchmarkResult]:
        self.results.clear()
        raw_rows: List[List[str]] = []

        entries = self.entries
        if algo_filter:
            filt = {a.strip().lower() for a in algo_filter}
            entries = [e for e in entries if any(f in e.label.lower() for f in filt)]

        first_write = reset
        for entry in entries:
            actual_runs = max(1, num_runs)
            runtimes: List[float] = []
            last_result: Optional[Result] = None

            for r in range(actual_runs):
                prob = entry.problem[r] if isinstance(entry.problem, list) else entry.problem
                res, elapsed = _run_single_entry(entry.algo_class, prob, entry.algo_kwargs, timeout)
                if res is None:
                    res = Result(success=False, runtime=timeout)
                    elapsed = timeout

                last_result = res
                if res.success:
                    runtimes.append(res.runtime)

                if csv_path:
                    append_result_to_csv(csv_path, entry.label, r + 1, res, reset=first_write)
                    first_write = False
                raw_rows.append([
                    entry.label, str(r + 1), str(res.success), str(res.path_cost),
                    str(res.nodes_expanded), str(res.nodes_generated),
                    str(round(res.runtime, 6)), str(res.max_frontier_size), _timestamp(),
                ])

                if verbose and not res.success and r == 0:
                    print(f"  FAIL/TIMEOUT [{entry.label}] ({elapsed:.2f}s)")

                # Adaptive scaling: relative threshold based on timeout
                if r == 0 and elapsed > timeout / 2 and actual_runs > 5:
                    print(
                        f"[INFO] Adaptive scaling: reducing runs from {num_runs} to 5 "
                        f"for '{entry.label}' (first run took {elapsed:.2f}s)"
                    )
                    actual_runs = min(num_runs, 5)

            if not last_result:
                last_result = Result(success=False, runtime=0.0)

            mean_runtime = sum(runtimes) / len(runtimes) if runtimes else last_result.runtime
            std_runtime = (
                math.sqrt(sum((x - mean_runtime) ** 2 for x in runtimes) / len(runtimes))
                if len(runtimes) > 1
                else 0.0
            )
            self.results.append(
                BenchmarkResult(
                    label=entry.label,
                    success=last_result.success,
                    path_cost=last_result.path_cost,
                    nodes_expanded=last_result.nodes_expanded,
                    nodes_generated=last_result.nodes_generated,
                    runtime=mean_runtime,
                    runtime_std=std_runtime,
                    max_frontier_size=last_result.max_frontier_size,
                    runs_count=actual_runs,
                )
            )

        if verbose:
            self._print_table()

        if csv_path:
            print(f"Saved raw runs -> {csv_path}")

        return self.results

    def _print_table(self):
        if not self.results:
            return
        cols = ["Label", "Success", "Path Cost", "Nodes Expanded", "Runtime (s)", "Runs"]
        widths = [max(len(c), max(len(str(getattr(r, k))) for r in self.results)) for c, k in zip(
            cols, ["label", "success", "path_cost", "nodes_expanded", "runtime", "runs_count"]
        )]
        header = "  ".join(c.ljust(w) for c, w in zip(cols, widths))
        print("\n" + header)
        print("  ".join("-" * w for w in widths))
        for r in self.results:
            row = [
                r.label, str(r.success), f"{r.path_cost:.1f}",
                str(r.nodes_expanded), f"{r.runtime:.5f}", str(r.runs_count),
            ]
            print("  ".join(v.ljust(w) for v, w in zip(row, widths)))
        print()
