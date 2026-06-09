import time

from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm,SearchStatus
from core.problem import SearchProblem



class OptimizedIDDFS(SearchAlgorithm):
  def __init__(self, problem:SearchProblem,max_height=5,visualize=True):
    super().__init__(problem)
    self.start_max_height=max_height
    self.visualize=visualize

    self.max_height = max_height
    self.height_updates=0

    self.frontier = [
      Node(
        state=problem.start,
        parent=None,
        action=None,
        path_cost=0
      )
    ]
    self.frontier_states = {
      problem.start
    }
    self.cutoff_nodes=[]

    self.explored = set()
    self.current_node = self.frontier[0]

  def search_step(self):
    if not self.frontier and not self.cutoff_nodes:
      self.status=SearchStatus.FAILURE
      return None
    
    if not self.frontier:
      if self.visualize:
        print(f"Doubling the depth limit. This will cause sleep for 1 second to make it more clear in the visualization. Depth before doubling {self.max_height}")
        time.sleep(1)

      self.height_updates+=1
      self.frontier=self.cutoff_nodes[::-1]
      self.frontier_states={node.state for node in self.frontier}
      self.cutoff_nodes=[]

      self.max_height*=2
    
    node = self.frontier.pop()
    self.current_node = node
    self.frontier_states.remove(
        node.state
    )
    self.nodes_expanded += 1

    if self.problem.is_goal_state(node.state):
      self.solution_node = node
      self.status=SearchStatus.SUCCESS

      return node

    self.explored.add(node.state)

    for action in self.problem.get_actions(node.state):
      child_state = self.problem.get_result(
          node.state,
          action
      )

      if child_state not in self.explored  and child_state not in self.frontier_states:
          child = Node(
              state=child_state,
              parent=node,
              action=action,
              path_cost=node.path_cost + 1
          )
          
          self.nodes_generated += 1
          self.frontier_states.add(
              child_state
          )

          if child.depth>self.max_height:
            self.cutoff_nodes.append(child)  
            continue 
          
          self.frontier.append(child)
          
          self.max_frontier_size = max(
              self.max_frontier_size,
              len(self.frontier)
          )

    return False

  def run(self):
    result = super().run()
    metadata = {
      "depth_updates": self.height_updates,
      "final_depth": self.max_height
    }

    result.metadata=metadata

    return result
  
  def reset(self):
    super().reset()
    self.frontier=[
      Node(
          state=self.problem.start,
          parent=None,
          action=None,
          path_cost=0
      )
    ]
    self.current_node=self.frontier[0]
    self.frontier_states={
      self.problem.start
    }
    self.max_height=self.start_max_height
    self.height_updates=0