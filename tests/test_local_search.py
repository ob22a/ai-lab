import pytest
from domains.n_queens.NQueensProblem import NQueensProblem
from search.local.HillClimbing import HillClimbing
from search.local.SimulatedAnnealing import SimulatedAnnealing
from search.local.LocalBeamSearch import LocalBeamSearch
from search.local.GeneticAlgorithm import GeneticAlgorithm

def test_hill_climbing():
    problem = NQueensProblem(n=4)
    algo = HillClimbing(problem)
    result = algo.run()
    assert algo.num_iterations > 0
    assert algo.current_value <= problem.max_fitness

def test_simulated_annealing():
    problem = NQueensProblem(n=4)
    algo = SimulatedAnnealing(problem)
    result = algo.run()
    assert algo.num_iterations > 0

def test_local_beam_search():
    problem = NQueensProblem(n=4)
    algo = LocalBeamSearch(problem, k=3)
    result = algo.run()
    assert algo.num_iterations > 0

def test_genetic_algorithm():
    problem = NQueensProblem(n=4)
    algo = GeneticAlgorithm(problem, pop_size=10, max_generations=50)
    result = algo.run()
    assert algo.num_iterations > 0
