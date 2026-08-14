import time
from typing import Any, List
from games.GameState import GameState
from games.GameSolver import GameSolver
from games.heuristics.KillerMoves import KillerMoves
from games.heuristics.HistoryHeuristic import HistoryHeuristic
from games.TranspositionTable import TranspositionTable, TTFlag

class AlphaBetaOrderedSolver(GameSolver):
    """
    Alpha-Beta Pruning with Move Ordering heuristics.
    Prioritizes exploring Killer Moves and moves with high History Scores to
    maximize the probability of early cutoffs.
    """
    
    def __init__(self, max_depth: int = -1, evaluation_function=None):
        super().__init__()
        self.max_depth = max_depth
        self.evaluation_function = evaluation_function
        self.killer_moves = KillerMoves()
        self.history = HistoryHeuristic()
        self.transposition_table = TranspositionTable()
        
        # Timeout handling
        self.start_time = None
        self.time_limit = None
        
    def _order_moves(self, state: GameState, depth: int) -> List[Any]:
        actions = state.get_legal_actions()
        killers = self.killer_moves.get_killers(depth)
        
        def move_score(action):
            score = 0
            # Killer moves get absolute highest priority
            if action in killers:
                # Give the primary killer more weight than the secondary
                score += 1000000 - killers.index(action)
            # Add the history score
            score += self.history.get_score(action)
            return score
            
        # Sort actions descending by score
        actions.sort(key=move_score, reverse=True)
        return actions
    
    def _check_timeout(self):
        if self.time_limit is not None and self.start_time is not None:
            if time.time() - self.start_time >= self.time_limit:
                from games.IterativeDeepening import TimeoutException
                raise TimeoutException()
                    
    def get_best_action(self, state: GameState, is_iterative: bool = False) -> Any:
        self.nodes_expanded = 0
        self.root_player = state.get_current_player()
        
        # Only reset tables if this is a fresh search, not an iterative deepening step
        if not is_iterative:
            self.killer_moves = KillerMoves()
            self.history = HistoryHeuristic()
            self.transposition_table.clear()
        
        best_value = float('-inf')
        best_action = None
        alpha = float('-inf')
        beta = float('inf')
        
        actions = self._order_moves(state, depth=0)
        for action in actions:
            child_state = state.apply_action(action)
            value = self._min_value(child_state, alpha, beta, depth=1)
            
            if value > best_value:
                best_value = value
                best_action = action
                
            alpha = max(alpha, best_value)
            
        return best_action
        
    def _max_value(self, state: GameState, alpha: float, beta: float, depth: int) -> float:
        self.nodes_expanded += 1
        self._check_timeout()
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
            
        if self.max_depth != -1 and depth >= self.max_depth:
            if self.evaluation_function:
                return self.evaluation_function(state, self.root_player)
            return 0.0 # Default to 0 if no eval function provided
            
        # Transposition Table Lookup
        if hasattr(state, 'get_hash'):
            h = state.get_hash()
            # The remaining depth is max_depth - depth
            rem_depth = self.max_depth - depth if self.max_depth != -1 else float('inf')
            found, cached_score = self.transposition_table.lookup(h, rem_depth, alpha, beta)
            if found:
                return cached_score
                
        value = float('-inf')
        original_alpha = alpha
        actions = self._order_moves(state, depth)
        
        for action in actions:
            child_state = state.apply_action(action)
            value = max(value, self._min_value(child_state, alpha, beta, depth + 1))
            
            if value >= beta:
                # Cutoff! Record heuristics.
                self.killer_moves.store_killer(depth, action)
                self.history.increment(action, depth)
                if hasattr(state, 'get_hash'):
                    self.transposition_table.store(h, rem_depth, value, TTFlag.LOWER_BOUND)
                return value
                
            alpha = max(alpha, value)
            
        # We searched all children, store EXACT or UPPER_BOUND
        if hasattr(state, 'get_hash'):
            flag = TTFlag.EXACT if value > original_alpha else TTFlag.UPPER_BOUND
            self.transposition_table.store(h, rem_depth, value, flag)
            
        return value
        
    def _min_value(self, state: GameState, alpha: float, beta: float, depth: int) -> float:
        self.nodes_expanded += 1
        self._check_timeout()
        
        if state.is_terminal():
            return state.get_utility(self.root_player)
            
        if self.max_depth != -1 and depth >= self.max_depth:
            if self.evaluation_function:
                return self.evaluation_function(state, self.root_player)
            return 0.0
            
        # Transposition Table Lookup
        if hasattr(state, 'get_hash'):
            h = state.get_hash()
            rem_depth = self.max_depth - depth if self.max_depth != -1 else float('inf')
            found, cached_score = self.transposition_table.lookup(h, rem_depth, alpha, beta)
            if found:
                return cached_score
                
        value = float('inf')
        original_beta = beta
        actions = self._order_moves(state, depth)
        
        for action in actions:
            child_state = state.apply_action(action)
            value = min(value, self._max_value(child_state, alpha, beta, depth + 1))
            
            if value <= alpha:
                # Cutoff! Record heuristics.
                self.killer_moves.store_killer(depth, action)
                self.history.increment(action, depth)
                if hasattr(state, 'get_hash'):
                    self.transposition_table.store(h, rem_depth, value, TTFlag.UPPER_BOUND)
                return value
                
            beta = min(beta, value)
            
        # We searched all children, store EXACT or LOWER_BOUND
        if hasattr(state, 'get_hash'):
            flag = TTFlag.EXACT if value < original_beta else TTFlag.LOWER_BOUND
            self.transposition_table.store(h, rem_depth, value, flag)
            
        return value
