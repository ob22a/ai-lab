import heapq

from core.node import Node
from search.SearchAlgorithm import (
    SearchAlgorithm,
    SearchStatus,
)


class SMAStar(SearchAlgorithm):

    def __init__(self, problem, memory_limit=1000):
        super().__init__(problem)
        self.memory_limit = memory_limit
        self.frontier = []
        self.frontier_states = {}
        self.explored = set()
        self._heuristic_cache = {}
    
    def reset(self):
        super().reset()
        self.frontier.clear()
        self.frontier_states.clear()
        self.explored.clear()
        self._heuristic_cache.clear()

        start = Node(
            state=self.problem.start,
            parent=None,
            action=None,
            path_cost=0.0,
        )
        start.f_cost = self._heuristic(start.state)

        self._push_to_frontier(start)

        self.current_node = start
        self.nodes_generated = 1
        self.nodes_expanded = 0
        self.max_frontier_size = 1
        self.status = SearchStatus.RUNNING

    def _heuristic(self, state):
        h = self._heuristic_cache.get(state)
        if h is None:
            h = self.problem.heuristic(state)
            self._heuristic_cache[state] = h
        return h

    def _push_to_frontier(self, node):
        heapq.heappush(self.frontier, node)
        self.frontier_states[node.state] = node.path_cost
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))

    def _remove_from_frontier(self, node):
        if node in self.frontier:
            self.frontier.remove(node)
            heapq.heapify(self.frontier)
        self.frontier_states.pop(node.state, None)

    def search_step(self):
        if self.status != SearchStatus.RUNNING:
            return

        if not self.frontier:
            self.status = SearchStatus.FAILURE
            return

        self.num_iterations += 1

        # 1. Pop the best leaf node from the frontier
        node = heapq.heappop(self.frontier)
        self.frontier_states.pop(node.state, None)
        self.current_node = node
        self.explored.add(node.state)

        # 2. Check for goal state
        if self.problem.is_goal_state(node.state):
            self.solution_node = node
            self.status = SearchStatus.SUCCESS
            return

        # 3. Load actions lazily once
        if not node.actions_generated:
            node.actions = list(self.problem.get_actions(node.state))
            node.actions_generated = True

        # 4. Check if this path is completely exhausted
        if not node.forgotten_children and node.successor_index >= len(node.actions):
            node.fully_expanded = True
            node.f_cost = min((c.f_cost for c in node.children), default=float('inf'))
            self._backup(node)
            return

        # 5. Extract next branch configuration (prioritizing forgotten paths)
        if node.forgotten_children:
            action, backed_up_f = node.forgotten_children.pop(0)
        else:
            action = node.actions[node.successor_index]
            backed_up_f = None
            node.successor_index += 1

        child_state = self.problem.get_result(node.state, action)

        # 6. Graph search optimization: skip trivial parent backtracking loops
        if node.parent is not None and child_state == node.parent.state:
            self._push_to_frontier(node)
            return

        # 7. Create child node (dataclass handles depth and self._id generation)
        g = node.path_cost + self.problem.get_cost(node.state, action, child_state)
        child = Node(state=child_state, parent=node, action=action, path_cost=g)

        # Apply path-max equation rules
        child_f = max(g + self._heuristic(child_state), node.f_cost)
        if backed_up_f is not None:
            child_f = max(child_f, backed_up_f)
        child.f_cost = child_f

        node.children.append(child)
        self.nodes_generated += 1

        # 8. Put parent back if it still has unexpanded or forgotten avenues
        if node.forgotten_children or node.successor_index < len(node.actions):
            self._push_to_frontier(node)

        # Push the newly generated child path into active exploration
        self._push_to_frontier(child)
        self.nodes_expanded += 1

        # 9. Enforce tight memory bounds
        while len(self.frontier) > self.memory_limit:
            self._prune()
    
    def _backup(self, node):
        if node is None:
            return

        old_f = node.f_cost
        base_f = node.path_cost + self._heuristic(node.state)
        
        if node.children:
            new_f = max(base_f, min(child.f_cost for child in node.children))
        else:
            new_f = float('inf') if node.fully_expanded else base_f
        
        if node.forgotten_f != float("inf"):
            new_f = min(new_f, node.forgotten_f)

        if new_f != old_f:
            node.f_cost = new_f
            if node.parent is not None:
                self._backup(node.parent)

    def _prune(self):
        # Filter endpoints from the frontier
        leaves = [n for n in self.frontier if not n.children]
        if not leaves:
            return

        # Uses the exact same prioritization structure as your dataclass __lt__
        leaf = max(leaves, key=lambda n: (n.f_cost, -n.depth, n._id))

        self._remove_from_frontier(leaf)
        self.explored.discard(leaf.state)

        parent = leaf.parent
        if parent is None:
            return

        if leaf in parent.children:
            parent.children.remove(leaf)

        # Store branch info in parent history
        parent.forgotten_children.append((leaf.action, leaf.f_cost))
        parent.forgotten_f = min(parent.forgotten_f, leaf.f_cost)

        # Revert parent to an active frontier leaf if all its children are pruned
        if not parent.children:
            self.explored.discard(parent.state)
            if parent not in self.frontier:
                self._push_to_frontier(parent)

        self._backup(parent)
