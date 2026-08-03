from domains.n_queens.NQueensProblem import NQueensProblem
from search.local.HillClimbing import HillClimbing
from visualization.NQueensVisualizer import NQueensVisualizer

def main():
    print("Initializing N-Queens Local Search Visualizer...")
    
    # 8-Queens is classic, but we can do any N!
    problem = NQueensProblem(n=8)
    
    # Hill Climbing will try to move a queen in its column to minimize conflicts
    solver = HillClimbing(problem)
    
    print("Launching Pygame Window! Press 'SPACE' to step or 'A' to auto-run.")
    visualizer = NQueensVisualizer(
        problem=problem,
        solver=solver,
        cell_size=60,
        fps=5
    )
    visualizer.run()

if __name__ == "__main__":
    main()
