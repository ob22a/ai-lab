import pytest
from core.online_problem import OnlineSearchEnvironment, OnlineSearchAgent
from core.nondeterministic_problem import NondeterministicProblem
from search.online.OnlineDFS import OnlineDFS
from search.online.LRTA import LRTAStar
from search.online.ANDORSearch import ANDORSearch

class DummyOnlineEnv(OnlineSearchEnvironment):
    def __init__(self, size=5, start=0, goal=4):
        self.size = size
        self.state = start
        self.goal_state = goal

    def get_percept(self):
        return self.state

    def execute_action(self, action):
        self.state = max(0, min(self.size - 1, self.state + action))
        return self.state

    def is_goal(self, state):
        return state == self.goal_state

    def get_actions(self, state):
        actions = []
        if state > 0: actions.append(-1)
        if state < self.size - 1: actions.append(1)
        return actions

    def get_cost(self, state, action, next_state):
        return 1.0

    def get_reverse_action(self, state, prev_state):
        return prev_state - state


class DummyNondeterministicProblem(NondeterministicProblem):
    def __init__(self):
        super().__init__(initial_state=0)

    def is_goal(self, state):
        return state == 2

    def get_actions(self, state):
        if state == 0: return ['step']
        if state == 1: return ['step']
        return []

    def results(self, state, action):
        if state == 0 and action == 'step':
            return {1, 2}
        if state == 1 and action == 'step':
            return {2}
        return set()


def test_online_dfs():
    env = DummyOnlineEnv()
    agent = OnlineDFS(env)
    
    # Run the online agent-environment loop
    percept = env.get_percept()
    steps = 0
    while agent.status == "RUNNING" and steps < 100:
        action = agent.search_step(percept)
        if action is None:
            break
        percept = env.execute_action(action)
        steps += 1
        
    assert agent.status == "SUCCESS"
    assert env.state == env.goal_state

def test_lrta_star():
    env = DummyOnlineEnv()
    # H estimate is simple distance to goal
    heuristic = lambda s: float(abs(s - env.goal_state))
    agent = LRTAStar(env, heuristic_func=heuristic)
    
    percept = env.get_percept()
    steps = 0
    while agent.status == "RUNNING" and steps < 100:
        action = agent.search_step(percept)
        if action is None:
            break
        percept = env.execute_action(action)
        steps += 1
        
    assert agent.status == "SUCCESS"
    assert env.state == env.goal_state

def test_and_or_search():
    problem = DummyNondeterministicProblem()
    solver = ANDORSearch(problem)
    plan = solver.run()
    assert plan is not None
    assert plan['action'] == 'step'
    assert 1 in plan['outcomes']
    assert 2 in plan['outcomes']
