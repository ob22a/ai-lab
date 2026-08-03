from typing import List, Tuple, Any
from games.GameState import GameState
from domains.crazy.CrazyCard import CrazyCard

class CrazyState(GameState):
    """
    State representation for 'Crazy'.
    current_player: 1 (MAX), 2 (MIN), or 0 (CHANCE - when drawing a card)
    """
    def __init__(self, p1_hand: List[CrazyCard], p2_hand: List[CrazyCard], 
                 deck_counts: dict, discard_pile: List[CrazyCard], 
                 current_player: int, active_suit: str = None, 
                 player_to_draw: int = None, pending_draws: int = 0,
                 turn_skipped: bool = False):
        
        self.p1_hand = sorted(p1_hand, key=lambda c: (str(c.rank), c.suit))
        self.p2_hand = sorted(p2_hand, key=lambda c: (str(c.rank), c.suit))
        self.deck_counts = deck_counts.copy() # Dictionary of card -> count in deck
        self.discard_pile = discard_pile[:]
        self.current_player = current_player
        
        # Game modifiers
        self.active_suit = active_suit or (self.discard_pile[-1].suit if self.discard_pile else None)
        
        # Chance node state
        self.player_to_draw = player_to_draw
        
        # Penalties
        self.pending_draws = pending_draws
        self.turn_skipped = turn_skipped

    def is_terminal(self) -> bool:
        # Game over if someone runs out of cards
        if len(self.p1_hand) == 0 or len(self.p2_hand) == 0:
            return True
        # Draw game if the deck is completely empty and no one can play
        if sum(self.deck_counts.values()) == 0 and self.current_player == 0:
            return True
        return False

    def get_utility(self, player: int) -> float:
        if len(self.p1_hand) == 0:
            return 1000.0 if player == 1 else -1000.0
        elif len(self.p2_hand) == 0:
            return 1000.0 if player == 2 else -1000.0
            
        # Heuristic for non-terminal states
        # The fewer cards you have, the better. But wild cards are valuable.
        my_hand = self.p1_hand if player == 1 else self.p2_hand
        opp_hand = self.p2_hand if player == 1 else self.p1_hand
        
        score = (len(opp_hand) - len(my_hand)) * 10.0
        
        # Add value for holding special cards
        for c in my_hand:
            if c.is_wild():
                score += 3.0
            elif c.get_draw_penalty() > 0 or c.skips_turn():
                score += 2.0
                
        return score

    def get_current_player(self) -> int:
        return self.current_player

    def get_chance_outcomes(self) -> List[Tuple[Any, float]]:
        """Returns a list of (card, probability) for CHANCE nodes."""
        total_cards = sum(self.deck_counts.values())
        outcomes = []
        if total_cards == 0:
            return [(None, 1.0)] # Empty deck, draw nothing
            
        for card, count in self.deck_counts.items():
            if count > 0:
                prob = count / total_cards
                outcomes.append((card, prob))
        return outcomes

    def _is_valid_play(self, card: CrazyCard) -> bool:
        if card.is_wild():
            return True
        top_card = self.discard_pile[-1]
        
        # The active suit takes precedence (in case a wild card was played previously)
        if self.active_suit and card.suit == self.active_suit:
            return True
        
        # Fallback to rank match
        if card.rank == top_card.rank:
            return True
            
        return False

    def _generate_valid_combos(self, hand: List[CrazyCard]) -> List[List[CrazyCard]]:
        """Generates all valid combinations of cards that can be played in one turn."""
        valid_combos = []
        
        # 1. Single card plays
        for i, card in enumerate(hand):
            if self._is_valid_play(card):
                # If it's a wild card, we must append a suit choice to the action
                if card.is_wild():
                    for suit in ['Spade', 'Heart', 'Diamond', 'Club']:
                        valid_combos.append([card, suit])
                else:
                    valid_combos.append([card])
                    
        # 2. Multi-card combinations (Rank Match or Suit Match starting with 7)
        # For performance, we only generate up to length 4 combos
        # (Generating all subsets is expensive, so we just group by rank and suit)
        
        # Rank Combos (e.g. 4s)
        ranks = {}
        for c in hand:
            if not c.is_wild():
                if c.rank not in ranks:
                    ranks[c.rank] = []
                ranks[c.rank].append(c)
                
        for rank, cards in ranks.items():
            if len(cards) > 1:
                # We can play this combo if the FIRST card is valid
                for first_idx in range(len(cards)):
                    if self._is_valid_play(cards[first_idx]):
                        combo = [cards[first_idx]]
                        # Add the rest
                        for i, c in enumerate(cards):
                            if i != first_idx:
                                combo.append(c)
                        # We could play subset combos, but playing ALL of them is always strictly better
                        valid_combos.append(combo)
                        
        # Suit Combos (Starting with 7)
        for i, first_card in enumerate(hand):
            if first_card.rank == 7 and self._is_valid_play(first_card):
                suit = first_card.suit
                combo = [first_card]
                for c in hand:
                    if c != first_card and c.suit == suit and not c.is_wild():
                        combo.append(c)
                if len(combo) > 1:
                    valid_combos.append(combo)
                    
        return valid_combos

    def get_legal_actions(self) -> List[Any]:
        if self.current_player == 0:
            return [outcome[0] for outcome in self.get_chance_outcomes()]
            
        # Standard player turn
        hand = self.p1_hand if self.current_player == 1 else self.p2_hand
        
        if self.pending_draws > 0:
            # We are forced to draw due to a penalty!
            # The player has no choice but to transition to a CHANCE node
            return ["DRAW_PENALTY"]
            
        if self.turn_skipped:
            return ["SKIP"]

        actions = self._generate_valid_combos(hand)
        
        # A player can always choose to draw a card if they have no valid moves (or just want to)
        actions.append(["DRAW_FROM_DECK"])
        
        return actions

    def apply_action(self, action: Any) -> 'CrazyState':
        p1 = list(self.p1_hand)
        p2 = list(self.p2_hand)
        deck = self.deck_counts.copy()
        discard = list(self.discard_pile)
        next_player = self.current_player
        active_suit = self.active_suit
        player_to_draw = self.player_to_draw
        pending = self.pending_draws
        skipped = self.turn_skipped

        if self.current_player == 0:
            # Resolving a CHANCE node (drawing a card)
            card_drawn = action
            if card_drawn is not None:
                deck[card_drawn] -= 1
                if player_to_draw == 1:
                    p1.append(card_drawn)
                else:
                    p2.append(card_drawn)
                    
            if pending > 0:
                pending -= 1
                if pending > 0:
                    # Still need to draw more penalty cards
                    return CrazyState(p1, p2, deck, discard, 0, active_suit, player_to_draw, pending, skipped)
                else:
                    # Penalty finished. Now it's this player's normal turn (unless they were skipped)
                    next_player = player_to_draw
                    return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, 0, skipped)
            else:
                # Normal draw from deck. Turn ends immediately after drawing (for simplicity in our AI model).
                # Actually, the rules say you can play it immediately.
                # To simplify the AI game tree, we will enforce that drawing ends the turn.
                next_player = 2 if player_to_draw == 1 else 1
                return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, 0, False)

        # Player turn actions
        if action == "DRAW_PENALTY":
            return CrazyState(p1, p2, deck, discard, 0, active_suit, self.current_player, pending, skipped)
            
        if action == "SKIP":
            next_player = 2 if self.current_player == 1 else 1
            return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, 0, False)
            
        if action == ["DRAW_FROM_DECK"]:
            return CrazyState(p1, p2, deck, discard, 0, active_suit, self.current_player, 0, False)

        # Playing a combo
        hand = p1 if self.current_player == 1 else p2
        new_suit = None
        
        for item in action:
            if isinstance(item, str):
                new_suit = item # Wild card suit selection
            else:
                hand.remove(item)
                discard.append(item)
                
        # Resolve abilities (only the top-most special cards trigger)
        # We aggregate abilities if they are the same rank, otherwise just the top card
        top_card = discard[-1]
        active_suit = new_suit if new_suit else top_card.suit
        
        penalty = 0
        skip = False
        
        for item in action:
            if isinstance(item, CrazyCard):
                if item.skips_turn():
                    skip = True
                penalty += item.get_draw_penalty()
                # 7 combo edge case: only add up penalty if all are 7s or something?
                # The python code says if it's a 7 combo, we add the penalties.
                
        next_player = 2 if self.current_player == 1 else 1
        
        return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, penalty, skip)
