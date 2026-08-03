from core.nondeterministic_problem import NondeterministicProblem


class ANDORSearch:
    """
    AND-OR Search for nondeterministic environments.
    Unlike standard search which returns a linear path, AND-OR search returns
    a Conditional Plan (a tree).
    
    OR nodes represent the agent's choice of action.
    AND nodes represent the environment's nondeterministic outcome.
    
    Returns a nested dictionary representing the plan.
    Example: {'action': 'up', 'outcomes': {'state1': {...}, 'state2': {...}}}
    """
    def __init__(self, problem: NondeterministicProblem):
        self.problem = problem
        self.nodes_expanded = 0
        self.nodes_generated = 0

    def run(self):
        return self.or_search(self.problem.initial_state, set())

    def or_search(self, state, path):
        """
        OR search: The agent chooses an action.
        """
        if self.problem.is_goal(state):
            return [] # Empty plan means we are at the goal
            
        if state in path:
            return None
            
        for action in self.problem.get_actions(state):
            self.nodes_expanded += 1
            plan = self.and_search(self.problem.results(state, action), path.union({state}))
            if plan is not None:
                return {'action': action, 'outcomes': plan}
                
        return None

    def and_search(self, states, path):
        """
        AND search: The environment chooses an outcome.
        """
        plan = {}
        for state in states:
            self.nodes_generated += 1
            state_plan = self.or_search(state, path)
            if state_plan is None:
                return None
            plan[state] = state_plan
        return plan
