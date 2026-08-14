import time

from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm,SearchStatus
from core.problem import SearchProblem
from core.result import Result

class DLS(SearchAlgorithm):
  def __init__(self, problem:SearchProblem,max_depth:int):
    super().__init__(problem)
    self.max_depth=max_depth
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

    self.explored=set()
    self.current_node=self.frontier[0]

  def search_step(self):
    if not self.frontier:
        self.status=SearchStatus.DEPTH_EXCEEDED
        return None

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
            if child.depth>self.max_depth:
              continue
            
            self.frontier.append(child)
            self.frontier_states.add(
                child_state
            )
            self.nodes_generated += 1
            
            self.max_frontier_size = max(
                self.max_frontier_size,
                len(self.frontier)
            )

    return False

class TrueIDDFS():
  def __init__(self, problem,start_depth,depth_increassing_rate=2,visualize=True):
     self.start_depth=start_depth
     self.rate = depth_increassing_rate
     self.problem = problem
     self.visualize=visualize

     self.cur_depth = self.start_depth
     self.search_engine = DLS(problem,self.cur_depth)

     self.num_iterations = 0
  
  @property
  def solution_node(self):
     return self.search_engine.solution_node
  
  @property
  def nodes_expanded(self):
     return self.search_engine.nodes_expanded
  
  @property
  def nodes_generated(self):
     return self.search_engine.nodes_generated
  
  @property
  def max_frontier_size(self):
     return self.search_engine.max_frontier_size
  
  @property
  def current_node(self):
     return self.search_engine.current_node

  @property
  def frontier_states(self):
     return self.search_engine.frontier_states
  
  @property
  def frontier(self):
     return self.search_engine.frontier

  @property
  def explored(self):
     return self.search_engine.explored
  
  @property
  def status(self):
     return self.search_engine.status

  def search_step(self):
      if self.status==SearchStatus.DEPTH_EXCEEDED:
        if self.visualize:
          print("Depth Limit Reached Doubling ...")
        
        self.cur_depth*=self.rate
        self.num_iterations+=1
        self.search_engine=DLS(self.problem,self.cur_depth)

        return False
    
      return self.search_engine.search_step()

  def run(self):
    start_time = time.time()

    while self.status == SearchStatus.RUNNING or self.status==SearchStatus.DEPTH_EXCEEDED:
        self.search_step()

    end_time = time.time()

    return Result(
        success=self.status == SearchStatus.SUCCESS,
        solution=self.solution_node,
        runtime=end_time - start_time,
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
        metadata={
           "number of iterations":self.num_iterations
        }
    )

        
  
  def reset(self):
     self.cur_depth=self.start_depth
     self.search_engine=DLS(self.problem,self.cur_depth)


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
        print(f"Doubling the depth limit. Depth before doubling {self.max_height}")

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

    try:
            from utils.auto_logger import auto_log_result
            auto_log_result(self, res)
        except Exception:
            pass
        return result
  
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