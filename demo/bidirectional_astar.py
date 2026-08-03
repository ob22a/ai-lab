from domains.n_puzzle.NPuzzleGenerator import NPuzzleGenerator
from domains.n_puzzle.NPuzzle import NPuzzle
from domains.n_puzzle.NPuzzleProblem import NPuzzleProblem
from domains.n_puzzle.PatternDatabase import PatternDatabase
from domains.n_puzzle.utils import print_puzzle
from search.informed.BidirectionalAStar import BidirectionalAStar
from search.informed.AStar import AStar

import copy


def main():
    size = 3
    generator = NPuzzleGenerator(size)
    puzzle = NPuzzle(size)

    start_state = generator.generate(moves=25)
    print(f"Start: {start_state}")
    print_puzzle(start_state, size)

    pdb_8puzzle = [
        PatternDatabase("./pdbs/8puzzle_1234.bin"),
        PatternDatabase("./pdbs/8puzzle_5678.bin"),
    ]

    problem_bidir = NPuzzleProblem(start_state, puzzle, heuristic_type="pattern_db", pdbs=pdb_8puzzle)
    problem_astar = copy.deepcopy(problem_bidir)

    print("\n--- Running Bidirectional A* ---")
    result_bidir = BidirectionalAStar(problem_bidir).run()
    print(result_bidir)

    print("\n--- Running A* (optimal reference) ---")
    result_astar = AStar(problem_astar).run()
    print(result_astar)

    assert result_bidir.success, "Bidirectional A* failed!"
    assert result_bidir.path_cost == result_astar.path_cost, (
        f"Optimality mismatch: BiA*={result_bidir.path_cost} A*={result_astar.path_cost}"
    )
    savings = 1 - result_bidir.nodes_expanded / max(result_astar.nodes_expanded, 1)
    print(f"\nPASS — Bidirectional A* is optimal.")
    print(f"Expansion savings vs A*: {savings:.1%} fewer nodes expanded.")


if __name__ == "__main__":
    main()
