"""
main.py
AI Lab – Interactive Launcher Hub.

This launcher allows users to interactively launch domain demos with visualizers.
All demo scripts in the 'demo/' directory are self-contained and designed to be opened,
edited, or run directly from the command line.
"""

import sys
import os
import subprocess

DEMO_REGISTRY = [
    # Category: Constraint Satisfaction Problems (CSP)
    {"category": "CSP SOLVERS", "id": "sudoku", "name": "Sudoku (9x9 Backtracking & AC-3)", "dir": "demo/csp_sudoku.py", "vis": True},
    {"category": "CSP SOLVERS", "id": "timetabling", "name": "University Timetabling CSP", "dir": "demo/csp_timetabling.py", "vis": False},
    {"category": "CSP SOLVERS", "id": "cryptarithmetic", "name": "Cryptarithmetic Letter Math (SEND+MORE=MONEY)", "dir": "demo/csp_cryptarithmetic.py", "vis": True},
    {"category": "CSP SOLVERS", "id": "map_coloring", "name": "Map Coloring CSP (Australia 3-Coloring)", "dir": "demo/csp_map_coloring.py", "vis": True},
    {"category": "CSP SOLVERS", "id": "tree_decomp", "name": "Tree Decomposition (Junction Tree CSP)", "dir": "demo/csp_tree_decomposition.py", "vis": True},
    {"category": "CSP SOLVERS", "id": "cycle_cutset", "name": "Cycle Cutset Conditioning", "dir": "demo/csp_cycle_cutset.py", "vis": True},
    {"category": "CSP SOLVERS", "id": "nqueens_csp", "name": "N-Queens CSP Backtracking", "dir": "demo/csp_nqueens_visualizer_demo.py", "vis": True},

    # Category: Classical Search Algorithms
    {"category": "CLASSICAL SEARCH", "id": "romanian_map", "name": "Romanian Map City Routing (A*, GBFS, BFS, DFS)", "dir": "demo/romanian_map_demo.py", "vis": True},
    {"category": "CLASSICAL SEARCH", "id": "word_ladder", "name": "Word Ladder Transformation (BFS, A*)", "dir": "demo/word_ladder_demo.py", "vis": False},
    {"category": "CLASSICAL SEARCH", "id": "maze", "name": "Maze Solving Pathfinding (A*, GBFS, IGBFS, SMA*)", "dir": "demo/maze.py", "vis": True},
    {"category": "CLASSICAL SEARCH", "id": "online_maze", "name": "Online Maze Exploration (Online DFS & LRTA*)", "dir": "demo/online_maze_demo.py", "vis": True},
    {"category": "CLASSICAL SEARCH", "id": "vacuum", "name": "AND-OR Search Vacuum World", "dir": "demo/and_or_vacuum.py", "vis": False},
    {"category": "CLASSICAL SEARCH", "id": "n_puzzle", "name": "N-Puzzle Sliding Tile Search (IDA*, A*, RBFS)", "dir": "demo/n-puzzle.py", "vis": True},
    {"category": "CLASSICAL SEARCH", "id": "sokoban", "name": "Sokoban Box Pushing Search", "dir": "demo/sokoban_demo.py", "vis": True},

    # Category: Optimization & Local Search
    {"category": "LOCAL SEARCH & OPTIMIZATION", "id": "tsp", "name": "TSP (Salesperson Tour Optimization)", "dir": "demo/local_search_tsp.py", "vis": True},
    {"category": "LOCAL SEARCH & OPTIMIZATION", "id": "nqueens_local", "name": "N-Queens Local Search (SA, Hill Climbing, GA, Beam)", "dir": "demo/local_search_nqueens.py", "vis": True},

    # Category: Game AI
    {"category": "GAME AI", "id": "crazy", "name": "Crazy Card Game (Obssa Heuristic, MCTS, AlphaBeta)", "dir": "demo/crazy_demo.py", "vis": True},
    {"category": "GAME AI", "id": "games", "name": "Board Game AI (Tic-Tac-Toe, Connect Four, Othello)", "dir": "demo/games_demo.py", "vis": True},
]


def display_menu():
    print("\n" + "=" * 75)
    print("                 AI LAB — UNIFIED EXPERIMENTATION LAUNCHER")
    print(" Note: You can open, edit, and run any demo file directly in the 'demo/' folder.")
    print(" Example:  python -m demo.maze --vis --algo AStar")
    print("=" * 75)
    
    current_cat = None
    for idx, item in enumerate(DEMO_REGISTRY, 1):
        if item["category"] != current_cat:
            current_cat = item["category"]
            print(f"\n [{current_cat}]")
        print(f"   {idx:2d}. {item['name']}")

    print("\n   [Q] Quit Launcher")
    print("=" * 75)


def launch_demo(item):
    script_path = item["dir"]
    full_path = os.path.abspath(script_path)
    if not os.path.exists(full_path):
        print(f"\nError: Demo script not found at {full_path}")
        return

    print(f"\n>>> Running '{script_path}' in an isolated process...")
    try:
        clean_path = script_path[:-3] if script_path.endswith('.py') else script_path
        module_command = clean_path.replace('/', '.')
        cmd = ['python', '-m', module_command]
        if item.get("vis", True):
            cmd.append('--vis')
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[Notice] Demo exited with status code {e.returncode}")
    except KeyboardInterrupt:
        print("\n[Notice] Interrupted by user.")


def main():
    while True:
        display_menu()
        choice = input(f"\nEnter choice number (1-{len(DEMO_REGISTRY)}) or 'q' to quit: ").strip().lower()
        if choice == 'q':
            print("\nExiting AI Lab Launcher. Goodbye!")
            sys.exit(0)

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(DEMO_REGISTRY):
                item = DEMO_REGISTRY[idx - 1]
                launch_demo(item)
            else:
                print(f"\nInvalid choice! Please enter a number between 1 and {len(DEMO_REGISTRY)}.")
        else:
            print("\nInvalid input. Please enter a valid number or 'q'.")


if __name__ == "__main__":
    main()


