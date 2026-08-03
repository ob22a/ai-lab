import pytest
from core.problem import SearchProblem
from core.node import Node
from search.uninformed.BFS import BFS
from search.uninformed.DFS import DFS
from search.uninformed.UCS import UCS
from search.uninformed.IDDFS import TrueIDDFS
from search.uninformed.BidirectionalSearch import BidirectionalSearch
from search.informed.AStar import AStar
from search.informed.BidirectionalAStar import BidirectionalAStar
from search.informed.GBFS import GreedyBestFirstSearch
from search.informed.IDAStar import IDAStar
from search.informed.IGBFS import IGBFS
from search.informed.RBFS import RBFS
from search.informed.SMAstar import SMAStar

class DummyGridProblem(SearchProblem):
    """A simple 5x5 grid search problem for fast unit tests."""
    def __init__(self, start=(0, 0), goal=(4, 4)):
        super().__init__(start, goal)
        self.width = 5
        self.height = 5

    def get_actions(self, state):
        x, y = state
        actions = []
        if x > 0: actions.append((-1, 0))
        if x < self.width - 1: actions.append((1, 0))
        if y > 0: actions.append((0, -1))
        if y < self.height - 1: actions.append((0, 1))
        return actions

    def get_result(self, state, action):
        return (state[0] + action[0], state[1] + action[1])

    def get_cost(self, state, action, next_state):
        return 1.0

    def heuristic(self, state):
        # Manhattan distance to goal
        return float(abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1]))

    def reverse_heuristic(self, state):
        # Manhattan distance to start
        return float(abs(state[0] - self.start[0]) + abs(state[1] - self.start[1]))


@pytest.mark.parametrize("algo_class", [
    BFS, DFS, UCS, BidirectionalSearch,
    AStar, BidirectionalAStar, GreedyBestFirstSearch, IDAStar, IGBFS, RBFS
])
def test_offline_search_algorithms(algo_class):
    problem = DummyGridProblem()
    algo = algo_class(problem)
    result = algo.run()
    assert result.success
    assert result.solution is not None
    assert result.path_cost >= 8.0 # shortest path on 5x5 from (0,0) to (4,4) is 8 moves

def test_iddfs_search():
    problem = DummyGridProblem()
    algo = TrueIDDFS(problem, start_depth=1, visualize=False)
    result = algo.run()
    assert result.success
    assert result.solution is not None
    assert result.path_cost >= 8.0

def test_sma_star_search():
    problem = DummyGridProblem()
    # Test SMA* with small frontier size limit
    algo = SMAStar(problem, memory_limit=5)
    result = algo.run()
    assert result.success
    assert result.solution is not None
    assert result.path_cost >= 8.0
