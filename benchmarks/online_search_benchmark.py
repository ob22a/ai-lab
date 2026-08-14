import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from domains.maze.UnknownMaze import UnknownMazeEnvironment
from search.online.LRTA import LRTAStar

def manhattan(state, goal):
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])

def main():
    print("=== Running Online Search (LRTA*) Benchmark (5 Mazes x 20 Trials) ===")
    
    csv_path = "results/online_search_maze.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Maze ID", "Trial", "Path Cost", "Nodes Expanded"])
        
        for maze_id in range(1, 6):
            print(f"  Testing Maze #{maze_id}...")
            maze = RandomizedKruskalGenerator(rows=20, cols=20).generate()
            start_pos = (0, 0)
            goal_pos = (19, 19)
            env = UnknownMazeEnvironment(maze, start_pos, goal_pos)
            
            agent = LRTAStar(env, heuristic_func=lambda s: manhattan(s, goal_pos))
            
            for trial in range(1, 21):
                agent.reset()
                steps = 0
                while agent.status == "RUNNING":
                    action = agent.search_step(env.get_percept())
                    if action is not None:
                        env.execute_action(action)
                        steps += 1
                        
                writer.writerow([f"Maze {maze_id}", trial, steps, agent.nodes_expanded])
    
    print(f"Saved raw runs -> {csv_path}")

if __name__ == "__main__":
    main()
