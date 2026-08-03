from typing import Set, Tuple, Any
from core.nondeterministic_problem import NondeterministicProblem


class VacuumWorld(NondeterministicProblem):
    """
    Vacuum World Environment.
    State is a tuple: ((agent_x, agent_y), frozenset(dirt_locations))
    Actions: 'Up', 'Down', 'Left', 'Right', 'Suck'
    If slippery=True, moving has a chance to slip (e.g. moving Left might end up Up or Down or nowhere).
    For simplicity in AND-OR search, we just return the set of possible outcomes.
    """
    def __init__(self, width: int, height: int, initial_agent_pos: Tuple[int, int], dirt_locations: Set[Tuple[int, int]], slippery: bool = False):
        self.width = width
        self.height = height
        self.slippery = slippery
        
        initial_state = (initial_agent_pos, frozenset(dirt_locations))
        super().__init__(initial_state=initial_state)

    def is_goal(self, state: Any) -> bool:
        # Goal is when there is no dirt left
        return len(state[1]) == 0

    def get_actions(self, state: Any) -> list:
        # Standard vacuum world actions
        return ['Up', 'Down', 'Left', 'Right', 'Suck']

    def results(self, state: Any, action: Any) -> set:
        """
        Returns the set of possible next states.
        If not slippery, the set contains 1 state.
        If slippery, movement actions might result in multiple possible states.
        """
        pos, dirt = state
        x, y = pos
        outcomes = set()

        if action == 'Suck':
            # Sucking is deterministic
            new_dirt = set(dirt)
            new_dirt.discard(pos)
            outcomes.add((pos, frozenset(new_dirt)))
            return outcomes

        # Movement outcomes
        intended_pos = self._move(x, y, action)
        outcomes.add((intended_pos, dirt))

        if self.slippery:
            # Slipped! We might stay in place, or slide orthogonally
            outcomes.add((pos, dirt))
            if action in ['Up', 'Down']:
                outcomes.add((self._move(x, y, 'Left'), dirt))
                outcomes.add((self._move(x, y, 'Right'), dirt))
            else:
                outcomes.add((self._move(x, y, 'Up'), dirt))
                outcomes.add((self._move(x, y, 'Down'), dirt))

        return outcomes

    def _move(self, x, y, action):
        new_x, new_y = x, y
        if action == 'Up':
            new_y = max(0, y - 1)
        elif action == 'Down':
            new_y = min(self.height - 1, y + 1)
        elif action == 'Left':
            new_x = max(0, x - 1)
        elif action == 'Right':
            new_x = min(self.width - 1, x + 1)
        return (new_x, new_y)
