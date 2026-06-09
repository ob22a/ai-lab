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
    
    def heuristic(self,state)->float:
        pass