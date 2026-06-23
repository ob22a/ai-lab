from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from search.informed.AStar import AStar
from visualization.NPuzzleVisualizer import NPuzzleVisualizer
from domains.n_puzzle.utils import print_puzzle

def main():
    print("Initializing 8-Puzzle (3x3) GUI...")
    size = 3
    generator = NPuzzleGenerator(size)
    puzzle = NPuzzle(size)
    
    # Generate a random state
    start_state = generator.generate()
    print(f"Generated Start State: {start_state}")
    
    # Setup problem and solver
    problem = NPuzzleProblem(start_state, puzzle, heuristic_type="manhattan")
    solver = AStar(problem)
    
    # Setup visualizer
    # Start with auto_run=False so user can press space or 'a' to watch it
    visualizer = NPuzzleVisualizer(
        puzzle_size=size,
        solver=solver,
        window_size=600,
        fps=60,
        auto_run=False,
        show_search_process=False
    )
    
    print("Launching Pygame Window! Press 'A' to auto-run the search.")
    visualizer.run()

    # Generate a random state
    start_state = generator.generate()
    print("Generated Valid Random Start State:")
    print_puzzle(start_state, size)
    
    print("Goal State:")
    print_puzzle(puzzle.goal_state, size)
    
    # Hook it up to A*
    problem = NPuzzleProblem(start_state, puzzle, heuristic_type='manhattan')
    print(f"Initial Manhattan Distance: {problem.heuristic(start_state)}")
    
    print("\nRunning A* Search... (this might take a second if it's a hard shuffle!)")
    solver = AStar(problem)
    result = solver.run()
    
    print(result)

    print("="*80)
    print("Using misplaced tiles Heuristic\n")

    problem2 = NPuzzleProblem(start_state,puzzle,heuristic_type='misplaced_tile')
    print(f"Initial Manhattan Distance: {problem2.heuristic(start_state)}")
    
    print("\nRunning A* Search... (this might take a second if it's a hard shuffle!)")
    solver = AStar(problem2)
    result = solver.run()
    
    print(result)

if __name__ == "__main__":
    main()