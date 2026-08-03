from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class HillClimbing(SearchAlgorithm):
    """
    Steepest-Ascent Hill Climbing.

    Evaluates all neighbors of the current state and moves to the one
    with the highest objective value. Stops when no neighbor is strictly
    better than the current state (reaches a local optimum).
    """

    def __init__(self, problem):
        super().__init__(problem)

    def reset(self):
        super().reset()
        # In optimization problems, we don't care about path cost or actions.
        self.current_state = self.problem.initial_state
        self.current_value = self.problem.value(self.current_state)

        # For visualizer compatibility
        self.current_node = Node(self.current_state, parent=None, action=None, path_cost=0)
        
        self.status = SearchStatus.RUNNING

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        self.num_iterations += 1

        neighbors = self.problem.get_all_neighbors(self.current_state)
        
        best_neighbor = None
        best_value = float('-inf')

        for neighbor in neighbors:
            val = self.problem.value(neighbor)
            self.nodes_generated += 1
            if val > best_value:
                best_value = val
                best_neighbor = neighbor

        self.nodes_expanded += 1

        # Strict improvement required
        if best_value <= self.current_value:
            # Reached a local (or global) optimum
            self.solution_node = self.current_node
            self.status = SearchStatus.SUCCESS
            return

        # Move to the best neighbor
        self.current_state = best_neighbor
        self.current_value = best_value
        
        # Update node for visualizer (we don't track paths, just current state)
        self.current_node = Node(self.current_state, parent=None, action=None, path_cost=0)

    # For visualizer compatibility
    @property
    def frontier_states(self):
        return set()

    @property
    def explored(self):
        return {self.current_state}

    @explored.setter
    def explored(self, value):
        pass
