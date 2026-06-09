import heapq

from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus
from core.problem import SearchProblem

class GreedyBestFirstSearch(SearchAlgorithm):
  def __init__(self, problem:SearchProblem):
    super().__init__(problem)

    self.frontier = [
      (0,
        Node(
          state=problem.start,
          parent=None,
          action=None,
          path_cost=0
        )
      )
    ]

    self.frontier_states = {
      problem.start
    }

    self.explored = set()
    self.current_node = self.frontier[0][1]
    self.explored.add(self.current_node.state)
  
  def search_step(self):
    if not self.frontier:
      self.status=SearchStatus.FAILURE
      return None
    
    _,node = heapq.heappop(self.frontier)
    self.current_node=node
    self.frontier_states.remove(node.state)
    self.nodes_expanded+=1

    if self.problem.is_goal_state(node.state):
      self.solution_node=node
      self.status=SearchStatus.SUCCESS

      return node

    for action in self.problem.get_actions(node.state):
      child_state = self.problem.get_result(node.state,action)
      
      if child_state not in self.explored and child_state not in self.frontier_states:
        child = Node(
          state=child_state,
          parent=node,
          action=action,
          path_cost=node.path_cost + 1
        )

        heuristic = self.problem.heuristic(child_state)

        heapq.heappush(self.frontier,(heuristic,child))
        self.explored.add(child_state)

        self.frontier_states.add(
          child_state
        )
        self.nodes_generated += 1
        
        self.max_frontier_size = max(
          self.max_frontier_size,
          len(self.frontier)
        )
    
    return False
  
  def reset(self):
    super().reset()
    self.frontier=[
      (0,
        Node(
          state=self.problem.start,
          parent=None,
          action=None,
          path_cost=0
        )
      )
    ]

    self.current_node=self.frontier[0]
    self.frontier_states={
      self.problem.start
    }