from abc import ABC, abstractmethod
from typing import Any, List


class OnlineSearchEnvironment(ABC):
    """
    Base interface for an environment in online search.
    The agent interacts with this environment by executing actions and receiving percepts.
    """
    @abstractmethod
    def get_percept(self) -> Any:
        """Returns the current percept (state) the agent observes."""
        pass

    @abstractmethod
    def execute_action(self, action: Any) -> Any:
        """
        Executes the action in the environment and returns the new percept (state).
        """
        pass

    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        """Checks if the given state is a goal state."""
        pass

    @abstractmethod
    def get_actions(self, state: Any) -> List[Any]:
        """Returns the list of valid actions from the given state."""
        pass
    
    @abstractmethod
    def get_cost(self, state: Any, action: Any, next_state: Any) -> float:
        """Returns the cost of taking the action from state to next_state."""
        pass


class OnlineSearchAgent(ABC):
    """
    Base interface for an online search agent.
    """
    def __init__(self, env: OnlineSearchEnvironment):
        self.env = env
        self.current_state = env.get_percept()

    @abstractmethod
    def search_step(self, percept: Any) -> Any:
        """
        Given the current percept, returns the next action to execute.
        If the agent has reached the goal or cannot move, it should return None.
        """
        pass
