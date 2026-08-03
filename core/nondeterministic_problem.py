from abc import ABC, abstractmethod
from typing import Any, List, Set
from core.problem import SearchProblem


class NondeterministicProblem(ABC):
    """
    Base interface for nondeterministic search problems.
    Unlike standard SearchProblem which has `get_result(state, action) -> state`,
    this has `results(state, action) -> set(state)` returning all possible outcomes.
    """
    def __init__(self, initial_state: Any):
        self.initial_state = initial_state
        
    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        pass
        
    @abstractmethod
    def get_actions(self, state: Any) -> List[Any]:
        pass

    @abstractmethod
    def results(self, state: Any, action: Any) -> Set[Any]:
        """
        Returns a set of all possible states that could result from executing
        the given action in the given state.
        """
        pass


