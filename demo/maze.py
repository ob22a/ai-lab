"""
demo/maze.py
Maze Solving Pathfinding Search Demo.

Supported Algorithms:
  - AStar (A* Search)
  - GBFS (Greedy Best-First Search)
  - IGBFS (Improved Greedy Best-First Search)
  - BidirectionalAStar (Bidirectional A* Search)
  - IDAStar (Iterative Deepening A*)
  - SMAStar (Simplified Memory-Bounded A*)
  - BFS (Breadth-First Search)
  - DFS (Depth-First Search)

Usage:
  python -m demo.maze [--vis] [--algo AStar|GBFS|IGBFS|BidirectionalAStar|IDAStar|SMAStar|BFS|DFS]
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from domains.maze.MazeSearch import MazeSearchProblem

# Search Solvers
from search.uninformed.BFS import BFS
from search.uninformed.DFS import DFS
from search.uninformed.BidirectionalSearch import BidirectionalSearch
from search.uninformed.IDDFS import TrueIDDFS, OptimizedIDDFS
from search.uninformed.UCS import UCS
from search.informed.AStar import AStar
from search.informed.GBFS import GreedyBestFirstSearch
from search.informed.IGBFS import IGBFS
from search.informed.BidirectionalAStar import BidirectionalAStar
from search.informed.IDAStar import IDAStar
from search.informed.SMAstar import SMAStar
from search.informed.RBFS import RBFS

from visualization.MazeVisualizer import MazeSearchVisualizer


def main():
    parser = argparse.ArgumentParser(description="Maze Pathfinding Search Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--algo", type=str, default="AStar",
                        choices=["AStar", "GBFS", "IGBFS", "BidirectionalAStar", "IDAStar", "SMAStar", "BFS", "DFS"],
                        help="Algorithm to run")
    parser.add_argument("--rows", type=int, default=20, help="Number of maze rows")
    parser.add_argument("--cols", type=int, default=30, help="Number of maze columns")
    args = parser.parse_args()

    print("=" * 65)
    print(f"             MAZE PATHFINDING SEARCH DEMO ({args.rows}x{args.cols})")
    print("=" * 65)

    # 1. Generate Maze using Randomized Kruskal's algorithm
    generator = RandomizedKruskalGenerator(rows=args.rows, cols=args.cols)
    maze = generator.generate()

    # 2. Define Search Problem
    start_pos = (0, 0)
    goal_pos = (args.rows - 1, args.cols - 1)
    problem = MazeSearchProblem(maze, start_pos, goal_pos)

    # 3. Setup Solver
    solvers = {
        "AStar": AStar(problem),
        "GBFS": GreedyBestFirstSearch(problem),
        "IGBFS": GreedyBestFirstSearch(problem),
        "BidirectionalAStar": BidirectionalAStar(problem),
        "IDAStar": IDAStar(problem),
        "SMAStar": SMAStar(problem),
        "BFS": BFS(problem),
        "DFS": DFS(problem),
        "BiSearch": BidirectionalSearch(problem),
        "IDDFS-T": TrueIDDFS(problem,start_depth=10),
        "IDDFS-O": OptimizedIDDFS(problem),
        "UCS": UCS(problem),
        "RBFS": RBFS(problem),
        "IGBFS":IGBFS(problem)
    }

    solver = solvers.get(args.algo, AStar(problem))
    print(f"Selected Solver: {solver.__class__.__name__}")

    if args.vis:
        print("\nLaunching Pygame Visualizer! Press SPACE to start/pause, 'A' to toggle auto-run.")
        vis = MazeSearchVisualizer(
            maze=maze,
            solver=solver,
            cell_size=28,
            fps=60,
            auto_run=True
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
