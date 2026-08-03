from domains.map_coloring.MapColoring import MapColoringCSP
from csp.Backtracking import BacktrackingSolver


def main():
    print("--- Constraint Satisfaction Problem (CSP) Demo ---")
    print("\nSolving Australia Map Coloring problem...")
    
    problem = MapColoringCSP()
    solver = BacktrackingSolver(problem)
    
    solution = solver.solve()
    
    if solver.status == "SUCCESS":
        print("\nSolution found!")
        for var, value in solution.items():
            print(f"  {var}: {value}")
    else:
        print("\nFailed to find a solution.")
        
    print(f"\nNodes expanded: {solver.nodes_expanded}")


if __name__ == "__main__":
    main()
