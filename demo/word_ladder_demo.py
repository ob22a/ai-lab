"""
demo/word_ladder_demo.py
Word Ladder Transformation Search Demo (BFS, A*, DFS, UCS, GBFS).

Usage:
  python -m demo.word_ladder_demo [START_WORD] [GOAL_WORD] [--algo BFS|AStar|DFS|UCS|GBFS]
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.word_ladder.WordLadder import WordLadderProblem
from search.uninformed.BFS import BFS
from search.uninformed.DFS import DFS
from search.uninformed.UCS import UCS
from search.informed.AStar import AStar
from search.informed.GBFS import GreedyBestFirstSearch


def main():
    parser = argparse.ArgumentParser(description="Word Ladder Search Demo")
    parser.add_argument("start", nargs="?", default="lead", help="Start word")
    parser.add_argument("goal", nargs="?", default="gold", help="Goal word")
    parser.add_argument("--algo", type=str, default="BFS", choices=["BFS", "AStar", "DFS", "UCS", "GBFS"], help="Algorithm to run")
    args = parser.parse_args()

    print("=" * 65)
    print(f"      WORD LADDER TRANSFORM DEMO ('{args.start.upper()}' -> '{args.goal.upper()}')")
    print("=" * 65)

    problem = WordLadderProblem(args.start.lower(), args.goal.lower())
    
    solvers = {
        "BFS": BFS(problem),
        "AStar": AStar(problem),
        "DFS": DFS(problem),
        "UCS": UCS(problem),
        "GBFS": GreedyBestFirstSearch(problem)
    }

    solver = solvers.get(args.algo, BFS(problem))
    print(f"Executing {solver.__class__.__name__}...")

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
        print(f"\nSolution Found in {dur:.4f}s ({res.nodes_expanded} nodes expanded, path length = {len(path)-1}):")
        print("  " + " -> ".join(w.upper() for w in path))
    else:
        print("\nNo word ladder transformation path found!")
    print("=" * 65)


if __name__ == "__main__":
    main()

