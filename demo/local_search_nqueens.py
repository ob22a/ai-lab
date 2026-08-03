from domains.n_queens.NQueensProblem import NQueensProblem
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm

def print_board(state):
    n = len(state)
    for row in range(n):
        line = []
        for col in range(n):
            if state[col] == row:
                line.append("Q")
            else:
                line.append(".")
        print(" ".join(line))
    print()


def main():
    N = 8
    print(f"--- {N}-Queens Local Search Demo ---")
    problem = NQueensProblem(N)
    
    print(f"Initial State: {problem.initial_state}")
    print(f"Initial Value: {problem.value(problem.initial_state)} / {problem.max_fitness}")
    print_board(problem.initial_state)

    print("1. Hill Climbing (Steepest-Ascent)")
    hc = HillClimbing(problem)
    hc.run()
    hc_val = problem.value(hc.solution_node.state)
    print(f"   Final Value: {hc_val} (Optimal? {hc_val == problem.max_fitness})")
    print(f"   Nodes Expanded: {hc.nodes_expanded}")

    print("\n2. Simulated Annealing")
    sa = SimulatedAnnealing(problem)
    sa.run()
    sa_val = problem.value(sa.solution_node.state)
    print(f"   Final Value: {sa_val} (Optimal? {sa_val == problem.max_fitness})")
    print(f"   Nodes Expanded: {sa.nodes_expanded}")

    print("\n3. Local Beam Search (k=5)")
    lbs = LocalBeamSearch(problem, k=5)
    lbs.run()
    lbs_val = problem.value(lbs.solution_node.state)
    print(f"   Final Value: {lbs_val} (Optimal? {lbs_val == problem.max_fitness})")
    print(f"   Nodes Expanded: {lbs.nodes_expanded}")

    print("\n4. Genetic Algorithm")
    ga = GeneticAlgorithm(problem, pop_size=50, max_generations=200)
    ga.run()
    ga_val = problem.value(ga.solution_node.state)
    print(f"   Final Value: {ga_val} (Optimal? {ga_val == problem.max_fitness})")
    print(f"   Nodes Expanded (Crossovers): {ga.nodes_expanded}")
    
    if ga_val == problem.max_fitness:
        print("\nOptimal Board Found by GA:")
        print_board(ga.solution_node.state)

if __name__ == "__main__":
    import random
    random.seed(42)
    main()
