"""
benchmarks/search_benchmark.py

Runs all search algorithms across:
  - 3 random 8-puzzle instances  (easy / medium / hard)
  - 2 random 15-puzzle instances (informed algorithms only)
  - 3 mazes (10x10, 30x30, 50x50)

Results printed and saved to results/search_benchmark.csv.

Timeout: 30s per entry via subprocess — guaranteed kill on Windows.
"""

import copy
import csv
import os
import subprocess
import sys
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from benchmarks.benchmark import Benchmark, BenchmarkEntry, BenchmarkResult, _COLUMNS

from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from domains.n_puzzle.PatternDatabase import PatternDatabase

from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from domains.maze.MazeSearch import MazeSearchProblem

from search.uninformed.DFS import DFS
from search.uninformed.BFS import BFS
from search.uninformed.UCS import UCS
from search.uninformed.IDDFS import OptimizedIDDFS as IDDFS
from search.uninformed.BidirectionalSearch import BidirectionalSearch
from search.informed.GBFS import GreedyBestFirstSearch
from search.informed.AStar import AStar
from search.informed.IDAStar import IDAStar
from search.informed.RBFS import RBFS
from search.informed.SMAstar import SMAStar
from search.informed.IGBFS import IGBFS
from search.informed.BidirectionalAStar import BidirectionalAStar

TIMEOUT_S = 30


# --------------------------------------------------------------------------- #
# Problem factories
# --------------------------------------------------------------------------- #

def make_8puzzle(generator, moves, pdb_8):
    state = generator.generate(moves=moves)
    return NPuzzleProblem(state, NPuzzle(3), heuristic_type="pattern_db", pdbs=pdb_8)


def make_15puzzle(generator, moves, pdb_15):
    state = generator.generate(moves=moves)
    return NPuzzleProblem(state, NPuzzle(4), heuristic_type="pattern_db", pdbs=pdb_15)


def make_maze(rows, cols):
    maze = RandomizedKruskalGenerator(rows=rows, cols=cols).generate()
    return MazeSearchProblem(maze, (0, 0), (rows - 1, cols - 1))


# --------------------------------------------------------------------------- #
# Algorithm roster
# --------------------------------------------------------------------------- #

UNINFORMED = [
    ("DFS",           DFS,                 {}),
    ("BFS",           BFS,                 {}),
    ("UCS",           UCS,                 {}),
    ("IDDFS",         IDDFS,               {"visualize": False}),
    ("Bidir-Search",  BidirectionalSearch, {}),
]

# IGBFS excluded from 15-puzzle: it's inadmissible and can produce astronomically
# long paths, making it hang even longer than uninformed algorithms.
INFORMED = [
    ("GBFS",          GreedyBestFirstSearch, {}),
    ("A*",            AStar,               {}),
    ("IDA*",          IDAStar,             {}),
    ("RBFS",          RBFS,                {}),
    ("SMA*(1000)",    SMAStar,             {"memory_limit": 1000}),
    ("Bidir-A*",      BidirectionalAStar,  {}),
]

INFORMED_WITH_IGBFS = INFORMED + [("IGBFS", IGBFS, {})]

ALL_ALGOS = UNINFORMED + INFORMED_WITH_IGBFS


# --------------------------------------------------------------------------- #
# Benchmark runner
# --------------------------------------------------------------------------- #

def run_entry(algo_class, problem, algo_kwargs, label):
    """Run one algorithm on one problem with a thread-based timeout."""
    import threading
    result_box = [None]
    err_box = [None]

    def target():
        try:
            algo = algo_class(problem, **algo_kwargs)
            result_box[0] = algo.run()
        except Exception as e:
            err_box[0] = str(e)

    t = threading.Thread(target=target, daemon=True)
    t0 = time.perf_counter()
    t.start()
    t.join(timeout=TIMEOUT_S)
    elapsed = time.perf_counter() - t0

    if t.is_alive():
        return BenchmarkResult(
            label=label, success=False, path_cost=0,
            nodes_expanded=0, nodes_generated=0,
            runtime=elapsed, max_frontier_size=0,
        ), "TIMEOUT"

    if err_box[0]:
        return BenchmarkResult(
            label=label, success=False, path_cost=0,
            nodes_expanded=0, nodes_generated=0,
            runtime=elapsed, max_frontier_size=0,
        ), err_box[0]

    r = result_box[0]
    return BenchmarkResult(
        label=label,
        success=r.success,
        path_cost=r.path_cost,
        nodes_expanded=r.nodes_expanded,
        nodes_generated=r.nodes_generated,
        runtime=r.runtime,
        max_frontier_size=r.max_frontier_size,
    ), None


def run_group(group_label, problem_fn, algos, results):
    base = problem_fn()
    print(f"\n  [{group_label}]")
    for name, cls, kwargs in algos:
        label = f"{name} / {group_label}"
        p = copy.deepcopy(base)
        br, err = run_entry(cls, p, kwargs, label)
        status = "TIMEOUT" if err == "TIMEOUT" else ("OK" if br.success else f"FAIL({err or 'no solution'})")
        print(f"    {name:<18} {status:<20} cost={br.path_cost:<8.0f} exp={br.nodes_expanded:<8} {br.runtime:.4f}s")
        results.append(br)


def save_csv(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(_COLUMNS)
        for r in results:
            writer.writerow([
                r.label, r.success, r.path_cost,
                r.nodes_expanded, r.nodes_generated,
                round(r.runtime, 6), r.max_frontier_size,
            ])
    print(f"\nSaved -> {path}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    import random
    random.seed(2026)

    print("Loading Pattern Databases...")
    pdb_8 = [
        PatternDatabase("./pdbs/8puzzle_1234.bin"),
        PatternDatabase("./pdbs/8puzzle_5678.bin"),
    ]
    pdb_15 = [
        PatternDatabase("./pdbs/15puzzle_12345.bin"),
        PatternDatabase("./pdbs/15puzzle_6789a.bin"),
        PatternDatabase("./pdbs/15puzzle_bcdef.bin"),
    ]

    gen_8  = NPuzzleGenerator(3)
    gen_15 = NPuzzleGenerator(4)

    results: list[BenchmarkResult] = []

    print("\n=== 8-Puzzle Benchmark ===")
    for diff_label, moves in [("8pzl easy", 8), ("8pzl medium", 18), ("8pzl hard", 28)]:
        run_group(diff_label, lambda m=moves: make_8puzzle(gen_8, m, pdb_8), ALL_ALGOS, results)

    print("\n=== 15-Puzzle Benchmark (informed only) ===")
    for diff_label, moves in [("15pzl medium", 25), ("15pzl hard", 45)]:
        run_group(diff_label, lambda m=moves: make_15puzzle(gen_15, m, pdb_15), INFORMED, results)

    print("\n=== Maze Benchmark ===")
    for rows, cols in [(10, 10), (30, 30), (50, 50)]:
        run_group(f"maze {rows}x{cols}", lambda r=rows, c=cols: make_maze(r, c), ALL_ALGOS, results)

    save_csv(results, "results/search_benchmark.csv")
    print(f"\nTotal entries: {len(results)}")


if __name__ == "__main__":
    main()
