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

    def __init__(self, problem, schedule_func=None, epsilon: float = 1e-6, patience: int = 200):
        super().__init__(problem)
        self.epsilon = epsilon
        self.patience = patience
        self._best_value = None
        self._stall_count = 0
        if schedule_func is None:
            scale = (problem.n // 4)**1.2 if hasattr(problem, 'n') and problem.n is not None else 1
            self.schedule = lambda t: 100 * (0.95 ** (t / scale))
        else:
            self.schedule = schedule_func

    def reset(self):
        super().reset()
        self.current_state = self.problem.initial_state
        self.current_value = self.problem.value(self.current_state)
        self._best_value = self.current_value
        self._stall_count = 0
        
        self.current_node = Node(self.current_state, parent=None, action=None, path_cost=0)
        self.status = SearchStatus.RUNNING

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        T = self.schedule(self.num_iterations)

        if T <= 1e-10:
            best = getattr(self, 'best_state', self.current_state)
            self.solution_node = Node(best, parent=None, action=None, path_cost=0)
            self.status = SearchStatus.SUCCESS
            return

        self.num_iterations += 1

        neighbor = self.problem.get_random_neighbor(self.current_state)
        neighbor_value = self.problem.value(neighbor)
        self.nodes_generated += 1
        
        delta_e = neighbor_value - self.current_value

        if delta_e > 0:
            self.current_state = neighbor
            self.current_value = neighbor_value
            self.nodes_expanded += 1
        else:
            probability = math.exp(delta_e / T)
            if random.random() < probability:
                self.current_state = neighbor
                self.current_value = neighbor_value
                self.nodes_expanded += 1

        self.current_node = Node(self.current_state, parent=None, action=None, path_cost=0)

        # Track the absolute best state found during the search
        if self._best_value is None or self.current_value > self._best_value + self.epsilon:
            self._best_value = self.current_value
            self.best_state = self.current_state

    @property
    def frontier_states(self):
        return set()

    @property
    def explored(self):
        return {self.current_state}

    @explored.setter
    def explored(self, value):
        pass
