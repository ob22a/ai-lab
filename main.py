from domains.maze.MazeSearch import MazeSearchProblem
from search.uninformed.IDDFS import OptimizedIDDFS,TrueIDDFS
from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from visualization.MazeVisualizer import MazeSearchVisualizer

if __name__ == "__main__":
    maze = RandomizedKruskalGenerator(
        20,
        20
    ).generate()

    problem = MazeSearchProblem(
        maze,
        (0, 0),
        (19, 19)
    )

    solver = TrueIDDFS(problem,5)

    visualizer = MazeSearchVisualizer(
        maze,
        solver,
        cell_size=30,
        auto_run=True
    )

    visualizer.run()

    # For benchmark recording
    benchmark_solver = TrueIDDFS(problem,5,visualize=False)

    result = benchmark_solver.run()
    print(result)