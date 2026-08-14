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
                 turn_skipped: bool = False, wild_suit_change_allowed: bool = True):
        
        self.p1_hand = list(p1_hand)
        self.p2_hand = list(p2_hand)
        self.deck_counts = deck_counts.copy() # Dictionary of card -> count in deck
        self.discard_pile = discard_pile[:]
        self.current_player = current_player

        # Game modifiers – active_suit is only set after the first card is played
        self.active_suit = active_suit if active_suit else (
            self.discard_pile[-1].suit if self.discard_pile else None
        )

        # Chance node state
        self.player_to_draw = player_to_draw

        # Penalties
        self.pending_draws = pending_draws
        self.turn_skipped = turn_skipped

        # Post-draw play opportunity: True when player drew and can still play
        self.just_drew = False   # set manually after construction when needed

        # Last action for the move log (set externally after apply_action)
        self.last_action_str = ""

        # Stacking wildcards rule: J/8/Joker cannot change the suit if played immediately
        # on top of another wild card, but can if a turn has passed (draw/pass/skip/non-wild).
        self.wild_suit_change_allowed = wild_suit_change_allowed

    def _can_reshuffle(self) -> bool:
        """Returns True if the discard pile can be reshuffled into the deck."""
        return sum(self.deck_counts.values()) == 0 and len(self.discard_pile) > 1

    def _reshuffled_deck(self) -> dict:
        """Returns a new deck_counts dict from the discard pile (keeping the top card)."""
        new_deck: dict = {}
        for card in self.discard_pile[:-1]:  # everything except the top card
            new_deck[card] = new_deck.get(card, 0) + 1
        return new_deck

    def is_terminal(self) -> bool:
        # Game over if someone runs out of cards
        if len(self.p1_hand) == 0 or len(self.p2_hand) == 0:
            return True
        # True draw: deck is empty, discard has only 1 card (can't reshuffle), and it's a CHANCE node
        if sum(self.deck_counts.values()) == 0 and not self._can_reshuffle() and self.current_player == 0:
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
        """Returns a list of (card, probability) for CHANCE nodes.
        If the deck is empty but the discard pile has cards, we reshuffle first.
        """
        deck = self.deck_counts
        total_cards = sum(deck.values())

        # Auto-reshuffle: deck is empty but discard has cards to recycle
        if total_cards == 0 and self._can_reshuffle():
            deck = self._reshuffled_deck()
            total_cards = sum(deck.values())

        outcomes = []
        if total_cards == 0:
            return [(None, 1.0)]  # Truly empty – draw nothing

        for card, count in deck.items():
            if count > 0:
                prob = count / total_cards
                outcomes.append((card, prob))
        return outcomes

    def _is_valid_play(self, card: CrazyCard) -> bool:
        # If no cards have been played yet, anything is valid (first move of the game)
        if not self.discard_pile:
            return True
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
        top_is_wild = self.discard_pile[-1].is_wild() if self.discard_pile else False
        allow_suit_change = (not top_is_wild) or self.wild_suit_change_allowed

        def search(seq, remaining):
            if len(seq) > 0:
                if len(seq) == 1 and seq[0].is_wild() and allow_suit_change:
                    for suit in ['Spade', 'Heart', 'Diamond', 'Club']:
                        valid_combos.append([seq[0], suit])
                else:
                    valid_combos.append(list(seq))
            
            if len(seq) >= 5:
                return

            for card in remaining:
                if not seq:
                    if self._is_valid_play(card):
                        new_rem = [c for c in remaining if c != card]
                        search([card], new_rem)
                else:
                    prev = seq[-1]
                    has_7 = any(c.rank == 7 for c in seq)
                    last_7 = None
                    if has_7:
                        for c in reversed(seq):
                            if c.rank == 7:
                                last_7 = c
                                break

                    if card.rank == prev.rank:
                        new_rem = [c for c in remaining if c != card]
                        search(seq + [card], new_rem)
                    elif prev.rank == 7 and card.suit == prev.suit:
                        new_rem = [c for c in remaining if c != card]
                        search(seq + [card], new_rem)
                    elif has_7 and (card.is_wild() or (last_7 and card.suit == last_7.suit)):
                        new_rem = [c for c in remaining if c != card]
                        search(seq + [card], new_rem)

        search([], hand)

        unique_combos = []
        seen = set()
        for combo in valid_combos:
            rep = tuple((c.rank, c.suit) if isinstance(c, CrazyCard) else c for c in combo)
            if rep not in seen:
                seen.add(rep)
                unique_combos.append(combo)

        return unique_combos

    def _calculate_combo_penalty(self, cards_played: List[CrazyCard]) -> int:
        """Calculates the total draw penalty generated by the played sequence of cards."""
        penalty = 0
        if cards_played:
            top_card = cards_played[-1]
            if top_card.get_draw_penalty() > 0:
                has_7 = any(c.rank == 7 for c in cards_played)
                has_other_than_7 = any(c.rank != 7 for c in cards_played)
                is_7_suit_combo = has_7 and has_other_than_7

                for c in reversed(cards_played):
                    if c.get_draw_penalty() > 0:
                        if is_7_suit_combo and c.rank == 7:
                            break  # 7 doesn't contribute and stops the penalty accumulation
                        
                        if c.rank == top_card.rank or (c.rank == 'A' and top_card.rank == 'A'):
                            penalty += c.get_draw_penalty()
                        else:
                            break
                    else:
                        break
        return penalty

    def _get_counter_penalty_actions(self, hand: List[CrazyCard]) -> List[Any]:
        """
        When under a pending draw penalty, a player may 'counter' by playing
        their own draw-penalty card(s) to pass the penalty along.
        A combo (single or multi-card) is a valid counter if:
          - It is a valid play from _generate_valid_combos(hand)
          - The combo itself results in a penalty target > 0 (by calculation)
        """
        valid_combos = self._generate_valid_combos(hand)
        counters = []
        for combo in valid_combos:
            cards_in_combo = [x for x in combo if isinstance(x, CrazyCard)]
            if cards_in_combo:
                if self._calculate_combo_penalty(cards_in_combo) > 0:
                    counters.append(combo)
        return counters

    def get_legal_actions(self) -> List[Any]:
        if self.current_player == 0:
            return [outcome[0] for outcome in self.get_chance_outcomes()]

        # Standard player turn
        hand = self.p1_hand if self.current_player == 1 else self.p2_hand

        # Post-draw opportunity: player can play the card they just drew or pass
        if getattr(self, 'just_drew', False):
            valid_plays = self._generate_valid_combos(hand)
            return [tuple(a) for a in valid_plays] + [("PASS_TURN",)]

        if self.pending_draws > 0:
            # Player can either accept the draw penalty OR counter with their own penalty card
            counter_actions = self._get_counter_penalty_actions(hand)
            if counter_actions:
                return [tuple(a) for a in counter_actions] + [("DRAW_PENALTY",)]
            return [("DRAW_PENALTY",)]

        actions = self._generate_valid_combos(hand)

        # A player can always choose to draw a card if they have no valid moves (or just want to)
        actions.append(("DRAW_FROM_DECK",))

        # Convert all combos to tuples so they are hashable
        return [tuple(a) for a in actions]

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
            # If the deck is empty, reshuffle the discard pile first
            if sum(deck.values()) == 0 and len(discard) > 1:
                new_deck = {}
                for card in discard[:-1]:
                    new_deck[card] = new_deck.get(card, 0) + 1
                deck = new_deck
                discard = [discard[-1]]  # Keep only the top card

            card_drawn = action
            if card_drawn is not None:
                deck[card_drawn] = max(0, deck.get(card_drawn, 0) - 1)
                if player_to_draw == 1:
                    p1.append(card_drawn)
                else:
                    p2.append(card_drawn)

            if pending > 0:
                pending -= 1
                if pending > 0:
                    # Still need to draw more penalty cards
                    return CrazyState(p1, p2, deck, discard, 0, active_suit, player_to_draw, pending, skipped, wild_suit_change_allowed=True)
                else:
                    # Penalty finished. Now it's this player's normal turn (unless they were skipped)
                    next_player = player_to_draw
                    if skipped:
                        next_player = 2 if player_to_draw == 1 else 1
                    return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, 0, False, wild_suit_change_allowed=True)
            else:
                # Normal draw from deck.
                # Give the player a chance to play the drawn card before ending turn.
                new_state = CrazyState(p1, p2, deck, discard, player_to_draw, active_suit, None, 0, False, wild_suit_change_allowed=True)
                new_state.just_drew = True  # Signal: player may play 1 card or pass
                return new_state

        # Player turn actions
        if action == ("DRAW_PENALTY",):
            return CrazyState(p1, p2, deck, discard, 0, active_suit, self.current_player, pending, skipped, wild_suit_change_allowed=True)

        if action == ("DRAW_FROM_DECK",):
            return CrazyState(p1, p2, deck, discard, 0, active_suit, self.current_player, 0, False, wild_suit_change_allowed=True)

        if action == ("PASS_TURN",):
            # Player drew a card and chose not to play it — end the turn
            next_player = 2 if self.current_player == 1 else 1
            return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, 0, False, wild_suit_change_allowed=True)

        # Playing a combo
        hand = p1 if self.current_player == 1 else p2
        new_suit = None
        
        for item in action:
            if isinstance(item, str):
                new_suit = item # Wild card suit selection
            else:
                hand.remove(item)
                discard.append(item)
                
        # Resolve abilities
        top_card   = discard[-1]
        top_is_wild = len(self.discard_pile) >= 1 and self.discard_pile[-1].is_wild()
        allow_suit_change = (not top_is_wild) or self.wild_suit_change_allowed

        # If a new wild is played on top of an existing wild, inherit the active_suit (no change)
        cards_played = [x for x in action if isinstance(x, CrazyCard)]
        first_played_is_wild = cards_played and cards_played[0].is_wild()
        new_suit_str = new_suit  # declared suit (if any) from the action

        has_7 = any(c.rank == 7 for c in cards_played)

        if has_7:
            # Stacked using 7: wildcards lose suit choice and it retains the topmost non-special suit
            active_suit = self.active_suit  # Default fallback
            for c in reversed(cards_played):
                if not c.is_wild():
                    active_suit = c.suit
                    break
        else:
            if first_played_is_wild and top_is_wild and not self.wild_suit_change_allowed:
                # Wild-on-wild without a turn passing: keep the existing active_suit
                active_suit = self.active_suit
            elif new_suit_str and allow_suit_change:
                active_suit = new_suit_str
            else:
                # If a wild card is played but no suit choice is declared/allowed, inherit the active suit.
                # Otherwise (non-wild play), inherit the top card's suit.
                if first_played_is_wild:
                    active_suit = self.active_suit if (self.active_suit and self.active_suit != 'Joker') else 'Spade'
                else:
                    active_suit = top_card.suit
                    if active_suit == 'Joker':
                        active_suit = 'Spade'

        # Set suit change allowed for next turn:
        # If a wild was played, it only restricts the next wildcard if it actually CHANGED the suit.
        # If it kept the suit the same, then wild_suit_change_allowed remains True.
        suit_changed = (active_suit != self.active_suit)
        if first_played_is_wild:
            new_wild_suit_change_allowed = not suit_changed
        else:
            new_wild_suit_change_allowed = True
        
        penalty = self._calculate_combo_penalty(cards_played)
        num_skips = sum(1 for c in cards_played if c.skips_turn())

        if penalty > 0:
            # Penalty active: target is the opponent
            next_player = 2 if self.current_player == 1 else 1
            next_skipped = (num_skips > 0)
            
            # If the current player countered an incoming draw penalty,
            # stack the new penalty on top and pass it to the opponent.
            if self.pending_draws > 0:
                combined_penalty = self.pending_draws + penalty
                return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, combined_penalty, next_skipped, wild_suit_change_allowed=new_wild_suit_change_allowed)
            
            return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, penalty, next_skipped, wild_suit_change_allowed=new_wild_suit_change_allowed)
        else:
            # No penalty: next player is toggled 1 + num_skips times
            toggles = 1 + num_skips
            next_player = self.current_player
            for _ in range(toggles):
                next_player = 2 if next_player == 1 else 1
            
            return CrazyState(p1, p2, deck, discard, next_player, active_suit, None, 0, False, wild_suit_change_allowed=new_wild_suit_change_allowed)


