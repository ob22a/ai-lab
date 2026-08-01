from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from domains.maze.MazeSearch import MazeSearchProblem
from search.informed.IDAStar import IDAStar
from search.informed.AStar import AStar
from visualization.MazeVisualizer import MazeSearchVisualizer

def main():
    print("Initializing Bidirectional Search Maze Benchmark...")
    
    # 1. Generate the Maze using Kruskal's algorithm
    generator = RandomizedKruskalGenerator(rows=20, cols=30)
    maze = generator.generate()
    
    # 2. Define the Search Problem
    problem = MazeSearchProblem(maze, (0, 0), (19, 29))
    
    # 3. Setup the Solver
    solver = IDAStar(problem)
    
    # 4. Launch Visualizer!
    print("Launching Pygame Window! Press 'SPACE' to step or 'A' to auto-run.")
    visualizer = MazeSearchVisualizer(
        maze=maze,
        solver=solver,
        cell_size=30,
        fps=60,
        auto_run=True
    )
    visualizer.run()

if __name__ == "__main__":
    main()