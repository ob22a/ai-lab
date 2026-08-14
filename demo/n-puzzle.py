"""
demo/n-puzzle.py
N-Puzzle Search Demo (8-Puzzle / 15-Puzzle).

Supports multiple search algorithms:
  - IDA* (Iterative Deepening A*)
  - A* Search (Manhattan / Pattern DB Heuristic)
  - SMA* (Simplified Memory-Bounded A*)
  - Bidirectional A* Search
  - RBFS (Recursive Best-First Search)
  - IGBFS (Improved Greedy Best-First Search)

Usage:
  python -m demo.n-puzzle [--vis] [--algo IDAStar|AStar|SMAStar|BidirectionalAStar|RBFS|IGBFS]
"""

import sys
import os
import argparse
import copy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from domains.n_puzzle.PatternDatabase import PatternDatabase
from domains.n_puzzle.utils import print_puzzle

# Available Solvers
from search.informed.AStar import AStar
from search.informed.IDAStar import IDAStar
from search.informed.SMAstar import SMAStar
from search.informed.BidirectionalAStar import BidirectionalAStar
from search.informed.RBFS import RBFS
from search.informed.IGBFS import ImprovedGBFS
from visualization.NPuzzleVisualizer import NPuzzleVisualizer


def main():
    parser = argparse.ArgumentParser(description="N-Puzzle Search Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--algo", type=str, default="IDAStar", choices=["IDAStar", "AStar", "SMAStar", "BidirectionalAStar", "RBFS", "IGBFS"], help="Algorithm to run")
    parser.add_argument("--size", type=int, default=3, help="Puzzle grid size (3 for 8-Puzzle, 4 for 15-Puzzle)")
    args = parser.parse_args()

    print("=" * 65)
    print(f"             N-PUZZLE SEARCH DEMO ({args.size}x{args.size})")
    print("=" * 65)

    size = args.size
    generator = NPuzzleGenerator(size)
    puzzle = NPuzzle(size)
    
    start_state = generator.generate()
    print(f"Generated Start State: {start_state}")
    print_puzzle(start_state, size)

    print("\nGoal State:")
    print_puzzle(puzzle.goal_state, size)

    # Load Pattern Databases if available
    pdb_8puzzle = []
    if os.path.exists("./pdbs/8puzzle_1234.bin") and os.path.exists("./pdbs/8puzzle_5678.bin"):
        pdb_8puzzle = [PatternDatabase("./pdbs/8puzzle_1234.bin"), PatternDatabase("./pdbs/8puzzle_5678.bin")]

    heuristic_type = "pattern_db" if pdb_8puzzle else "manhattan"
    problem = NPuzzleProblem(start_state, puzzle, heuristic_type=heuristic_type, pdbs=pdb_8puzzle)

    # Select algorithm
    solvers = {
        "IDAStar": IDAStar(problem),
        "AStar": AStar(problem),
        "SMAStar": SMAStar(problem, memory_limit=500),
        "BidirectionalAStar": BidirectionalAStar(problem),
        "RBFS": RBFS(problem),
        "IGBFS": ImprovedGBFS(problem),
    }

    solver = solvers.get(args.algo, IDAStar(problem))
    print(f"\nSelected Algorithm: {solver.__class__.__name__}")

    if args.vis:
        print("\nLaunching Pygame Visualizer! Press SPACE to start/pause, 'A' to toggle auto-run.")
        vis = NPuzzleVisualizer(
            puzzle_size=size,
            solver=solver,
            window_size=600,
            fps=60,
            auto_run=False,
            show_search_process=False
        )
        vis.run()
    else:
        print(f"\nExecuting {solver.__class__.__name__} without GUI...")
        result = solver.run()
        print("\n--- Search Result ---")
        print(f"Status:         {result.status}")
        print(f"Nodes Expanded: {result.nodes_expanded}")
        print(f"Path Cost:      {result.path_cost}")
        print(f"Runtime:        {result.runtime:.4f} seconds")
        print("=" * 65)


if __name__ == "__main__":
    main()