from abc import ABC, abstractmethod
from enum import Enum, auto

class SearchStatus(Enum):
    RUNNING = auto()
    SUCCESS = auto()
    FAILURE = auto()

class SearchAlgorithm(ABC):

    def __init__(self, problem):
        self.problem = problem

        self.frontier = []
        self.explored = set()

        self.current_node = None
        self.solution_node = None
        self.status = SearchStatus.RUNNING

    @abstractmethod
    def search_step(self):
        pass
    
    @property
    def solved(self):
      return self.status == SearchStatus.SUCCESS
    
    @property
    def failed(self):
      return self.status == SearchStatus.FAILURE