def determinize_crazy_state(state: CrazyState) -> CrazyState:
    """
    Creates a hypothetical state for Information Set MCTS (IS-MCTS).
    The observing player keeps their own hand and discard pile intact, while the
    opponent's hidden hand cards are randomly sampled from the unobserved deck pool!
    """
    import random
    cp = state.current_player
    my_hand = list(state.p1_hand if cp == 1 else state.p2_hand)
    opp_hand_size = len(state.p2_hand if cp == 1 else state.p1_hand)

    # Pool of unobserved cards (deck pool)
    deck_pool = []
    for card, count in state.deck_counts.items():
        deck_pool.extend([card] * count)

    random.shuffle(deck_pool)
    sampled_opp_hand = deck_pool[:opp_hand_size]
    remaining_deck = deck_pool[opp_hand_size:]

    new_deck_counts = {}
    for card in remaining_deck:
        new_deck_counts[card] = new_deck_counts.get(card, 0) + 1

    p1_h = my_hand if cp == 1 else sampled_opp_hand
    p2_h = sampled_opp_hand if cp == 1 else my_hand

    st = CrazyState(
        p1_hand=p1_h,
        p2_hand=p2_h,
        deck_counts=new_deck_counts,
        discard_pile=list(state.discard_pile),
        current_player=cp,
        pending_draws=state.pending_draws
    )
    st.just_drew = getattr(state, 'just_drew', False)
    return st

