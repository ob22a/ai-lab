import collections
from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus

class BidirectionalSearch(SearchAlgorithm):
    """
    Bidirectional Search.
    Runs two simultaneous Breadth-First Searches:
    1. Forward from the Start State
    2. Backward from the Goal State
    When the two frontiers intersect, the search stops, yielding a massive reduction in search space (O(b^(d/2))).
    """
    def __init__(self, problem):
        super().__init__(problem)
        self.reset()
        
    def reset(self):
        super().reset()
        
        # Forward search components
        start_node = Node(state=self.problem.start, parent=None, action=None, path_cost=0.0)
        self.frontier_fwd = collections.deque([start_node])
        self.explored_fwd = {start_node.state: start_node}
        
        # Backward search components
        goal_node = Node(state=self.problem.goal, parent=None, action=None, path_cost=0.0)
        self.frontier_bwd = collections.deque([goal_node])
        self.explored_bwd = {goal_node.state: goal_node}
        
        self.status = SearchStatus.RUNNING
        self.current_node = start_node
        
    @property
    def explored(self):
        """Expose a unified explored set for the visualizers."""
        return set(self.explored_fwd.keys()).union(self.explored_bwd.keys())
        
    @explored.setter
    def explored(self, value):
        pass # Ignore base class reset
        
    @property
    def frontier_states(self):
        """Expose a unified frontier states set for the visualizers."""
        fwd = {node.state for node in self.frontier_fwd}
        bwd = {node.state for node in self.frontier_bwd}
        return fwd.union(bwd)
        
    def _build_solution(self, fwd_node: Node, bwd_node: Node) -> Node:
        """
        Stitches the forward path and reversed backward path.
        fwd_node: Traces back to START.
        bwd_node: Traces back to GOAL. Both represent the same Intersection State.
        """
        current = bwd_node.parent
        prev = fwd_node
        
        current_path_cost = fwd_node.path_cost
        prev_bwd_cost = bwd_node.path_cost

        while current:
            nxt = current.parent
            step_cost = prev_bwd_cost - current.path_cost
            current_path_cost += step_cost
            prev_bwd_cost = current.path_cost
            
            current.parent = prev
            current.path_cost = current_path_cost
            
            prev = current
            current = nxt

        return prev # This is now the goal

    def search_step(self):
        if not self.frontier_fwd and not self.frontier_bwd:
            self.status = SearchStatus.FAILURE
            return

        # 1. Expand Forward Frontier
        if self.frontier_fwd:
            node_fwd = self.frontier_fwd.popleft()
            self.current_node = node_fwd
            self.nodes_expanded += 1
            
            # Check for intersection!
            if node_fwd.state in self.explored_bwd:
                self.solution_node = self._build_solution(node_fwd, self.explored_bwd[node_fwd.state])
                self.status = SearchStatus.SUCCESS
                return
                
            for action in self.problem.get_actions(node_fwd.state):
                child_state = self.problem.get_result(node_fwd.state, action)
                if child_state not in self.explored_fwd:
                    step_cost = self.problem.get_cost(node_fwd.state, action, child_state)
                    child_node = Node(
                        state=child_state,
                        parent=node_fwd,
                        action=action,
                        path_cost=node_fwd.path_cost + step_cost
                    )
                    self.explored_fwd[child_state] = child_node
                    self.frontier_fwd.append(child_node)
                    self.nodes_generated += 1

        # 2. Expand Backward Frontier
        if self.frontier_bwd:
            node_bwd = self.frontier_bwd.popleft()
            self.current_node = node_bwd
            self.nodes_expanded += 1
            
            # Check for intersection!
            if node_bwd.state in self.explored_fwd:
                self.solution_node = self._build_solution(self.explored_fwd[node_bwd.state], node_bwd)
                self.status = SearchStatus.SUCCESS
                return
                
            for action in self.problem.get_actions(node_bwd.state):
                child_state = self.problem.get_result(node_bwd.state, action)
                if child_state not in self.explored_bwd:
                    step_cost = self.problem.get_cost(node_bwd.state, action, child_state)
                    child_node = Node(
                        state=child_state,
                        parent=node_bwd,
                        action=action,
                        path_cost=node_bwd.path_cost + step_cost
                    )
                    self.explored_bwd[child_state] = child_node
                    self.frontier_bwd.append(child_node)
                    self.nodes_generated += 1
                    
        # Update metrics
        total_frontier = len(self.frontier_fwd) + len(self.frontier_bwd)
        if total_frontier > getattr(self, 'max_frontier_size', 0):
            self.max_frontier_size = total_frontier
