import time
from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class RBFS(SearchAlgorithm):
    """
    Recursive Best-First Search (RBFS).

    Memory: O(b * d). Time: worse than A* in practice but far less memory.
    Unlike IDA*, RBFS remembers the best alternative f per subtree to avoid
    full restarts — it backs up the minimum f seen when cutting off a branch.
    """

    def __init__(self, problem):
        super().__init__(problem)
        self._heuristic_cache: dict = {}

    def reset(self):
        super().reset()
        self._heuristic_cache.clear()

    def search_step(self):
        raise NotImplementedError("RBFS is recursive — call run() directly.")

    def run(self, metadata=None):
        self.reset()
        if metadata is None:
            metadata = {}

        start = Node(state=self.problem.start, parent=None, action=None, path_cost=0.0)
        start.f_cost = self._h(self.problem.start)
        self.nodes_generated = 1

        t0 = time.time()
        solution, _ = self._rbfs(start, f_limit=float("inf"))
        runtime = time.time() - t0

        if solution is not None:
            self.status = SearchStatus.SUCCESS
            self.solution_node = solution
        else:
            self.status = SearchStatus.FAILURE

        metadata["num_iterations"] = self.num_iterations
        return self.get_result(runtime=runtime, metadata=metadata)

    def _rbfs(self, node: Node, f_limit: float):
        """Returns (solution_node | None, backed_up_f)."""
        self.num_iterations += 1

        if self.problem.is_goal_state(node.state):
            return node, 0.0

        actions = list(self.problem.get_actions(node.state))
        if not actions:
            return None, float("inf")

        children: list[Node] = []
        for action in actions:
            child_state = self.problem.get_result(node.state, action)
            g = node.path_cost + self.problem.get_cost(node.state, action, child_state)
            child = Node(state=child_state, parent=node, action=action, path_cost=g)
            # Path-max: f must be non-decreasing along any path.
            child.f_cost = max(g + self._h(child_state), node.f_cost)
            children.append(child)
            self.nodes_generated += 1

        self.nodes_expanded += 1
        self.current_node = node

        while True:
            best = min(children, key=lambda c: c.f_cost)

            if best.f_cost > f_limit:
                return None, best.f_cost

            alternative_f = min(
                (c.f_cost for c in children if c is not best),
                default=float("inf"),
            )
            self.max_frontier_size = max(self.max_frontier_size, len(children))

            result, best.f_cost = self._rbfs(best, min(f_limit, alternative_f))

            if result is not None:
                return result, 0.0

    def _h(self, state) -> float:
        h = self._heuristic_cache.get(state)
        if h is None:
            h = self.problem.heuristic(state)
            self._heuristic_cache[state] = h
        return h
