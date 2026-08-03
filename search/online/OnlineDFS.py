from core.online_problem import OnlineSearchAgent, OnlineSearchEnvironment


class OnlineDFS(OnlineSearchAgent):
    """
    Online Depth-First Search agent.
    """
    def __init__(self, env: OnlineSearchEnvironment):
        super().__init__(env)
        
        self.result = {}       # result[(s, a)] = s'
        self.unexplored = {}   # unexplored[s] = [a, ...]
        self.unbacktracked = {} # unbacktracked[s] = [s', ...]
        
        self.s = None          # previous state
        self.a = None          # previous action
        
        # Visualizer attributes (mimicking offline search algorithms)
        self.status = "RUNNING"
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.frontier_states = set()
        self.explored = set()

    def search_step(self, percept):
        s_prime = percept
        self.explored.add(s_prime)
        
        if self.env.is_goal(s_prime):
            self.a = None
            self.status = "SUCCESS"
            return None

        # Initialize unexplored actions for new states
        is_new = False
        if s_prime not in self.unexplored:
            is_new = True
            self.unexplored[s_prime] = self.env.get_actions(s_prime)
            self.unbacktracked[s_prime] = []
            
            if self.s is not None and hasattr(self.env, "get_reverse_action"):
                reverse_a = self.env.get_reverse_action(s_prime, self.s)
                if reverse_a in self.unexplored[s_prime]:
                    self.unexplored[s_prime].remove(reverse_a)

        if self.s is not None and self.a is not None:
            self.result[(self.s, self.a)] = s_prime
            
            if is_new and self.s != s_prime:
                self.unbacktracked[s_prime].append(self.s)

        if len(self.unexplored[s_prime]) == 0:
            if len(self.unbacktracked[s_prime]) == 0:
                self.a = None
                self.status = "FAILURE"
                return None
            else:
                back_state = self.unbacktracked[s_prime].pop()
                b = None
                for act in self.env.get_actions(s_prime):
                    if (s_prime, act) in self.result and self.result[(s_prime, act)] == back_state:
                        b = act
                        break
                
                if b is None:
                    if hasattr(self.env, "get_reverse_action"):
                        b = self.env.get_reverse_action(s_prime, back_state)
                    else:
                        raise ValueError(f"Environment must provide get_reverse_action to backtrack in Online DFS.")
                
                self.a = b
        else:
            self.a = self.unexplored[s_prime].pop()
            self.nodes_expanded += 1

        self.s = s_prime
        return self.a

    def reset(self):
        self.result = {}
        self.unexplored = {}
        self.unbacktracked = {}
        self.s = None
        self.a = None
        self.status = "RUNNING"
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.explored = set()
        if hasattr(self.env, "reset"):
            self.env.reset()
