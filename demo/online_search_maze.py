import math
from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator
from domains.maze.UnknownMaze import UnknownMazeEnvironment
from search.online.OnlineDFS import OnlineDFS
from search.online.LRTA import LRTAStar


def manhattan_heuristic(state, goal):
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])


def main():
    print("--- Online Search in Unknown Maze ---")
    rows, cols = 15, 15
    start = (0, 0)
    goal = (rows - 1, cols - 1)
    
    print(f"Generating a {rows}x{cols} maze...")
    maze = RandomizedKruskalGenerator(rows, cols).generate()
    
    # 1. Online DFS
    print("\n1. Online DFS Agent Exploring...")
    env_dfs = UnknownMazeEnvironment(maze, start, goal)
    agent_dfs = OnlineDFS(env_dfs)
    
    steps = 0
    while agent_dfs.status == "RUNNING":
        action = agent_dfs.search_step(agent_dfs.env.get_percept())
        if action is not None:
            agent_dfs.env.execute_action(action)
            steps += 1
            if steps > 10000:
                print("   Agent got lost (too many steps).")
                break
                
    if agent_dfs.status == "SUCCESS":
        print(f"   Success! Reached goal in {steps} steps.")
        print(f"   (Nodes expanded in internal map: {agent_dfs.nodes_expanded})")
        
    # 2. LRTA* Learning Over Repeated Trials
    print("\n2. LRTA* Learning Over Repeated Trials...")
    env_lrta = UnknownMazeEnvironment(maze, start, goal)
    heuristic = lambda state: manhattan_heuristic(state, goal)
    agent_lrta = LRTAStar(env_lrta, heuristic_func=heuristic)
    
    for trial in range(1, 11):
        agent_lrta.reset() # Resets position, keeps H table
        steps = 0
        while agent_lrta.status == "RUNNING":
            action = agent_lrta.search_step(agent_lrta.env.get_percept())
            if action is not None:
                agent_lrta.env.execute_action(action)
                steps += 1
                if steps > 10000:
                    break
        print(f"   Trial {trial:2d}: Reached goal in {steps:4d} steps. (H[{start}] = {agent_lrta.get_H(start):.1f})")


if __name__ == "__main__":
    import random
    random.seed(42)
    main()
