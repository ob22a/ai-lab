from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class IGBFS(SearchAlgorithm):
    """
    Iterative-Deepening Greedy Best-First Search (IGBFS).

    Same iterative-deepening structure as IDA*, but the cutoff is based
    on h(n) alone instead of f(n) = g(n) + h(n).

    This makes IGBFS inadmissible — it ignores path cost, so it will not
    guarantee an optimal solution. In exchange it tends to find *a* solution
    faster than IDA* on problems where the heuristic is very informative,
    because states closer to the goal (by h) are explored first regardless
    of how expensive the path to reach them was.

    Memory: O(b * d) — same as IDA*.
    """

    def __init__(self, problem):
        super().__init__(problem)
        self.limit = 0
        self.next_limit = float("inf")
        self.frontier = []
        self.frontier_states = set()
        self.explored = set()
        self.path = set()
        self._heuristic_cache = {}

    def reset(self):
        super().reset()
        self._heuristic_cache.clear()

        start = Node(state=self.problem.start, parent=None, action=None, path_cost=0)
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
            from utils.auto_logger import auto_log_result
            auto_log_result(self, result)
        except Exception:
            pass
        return result

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        self.num_iterations += 1

        if not self.frontier:
            if self.next_limit == float("inf"):
                self.status = SearchStatus.FAILURE
                return

            self.limit = self.next_limit
            self.next_limit = float("inf")
            self.path.clear()
            self.frontier_states.clear()

            start = Node(state=self.problem.start, parent=None, action=None, path_cost=0)
            self.frontier = [(start, False)]
            self.frontier_states.add(start.state)
            self.current_node = start
            return

        node, exiting = self.frontier.pop()

        if exiting:
            self.path.discard(node.state)
            self.frontier_states.discard(node.state)
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
        self.frontier.append((node, True))  # exit marker

        for action in reversed(list(self.problem.get_actions(node.state))):
            child_state = self.problem.get_result(node.state, action)

            if child_state in self.path:
                continue

            h = self._heuristic_cache.get(child_state)
            if h is None:
                h = self.problem.heuristic(child_state)
                self._heuristic_cache[child_state] = h

            if h > self.limit:
                if h < self.next_limit:
                    self.next_limit = h
                continue

            g = node.path_cost + self.problem.get_cost(node.state, action, child_state)
            child = Node(state=child_state, parent=node, action=action, path_cost=g)
            self.nodes_generated += 1
            self.frontier.append((child, False))
            self.frontier_states.add(child_state)

        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
