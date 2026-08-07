"""
Online Search Demo: LRTA* (Learning Real-Time A*) in an Unknown Maze.

Showcases:
  - Online agent-environment interaction in a maze with hidden walls.
  - In-cell dynamic heuristic overlay H(s) rendered directly inside each cell.
  - Real-time heat-map and highlight when dead-end heuristics are updated.
  - Multi-trial learning progression: press [T] after reaching goal to watch the agent
    navigate the maze in significantly fewer steps on subsequent trials!
  - Step, cumulative iteration, and trial history counters.
"""

from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from domains.maze.UnknownMaze import UnknownMazeEnvironment
from search.online.LRTA import LRTAStar
from search.online.OnlineDFS import OnlineDFS
from visualization.MazeVisualizer import MazeSearchVisualizer


def main():
    print("=" * 65)
    print("  ONLINE SEARCH DEMO - LRTA* IN UNKNOWN MAZE")
    print("=" * 65)
    print("Features:")
    print("  * In-cell H(s) values trace how the agent learns cost-to-goal.")
    print("  * Amber highlight indicates when a cell's H value is updated.")
    print("  * Multi-trial learning: watch step count drop over successive runs!")
    print("Controls:")
    print("  [SPACE]     Step agent forward / trigger next action")
    print("  [A]         Toggle continuous auto-run")
    print("  [T]         Start Next Trial (resets position, preserves learned H)")
    print("  [R]         Full Reset (clears learned H table back to Trial #1)")
    print("  [H]         Toggle in-cell heuristic numbers ON / OFF")
    print("  [UP / DOWN] Adjust agent speed (FPS)")
    print("  [ESC]       Exit")
    print("=" * 65)

    # 1. Generate a maze with corridors and dead ends
    rows, cols = 12, 16
    generator = RandomizedKruskalGenerator(rows=rows, cols=cols)
    maze = generator.generate()

    start_pos = (0, 0)
    goal_pos = (rows - 1, cols - 1)

    # 2. Wrap the maze in an Online Environment
    env = UnknownMazeEnvironment(maze, start_pos=start_pos, goal_pos=goal_pos)

    # 3. Define initial admissible heuristic (Manhattan distance)
    def manhattan_heuristic(state):
        return float(abs(state[0] - goal_pos[0]) + abs(state[1] - goal_pos[1]))

    # 4. Instantiate LRTA* Online Agent
    agent = LRTAStar(env, heuristic_func=manhattan_heuristic)
    agent_2 = OnlineDFS(env)  # Optional: Another agent for comparison

    # 5. Launch Visualizer!
    visualizer = MazeSearchVisualizer(
        maze=maze,
        solver=agent,
        cell_size=44,
        fps=15,
        auto_run=False,
        show_heuristics=True
    )
    visualizer.run()


if __name__ == "__main__":
    main()
