from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from search.informed.IDAStar import IDAStar
from search.informed.AStar import AStar
from visualization.NPuzzleVisualizer import NPuzzleVisualizer
from domains.n_puzzle.PatternDatabase import PatternDatabase
from domains.n_puzzle.utils import print_puzzle

import copy

def main():
    print("Initializing 8-Puzzle (3x3) GUI...")
    size = 4
    generator = NPuzzleGenerator(size)
    puzzle = NPuzzle(size)
    
    # Generate a random state
    start_state = generator.generate()
    print(f"Generated Start State: {start_state}")
    print_puzzle(start_state, size)

    print("Goal State:")
    print_puzzle(puzzle.goal_state, size)

    # pattern dbs
    pdb_15puzzle = [PatternDatabase("./pdbs/15puzzle_12345.bin"),PatternDatabase('./pdbs/15puzzle_6789a.bin'),PatternDatabase('./pdbs/15puzzle_bcdef.bin')]
    
    # Setup problem and solver
    problem = NPuzzleProblem(start_state, puzzle, heuristic_type="pattern_db", pdbs=pdb_15puzzle)
    problem_without_gui = copy.deepcopy(problem)
    problem_a_star = copy.deepcopy(problem)

    solver = IDAStar(problem)

    
    # Setup visualizer
    # Start with auto_run=False so user can press space or 'a' to watch it
    # visualizer = NPuzzleVisualizer(
    #     puzzle_size=size,
    #     solver=solver,
    #     window_size=600,
    #     fps=60,
    #     auto_run=False,
    #     show_search_process=False
    # )
    
    # print("Launching Pygame Window! Press 'A' to auto-run the search.")
    # visualizer.run()

    print("Running IDA* without GUI for performance measurement...")
    solver_without_gui = IDAStar(problem_without_gui)
    result = solver_without_gui.run()
    print(result)
    
    print("Running A* without GUI for performance measurement...")
    solver_a_star = AStar(problem_a_star)
    result_a_star = solver_a_star.run()
    print(result_a_star)

if __name__ == "__main__":
    main()