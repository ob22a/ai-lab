from core.node import Node
from search.SearchAlgorithm import SearchAlgorithm, SearchStatus
from core.problem import SearchProblem

class DFS(SearchAlgorithm):
    def __init__(self, problem:SearchProblem):
        super().__init__(problem)

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

        self.explored = set()
        self.current_node = self.frontier[0]

        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.max_frontier_size = 1

    def search_step(self):
        if not self.frontier:
            self.status=SearchStatus.FAILURE
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
    