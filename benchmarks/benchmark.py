"""
benchmarks/benchmark.py — Reusable benchmark engine.

Usage:
    from benchmarks.benchmark import Benchmark, BenchmarkEntry
    entries = [
        BenchmarkEntry(label="A* / 8-puzzle easy", algo_class=AStar, algo_kwargs={}, problem=p1),
        BenchmarkEntry(label="IDA* / 8-puzzle easy", algo_class=IDAStar, algo_kwargs={}, problem=p2),
    ]
    Benchmark(entries).run(csv_path="results/search.csv")
"""

import csv
import time
from dataclasses import dataclass
from typing import Any

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


_COLUMNS = [
    "Label", "Success", "Path Cost",
    "Nodes Expanded", "Nodes Generated",
    "Runtime (s)", "Max Frontier",
]


class Benchmark:
    def __init__(self, entries: list[BenchmarkEntry]):
        self.entries = entries
        self.results: list[BenchmarkResult] = []

    def run(self, csv_path: str = None, verbose: bool = True) -> list[BenchmarkResult]:
        self.results.clear()

        for entry in self.entries:
            kwargs = entry.algo_kwargs or {}
            try:
                algo = entry.algo_class(entry.problem, **kwargs)
                result: Result = algo.run()
            except Exception as e:
                result = Result(success=False, runtime=0.0)
                if verbose:
                    print(f"  ERROR [{entry.label}]: {e}")

            br = BenchmarkResult(
                label=entry.label,
                success=result.success,
                path_cost=result.path_cost,
                nodes_expanded=result.nodes_expanded,
                nodes_generated=result.nodes_generated,
                runtime=result.runtime,
                max_frontier_size=result.max_frontier_size,
            )
            self.results.append(br)

        if verbose:
            self._print_table()

        if csv_path:
            self._save_csv(csv_path)

        return self.results

    def _print_table(self):
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
                str(r.max_frontier_size),
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
                    round(r.runtime, 6), r.max_frontier_size,
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
        "Max Frontier": "max_frontier_size",
    }
    return mapping[col]
