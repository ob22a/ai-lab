from domains.maze.MazeSearch import MazeSearchProblem
from search.uninformed.UCS import UCS
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

    solver = UCS(problem)

    visualizer = MazeSearchVisualizer(
        maze,
        solver,
        cell_size=30,
        auto_run=True
    )

    visualizer.run()

    # For benchmark recording
    benchmark_solver = UCS(problem)

    result = benchmark_solver.run()
    print(result)