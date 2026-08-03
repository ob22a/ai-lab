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
        
    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 0
        start_time = time.time()
        
        best_action_overall = None
        
        # We share the same underlying solver so it can retain its Transposition Table
        # across iterative deepening depths! (This is crucial for performance).
        ab_solver = AlphaBetaOrderedSolver(evaluation_function=self.evaluation_function)
        
        depth = 1
        while True:
            ab_solver.max_depth = depth
            ab_solver.start_time = start_time
            ab_solver.time_limit = self.time_limit
            
            try:
                action = ab_solver.get_best_action(state, is_iterative=True)
                
                # If we successfully completed this depth without throwing TimeoutException
                best_action_overall = action
                self.max_depth_reached = depth
                self.nodes_expanded += ab_solver.nodes_expanded
                
                # If the game was proven to be mathematically over at this depth (terminal state found)
                # we can break early, but checking that is complex. For now, we just go deeper.
                
                depth += 1
                
            except TimeoutException:
                # Time limit exceeded during the search at this depth.
                # We discard the partial results of this depth and break.
                self.nodes_expanded += ab_solver.nodes_expanded
                break
                
        return best_action_overall
