import time
from typing import Any
from games.GameState import GameState
from games.GameSolver import GameSolver
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver

class TimeoutException(Exception):
    pass

class IterativeDeepeningSolver(GameSolver):
    """
    Time-limited Iterative Deepening wrapper.
    Searches depth 1, then depth 2, etc., until the time limit is reached.
    Always returns the best move found from the deepest *fully completed* search.
    """
    def __init__(self, time_limit_seconds: float, evaluation_function=None):
        super().__init__()
        self.time_limit = time_limit_seconds
        self.evaluation_function = evaluation_function
        self.max_depth_reached = 0
        
    def _time_exceeded(self, start_time: float) -> bool:
        return time.time() - start_time >= self.time_limit

    def _is_forced_win(self, state: GameState, action: Any) -> bool:
        """Return True if action immediately wins for the current player."""
        child = state.apply_action(action)
        if child.is_terminal():
            return child.get_utility(state.get_current_player()) > 0
        return False

    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 0
        start_time = time.time()

        best_action_overall = None

        # We share the same underlying solver so it can retain its Transposition Table
        # across iterative deepening depths! (This is crucial for performance).
        ab_solver = AlphaBetaOrderedSolver(evaluation_function=self.evaluation_function)

        # Upper bound on useful search depth (remaining plies in the game).
        legal_actions = state.get_legal_actions()
        max_depth = max(len(legal_actions) * 2, 1) if legal_actions else 1

        depth = 1
        while depth <= max_depth:
            if self._time_exceeded(start_time):
                break

            ab_solver.max_depth = depth
            ab_solver.start_time = start_time
            ab_solver.time_limit = self.time_limit

            try:
                action = ab_solver.get_best_action(state, is_iterative=True)

                if action is not None:
                    best_action_overall = action
                    self.max_depth_reached = depth
                self.nodes_expanded += ab_solver.nodes_expanded

                # Stop early once a proven winning move is found.
                if action is not None and self._is_forced_win(state, action):
                    break

                depth += 1

            except TimeoutException:
                self.nodes_expanded += ab_solver.nodes_expanded
                break

        return best_action_overall
