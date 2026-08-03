from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from domains.n_puzzle.PatternDatabase import PatternDatabase
from domains.n_puzzle.utils import print_puzzle
from search.informed.IGBFS import IGBFS
from search.informed.IDAStar import IDAStar
from search.informed.AStar import AStar

import copy


def main():
    size = 3
    generator = NPuzzleGenerator(size)
    puzzle = NPuzzle(size)

    start_state = generator.generate(moves=20)
    print(f"Start: {start_state}")
    print_puzzle(start_state, size)

    pdb_8puzzle = [
        PatternDatabase("./pdbs/8puzzle_1234.bin"),
        PatternDatabase("./pdbs/8puzzle_5678.bin"),
    ]

    problem_igbfs = NPuzzleProblem(start_state, puzzle, heuristic_type="pattern_db", pdbs=pdb_8puzzle)
    problem_ida   = copy.deepcopy(problem_igbfs)
    problem_astar = copy.deepcopy(problem_igbfs)

    print("\n--- Running IGBFS ---")
    result_igbfs = IGBFS(problem_igbfs).run()
    print(result_igbfs)

    print("\n--- Running IDA* (optimal reference) ---")
    result_ida = IDAStar(problem_ida).run()
    print(result_ida)

    print("\n--- Running A* (optimal reference) ---")
    result_astar = AStar(problem_astar).run()
    print(result_astar)

    assert result_igbfs.success, "IGBFS failed to find a solution!"

    optimal = result_astar.path_cost
    igbfs_cost = result_igbfs.path_cost
    suboptimality = igbfs_cost - optimal

    print(f"\nOptimal cost (A*): {optimal}")
    print(f"IGBFS cost:        {igbfs_cost}  (suboptimality = +{suboptimality})")
    if suboptimality == 0:
        print("IGBFS happened to find the optimal solution on this instance.")
    else:
        print("IGBFS traded optimality for speed — expected behaviour.")


if __name__ == "__main__":
    main()
