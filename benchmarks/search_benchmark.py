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
import copy
import csv
import os
import sys
import time

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

TIMEOUT_S = 45

UNINFORMED = [
    ("DFS",           DFS,                 {}),
    ("BFS",           BFS,                 {}),
    ("UCS",           UCS,                 {}),
    ("IDDFS",         IDDFS,               {"visualize": False}),
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


def make_8puzzle(generator, moves, pdb_8):
    state = generator.generate(moves=moves)
    return NPuzzleProblem(state, NPuzzle(3), heuristic_type="pattern_db", pdbs=pdb_8)


def make_15puzzle(generator, moves, pdb_15):
    state = generator.generate(moves=moves)
    return NPuzzleProblem(state, NPuzzle(4), heuristic_type="pattern_db", pdbs=pdb_15)


def make_maze(rows, cols):
    maze = RandomizedKruskalGenerator(rows=rows, cols=cols).generate()
    return MazeSearchProblem(maze, (0, 0), (rows - 1, cols - 1))


def run_benchmark_for_group(entries, num_runs=30):
    runner = Benchmark(entries)
    return runner.run(num_runs=num_runs, verbose=False)


def save_domain_csv(results, csv_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(_COLUMNS)
        for r in results:
            writer.writerow([
                r.label, r.success, r.path_cost,
                r.nodes_expanded, r.nodes_generated,
                round(r.runtime, 6), round(r.runtime_std, 6),
                r.max_frontier_size, r.runs_count
            ])
    print(f"Saved domain benchmark -> {csv_path}")


def main(num_runs=30,domains=['8pzl','15pzl','maze']):
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

    if '8pzl' in domains:
        # 1. 8-Puzzle Domain
        print(f"\n=== Running 8-Puzzle Benchmark ({num_runs} runs) ===")
        p8_entries = []
        for diff_label, moves in [("8pzl easy", 8), ("8pzl medium", 18), ("8pzl hard", 28)]:
            base_prob = make_8puzzle(gen_8, moves, pdb_8)
            for name, cls, kwargs in ALL_ALGOS:
                p8_entries.append(BenchmarkEntry(label=f"{name} / {diff_label}", algo_class=cls, problem=base_prob, algo_kwargs=kwargs))
        p8_res = run_benchmark_for_group(p8_entries, num_runs=num_runs)
        save_domain_csv(p8_res, "results/search_8puzzle.csv")

    if '15pzl' in domains:
        # 2. 15-Puzzle Domain
        print(f"\n=== Running 15-Puzzle Benchmark ({num_runs} runs) ===")
        p15_entries = []
        for diff_label, moves in [("15pzl medium", 25), ("15pzl hard", 45), ("15pzl complex", 90)]:
            base_prob = make_15puzzle(gen_15, moves, pdb_15)
            for name, cls, kwargs in INFORMED:
                p15_entries.append(BenchmarkEntry(label=f"{name} / {diff_label}", algo_class=cls, problem=base_prob, algo_kwargs=kwargs))
        p15_res = run_benchmark_for_group(p15_entries, num_runs=num_runs)
        save_domain_csv(p15_res, "results/search_15puzzle.csv")

    if 'maze' in domains:
        # 3. Maze Domain
        print(f"\n=== Running Maze Benchmark ({num_runs} runs) ===")
        maze_entries = []
        for rows, cols in [(10, 10), (30, 30), (50, 50)]:
            base_prob = make_maze(rows, cols)
            for name, cls, kwargs in ALL_ALGOS:
                maze_entries.append(BenchmarkEntry(label=f"{name} / maze {rows}x{cols}", algo_class=cls, problem=base_prob, algo_kwargs=kwargs))
        maze_res = run_benchmark_for_group(maze_entries, num_runs=num_runs)
        save_domain_csv(maze_res, "results/search_maze.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30, help="Number of runs per algorithm (default: 30)")
    parser.add_argument("--domains", type=str, default="8pzl,15pzl,maze", help="Comma-separated domains to run (8pzl,15pzl,maze)")
    args = parser.parse_args()
    domain_list = [d.strip() for d in args.domains.split(",") if d.strip()]
    main(num_runs=args.runs, domains=domain_list)
