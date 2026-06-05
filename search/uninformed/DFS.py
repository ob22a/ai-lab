from core.node import Node

class DFS:
    def __init__(self, problem):
        self.problem = problem

        self.frontier = [
            Node(
                state=problem.start,
                parent=None,
                action=None,
                path_cost=0
            )
        ]

        self.explored = set()

    def search_step(self):
        if not self.frontier:
            return None

        node = self.frontier.pop()

        if self.problem.is_goal_state(node.state):
            return node

        self.explored.add(node.state)

        for action in self.problem.get_actions(node.state):
            child_state = self.problem.get_result(
                node.state,
                action
            )

            if child_state not in self.explored:
                child = Node(
                    state=child_state,
                    parent=node,
                    action=action,
                    path_cost=node.path_cost + 1
                )

                self.frontier.append(child)

        return False
    