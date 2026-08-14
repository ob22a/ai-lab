"""
demo/romanian_map_demo.py
Romanian Map City Routing Search Demo (A*, GBFS, BFS, DFS, UCS, BidirectionalAStar).

Usage:
  python -m demo.romanian_map_demo [--vis] [--start Arad] [--goal Bucharest] [--algo AStar|GBFS|BFS|DFS|UCS|BidirectionalAStar]
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Top-Level Imports for Easy Code Substitution ---
from domains.romanian_map.RomanianMap import RomanianMapProblem
from search.informed.AStar import AStar
from search.informed.GBFS import GreedyBestFirstSearch
from search.uninformed.BFS import BFS
from search.uninformed.DFS import DFS
from search.uninformed.UCS import UCS
from search.informed.BidirectionalAStar import BidirectionalAStar
from visualization.RomanianMapVisualizer import RomanianMapVisualizer


def main():
    parser = argparse.ArgumentParser(description="Romanian Map Search Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--start", type=str, default="Arad", help="Start city")
    parser.add_argument("--goal", type=str, default="Bucharest", help="Goal city")
    parser.add_argument("--algo", type=str, default="AStar",
                        choices=["AStar", "GBFS", "BFS", "DFS", "UCS", "BidirectionalAStar"],
                        help="Search algorithm class")
    args = parser.parse_args()

    print("=" * 65)
    print(f"      ROMANIAN MAP SEARCH DEMO ({args.start} -> {args.goal})")
    print("=" * 65)

    problem = RomanianMapProblem(args.start, args.goal)

    solvers = {
        "AStar": AStar,
        "GBFS": GreedyBestFirstSearch,
        "BFS": BFS,
        "DFS": DFS,
        "UCS": UCS,
        "BidirectionalAStar": BidirectionalAStar
    }
    solver_cls = solvers.get(args.algo, AStar)

    print(f"Executing {solver_cls.__name__}...")
    solver = solver_cls(problem)

    t0 = time.time()
    res = solver.run()
    dur = time.time() - t0

    if res.solution:
        path = []
        node = res.solution
        while node:
            path.append(node.state)
            node = node.parent
        path = list(reversed(path))
        print(f"\nRoute Found in {dur:.4f}s ({res.nodes_expanded} nodes expanded, total cost = {res.path_cost:.1f} km):")
        print("  " + " -> ".join(path))
    else:
        print("\nNo routing path found!")

    if args.vis:
        print(f"\nLaunching Pygame Romanian Map Visualizer with {solver_cls.__name__}...")
        vis = RomanianMapVisualizer(problem=problem, solver_class=solver_cls)
        vis.run()
    else:
        print("=" * 65)


if __name__ == "__main__":
    main()

