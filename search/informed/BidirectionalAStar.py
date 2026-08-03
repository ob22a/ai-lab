import heapq
from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus


class BidirectionalAStar(SearchAlgorithm):
    """
    Bidirectional A* with μ-bound stopping condition.

    Stops when f_min_fwd + f_min_bwd >= μ (best path cost seen so far).
    Uses reverse_heuristic for the backward direction.
    """

    def __init__(self, problem):
        super().__init__(problem)
        self.reset()

    def reset(self):
        super().reset()

        start_node = Node(state=self.problem.start, parent=None, action=None, path_cost=0.0)
        start_node.f_cost = self.problem.heuristic(self.problem.start)

        goal_node = Node(state=self.problem.goal, parent=None, action=None, path_cost=0.0)
        goal_node.f_cost = self.problem.reverse_heuristic(self.problem.goal)

        self.frontier_fwd = [start_node]
        self.explored_fwd: dict = {self.problem.start: start_node}

        self.frontier_bwd = [goal_node]
        self.explored_bwd: dict = {self.problem.goal: goal_node}

        self.mu = float("inf")
        self._mu_fwd_node = None
        self._mu_bwd_node = None

        self._h_cache_fwd: dict = {}
        self._h_cache_bwd: dict = {}

        self.status = SearchStatus.RUNNING
        self.current_node = start_node

    @property
    def explored(self):
        return set(self.explored_fwd) | set(self.explored_bwd)

    @explored.setter
    def explored(self, value):
        pass

    @property
    def frontier_states(self):
        return {n.state for n in self.frontier_fwd} | {n.state for n in self.frontier_bwd}

    def _build_solution(self, fwd_node: Node, bwd_node: Node) -> Node:
        """
        Splice forward chain and reversed backward chain at the meeting state.
        Repairs path_cost and depth in the backward segment after splicing.
        """
        bwd_segment = []
        cur = bwd_node.parent
        while cur is not None:
            bwd_segment.append(cur)
            cur = cur.parent

        if not bwd_segment:
            return fwd_node

        # Reverse backward chain in-place (same as BidirectionalSearch)
        current = bwd_node.parent
        tail = current
        prev = None
        while current:
            nxt = current.parent
            current.parent = prev
            prev = current
            current = nxt

        tail.parent = fwd_node
        goal_node = prev

        # Repair costs: bwd_segment collected BEFORE reversal → correct forward order
        preceding = fwd_node
        for node in bwd_segment:
            node.path_cost = preceding.path_cost + self.problem.get_cost(
                preceding.state, node.action, node.state
            )
            node.depth = preceding.depth + 1
            preceding = node

        return goal_node

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        self.num_iterations += 1

        f_min_fwd = self.frontier_fwd[0].f_cost if self.frontier_fwd else float("inf")
        f_min_bwd = self.frontier_bwd[0].f_cost if self.frontier_bwd else float("inf")

        if f_min_fwd + f_min_bwd >= self.mu and self.mu < float("inf"):
            self.solution_node = self._build_solution(self._mu_fwd_node, self._mu_bwd_node)
            self.status = SearchStatus.SUCCESS
            return

        if not self.frontier_fwd and not self.frontier_bwd:
            self.status = SearchStatus.FAILURE
            return

        if f_min_fwd <= f_min_bwd:
            self._expand_forward()
        else:
            self._expand_backward()

        self.max_frontier_size = max(
            self.max_frontier_size, len(self.frontier_fwd) + len(self.frontier_bwd)
        )

    def _expand_forward(self):
        if not self.frontier_fwd:
            return

        node = heapq.heappop(self.frontier_fwd)
        self.current_node = node
        self.nodes_expanded += 1

        best = self.explored_fwd.get(node.state)
        if best is not None and best.path_cost < node.path_cost:
            return

        for action in self.problem.get_actions(node.state):
            child_state = self.problem.get_result(node.state, action)
            g = node.path_cost + self.problem.get_cost(node.state, action, child_state)

            existing = self.explored_fwd.get(child_state)
            if existing is not None and existing.path_cost <= g:
                continue

            h = self._h_cache_fwd.get(child_state)
            if h is None:
                h = self.problem.heuristic(child_state)
                self._h_cache_fwd[child_state] = h

            child = Node(state=child_state, parent=node, action=action, path_cost=g)
            child.f_cost = g + h
            self.explored_fwd[child_state] = child
            heapq.heappush(self.frontier_fwd, child)
            self.nodes_generated += 1

            bwd_match = self.explored_bwd.get(child_state)
            if bwd_match is not None:
                candidate = g + bwd_match.path_cost
                if candidate < self.mu:
                    self.mu = candidate
                    self._mu_fwd_node = child
                    self._mu_bwd_node = bwd_match

    def _expand_backward(self):
        if not self.frontier_bwd:
            return

        node = heapq.heappop(self.frontier_bwd)
        self.current_node = node
        self.nodes_expanded += 1

        best = self.explored_bwd.get(node.state)
        if best is not None and best.path_cost < node.path_cost:
            return

        for action in self.problem.get_actions(node.state):
            child_state = self.problem.get_result(node.state, action)
            g = node.path_cost + self.problem.get_cost(node.state, action, child_state)

            existing = self.explored_bwd.get(child_state)
            if existing is not None and existing.path_cost <= g:
                continue

            h = self._h_cache_bwd.get(child_state)
            if h is None:
                h = self.problem.reverse_heuristic(child_state)
                self._h_cache_bwd[child_state] = h

            child = Node(state=child_state, parent=node, action=action, path_cost=g)
            child.f_cost = g + h
            self.explored_bwd[child_state] = child
            heapq.heappush(self.frontier_bwd, child)
            self.nodes_generated += 1

            fwd_match = self.explored_fwd.get(child_state)
            if fwd_match is not None:
                candidate = fwd_match.path_cost + g
                if candidate < self.mu:
                    self.mu = candidate
                    self._mu_fwd_node = fwd_match
                    self._mu_bwd_node = child
