from domains.maze.MazeSearch import MazeSearchProblem
from search.uninformed.BFS import BFS
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

    solver = BFS(problem)

    visualizer = MazeSearchVisualizer(
        maze,
        solver,
        cell_size=30,
        auto_run=True
    )

    visualizer.run()

    # For benchmark recording

    result = solver.run()
    print(result)