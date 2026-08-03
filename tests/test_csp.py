import pytest
from csp.CSPProblem import CSPProblem, Constraint
from domains.map_coloring.MapColoring import MapColoringCSP, NotEqualConstraint
from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default, inference_default
from csp.heuristics.MRV import mrv
from csp.inference.ForwardChecking import forward_checking
from csp.inference.MAC import mac


def test_csp_problem_initialization():
    variables = ['A', 'B']
    domains = {'A': [1, 2], 'B': [2, 3]}
    problem = CSPProblem(variables, domains)
    
    assert problem.variables == ['A', 'B']
    assert problem.domains['A'] == [1, 2]
    assert problem.domains['B'] == [2, 3]
    # Constraints dict should be initialized to empty lists for each var
    assert problem.constraints['A'] == []
    assert problem.constraints['B'] == []


def test_not_equal_constraint():
    constraint = NotEqualConstraint('A', 'B')
    
    # Not fully assigned
    assert constraint.is_satisfied({'A': 1}) == True
    
    # Satisfied
    assert constraint.is_satisfied({'A': 1, 'B': 2}) == True
    
    # Violated
    assert constraint.is_satisfied({'A': 2, 'B': 2}) == False


def test_map_coloring_backtracking():
    problem = MapColoringCSP()
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=unassigned_variable_default,
        order_domain_values=order_domain_values_default,
        inference=inference_default
    )
    
    solution = solver.solve()
    assert solver.status == "SUCCESS"
    assert solution is not None
    assert len(solution) == 7
    
    # Verify no adjacent regions have the same color
    assert solution['WA'] != solution['NT']
    assert solution['WA'] != solution['SA']
    assert solution['NT'] != solution['SA']
    assert solution['NT'] != solution['Q']
    assert solution['SA'] != solution['Q']
    assert solution['SA'] != solution['NSW']
    assert solution['SA'] != solution['V']
    assert solution['Q'] != solution['NSW']
    assert solution['NSW'] != solution['V']


def test_map_coloring_mac():
    problem = MapColoringCSP()
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=mrv,
        order_domain_values=order_domain_values_default,
        inference=mac
    )
    
    solution = solver.solve()
    assert solver.status == "SUCCESS"
    assert solution is not None
    assert len(solution) == 7
    # MAC should solve Australia with zero backtracks (7 node expansions)
    assert solver.nodes_expanded == 7

def test_n_queens_csp():
    from domains.n_queens.NQueensCSP import NQueensCSP
    problem = NQueensCSP(n=4)
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=mrv,
        order_domain_values=order_domain_values_default,
        inference=mac
    )
    solution = solver.solve()
    assert solver.status == "SUCCESS"
    assert solution is not None
    assert len(solution) == 4
    
    # Verify no queens attack each other
    for r1 in range(4):
        for r2 in range(r1 + 1, 4):
            c1 = solution[r1]
            c2 = solution[r2]
            assert c1 != c2
            assert abs(r1 - r2) != abs(c1 - c2)

