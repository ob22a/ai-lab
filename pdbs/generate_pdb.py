import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.PDBGenerator import PDBGenerator
import os

def main():
    print("Initializing 15-Puzzle PDB Generator...")
    puzzle = NPuzzle(4) # 15-puzzle
    
    if puzzle.size == 3:
        print("Generating 8-Puzzle Disjoint Pattern Databases...")

        # Splitting 4-4
        
        # Generate PDB 1: top half tiles 1, 2, 3, 4
        gen1 = PDBGenerator(puzzle, ['1', '2', '3', '4'])
        gen1.generate('./pdbs/8puzzle_1234.bin')
        
        # Generate PDB 2: bottom half tiles 5, 6, 7, 8
        gen2 = PDBGenerator(puzzle, ['5', '6', '7', '8'])
        gen2.generate('./pdbs/8puzzle_5678.bin')

        print("Finished generating 8-Puzzle Disjoint PDBs!")
    
    elif puzzle.size == 4:
        print("Generating 15-Puzzle Disjoint Pattern Databases...")

        # Splitting 5-5-5
        
        # Generate PDB 1: top half tiles 1, 2, 3, 4, 5,
        gen1 = PDBGenerator(puzzle, ['1', '2', '3', '4', '5'])
        gen1.generate('./pdbs/15puzzle_12345.bin')
        
        # Generate PDB 2: middle tiles 6, 7, 8, 9, a
        gen2 = PDBGenerator(puzzle, ['6','7','8','9', 'a'])
        gen2.generate('./pdbs/15puzzle_6789a.bin')

        # Generate PDB 3: bottom half tiles b, c, d, e, f
        gen3 = PDBGenerator(puzzle, ['b', 'c', 'd', 'e', 'f'])
        gen3.generate('./pdbs/15puzzle_bcdef.bin')

        print("Finished generating 15-Puzzle Disjoint PDBs!")

    else:
        print("Unsupported puzzle size for PDB generation. Only 3x3 and 4x4 are supported.")
    
    

if __name__ == "__main__":
    main()
