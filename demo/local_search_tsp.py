import random
from domains.tsp.TSPProblem import TSPProblem
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm

def generate_random_cities(n, width=100, height=100):
    return [(random.uniform(0, width), random.uniform(0, height)) for _ in range(n)]

def main():
    N_CITIES = 15
    print(f"--- TSP Local Search Demo ({N_CITIES} cities) ---")
    
    cities = generate_random_cities(N_CITIES)
    problem = TSPProblem(cities)
    
    initial_dist = -problem.value(problem.initial_state)
    print(f"Initial Distance: {initial_dist:.2f}")

    print("\n1. Hill Climbing (Steepest-Ascent)")
    hc = HillClimbing(problem)
    hc.run()
    hc_dist = -problem.value(hc.solution_node.state)
    print(f"   Final Distance: {hc_dist:.2f}")

    print("\n2. Simulated Annealing")
    sa = SimulatedAnnealing(problem)
    sa.run()
    sa_dist = -problem.value(sa.solution_node.state)
    print(f"   Final Distance: {sa_dist:.2f}")

    print("\n3. Local Beam Search (k=5)")
    lbs = LocalBeamSearch(problem, k=5)
    lbs.run()
    lbs_dist = -problem.value(lbs.solution_node.state)
    print(f"   Final Distance: {lbs_dist:.2f}")

    print("\n4. Genetic Algorithm")
    ga = GeneticAlgorithm(problem, pop_size=50, max_generations=500)
    ga.run()
    ga_dist = -problem.value(ga.solution_node.state)
    print(f"   Final Distance: {ga_dist:.2f}")

if __name__ == "__main__":
    random.seed(42)
    main()
