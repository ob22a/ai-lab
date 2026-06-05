from domains.maze.MazeSearch import MazeSearchProblem
from search.uninformed.DFS import DFS
from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from visualization.MazeVisualizer import MazeSearchVisualizer

if __name__ == "__main__":
    maze = RandomizedKruskalGenerator(
        50,
        50
    ).generate()

    problem = MazeSearchProblem(
        maze,
        (0, 0),
        (49, 49)
    )

    solver = DFS(problem)

    visualizer = MazeSearchVisualizer(
        maze,
        solver,
        cell_size=20,
        auto_run=True
    )

    visualizer.run()

    # For benchmark recording

    result = solver.run()
    print(result)