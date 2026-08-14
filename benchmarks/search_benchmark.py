"""
benchmarks/search_benchmark.py

Runs all search algorithms across:
  - 8-Puzzle instances (easy / medium / hard)
  - 15-Puzzle instances (informed algorithms)
  - Mazes (10x10, 30x30, 50x50)

Outputs saved to separate CSV files:
  - results/search_8puzzle.csv
  - results/search_15puzzle.csv
  - results/search_maze.csv
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from benchmarks.benchmark import Benchmark, BenchmarkEntry

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

SEARCH_TIMEOUT_S = 20.0

UNINFORMED = [
    ("DFS",           DFS,                 {}),
    ("BFS",           BFS,                 {}),
    ("UCS",           UCS,                 {}),
    ("IDDFS",         IDDFS,               {"visualize": False, "max_height": 20}),
    ("Bidir-Search",  BidirectionalSearch, {}),
]

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


def make_8puzzle(generator, moves, pdb_8, heuristic_type="pattern_db"):
    state = generator.generate(moves=moves)
    return NPuzzleProblem(state, NPuzzle(3), heuristic_type=heuristic_type, pdbs=pdb_8)


def make_15puzzle(generator, moves, pdb_15):
    state = generator.generate(moves=moves)
    return NPuzzleProblem(state, NPuzzle(4), heuristic_type="pattern_db", pdbs=pdb_15)


def make_maze(rows, cols, heuristic_type="Manhatten"):
    maze = RandomizedKruskalGenerator(rows=rows, cols=cols).generate()
    return MazeSearchProblem(maze, (0, 0), (rows - 1, cols - 1), heuristic_type=heuristic_type)


def _filter_algos(algo_list, algo_filter):
    if not algo_filter:
        return algo_list
    filt = {a.strip().lower() for a in algo_filter}
    return [(n, c, k) for n, c, k in algo_list if any(f in n.lower() for f in filt)]


def main(num_runs=30, domains=None, algo_filter=None, reset=False):
    import random
    random.seed(2026)
    domains = domains or ["8pzl", "15pzl", "maze"]

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

    gen_8 = NPuzzleGenerator(3)
    gen_15 = NPuzzleGenerator(4)
    filtered = _filter_algos(ALL_ALGOS, algo_filter)

    if "8pzl" in domains:
        print(f"\n=== Running 8-Puzzle Benchmark ({num_runs} runs) ===")
        p8_entries = []
        for diff_label, moves, algos, h_type in [
            ("8pzl easy", 8, filtered, "misplaced_tile"),
            ("8pzl medium", 18, filtered, "pattern_db"),
            ("8pzl hard", 28, _filter_algos(INFORMED_WITH_IGBFS, algo_filter), "pattern_db"),
        ]:
            base_probs = [make_8puzzle(gen_8, moves, pdb_8, heuristic_type=h_type) for _ in range(num_runs)]
            for name, cls, kwargs in algos:
                p8_entries.append(BenchmarkEntry(label=f"{name} / {diff_label}", algo_class=cls, problem=base_probs, algo_kwargs=kwargs))

        # Heuristic comparison on 8-puzzle medium
        for h in ("misplaced_tile", "manhattan", "pattern_db"):
            probs = [make_8puzzle(gen_8, 18, pdb_8, heuristic_type=h) for _ in range(num_runs)]
            for name, cls, kwargs in _filter_algos([("A*", AStar, {}), ("IDA*", IDAStar, {})], algo_filter):
                p8_entries.append(BenchmarkEntry(label=f"{name} ({h}) / 8pzl medium", algo_class=cls, problem=probs, algo_kwargs=kwargs))

        Benchmark(p8_entries).run(
            csv_path="results/search_8puzzle.csv",
            num_runs=num_runs,
            timeout=SEARCH_TIMEOUT_S,
            verbose=True,
            reset=reset,
            algo_filter=algo_filter,
        )

    if "15pzl" in domains:
        print(f"\n=== Running 15-Puzzle Benchmark ({num_runs} runs) ===")
        p15_entries = []
        for diff_label, moves in [("15pzl medium", 25), ("15pzl hard", 45)]:
            base_probs = [make_15puzzle(gen_15, moves, pdb_15) for _ in range(num_runs)]
            for name, cls, kwargs in _filter_algos(INFORMED_WITH_IGBFS, algo_filter):
                p15_entries.append(BenchmarkEntry(label=f"{name} / {diff_label}", algo_class=cls, problem=base_probs, algo_kwargs=kwargs))
        Benchmark(p15_entries).run(
            csv_path="results/search_15puzzle.csv",
            num_runs=num_runs,
            timeout=SEARCH_TIMEOUT_S,
            verbose=True,
            reset=reset,
            algo_filter=algo_filter,
        )

    if "maze" in domains:
        print(f"\n=== Running Maze Benchmark ({num_runs} runs) ===")
        maze_entries = []
        for diff_label, rows, cols in [("maze 10x10", 10, 10), ("maze 30x30", 30, 30), ("maze 50x50", 50, 50)]:
            base_probs = [make_maze(rows, cols) for _ in range(num_runs)]
            for name, cls, kwargs in _filter_algos(ALL_ALGOS, algo_filter):
                maze_entries.append(BenchmarkEntry(label=f"{name} / {diff_label}", algo_class=cls, problem=base_probs, algo_kwargs=kwargs))

        # Maze heuristic comparison on 30x30
        for h_label, h_type in [("manhattan", "Manhatten"), ("euclidean", "Euclidean")]:
            prob = [make_maze(30, 30, heuristic_type=h_type) for _ in range(num_runs)]
            for name, cls, kwargs in _filter_algos([("A*", AStar, {})], algo_filter):
                maze_entries.append(BenchmarkEntry(label=f"{name} ({h_label}) / maze 30x30", algo_class=cls, problem=prob, algo_kwargs=kwargs))

        Benchmark(maze_entries).run(
            csv_path="results/search_maze.csv",
            num_runs=num_runs,
            timeout=SEARCH_TIMEOUT_S,
            verbose=True,
            reset=reset,
            algo_filter=algo_filter,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30, help="Number of runs per algorithm (default: 30)")
    parser.add_argument("--domains", type=str, default="8pzl,15pzl,maze", help="Comma-separated domains (8pzl,15pzl,maze)")
    parser.add_argument("--algos", type=str, default="", help="Comma-separated algorithm name filter")
    parser.add_argument("--reset", action="store_true", help="Clear existing CSV before writing")
    args = parser.parse_args()
    domain_list = [d.strip() for d in args.domains.split(",") if d.strip()]
    algo_list = [a.strip() for a in args.algos.split(",") if a.strip()] or None
    main(num_runs=args.runs, domains=domain_list, algo_filter=algo_list, reset=args.reset)
