import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
import pygame

from domains.n_queens.NQueensProblem import NQueensProblem
from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from domains.maze.UnknownMaze import UnknownMazeEnvironment
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm
from search.online.LRTA import LRTAStar
from search.online.OnlineDFS import OnlineDFS
from search.informed.AStar import AStar
from domains.maze.MazeSearch import MazeSearchProblem

from visualization.NQueensVisualizer import NQueensVisualizer
from visualization.BeamSearchVisualizer import BeamSearchVisualizer
from visualization.GeneticAlgorithmVisualizer import GeneticAlgorithmVisualizer
from visualization.MazeVisualizer import MazeSearchVisualizer


def test_beam_search_visualizer_headless():
    problem = NQueensProblem(n=8)
    solver = LocalBeamSearch(problem, k=4)
    visualizer = BeamSearchVisualizer(problem, solver, cell_size=40, fps=10)
    
    assert len(visualizer.history) == 1
    assert len(visualizer.history[0]["beam_states"]) == 4

    # Perform steps
    visualizer._step_forward()
    visualizer._step_forward()
    assert len(visualizer.history) == 3
    assert visualizer.history_index == 2

    # Step backward
    visualizer._step_backward()
    assert visualizer.history_index == 1

    # Render frame
    visualizer.render()

    # Test selection
    visualizer.selected_beam_idx = 2
    visualizer.render()

    # Test restart
    visualizer.restart()
    assert visualizer.history_index == 0
    assert len(visualizer.history) == 1


def test_genetic_algorithm_visualizer_headless():
    problem = NQueensProblem(n=8)
    solver = GeneticAlgorithm(problem, pop_size=20, max_generations=50)
    visualizer = GeneticAlgorithmVisualizer(problem, solver, cell_size=40, fps=10)

    assert len(visualizer.history) == 1
    assert len(visualizer.history[0]["top_elites"]) == 4

    # Step generations
    for _ in range(5):
        visualizer._step_forward()

    assert len(visualizer.history) == 6
    assert visualizer.history_index == 5

    # Step backward
    visualizer._step_backward()
    assert visualizer.history_index == 4

    # Render frame with fitness chart and elite showcase
    visualizer.render()

    # Test selecting elite
    visualizer.selected_elite_idx = 3
    visualizer.render()

    # Restart
    visualizer.restart()
    assert visualizer.history_index == 0


def test_lrta_maze_visualizer_headless():
    rows, cols = 8, 8
    generator = RandomizedKruskalGenerator(rows=rows, cols=cols)
    maze = generator.generate()

    start_pos = (0, 0)
    goal_pos = (rows - 1, cols - 1)
    env = UnknownMazeEnvironment(maze, start_pos=start_pos, goal_pos=goal_pos)
    heuristic = lambda s: float(abs(s[0] - goal_pos[0]) + abs(s[1] - goal_pos[1]))
    agent = LRTAStar(env, heuristic_func=heuristic)

    visualizer = MazeSearchVisualizer(maze=maze, solver=agent, cell_size=30, fps=10, show_heuristics=True)

    # Verify initial state
    assert visualizer.is_online is True
    assert visualizer.trial_number == 1
    assert visualizer.current_trial_steps == 0

    # Step solver multiple times
    for _ in range(15):
        visualizer._step_solver()
        if agent.status == "SUCCESS":
            break

    assert visualizer.current_trial_steps > 0
    assert visualizer.total_steps > 0
    assert len(agent.H) > 0

    # Render frame with in-cell heuristics
    visualizer.render()

    # Start next trial
    visualizer.next_trial()
    assert visualizer.trial_number == 2
    assert visualizer.current_trial_steps == 0
    assert len(agent.H) > 0  # Preserved H table across trials!

    visualizer.render()


def test_online_dfs_maze_visualizer_headless():
    rows, cols = 6, 6
    generator = RandomizedKruskalGenerator(rows=rows, cols=cols)
    maze = generator.generate()

    env = UnknownMazeEnvironment(maze, start_pos=(0, 0), goal_pos=(5, 5))
    agent = OnlineDFS(env)

    visualizer = MazeSearchVisualizer(maze=maze, solver=agent, cell_size=30, fps=10)

    for _ in range(10):
        visualizer._step_solver()
        if agent.status == "SUCCESS":
            break

    visualizer.render()


def test_offline_maze_visualizer_headless():
    rows, cols = 8, 8
    generator = RandomizedKruskalGenerator(rows=rows, cols=cols)
    maze = generator.generate()

    problem = MazeSearchProblem(maze, (0, 0), (7, 7))
    solver = AStar(problem)

    visualizer = MazeSearchVisualizer(maze=maze, solver=solver, cell_size=30, fps=10)
    assert visualizer.is_online is False

    for _ in range(10):
        visualizer._step_solver()

    visualizer.render()


def test_nqueens_all_solvers_headless():
    # 1. Test local search optimizers
    problem_opt = NQueensProblem(n=6)
    for solver_cls in [HillClimbing, SimulatedAnnealing, LocalBeamSearch, GeneticAlgorithm]:
        solver = solver_cls(problem_opt)
        visualizer = NQueensVisualizer(problem_opt, solver, cell_size=40, fps=10)
        
        assert len(visualizer.history[0]["queens"]) == 6
        visualizer._step_forward()
        visualizer._step_forward()
        assert len(visualizer.history[-1]["queens"]) == 6
        visualizer.render()
        visualizer.restart()
        assert len(visualizer.history[0]["queens"]) == 6

    # 2. Test CSP solvers
    from domains.n_queens.NQueensCSP import NQueensCSP
    from csp.Backtracking import BacktrackingSolver
    from csp.SymmetricBacktracking import SymmetricBacktrackingSolver
    from csp.MinConflicts import MinConflictsSolver
    from csp.inference.MAC import mac
    
    problem_csp = NQueensCSP(n=6, break_symmetry=True)
    for csp_solver in [
        BacktrackingSolver(problem_csp),
        SymmetricBacktrackingSolver(problem_csp, inference=mac),
        MinConflictsSolver(problem_csp, max_steps=100)
    ]:
        vis_csp = NQueensVisualizer(problem_csp, csp_solver, cell_size=40, fps=10)
        vis_csp._step_forward()
        vis_csp._step_forward()
        vis_csp.render()
        vis_csp.restart()
        assert vis_csp.history_index == 0
