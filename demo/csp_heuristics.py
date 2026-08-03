from domains.map_coloring.MapColoring import MapColoringCSP
from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default, inference_default
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.heuristics.LCV import lcv
from csp.inference.ForwardChecking import forward_checking


def run_solver(name, variable_selector, value_orderer, inference_engine):
    print(f"\n--- {name} ---")
    problem = MapColoringCSP()
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=variable_selector,
        order_domain_values=value_orderer,
        inference=inference_engine
    )
    
    solution = solver.solve()
    print(f"Nodes expanded: {solver.nodes_expanded}")
    return solver.nodes_expanded


def main():
    print("Evaluating CSP Heuristics and Inference on Map Coloring")
    
    # 1. Naive Backtracking
    run_solver(
        "Naive Backtracking",
        unassigned_variable_default,
        order_domain_values_default,
        inference_default
    )
    
    # 2. MRV + Degree
    run_solver(
        "MRV + Degree Heuristic",
        mrv_with_degree_heuristic,
        order_domain_values_default,
        inference_default
    )
    
    # 3. MRV + Degree + Forward Checking
    run_solver(
        "MRV + Degree Heuristic + Forward Checking",
        mrv_with_degree_heuristic,
        order_domain_values_default,
        forward_checking
    )
    
    # 4. MRV + Degree + LCV + Forward Checking
    run_solver(
        "MRV + Degree + LCV + Forward Checking",
        mrv_with_degree_heuristic,
        lcv,
        forward_checking
    )


if __name__ == "__main__":
    main()
