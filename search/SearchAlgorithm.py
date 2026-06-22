import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from core.result import Result

class SearchStatus(Enum):
    RUNNING = auto()
    SUCCESS = auto()
    FAILURE = auto()
    DEPTH_EXCEEDED = auto()

class SearchAlgorithm(ABC):

    def __init__(self, problem):
        self.problem = problem

        self.frontier = []
        self.explored = set()

        self.current_node = None
        self.solution_node = None
        self.status = SearchStatus.RUNNING

        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.max_frontier_size = 1

    @abstractmethod
    def search_step(self):
        pass
    
    @property
    def solved(self):
      return self.status == SearchStatus.SUCCESS
    
    @property
    def failed(self):
      return self.status == SearchStatus.FAILURE
    
    @property
    def depth_exceeded(self):
        return self.search_step==SearchStatus.DEPTH_EXCEEDED
    
    def get_result(self, runtime=0.0, metadata=None):
        if metadata is None:
            metadata = {}
        return Result(
            success=self.status == SearchStatus.SUCCESS,
            solution=self.solution_node,
            runtime=runtime,
            nodes_expanded=getattr(self, "nodes_expanded", 0),
            nodes_generated=getattr(self, "nodes_generated", 0),
            path_cost=(
                self.solution_node.path_cost
                if self.solution_node else 0
            ),
            solution_depth=(
                self.solution_node.depth
                if self.solution_node else 0
            ),
            max_frontier_size=getattr(
                self, "max_frontier_size", 0
            ),
            metadata=metadata
        )

    def run(self,metadata=None):
        self.reset()

        start_time = time.time()

        while self.status == SearchStatus.RUNNING:
            self.search_step()

        end_time = time.time()

        return self.get_result(runtime=end_time - start_time, metadata=metadata)

    def reset(self):
        self.frontier = []
        self.explored = set()
        
        self.current_node = None
        self.solution_node = None
        self.status = SearchStatus.RUNNING

        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.max_frontier_size = 1