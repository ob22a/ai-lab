from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from domains.n_puzzle.PatternDatabase import PatternDatabase
from domains.n_puzzle.utils import print_puzzle
from search.informed.RBFS import RBFS
from search.informed.AStar import AStar
from search.informed.IDAStar import IDAStar

import copy


def main():
    size = 3
    generator = NPuzzleGenerator(size)
    puzzle = NPuzzle(size)

    start_state = generator.generate(moves=20)
    print(f"Start state: {start_state}")
    print_puzzle(start_state, size)
    print(f"Goal  state: {puzzle.goal_state}")
    print_puzzle(puzzle.goal_state, size)

    pdb_8puzzle = [
        PatternDatabase("./pdbs/8puzzle_1234.bin"),
        PatternDatabase("./pdbs/8puzzle_5678.bin"),
    ]

    problem_rbfs  = NPuzzleProblem(start_state, puzzle, heuristic_type="pattern_db", pdbs=pdb_8puzzle)
    problem_astar = copy.deepcopy(problem_rbfs)
    problem_ida   = copy.deepcopy(problem_rbfs)

    print("\n--- Running RBFS ---")
    result_rbfs = RBFS(problem_rbfs).run()
    print(result_rbfs)

    print("\n--- Running A* (reference) ---")
    result_astar = AStar(problem_astar).run()
    print(result_astar)

    print("\n--- Running IDA* (reference) ---")
    result_ida = IDAStar(problem_ida).run()
    print(result_ida)

    assert result_rbfs.success, "RBFS failed!"
    assert result_rbfs.path_cost == result_astar.path_cost, (
        f"Optimality mismatch: RBFS={result_rbfs.path_cost} A*={result_astar.path_cost}"
    )
    print("\nPASS — RBFS solution is optimal (matches A*).")


if __name__ == "__main__":
    main()
