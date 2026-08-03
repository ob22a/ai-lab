from core.online_problem import OnlineSearchAgent, OnlineSearchEnvironment


class LRTAStar(OnlineSearchAgent):
    """
    Learning Real-Time A* (LRTA*).
    Builds a map of the environment and updates a heuristic table H[s].
    Over multiple trials, H[s] converges to the exact cost to reach the goal.
    """
    def __init__(self, env: OnlineSearchEnvironment, heuristic_func=None):
        super().__init__(env)
        self.H = {}             # H[s] = estimated cost to goal
        self.result = {}        # result[(s, a)] = s'
        
        self.heuristic = heuristic_func if heuristic_func else (lambda s: 0.0)
        
        self.s = None
        self.a = None
        
        self.status = "RUNNING"
        self.nodes_expanded = 0
        self.explored = set()

    def get_H(self, state):
        if state not in self.H:
            self.H[state] = self.heuristic(state)
        return self.H[state]

    def search_step(self, percept):
        s_prime = percept
        self.explored.add(s_prime)
        
        if self.env.is_goal(s_prime):
            self.a = None
            self.status = "SUCCESS"
            return None
            
        if s_prime not in self.H:
            self.H[s_prime] = self.heuristic(s_prime)
            
        if self.s is not None and self.a is not None:
            self.result[(self.s, self.a)] = s_prime
            
            min_cost = float('inf')
            for act in self.env.get_actions(self.s):
                cost = self._lrta_cost(self.s, act, self.result.get((self.s, act)))
                if cost < min_cost:
                    min_cost = cost
            
            self.H[self.s] = max(self.H[self.s], min_cost)

        best_a = None
        best_cost = float('inf')
        for act in self.env.get_actions(s_prime):
            cost = self._lrta_cost(s_prime, act, self.result.get((s_prime, act)))
            if cost < best_cost:
                best_cost = cost
                best_a = act
                
        self.a = best_a
        self.s = s_prime
        self.nodes_expanded += 1
        
        return self.a

    def _lrta_cost(self, state, action, next_state):
        if next_state is None:
            return self.heuristic(state)
        else:
            return self.env.get_cost(state, action, next_state) + self.get_H(next_state)

    def reset(self):
        self.s = None
        self.a = None
        self.status = "RUNNING"
        self.nodes_expanded = 0
        if hasattr(self.env, "reset"):
            self.env.reset()
