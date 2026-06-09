from domains.maze.MazeSearch import MazeSearchProblem
from search.informed.GBFS import GreedyBestFirstSearch
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

    solver = GreedyBestFirstSearch(problem)

    visualizer = MazeSearchVisualizer(
        maze,
        solver,
        cell_size=30
    )

    visualizer.run()

    # For benchmark recording
    benchmark_solver = GreedyBestFirstSearch(problem)

    result = benchmark_solver.run()
    print(result)