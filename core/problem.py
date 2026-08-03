from abc import ABC, abstractmethod

class SearchProblem(ABC):
    def __init__(self, start, goal):
        self.start = start
        self.goal = goal
    
    def is_goal_state(self, state) -> bool:
        return state==self.goal

    @abstractmethod
    def get_actions(self, state) -> list:
        pass

    @abstractmethod
    def get_result(self, state, action):
        pass

    def get_cost(self, state, action, next_state)->float:
        return 1
    
    def heuristic(self, state) -> float:
        """Forward heuristic: estimated cost from `state` to the goal."""
        pass

    def reverse_heuristic(self, state) -> float:
        """Backward heuristic: estimated cost from `state` to the start.

        Most domains use symmetric distance metrics (Manhattan, Euclidean),
        so the default implementation delegates to the forward heuristic.
        Override this in asymmetric domains or when the backward search
        direction requires a different admissible estimate.
        """
        return self.heuristic(state)