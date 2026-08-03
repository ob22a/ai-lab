import random
from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class LocalBeamSearch(SearchAlgorithm):
    """
    Local Beam Search.

    Maintains k states rather than just 1. At each step, it generates all
    successors of all k states. If any successor is a goal (or we reach an optimum),
    it halts. Otherwise, it selects the k best successors from the complete list
    and repeats.
    """

    def __init__(self, problem, k=5):
        super().__init__(problem)
        self.k = k
        self.beam_states = []
        self.best_state = None
        self.best_value = float('-inf')

    def reset(self):
        super().reset()
        # Initialize with k random states (including initial state as one of them to guarantee we search around it)
        self.beam_states = [self.problem.initial_state]
        for _ in range(self.k - 1):
            self.beam_states.append(self.problem.get_random_state())
        
        self.best_state = max(self.beam_states, key=self.problem.value)
        self.best_value = self.problem.value(self.best_state)

        # Visualizer representation (just show the best node)
        self.current_node = Node(self.best_state, parent=None, action=None, path_cost=0)
        self.status = SearchStatus.RUNNING

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        self.num_iterations += 1

        all_successors = []
        for state in self.beam_states:
            neighbors = self.problem.get_all_neighbors(state)
            self.nodes_expanded += 1
            all_successors.extend(neighbors)

        # Optional: remove duplicates to maintain diversity in the beam
        unique_successors = list(set(all_successors))
        
        # Evaluate all successors
        scored_successors = []
        for neighbor in unique_successors:
            val = self.problem.value(neighbor)
            self.nodes_generated += 1
            scored_successors.append((val, neighbor))

        # Sort by value descending
        scored_successors.sort(key=lambda x: x[0], reverse=True)

        new_best_value, new_best_state = scored_successors[0]

        if new_best_value <= self.best_value:
            # We reached a peak where no successor across the entire beam is better
            self.solution_node = self.current_node
            self.status = SearchStatus.SUCCESS
            return

        # Keep the top k
        self.beam_states = [s[1] for s in scored_successors[:self.k]]
        self.best_value = new_best_value
        self.best_state = new_best_state
        
        self.current_node = Node(self.best_state, parent=None, action=None, path_cost=0)

    @property
    def frontier_states(self):
        # We can expose the beam as the frontier for the visualizer
        return set(self.beam_states)

    @property
    def explored(self):
        return {self.best_state}

    @explored.setter
    def explored(self, value):
        pass
