"""
ObssaHeuristic.py
Evaluation heuristic function and solver for the 'Crazy' card game domain.

Heuristic Principles (Obssa's Heuristic):
1. Card Dumping: Prefer playing as many cards as possible in a single turn.
2. Turn Retention: Play 5s strategically to skip the opponent and retain turn.
   - Playing ONE 5 skips the opponent and retains your turn.
   - Playing TWO 5s in one combo skips twice, returning turn to opponent (losing turn advantage).
3. Wildcard Preservation: Hold Joker, 8, and J for suit changes when needed.
   - Do NOT play 8 or J if suit change is restricted or when it wastes suit-changing power.
4. Suit Alignment: Align active/declared suit to match the majority suit of remaining cards in hand.
5. Penalty Delegation: Delegate draw penalties to the opponent as aggressively as possible.
"""

from typing import Any, List, Dict
from games.GameState import GameState
from games.GameSolver import GameSolver


def obssa_heuristic(state: Any, player: int) -> float:
    """
    Evaluates a CrazyState from the perspective of 'player' (1 or 2).
    Higher scores indicate a more favorable board state for 'player'.
    """
    if state.is_terminal():
        return state.get_utility(player)

    my_hand = state.p1_hand if player == 1 else state.p2_hand
    opp_hand = state.p2_hand if player == 1 else state.p1_hand

    # 1. Base card advantage: minimizing own cards and maximizing opponent's cards
    score = (len(opp_hand) - len(my_hand)) * 25.0

    # 2. Wildcard Preservation:
    # Holding 8, J, Joker until needed provides strategic dominance.
    for card in my_hand:
        if card.rank == 0:  # Joker is the ultimate trump card
            score += 15.0
        elif card.rank in (8, 'J'):  # 8 and J are versatile wildcards
            score += 8.0
        elif card.get_draw_penalty() > 0:  # Offensive penalty cards held
            score += 4.0

    # 3. Suit Alignment: Bonus if active suit matches the majority suit in hand
    if state.active_suit and my_hand:
        suit_counts: Dict[str, int] = {}
        for c in my_hand:
            if c.suit != 'Joker':
                suit_counts[c.suit] = suit_counts.get(c.suit, 0) + 1
        
        if suit_counts:
            most_frequent_suit = max(suit_counts, key=suit_counts.get)
            if state.active_suit == most_frequent_suit:
                score += 12.0

    # 4. Penalty Delegation: Bonus if opponent is currently under pending draw penalty
    if state.pending_draws > 0:
        if state.current_player != player and state.current_player != 0:
            score += state.pending_draws * 15.0
        elif state.player_to_draw and state.player_to_draw != player:
            score += state.pending_draws * 15.0
        elif state.current_player == player:
            score -= state.pending_draws * 15.0

    return score


def evaluate_action_quality(state: Any, action: Any, player: int) -> float:
    """
    Evaluates the strategic quality of taking 'action' from 'state' for 'player'.
    Includes turn-retention check (5s), wildcard conservation (8/J), and suit alignment.
    """
    next_state = state.apply_action(action)
    score = obssa_heuristic(next_state, player)

    # Extract played cards from action tuple
    cards_played = [x for x in action if not isinstance(x, str) and hasattr(x, 'rank')]
    declared_suit = next(x for x in action if isinstance(x, str)) if any(isinstance(x, str) for x in action) else None

    # --- Rule A: Turn Retention & 5s Handling ---
    # Rank 5 skips the opponent. Playing 1 5 keeps your turn; playing 2 5s in one combo
    # skips twice, returning the turn to the opponent.
    num_fives = sum(1 for c in cards_played if c.rank == 5)
    if num_fives == 1 and next_state.current_player == player:
        score += 15.0  # Bonus for successfully keeping your turn!
    elif num_fives >= 2 and next_state.current_player != player:
        score -= 20.0  # Penalty for wasting two 5s and losing turn advantage

    # --- Rule B: Wildcard Conservation (8 and J) ---
    # Wildcards derive their power from changing the active suit.
    # If wild suit change is restricted on top of another wild card, playing 8/J wastes its power.
    my_hand = state.p1_hand if player == 1 else state.p2_hand
    num_wildcards = sum(1 for c in cards_played if c.is_wild())
    
    if num_wildcards > 0:
        top_was_wild = len(state.discard_pile) >= 1 and state.discard_pile[-1].is_wild()
        if top_was_wild and not getattr(state, 'wild_suit_change_allowed', True):
            score -= 18.0  # Wasting wildcard when suit change is restricted

        # Multi-Wildcard Hoarding Rule:
        # Playing multiple 8s/Js together when holding > 6 cards wastes suit-changing power,
        # as opponents will likely change the suit again before your next turn.
        # Preserve wildcards until hand size is <= 6 or when the play wins the game immediately!
        wins_game = (len(my_hand) - len(cards_played)) == 0
        if num_wildcards > 1 and len(my_hand) > 6 and not wins_game:
            score -= 25.0  # Heavy penalty for wasting multiple wildcards in early/mid game

        # If player has non-wild options, discourage playing 8/J unless hand is small
        if len(my_hand) > 2 and not declared_suit:
            score -= 5.0

    # --- Rule C: Suit Alignment for Remaining Hand ---
    # Prefer actions that set active/declared suit to match majority suit of remaining hand.
    remaining_hand = next_state.p1_hand if player == 1 else next_state.p2_hand
    if remaining_hand:
        suit_counts: Dict[str, int] = {}
        for c in remaining_hand:
            if c.suit != 'Joker':
                suit_counts[c.suit] = suit_counts.get(c.suit, 0) + 1
        if suit_counts:
            best_remaining_suit = max(suit_counts, key=suit_counts.get)
            target_suit = declared_suit if declared_suit else next_state.active_suit
            if target_suit == best_remaining_suit:
                score += 10.0

    return score


class ObssaHeuristicSolver(GameSolver):
    """
    Game solver agent driven by Obssa's Heuristic.
    Evaluates successor states using 1-step lookahead and action strategic quality scoring.
    """
    def get_best_action(self, state: GameState) -> Any:
        self.nodes_expanded = 0
        player = state.get_current_player()
        legal = state.get_legal_actions()
        if not legal:
            return None

        best_score = float('-inf')
        best_action = legal[0]

        for action in legal:
            self.nodes_expanded += 1
            score = evaluate_action_quality(state, action, player)
            if score > best_score:
                best_score = score
                best_action = action

        return best_action

