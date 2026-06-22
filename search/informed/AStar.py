import heapq

from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus
from core.problem import SearchProblem


class AStar(SearchAlgorithm):
  def __init__(self, problem: SearchProblem):
    super().__init__(problem)

    self.problem=problem
    start_node = Node(
      state=problem.start,
      parent=None,
      action=None,
      path_cost=0
    )

    start_priority = problem.heuristic(problem.start)

    self.frontier = [(start_priority, start_node)]
    self.frontier_states = {
      problem.start
    }
    
    self.current_node=start_node
    self.explored=set()
    self.explored.add(self.current_node.state)

    heapq.heapify(self.frontier)

    # g(n) table
    self.best_cost = {
      problem.start: 0
    }

    self.current_node = start_node


  def search_step(self):
    if not self.frontier:
      self.status = SearchStatus.FAILURE
      return None

    f, node = heapq.heappop(self.frontier)
    self.current_node=node
    self.frontier_states.remove(node.state)

    # Ignore stale entries
    if node.path_cost > self.best_cost[node.state]:
        return False

    self.current_node = node
    self.nodes_expanded += 1

    if self.problem.is_goal_state(node.state):
      self.solution_node = node
      self.status = SearchStatus.SUCCESS
      return node

    for action in self.problem.get_actions(node.state):
      child_state = self.problem.get_result(
        node.state,
        action
      )

      # g(n)
      new_cost = node.path_cost + self.problem.get_cost(node,action,child_state)

      if (
        child_state not in self.best_cost
        or new_cost < self.best_cost[child_state]
      ):
          self.best_cost[child_state] = new_cost

          child = Node(
            state=child_state,
            parent=node,
            action=action,
            path_cost=new_cost
          )

          self.frontier_states.add(
            child_state
          )
          self.explored.add(child_state)

          # f(n) = g(n) + h(n)
          priority = (
            new_cost
            + self.problem.heuristic(child_state)
          )

          heapq.heappush(
            self.frontier,
            (priority, child)
          )

          self.nodes_generated += 1

          self.max_frontier_size = max(
            self.max_frontier_size,
            len(self.frontier)
          )

    return False

  def reset(self):
    super().reset()

    start_node = Node(
        state=self.problem.start,
        parent=None,
        action=None,
        path_cost=0
    )

    start_priority = self.problem.heuristic(
        self.problem.start
    )

    self.frontier = [
        (start_priority, start_node)
    ]

    self.frontier_states={
      self.problem.start
    }

    heapq.heapify(self.frontier)

    self.best_cost = {
        self.problem.start: 0
    }

    self.current_node = start_node