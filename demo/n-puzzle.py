"""
demo/n-puzzle.py
N-Puzzle Search Demo (8-Puzzle / 15-Puzzle).

Supports 6 Informed Search Solvers:
  1. IDAStar             (Iterative Deepening A*)
  2. AStar               (A* Search with Disjoint Pattern Databases)
  3. SMAStar             (Simplified Memory-Bounded A*)
  4. BidirectionalAStar  (Bidirectional A* Search)
  5. RBFS                (Recursive Best-First Search)
  6. IGBFS               (Improved Greedy Best-First Search)

Usage:
  python -m demo.n-puzzle [--vis] [--algo IDAStar|AStar|SMAStar|BidirectionalAStar|RBFS|IGBFS] [--size 3|4]
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Top-Level Imports for Easy Code Substitution ---
from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from domains.n_puzzle.PatternDatabase import PatternDatabase
from domains.n_puzzle.utils import print_puzzle

from search.informed.AStar import AStar
from search.informed.IDAStar import IDAStar
from search.informed.SMAstar import SMAStar
from search.informed.BidirectionalAStar import BidirectionalAStar
from search.informed.RBFS import RBFS
from search.informed.IGBFS import IGBFS
from visualization.NPuzzleVisualizer import NPuzzleVisualizer


def main():
    parser = argparse.ArgumentParser(description="N-Puzzle Search Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--algo", type=str, default="IDAStar",
                        choices=["IDAStar", "AStar", "SMAStar", "BidirectionalAStar", "RBFS", "IGBFS"],
                        help="Search algorithm class")
    parser.add_argument("--size", type=int, default=3, help="Puzzle grid size (3 for 8-Puzzle, 4 for 15-Puzzle)")
    args = parser.parse_args()

    print("=" * 65)
    print(f"             N-PUZZLE SEARCH DEMO ({args.size}x{args.size})")
    print("=" * 65)

    size = args.size
    generator = NPuzzleGenerator(size)
    puzzle = NPuzzle(size)

    # 1. Generate Start State
    start_state = generator.generate(moves=15 if size == 3 else 25)
    print(f"Generated Start State ({size}x{size}): {start_state}")
    print_puzzle(start_state, size)

    print("\nGoal State:")
    print_puzzle(puzzle.goal_state, size)

    # 2. Dynamically Load Disjoint Pattern Databases (PDBs) based on Grid Size
    pdbs = []
    if size == 3:
        # 8-Puzzle PDBs (4-4 Partition)
        f1, f2 = "./pdbs/8puzzle_1234.bin", "./pdbs/8puzzle_5678.bin"
        if os.path.exists(f1) and os.path.exists(f2):
            pdbs = [PatternDatabase(f1), PatternDatabase(f2)]
            print("\n[PDB] Loaded 8-Puzzle Disjoint Pattern Databases (1234, 5678).")
    elif size == 4:
        # 15-Puzzle PDBs (5-5-5 Partition)
        f1, f2, f3 = "./pdbs/15puzzle_12345.bin", "./pdbs/15puzzle_6789a.bin", "./pdbs/15puzzle_bcdef.bin"
        if os.path.exists(f1) and os.path.exists(f2) and os.path.exists(f3):
            pdbs = [PatternDatabase(f1), PatternDatabase(f2), PatternDatabase(f3)]
            print("\n[PDB] Loaded 15-Puzzle Disjoint Pattern Databases (12345, 6789a, bcdef).")

    heuristic_type = "pattern_db" if pdbs else "manhattan"
    problem = NPuzzleProblem(start_state, puzzle, heuristic_type=heuristic_type, pdbs=pdbs)

    # 3. Instantiate Selected Algorithm
    solvers = {
        "IDAStar": IDAStar(problem),
        "AStar": AStar(problem),
        "SMAStar": SMAStar(problem, memory_limit=500),
        "BidirectionalAStar": BidirectionalAStar(problem),
        "RBFS": RBFS(problem),
        "IGBFS": IGBFS(problem),
    }

    solver = solvers.get(args.algo, IDAStar(problem))
    print(f"Selected Solver:   {solver.__class__.__name__}")
    print(f"Heuristic Type:    {heuristic_type.upper()}")

    # 4. Execute or Launch Visualizer
    if args.vis:
        print("\nLaunching Pygame NPuzzle Visualizer... Press SPACE to play/pause.")
        vis = NPuzzleVisualizer(
            puzzle_size=size,
            solver=solver,
            window_size=600,
            fps=30,
            auto_run=False,
            show_search_process=False
        )
        vis.run()
    else:
        print(f"\nExecuting {solver.__class__.__name__}...")
        t0 = time.time()
        result = solver.run()
        dur = time.time() - t0

        print("\n--- Search Results ---")
        print(f"Status:         {result.status}")
        print(f"Nodes Expanded: {result.nodes_expanded}")
        print(f"Path Cost:      {result.path_cost}")
        print(f"Runtime:        {dur:.4f} seconds")
        print("=" * 65)


if __name__ == "__main__":
    main()

