import random
from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class GeneticAlgorithm(SearchAlgorithm):
    """
    Genetic Algorithm.

    Maintains a population of states. Iteratively selects parents based on fitness,
    crosses them over, and mutates the offspring to form the next generation.
    """

    def __init__(self, problem, pop_size=100, mutation_rate=0.1, max_generations=1000):
        super().__init__(problem)
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.max_generations = max_generations
        self.population = []
        self.best_state = None
        self.best_value = float('-inf')

    def reset(self):
        super().reset()
        
        self.population = [self.problem.initial_state]
        for _ in range(self.pop_size - 1):
            self.population.append(self.problem.get_random_state())

        self.best_state = max(self.population, key=self.problem.value)
        self.best_value = self.problem.value(self.best_state)

        self.current_node = Node(self.best_state, parent=None, action=None, path_cost=0)
        self.status = SearchStatus.RUNNING

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        if self.num_iterations >= self.max_generations:
            self.solution_node = self.current_node
            self.status = SearchStatus.SUCCESS
            return

        self.num_iterations += 1

        # Evaluate fitness for the current population
        fitnesses = []
        for state in self.population:
            val = self.problem.value(state)
            self.nodes_generated += 1
            # Adjust fitness to be strictly positive if needed for roulette wheel,
            # but usually value() is designed appropriately or we use rank selection.
            # Assuming value > 0 for standard probability selection.
            # If value can be negative, we might need fitness shifting.
            fitnesses.append(val)
        
        # Shift fitnesses to be > 0 if there are negative values
        min_fit = min(fitnesses)
        if min_fit <= 0:
            shift = abs(min_fit) + 1e-5
            fitnesses = [f + shift for f in fitnesses]

        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            probabilities = [1 / self.pop_size] * self.pop_size
        else:
            probabilities = [f / total_fitness for f in fitnesses]

        new_population = []

        # Elitism: carry over the best state automatically
        new_population.append(self.best_state)

        for _ in range((self.pop_size - 1) // 2):
            # Select two parents
            parents = random.choices(self.population, weights=probabilities, k=2)
            
            # Crossover
            child1, child2 = self.problem.crossover(parents[0], parents[1])
            self.nodes_expanded += 2 # Treating a crossover as expanding a pair

            # Mutation
            if random.random() < self.mutation_rate:
                child1 = self.problem.mutate(child1)
            if random.random() < self.mutation_rate:
                child2 = self.problem.mutate(child2)

            new_population.extend([child1, child2])

        # If pop_size was even, we might have added one too many because of elitism
        self.population = new_population[:self.pop_size]

        # Update best state
        current_best = max(self.population, key=self.problem.value)
        current_best_val = self.problem.value(current_best)

        if current_best_val > self.best_value:
            self.best_value = current_best_val
            self.best_state = current_best

        self.current_node = Node(self.best_state, parent=None, action=None, path_cost=0)

    @property
    def current_state(self):
        return self.best_state

    @current_state.setter
    def current_state(self, value):
        self.best_state = value

    @property
    def frontier_states(self):
        return set(self.population)

    @property
    def explored(self):
        return {self.best_state}

    @explored.setter
    def explored(self, value):
        pass
