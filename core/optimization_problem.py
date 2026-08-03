from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class OptimizationProblem(ABC):
    """
    Base interface for optimization/local search problems.
    Unlike path-finding search, optimization cares only about the final state,
    not how we got there.
    """
    
    def __init__(self, initial_state: Any):
        self.initial_state = initial_state

    @abstractmethod
    def value(self, state: Any) -> float:
        """
        The objective value of the state.
        By default, we assume we want to MAXIMIZE this value.
        If a problem naturally minimizes (e.g. TSP distance), return the negative of the distance.
        """
        pass

    @abstractmethod
    def get_random_neighbor(self, state: Any) -> Any:
        """
        Returns a single random neighbor of the state.
        Used by Simulated Annealing and Stochastic Hill Climbing.
        """
        pass

    @abstractmethod
    def get_all_neighbors(self, state: Any) -> List[Any]:
        """
        Returns all possible neighbors of the state.
        Used by Steepest-Ascent Hill Climbing.
        """
        pass

    # Optional methods for Genetic Algorithms (can be overridden if GA is used)
    def crossover(self, state1: Any, state2: Any) -> Tuple[Any, Any]:
        """
        Returns two child states produced by crossing over state1 and state2.
        """
        raise NotImplementedError("Crossover not implemented for this problem.")

    def mutate(self, state: Any) -> Any:
        """
        Returns a mutated version of the state.
        """
        raise NotImplementedError("Mutation not implemented for this problem.")

    def get_random_state(self) -> Any:
        """
        Returns a completely random valid state.
        Used to initialize the population for GA or beam search.
        """
        raise NotImplementedError("Random state generation not implemented for this problem.")
