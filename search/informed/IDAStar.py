from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class IDAStar(SearchAlgorithm):

    def __init__(self, problem):
        super().__init__(problem)

        self.limit = 0
        self.next_limit = float("inf")

        # Explicit DFS stack
        self.frontier = []

        # Used only for visualization
        self.frontier_states = set()
        self.explored = set()

        # Current DFS recursion path
        self.path = set()

        self._heuristic_cache = {}

    def reset(self):
        super().reset()

        self._heuristic_cache.clear()

        start = Node(
            state=self.problem.start,
            parent=None,
            action=None,
            path_cost=0
        )

        h = self.problem.heuristic(self.problem.start)
        self._heuristic_cache[self.problem.start] = h

        self.limit = h
        self.next_limit = float("inf")

        self.frontier = [(start, False)]

        self.frontier_states = {start.state}
        self.path.clear()
        self.explored.clear()

        self.current_node = start

        self.nodes_generated = 1
        self.nodes_expanded = 0
        self.max_frontier_size = 1

        self.status = SearchStatus.RUNNING

    def run(self, metadata=None):
        result = super().run(metadata)

        result.metadata["num_iterations"] = self.num_iterations

        try:
            from utils.auto_logger import auto_log_result
            auto_log_result(self, res)
        except Exception:
            pass
        return result

    def search_step(self):

        if self.status != SearchStatus.RUNNING:
            return

        self.num_iterations += 1

        if not self.frontier:

            if self.next_limit == float("inf"):
                print("No solution found within the current limit.")
                self.status = SearchStatus.FAILURE
                return

            self.limit = self.next_limit
            self.next_limit = float("inf")

            self.path.clear()
            self.frontier_states.clear()

            start = Node(
                state=self.problem.start,
                parent=None,
                action=None,
                path_cost=0
            )

            self.frontier = [(start, False)]
            self.frontier_states.add(start.state)

            self.current_node = start

            return

        node, exiting = self.frontier.pop()

        if exiting:
            self.path.discard(node.state)
            self.frontier_states.discard(node.state)
            #self.explored.add(node.state)
            return

        self.current_node = node

        if self.problem.is_goal_state(node.state):
            self.solution_node = node
            self.status = SearchStatus.SUCCESS
            return

        self.nodes_expanded += 1

        self.path.add(node.state)
        self.explored.add(node.state)
        
        self.frontier_states.discard(node.state)

        # Exit marker
        self.frontier.append((node, True))

        actions = list(self.problem.get_actions(node.state))

        # Reverse so recursive order matches
        for action in reversed(actions):

            child_state = self.problem.get_result(
                node.state,
                action
            )

            if child_state in self.path:
                continue

            cost = (
                node.path_cost + self.problem.get_cost(
                    node.state,
                    action,
                    child_state
                )
            )

            h = self._heuristic_cache.get(child_state)

            if h is None:
                h = self.problem.heuristic(child_state)
                self._heuristic_cache[child_state] = h

            f = cost + h

            if f > self.limit:
                if f < self.next_limit:
                    self.next_limit = f
                continue

            child = Node(
                state=child_state,
                parent=node,
                action=action,
                path_cost=cost
            )

            self.nodes_generated += 1

            self.frontier.append((child, False))
            self.frontier_states.add(child_state)

        self.max_frontier_size = max(
            self.max_frontier_size,
            len(self.frontier)
        )