import heapq
from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus
from core.problem import SearchProblem

class AStar(SearchAlgorithm):
    def __init__(self, problem: SearchProblem):
        super().__init__(problem)
        self.problem = problem
        
        start_node = Node(
            state=problem.start,
            parent=None,
            action=None,
            path_cost=0
        )
        h_cost = self.problem.heuristic(problem.start)
        
        self.frontier = [(h_cost, start_node)]
        # Map state -> best path_cost found to avoid duplicate checks
        self.frontier_states = {problem.start: 0.0} 
        self.explored = {} 
        
        self.current_node = self.frontier[0][1]

    def reset(self):
        super().reset()
        start_node = Node(
            state=self.problem.start,
            parent=None,
            action=None,
            path_cost=0
        )
        h_cost = self.problem.heuristic(self.problem.start)
        
        self.frontier = [(h_cost, start_node)]
        self.frontier_states = {self.problem.start: 0.0}
        self.explored = {}
        self.current_node = self.frontier[0][1]

    def search_step(self):
        if not self.frontier:
            self.status = SearchStatus.FAILURE
            return None

        _, node = heapq.heappop(self.frontier)
        
        # A* Graph Search: Skip node if we already expanded it via a cheaper path
        if node.state in self.explored and self.explored[node.state] <= node.path_cost:
            return False
            
        self.current_node = node
        
        if node.state in self.frontier_states:
            del self.frontier_states[node.state]
            
        self.explored[node.state] = node.path_cost
        self.nodes_expanded += 1

        if self.problem.is_goal_state(node.state):
            self.solution_node = node
            self.status = SearchStatus.SUCCESS
            return node

        for action in self.problem.get_actions(node.state):
            child_state = self.problem.get_result(node.state, action)

            step_cost = self.problem.get_cost(node.state, action, child_state)
            new_path_cost = node.path_cost + step_cost

            # Pruning: skip if we've already found a better or equal path to this state
            if child_state in self.explored and self.explored[child_state] <= new_path_cost:
                continue
            if child_state in self.frontier_states and self.frontier_states[child_state] <= new_path_cost:
                continue

            child = Node(
                state=child_state,
                parent=node,
                action=action,
                path_cost=new_path_cost
            )

            h_cost = self.problem.heuristic(child_state)
            # A* uses f(n) = g(n) + h(n)
            f_cost = new_path_cost + h_cost

            heapq.heappush(self.frontier, (f_cost, child))
            self.frontier_states[child_state] = new_path_cost
            self.nodes_generated += 1

            self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))

        return False