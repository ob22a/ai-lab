# =====================================================================
# TWEAKABLE CONFIGURATION - Modify these variables to test variations!
# =====================================================================
# Solvers available:   AStar, GreedyBestFirstSearch, BFS, DFS, UCS, BidirectionalAStar
# Cities available:    Arad, Zerind, Oradea, Sibiu, Timisoara, Lugoj, Mehadia,
#                      Drobeta, Craiova, Rimnicu, Fagaras, Pitesti, Bucharest, etc.
# =====================================================================

import sys
import time
from domains.romanian_map.RomanianMap import RomanianMapProblem
from search.informed.AStar import AStar
from search.informed.GBFS import GreedyBestFirstSearch
from search.uninformed.BFS import BFS
from search.uninformed.DFS import DFS
from search.uninformed.UCS import UCS
from search.informed.BidirectionalAStar import BidirectionalAStar
from visualization.RomanianMapVisualizer import RomanianMapVisualizer

# ── User Configuration ────────────────────────────────────────────────
START_CITY    = "Arad"
GOAL_CITY     = "Bucharest"
CHOSEN_SOLVER = BFS  # Options: AStar, GreedyBestFirstSearch, BFS, DFS, UCS, BidirectionalAStar
VISUALIZE     = True   # Set to False for text-only output


def solve_romanian_map(start=START_CITY, goal=GOAL_CITY, visualize=True):
    print(f"\n--- Romanian Map Search: {start} -> {goal} ---")
    problem = RomanianMapProblem(start, goal)
    
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
        print(f"Path Cost: {res.path_cost:.1f} | Nodes Expanded: {res.nodes_expanded} | Runtime: {dur:.4f}s")
        print(" -> ".join(path))
    else:
        print("No solution found!")

    if visualize:
        print("\nLaunching Pygame Romanian Map Visualizer...")
        vis = RomanianMapVisualizer(problem=problem, solver_class=CHOSEN_SOLVER)
        vis.run()


def main():
    visualize = VISUALIZE and ("--no-vis" not in sys.argv)
    clean_argv = [a for a in sys.argv if a != "--no-vis"]
    if len(clean_argv) == 3:
        start_city, goal_city = clean_argv[1], clean_argv[2]
        solve_romanian_map(start_city, goal_city, visualize=visualize)
    else:
        solve_romanian_map(START_CITY, GOAL_CITY, visualize=visualize)


if __name__ == "__main__":
    main()
