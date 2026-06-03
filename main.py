# DEBUG LINES TO TEST IF THE MAZE IS PROPERLY GENERATED
from domains.maze.RandomizedKruskal import RandomizedKruskalGenerator

if __name__ == "__main__":

    rows, cols = 15, 15
    generator = RandomizedKruskalGenerator(rows, cols)
    generator.maze.printMaze()
    print("\nGenerating maze...\n")
    maze = generator.generate()

    maze.printMaze()