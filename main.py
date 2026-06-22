from domains.maze.MazeSearch import MazeSearchProblem
from search.informed.AStar import AStar
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

    solver = AStar(problem)

    visualizer = MazeSearchVisualizer(
        maze,
        solver,
        cell_size=30,
        auto_run=True
    )

    visualizer.run()

    # For benchmark recording
    benchmark_solver = AStar(problem)

    result = benchmark_solver.run()
    print(result)
    print("="*80)

    # Second run to compare the euclidean and manhatten
    solver.reset()
    solver.problem.heuristic_type="Euclidean"

    second_visualizer = MazeSearchVisualizer(
        maze,
        solver,
        cell_size=30,
        auto_run=True
    )
    
    second_visualizer.run()

    benchmark_solver = AStar(problem)

    result = benchmark_solver.run()
    print(result)