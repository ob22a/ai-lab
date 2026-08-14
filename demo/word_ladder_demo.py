# =====================================================================
# TWEAKABLE CONFIGURATION - Modify these variables to test variations!
# =====================================================================
# Solvers available:   BFS, AStar, DFS, UCS, GreedyBestFirstSearch
# Words available:     lead, gold, obssa, great, stone, money, etc.
# =====================================================================

import sys
import time
from domains.word_ladder.WordLadder import WordLadderProblem
from search.uninformed.BFS import BFS
from search.uninformed.DFS import DFS
from search.uninformed.UCS import UCS
from search.informed.AStar import AStar
from search.informed.GBFS import GreedyBestFirstSearch
from visualization.WordLadderVisualizer import WordLadderVisualizer

# ── User Configuration ────────────────────────────────────────────────
START_WORD    = "lead"
GOAL_WORD     = "gold"
CHOSEN_SOLVER = BFS   # Options: BFS, AStar, DFS, UCS, GreedyBestFirstSearch
VISUALIZE     = True  # Set to False for text-only output


def solve_word_ladder(start_word=START_WORD, goal_word=GOAL_WORD, visualize=True):
    print(f"\n--- Word Ladder Search: '{start_word.upper()}' -> '{goal_word.upper()}' ---")
    problem = WordLadderProblem(start_word, goal_word)
    
    print(f"Solving using {CHOSEN_SOLVER.__name__}...")
    solver = CHOSEN_SOLVER(problem)
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
        print(f"Solution found in {dur:.4f}s ({res.nodes_expanded} nodes expanded, cost={res.path_cost}):")
        print(" -> ".join(w.upper() for w in path))
    else:
        print("No word ladder solution found!")

    if visualize:
        print(f"\nLaunching Pygame Word Ladder Visualizer with {CHOSEN_SOLVER.__name__}...")
        vis = WordLadderVisualizer(start_word=start_word, goal_word=goal_word, solver_class=CHOSEN_SOLVER)
        vis.run()


def main():
    visualize = VISUALIZE and ("--no-vis" not in sys.argv)
    clean_argv = [a for a in sys.argv if a != "--no-vis"]
    if len(clean_argv) == 3:
        w1, w2 = clean_argv[1], clean_argv[2]
        solve_word_ladder(w1, w2, visualize=visualize)
    else:
        solve_word_ladder(START_WORD, GOAL_WORD, visualize=visualize)


if __name__ == "__main__":
    main()
