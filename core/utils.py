from .node import Node

def reconstruct_path(node: Node):
    path = []

    while node:
        path.append(node.state)
        node = node.parent

    return path[::-1]