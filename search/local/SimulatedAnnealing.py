import math
import random
from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class SimulatedAnnealing(SearchAlgorithm):
    """
    Simulated Annealing.

    Uses a temperature schedule to probabilistically accept worse states,
    allowing the algorithm to escape local optima early in the search.
    As temperature decreases, it behaves more like stochastic hill climbing.
    """

    def __init__(self, problem, schedule_func=None):
        super().__init__(problem)
        # Default exponential cooling schedule: T = 1000 * (0.95 ^ t)
        # Drops below 0.001 after ~270 iterations
        if schedule_func is None:
            self.schedule = lambda t: 1000 * (0.95 ** t)
        else:
            self.schedule = schedule_func

    def reset(self):
        super().reset()
        self.current_state = self.problem.initial_state
        self.current_value = self.problem.value(self.current_state)
        
        self.current_node = Node(self.current_state, parent=None, action=None, path_cost=0)
        self.status = SearchStatus.RUNNING

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        T = self.schedule(self.num_iterations)

        if T <= 1e-10:
            # Temperature cooled down, stop
            self.solution_node = self.current_node
            self.status = SearchStatus.SUCCESS
            return

        self.num_iterations += 1

        neighbor = self.problem.get_random_neighbor(self.current_state)
        neighbor_value = self.problem.value(neighbor)
        self.nodes_generated += 1
        
        delta_e = neighbor_value - self.current_value

        if delta_e > 0:
            # Better state, always accept
            self.current_state = neighbor
            self.current_value = neighbor_value
        else:
            # Worse state, accept with probability e^(delta_E / T)
            # (Note: delta_E is negative, so this is e^(-|delta_E| / T) <= 1)
            probability = math.exp(delta_e / T)
            if random.random() < probability:
                self.current_state = neighbor
                self.current_value = neighbor_value

        self.nodes_expanded += 1
        self.current_node = Node(self.current_state, parent=None, action=None, path_cost=0)

    @property
    def frontier_states(self):
        return set()

    @property
    def explored(self):
        return {self.current_state}

    @explored.setter
    def explored(self, value):
        pass
