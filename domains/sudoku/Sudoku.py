from typing import Dict, List, Tuple
from csp.CSPProblem import CSPProblem
from domains.map_coloring.MapColoring import NotEqualConstraint


class SudokuCSP(CSPProblem):
    """
    9x9 Sudoku CSP.
    Variables are (row, col) tuples.
    Domains are [1..9] for empty cells, and [clue] for pre-filled cells.
    Constraints are NotEqual between all pairs in the same row, column, and 3x3 box.
    """
    def __init__(self, board: List[List[int]]):
        """
        board: 9x9 list of ints. 0 represents an empty cell. 1-9 represent clues.
        """
        variables = []
        domains = {}
        
        for r in range(9):
            for c in range(9):
                var = (r, c)
                variables.append(var)
                val = board[r][c]
                if val == 0:
                    domains[var] = list(range(1, 10))
                else:
                    domains[var] = [val]
                    
        super().__init__(variables, domains)
        
        # Generate binary NotEqual constraints for all pairs in same row/col/box.
        # We track added_pairs to prevent duplicate constraint objects.
        added_pairs = set()
        
        def add_alldiff_binary_constraints(var_group: List[Tuple[int, int]]):
            for i in range(len(var_group)):
                for j in range(i + 1, len(var_group)):
                    v1 = var_group[i]
                    v2 = var_group[j]
                    
                    pair = tuple(sorted([v1, v2]))
                    if pair not in added_pairs:
                        added_pairs.add(pair)
                        self.add_constraint(NotEqualConstraint(v1, v2))

        # Add Row constraints
        for r in range(9):
            row_vars = [(r, c) for c in range(9)]
            add_alldiff_binary_constraints(row_vars)
            
        # Add Column constraints
        for c in range(9):
            col_vars = [(r, c) for r in range(9)]
            add_alldiff_binary_constraints(col_vars)
            
        # Add 3x3 Box constraints
        for box_r in range(3):
            for box_c in range(3):
                box_vars = []
                for r in range(box_r * 3, box_r * 3 + 3):
                    for c in range(box_c * 3, box_c * 3 + 3):
                        box_vars.append((r, c))
                add_alldiff_binary_constraints(box_vars)


# Sample Boards
SUDOKU_EASY = [
    [0, 0, 3, 0, 2, 0, 6, 0, 0],
    [9, 0, 0, 3, 0, 5, 0, 0, 1],
    [0, 0, 1, 8, 0, 6, 4, 0, 0],
    [0, 0, 8, 1, 0, 2, 9, 0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 8],
    [0, 0, 6, 7, 0, 8, 2, 0, 0],
    [0, 0, 2, 6, 0, 9, 5, 0, 0],
    [8, 0, 0, 2, 0, 3, 0, 0, 9],
    [0, 0, 5, 0, 1, 0, 3, 0, 0]
]

SUDOKU_HARD = [
    [0, 0, 0, 6, 0, 0, 4, 0, 0],
    [7, 0, 0, 0, 0, 3, 6, 0, 0],
    [0, 0, 0, 0, 9, 1, 0, 8, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 5, 0, 1, 8, 0, 0, 0, 3],
    [0, 0, 0, 3, 0, 6, 0, 4, 5],
    [0, 4, 0, 2, 0, 0, 0, 6, 0],
    [9, 0, 3, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 1, 0, 0]
]
