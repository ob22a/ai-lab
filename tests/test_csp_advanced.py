import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pytest
from csp.CSPProblem import CSPProblem
from domains.map_coloring.MapColoring import MapColoringCSP, NotEqualConstraint
from domains.n_queens.NQueensCSP import NQueensCSP
from csp.TreeCSP import TreeCSPSolver, is_tree_graph, get_constraint_graph
from csp.CycleCutset import CycleCutsetSolver, find_cycle_cutset
from csp.TreeDecomposition import TreeDecomposition, TreeDecompositionSolver, auto_tree_decomposition
from csp.SymmetricBacktracking import SymmetricBacktrackingSolver
from csp.Backtracking import BacktrackingSolver
from csp.heuristics.MRV import mrv
from csp.inference.MAC import mac
from csp.inference.ForwardChecking import forward_checking
from visualization.NQueensVisualizer import NQueensVisualizer


def test_tree_csp_solver():
    # Tree graph: A - B, A - C, C - D
    variables = ['A', 'B', 'C', 'D']
    domains = {
        'A': [1, 2],
        'B': [1, 2],
        'C': [1, 2],
        'D': [1, 2]
    }
    problem = CSPProblem(variables, domains)
    problem.add_constraint(NotEqualConstraint('A', 'B'))
    problem.add_constraint(NotEqualConstraint('A', 'C'))
    problem.add_constraint(NotEqualConstraint('C', 'D'))

    solver = TreeCSPSolver(problem, root='A')
    solution = solver.solve()

    assert solver.status == "SUCCESS"
    assert solution is not None
    assert len(solution) == 4
    assert solution['A'] != solution['B']
    assert solution['A'] != solution['C']
    assert solution['C'] != solution['D']


def test_tree_csp_cycle_detection():
    # Cyclic graph: A - B, B - C, C - A (Triangle)
    variables = ['A', 'B', 'C']
    domains = {'A': [1, 2], 'B': [1, 2], 'C': [1, 2]}
    problem = CSPProblem(variables, domains)
    problem.add_constraint(NotEqualConstraint('A', 'B'))
    problem.add_constraint(NotEqualConstraint('B', 'C'))
    problem.add_constraint(NotEqualConstraint('C', 'A'))

    solver = TreeCSPSolver(problem)
    with pytest.raises(ValueError, match="contains cycles"):
        solver.solve()


def test_cycle_cutset_solver_map_coloring():
    problem = MapColoringCSP()
    # Australia map coloring with cutset ['SA']
    solver = CycleCutsetSolver(problem, cutset=['SA'])
    solution = solver.solve()

    assert solver.status == "SUCCESS"
    assert solution is not None
    assert len(solution) == 7

    # Verify all constraints
    assert solution['WA'] != solution['NT']
    assert solution['WA'] != solution['SA']
    assert solution['NT'] != solution['SA']
    assert solution['NT'] != solution['Q']
    assert solution['SA'] != solution['Q']
    assert solution['SA'] != solution['NSW']
    assert solution['SA'] != solution['V']
    assert solution['Q'] != solution['NSW']
    assert solution['NSW'] != solution['V']


def test_cycle_cutset_auto_detection():
    problem = MapColoringCSP()
    cutset = find_cycle_cutset(problem)
    assert len(cutset) > 0
    solver = CycleCutsetSolver(problem)
    solution = solver.solve()
    assert solver.status == "SUCCESS"
    assert solution is not None


def test_tree_decomposition_solver_map_coloring():
    problem = MapColoringCSP()
    
    # Manual Tree Decomposition for Australia
    clusters = {
        "C1": ["WA", "NT", "SA"],
        "C2": ["NT", "SA", "Q"],
        "C3": ["SA", "Q", "NSW"],
        "C4": ["SA", "NSW", "V"],
        "C5": ["T"]
    }
    edges = [
        ("C1", "C2"),
        ("C2", "C3"),
        ("C3", "C4"),
        ("C4", "C5")
    ]
    decomp = TreeDecomposition(clusters, edges)
    is_valid, msg = decomp.validate(problem)
    assert is_valid, msg

    solver = TreeDecompositionSolver(problem, decomposition=decomp)
    solution = solver.solve()

    assert solver.status == "SUCCESS"
    assert solution is not None
    assert len(solution) == 7
    assert solution['WA'] != solution['NT']
    assert solution['WA'] != solution['SA']
    assert solution['NT'] != solution['SA']
    assert solution['NT'] != solution['Q']
    assert solution['SA'] != solution['Q']
    assert solution['SA'] != solution['NSW']
    assert solution['SA'] != solution['V']
    assert solution['Q'] != solution['NSW']
    assert solution['NSW'] != solution['V']


def test_auto_tree_decomposition():
    problem = MapColoringCSP()
    decomp = auto_tree_decomposition(problem)
    is_valid, msg = decomp.validate(problem)
    assert is_valid, msg

    solver = TreeDecompositionSolver(problem, decomposition=decomp)
    solution = solver.solve()
    assert solver.status == "SUCCESS"
    assert solution is not None


def test_symmetric_backtracking_map_coloring():
    problem = MapColoringCSP()
    solver = SymmetricBacktrackingSolver(problem, value_symmetry=True)
    solution = solver.solve()
    assert solver.status == "SUCCESS"
    assert solution is not None
    assert solver.symmetric_branches_pruned > 0


def test_symmetric_backtracking_nqueens():
    problem = NQueensCSP(n=8, break_symmetry=True)
    solver = SymmetricBacktrackingSolver(
        problem,
        select_unassigned_variable=mrv,
        inference=mac
    )
    solution = solver.solve()
    assert solver.status == "SUCCESS"
    assert solution is not None
    assert len(solution) == 8
    
    # Ensure no attacking pairs
    for r1 in range(8):
        for r2 in range(r1 + 1, 8):
            c1, c2 = solution[r1], solution[r2]
            assert c1 != c2
            assert abs(r1 - r2) != abs(c1 - c2)


def test_nqueens_visualizer_csp_headless():
    problem = NQueensCSP(n=6, break_symmetry=True)
    solver = SymmetricBacktrackingSolver(problem, select_unassigned_variable=mrv, inference=mac)
    visualizer = NQueensVisualizer(problem, solver, cell_size=40, fps=10)

    assert visualizer.is_csp is True
    assert len(visualizer.history) > 1

    # Step forward and backward
    visualizer._step_forward()
    visualizer._step_forward()
    assert visualizer.history_index == 2
    visualizer._step_backward()
    assert visualizer.history_index == 1

    # Render frame
    visualizer.render()

    # Restart
    visualizer.restart()
    assert visualizer.history_index == 0
