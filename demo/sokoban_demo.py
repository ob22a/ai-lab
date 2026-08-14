from domains.sokoban.Sokoban import SokobanProblem
from search.informed.AStar import AStar
from visualization.SokobanVisualizer import SokobanVisualizer

from domains.sokoban.RandomizedSokobanGenerator import RandomizedSokobanGenerator

def main():
    print("Initializing Sokoban Visualizer with Randomized Level...")
    
    # Procedurally generate a guaranteed solvable level using Reverse Play
    generator = RandomizedSokobanGenerator(width=10, height=10, num_boxes=6, num_pulls=10000)
    level = generator.generate()
    
    print("Generated Level:")
    print(level)
    
    problem = SokobanProblem(level)
    solver = AStar(problem)
    
    print("Launching Pygame Window! The algorithm will solve the puzzle in the background, then you can press 'A' to watch the playback.")
    
    visualizer = SokobanVisualizer(
        problem=problem,
        solver=solver,
        cell_size=60,
        fps=60,
        show_search_process=False # Set to True to watch the AI's chaotic thought process
    )
    visualizer.run()

if __name__ == "__main__":
    main()
