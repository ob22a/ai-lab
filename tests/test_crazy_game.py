"""
test_crazy_game.py
Unit tests for the 'Crazy' card game logic in domains/crazy/.

Run with:
    pytest tests/test_crazy_game.py -v
"""

import pytest
from domains.crazy.CrazyCard import CrazyCard, create_deck
from domains.crazy.CrazyState import CrazyState


def make_card(rank, suit='Spade'):
    return CrazyCard(rank, suit)

def make_state(p1_hand, p2_hand, discard_top, deck_cards=None,
               current_player=1, pending_draws=0, turn_skipped=False):
    """Helper to build a CrazyState quickly."""
    deck_counts = {}
    for c in (deck_cards or []):
        deck_counts[c] = deck_counts.get(c, 0) + 1
    return CrazyState(
        p1_hand=p1_hand,
        p2_hand=p2_hand,
        deck_counts=deck_counts,
        discard_pile=[discard_top],
        current_player=current_player,
        pending_draws=pending_draws,
        turn_skipped=turn_skipped,
    )


class TestCrazyCard:
    def test_joker_is_wild(self):
        assert make_card(0, 'Joker').is_wild()

    def test_8_is_wild(self):
        assert make_card(8, 'Heart').is_wild()

    def test_j_is_wild(self):
        assert make_card('J', 'Club').is_wild()

    def test_normal_card_not_wild(self):
        assert not make_card(7, 'Spade').is_wild()

    def test_joker_penalty_7(self):
        assert make_card(0, 'Joker').get_draw_penalty() == 7

    def test_ace_of_spades_penalty_5(self):
        assert make_card('A', 'Spade').get_draw_penalty() == 5

    def test_ace_of_heart_no_penalty(self):
        assert make_card('A', 'Heart').get_draw_penalty() == 0

    def test_2_penalty_2(self):
        assert make_card(2, 'Spade').get_draw_penalty() == 2

    def test_7_penalty_1(self):
        assert make_card(7, 'Club').get_draw_penalty() == 1

    def test_5_skips_turn(self):
        assert make_card(5, 'Diamond').skips_turn()

    def test_non_skip_card(self):
        assert not make_card(3, 'Heart').skips_turn()

    def test_create_deck_54_cards(self):
        deck = create_deck()
        assert len(deck) == 54


class TestValidPlay:
    def test_same_suit_valid(self):
        top = make_card(4, 'Heart')
        state = make_state([make_card(9, 'Heart')], [make_card(3, 'Spade')], top)
        assert (make_card(9, 'Heart'),) in state.get_legal_actions()

    def test_same_rank_valid(self):
        top = make_card(4, 'Spade')
        state = make_state([make_card(4, 'Diamond')], [make_card(3, 'Spade')], top)
        assert (make_card(4, 'Diamond'),) in state.get_legal_actions()

    def test_different_suit_and_rank_invalid(self):
        top = make_card(4, 'Spade')
        state = make_state([make_card(9, 'Heart')], [make_card(3, 'Club')], top)
        legal = state.get_legal_actions()
        assert (make_card(9, 'Heart'),) not in legal

    def test_wild_8_always_valid(self):
        top = make_card(4, 'Spade')
        state = make_state([make_card(8, 'Heart')], [make_card(3, 'Club')], top)
        # 8 of Heart should appear as (8_Heart, suit) combos
        legal = state.get_legal_actions()
        card_8 = make_card(8, 'Heart')
        has_wild = any(isinstance(a[0], CrazyCard) and a[0] == card_8 for a in legal)
        assert has_wild, "Wild card 8 should always be playable"

    def test_active_suit_respected(self):
        """After a wild card changes suit to Club, only Clubs (or same rank) are valid."""
        top = make_card(8, 'Spade')
        # active_suit set to Club
        state = CrazyState(
            p1_hand=[make_card(7, 'Club'), make_card(4, 'Heart')],
            p2_hand=[make_card(3, 'Spade')],
            deck_counts={},
            discard_pile=[top],
            current_player=1,
            active_suit='Club'
        )
        legal = state.get_legal_actions()
        assert (make_card(7, 'Club'),) in legal
        assert (make_card(4, 'Heart'),) not in legal

class TestCombos:
    def test_rank_combo_two_fours(self):
        top = make_card(4, 'Spade')
        four_s = make_card(4, 'Spade')
        four_h = make_card(4, 'Heart')
        state = make_state([four_s, four_h], [make_card(3, 'Club')], top)
        legal = state.get_legal_actions()
        # A rank combo of both 4s should exist
        has_combo = any(
            len([x for x in a if isinstance(x, CrazyCard)]) == 2
            for a in legal
        )
        assert has_combo, "Rank combo of two 4s should be legal"

    def test_suit_combo_starting_with_7(self):
        """7 of Spade can start a combo with other Spades."""
        top = make_card(7, 'Spade')
        seven_s = make_card(7, 'Spade')
        nine_s  = make_card(9, 'Spade')
        three_h = make_card(3, 'Heart')
        state = make_state([seven_s, nine_s, three_h], [make_card(2, 'Club')], top)
        legal = state.get_legal_actions()
        cards_in_combos = [
            tuple(sorted([x for x in a if isinstance(x, CrazyCard)], key=lambda c: (str(c.rank), c.suit)))
            for a in legal
        ]
        expected = tuple(sorted([seven_s, nine_s], key=lambda c: (str(c.rank), c.suit)))
        assert expected in cards_in_combos, "7♠ + 9♠ suit combo should be legal"


class TestPenalties:
    def test_2_forces_opponent_to_draw_2(self):
        top  = make_card(4, 'Spade')
        two  = make_card(2, 'Spade')
        state = make_state([two], [make_card(3, 'Club')], top)
        new_state = state.apply_action((two,))
        assert new_state.pending_draws == 2
        assert new_state.current_player == 2

    def test_joker_forces_opponent_to_draw_7(self):
        top   = make_card(4, 'Spade')
        joker = make_card(0, 'Joker')
        state = make_state([joker], [make_card(3, 'Club')], top)
        new_state = state.apply_action((joker, 'Spade'))
        assert new_state.pending_draws == 7

    def test_counter_penalty_with_2(self):
        """Player 2 can counter a +2 penalty by playing their own 2."""
        top   = make_card(2, 'Spade')
        two_h = make_card(2, 'Heart')
        state = make_state(
            p1_hand=[make_card(9, 'Club')],
            p2_hand=[two_h],
            discard_top=top,
            current_player=2,
            pending_draws=2
        )
        legal = state.get_legal_actions()
        assert (two_h,) in legal, "Player should be able to counter with 2"
        assert ('DRAW_PENALTY',) in legal, "Player should be able to accept penalty"

    def test_counter_stacks_penalties(self):
        """Countering a +2 with your own +2 makes the opponent draw +4."""
        top   = make_card(2, 'Spade')
        two_h = make_card(2, 'Heart')
        state = make_state([make_card(9, 'Club')], [two_h], top,
                           current_player=2, pending_draws=2)
        new_state = state.apply_action((two_h,))
        assert new_state.pending_draws == 4
        assert new_state.current_player == 1, "Penalty now passes back to P1"

    def test_skip_with_5(self):
        top   = make_card(5, 'Spade')
        five  = make_card(5, 'Spade')
        state = make_state([five], [make_card(3, 'Club')], top, current_player=1)
        new_state = state.apply_action((five,))
        assert new_state.current_player == 1, "Single skip card skips opponent, so it goes back to P1"

    def test_double_skip_with_5s(self):
        top    = make_card(5, 'Spade')
        five_s = make_card(5, 'Spade')
        five_h = make_card(5, 'Heart')
        state  = make_state([five_s, five_h], [make_card(3, 'Club')], top, current_player=1)
        new_state = state.apply_action((five_s, five_h))
        assert new_state.current_player == 2, "Double skip card skips both P2 and P1, so it goes to P2"

    def test_wildcard_stacking_suit_change(self):
        """Test J/8/Joker stacking: immediate wild on top of wild inherits suit, but after a turn it can change."""
        top = make_card(8, 'Spade')
        # P1 has J of Spade, P2 has 8 of Heart.
        # Starting: active_suit = Spade.
        # 1. P1 plays J and changes it to Heart.
        state = CrazyState([make_card('J', 'Spade')], [make_card(8, 'Heart')], {}, [top], current_player=1)
        legal_1 = state.get_legal_actions()
        assert (make_card('J', 'Spade'), 'Heart') in legal_1
        
        state_after_j = state.apply_action((make_card('J', 'Spade'), 'Heart'))
        assert state_after_j.active_suit == 'Heart'
        assert state_after_j.wild_suit_change_allowed is False
        
        # 2. P2 plays 8 of Heart immediately. Since wild_suit_change_allowed is False,
        # P2's 8 of Heart should NOT allow changing suit. It must inherit Heart.
        legal_2 = state_after_j.get_legal_actions()
        assert (make_card(8, 'Heart'),) in legal_2
        assert not any(len(a) > 1 and a[0] == make_card(8, 'Heart') and isinstance(a[1], str) for a in legal_2)
        
        state_after_8 = state_after_j.apply_action((make_card(8, 'Heart'),))
        assert state_after_8.active_suit == 'Heart'
        assert state_after_8.wild_suit_change_allowed is True
        
        # 3. Now let's simulate P1 drawing and passing (passing the turn).
        # Passing should set wild_suit_change_allowed back to True.
        state_after_pass = state_after_8.apply_action(("DRAW_FROM_DECK",))
        # Chance outcome draws card...
        state_after_draw = state_after_pass.apply_action(None) # drawn nothing
        assert state_after_draw.wild_suit_change_allowed is True
        
        # 4. P1 passes the turn, making it P2's turn.
        state_p2_turn = state_after_draw.apply_action(("PASS_TURN",))
        state_p2_turn.p2_hand = [make_card(0, 'Joker')]
        legal_3 = state_p2_turn.get_legal_actions()
        assert (make_card(0, 'Joker'), 'Diamond') in legal_3

    def test_combo_penalties(self):
        """Test combination penalties for various combos: 7+2, 7+2+2, 7+7, 7+4, 7+2+4."""
        # 1. 7 Spade + 2 Spade -> penalty should be 2 (from 2 Spade)
        seven_s = make_card(7, 'Spade')
        two_s = make_card(2, 'Spade')
        state = make_state([seven_s, two_s], [make_card(3, 'Club')], make_card(4, 'Spade'))
        res1 = state.apply_action((seven_s, two_s))
        assert res1.pending_draws == 2, f"Expected 2, got {res1.pending_draws}"

        # 2. 7 Spade + 2 Spade + 2 Club -> penalty should be 4 (from both 2s)
        two_c = make_card(2, 'Club')
        state = make_state([seven_s, two_s, two_c], [make_card(3, 'Club')], make_card(4, 'Spade'))
        res2 = state.apply_action((seven_s, two_s, two_c))
        assert res2.pending_draws == 4, f"Expected 4, got {res2.pending_draws}"

        # 3. Rank combo: 7 Spade + 7 Heart -> penalty should be 2 (sum of both 7s)
        seven_h = make_card(7, 'Heart')
        state = make_state([seven_s, seven_h], [make_card(3, 'Club')], make_card(7, 'Diamond'))
        res3 = state.apply_action((seven_s, seven_h))
        assert res3.pending_draws == 2, f"Expected 2, got {res3.pending_draws}"

        # 4. 7 Spade + 4 Spade (non-penalty card) -> penalty should be 0
        four_s = make_card(4, 'Spade')
        state = make_state([seven_s, four_s], [make_card(3, 'Club')], make_card(4, 'Spade'))
        res4 = state.apply_action((seven_s, four_s))
        assert res4.pending_draws == 0, f"Expected 0, got {res4.pending_draws}"

        # 5. 7 Spade + 2 Spade + 4 Spade -> penalty should be 0
        state = make_state([seven_s, two_s, four_s], [make_card(3, 'Club')], make_card(4, 'Spade'))
        res5 = state.apply_action((seven_s, two_s, four_s))
        assert res5.pending_draws == 0, f"Expected 0, got {res5.pending_draws}"

    def test_counter_penalty_with_combo_of_2s(self):
        """Under +2 penalty, player can counter with a combo of 2s (e.g. playing two 2s)."""
        top = make_card(2, 'Spade')
        two_h = make_card(2, 'Heart')
        two_c = make_card(2, 'Club')
        state = make_state(
            p1_hand=[make_card(9, 'Club')],
            p2_hand=[two_h, two_c],
            discard_top=top,
            current_player=2,
            pending_draws=2
        )
        legal = state.get_legal_actions()
        # They should be able to play the combo (two_h, two_c)
        assert (two_h, two_c) in legal or (two_c, two_h) in legal, "Should be able to play combo of two 2s"
        
        # Stacking the two 2s (+4) on top of the pending +2 should result in +6 penalty
        action = (two_h, two_c) if (two_h, two_c) in legal else (two_c, two_h)
        new_state = state.apply_action(action)
        assert new_state.pending_draws == 6, f"Expected 6, got {new_state.pending_draws}"

    def test_mixed_combo_defense_invalid(self):
        """Combos resulting in draw penalty > 0 are valid counters, but non-penalty cards/wildcards (like 8) are invalid for defense."""
        top = make_card(2, 'Heart')
        seven_h = make_card(7, 'Heart')
        two_h = make_card(2, 'Heart')
        eight_h = make_card(8, 'Heart')
        
        state = make_state(
            p1_hand=[make_card(9, 'Club')],
            p2_hand=[seven_h, two_h, eight_h],
            discard_top=top,
            current_player=2,
            pending_draws=2
        )
        legal = state.get_legal_actions()
        # (eight_h,) is wildcard but has 0 penalty, so invalid to counter
        assert (eight_h,) not in legal
        # (seven_h, two_h) ends in 2H (+2 penalty), so it is a valid counter combo
        assert (seven_h, two_h) in legal or (two_h, seven_h) in legal
        assert (two_h,) in legal
        assert ('DRAW_PENALTY',) in legal

    def test_user_bug_6d_8d_illegal(self):
        """6D and 8D played together without a 7 is illegal."""
        top = make_card(6, 'Diamond')
        c6d = make_card(6, 'Diamond')
        c8d = make_card(8, 'Diamond')
        state = make_state([c6d, c8d], [make_card(3, 'Club')], top)
        legal = state.get_legal_actions()
        assert (c6d, c8d) not in legal
        assert (c8d, c6d) not in legal

    def test_user_bug_j_joker_8_illegal_together(self):
        """J, Joker, 8 played together without a 7 is illegal sequence."""
        top = make_card(4, 'Spade')
        cj = make_card('J', 'Spade')
        cjoker = make_card(0, 'Joker')
        c8 = make_card(8, 'Heart')
        state = make_state([cj, cjoker, c8], [make_card(3, 'Club')], top)
        legal = state.get_legal_actions()
        # Wilds cannot chain to each other directly in a single combo without 7 or matching rank
        has_wild_chain = any(
            len(a) > 1 and all(isinstance(x, CrazyCard) and x.is_wild() for x in a)
            for a in legal
        )
        assert not has_wild_chain

    def test_user_bug_7s_8c_jh_suit_is_spade(self):
        """If 7S 8C JH played together, the suit is Spade (topmost non-special card)."""
        top = make_card(4, 'Spade')
        c7s = make_card(7, 'Spade')
        c8c = make_card(8, 'Club')
        cjh = make_card('J', 'Heart')
        state = make_state([c7s, c8c, cjh], [make_card(3, 'Club')], top)
        res = state.apply_action((c7s, c8c, cjh))
        assert res.active_suit == 'Spade'

    def test_user_bug_7d_3d_3c_8s_joker_suit_is_club(self):
        """If 7D 3D 3C 8S Joker played together, the suit is Club (topmost non-special card)."""
        top = make_card(4, 'Diamond')
        c7d = make_card(7, 'Diamond')
        c3d = make_card(3, 'Diamond')
        c3c = make_card(3, 'Club')
        c8s = make_card(8, 'Spade')
        cjoker = make_card(0, 'Joker')
        state = make_state([c7d, c3d, c3c, c8s, cjoker], [make_card(3, 'Club')], top)
        res = state.apply_action((c7d, c3d, c3c, c8s, cjoker))
        assert res.active_suit == 'Club'

    def test_user_bug_7d_7c_3c_3s_8d_8s_jc_valid_suit_spade(self):
        """7D 7C 3C 3S 8D 8S JC is valid and suit is Spade."""
        top = make_card(4, 'Diamond')
        cards = [
            make_card(7, 'Diamond'), make_card(7, 'Club'),
            make_card(3, 'Club'), make_card(3, 'Spade'),
            make_card(8, 'Diamond'), make_card(8, 'Spade'),
            make_card('J', 'Club')
        ]
        state = make_state(list(cards), [make_card(4, 'Club')], top)
        res = state.apply_action(tuple(cards))
        assert res.active_suit == 'Spade'

    def test_user_bug_10s_8d_illegal(self):
        """10S and 8D illegal (mismatched rank, no 7)."""
        top = make_card(10, 'Spade')
        c10s = make_card(10, 'Spade')
        c8d = make_card(8, 'Diamond')
        state = make_state([c10s, c8d], [make_card(3, 'Club')], top)
        legal = state.get_legal_actions()
        assert (c10s, c8d) not in legal

    def test_user_bug_4d_4s_js_jd_illegal_without_7(self):
        """4D 4S JS JD illegal without a 7 linking them."""
        top = make_card(4, 'Diamond')
        c4d = make_card(4, 'Diamond')
        c4s = make_card(4, 'Spade')
        cjs = make_card('J', 'Spade')
        cjd = make_card('J', 'Diamond')
        state = make_state([c4d, c4s, cjs, cjd], [make_card(3, 'Club')], top)
        legal = state.get_legal_actions()
        assert (c4d, c4s, cjs, cjd) not in legal

    def test_user_bug_7c_5c_ac_as_counter_penalty_target(self):
        """7C 5C AC AS targets opponent for penalty and doesn't reverse to current player."""
        top = make_card(7, 'Club')
        c7c = make_card(7, 'Club')
        c5c = make_card(5, 'Club')
        cac = make_card('A', 'Club')
        cas = make_card('A', 'Spade')
        state = make_state([c7c, c5c, cac, cas], [make_card(3, 'Club')], top, current_player=1)
        res = state.apply_action((c7c, c5c, cac, cas))
        # P1 played it, so penalty should target P2 (current_player=2)
        assert res.current_player == 2
        assert res.pending_draws == 5
        assert res.turn_skipped is True

    def test_complex_7_combo_stack(self):
        """Test sequence 7 D + 7 H + 8 H + 9 H is valid on top of Diamond."""
        top = make_card(4, 'Diamond')
        c7d = make_card(7, 'Diamond')
        c7h = make_card(7, 'Heart')
        c8h = make_card(8, 'Heart')
        c9h = make_card(9, 'Heart')
        
        state = make_state(
            p1_hand=[c7d, c7h, c8h, c9h],
            p2_hand=[make_card(3, 'Club')],
            discard_top=top,
            current_player=1
        )
        legal = state.get_legal_actions()
        # Find if the combo (7D, 7H, 8H, 9H) is in legal (in any order since it gets generated)
        found = False
        for action in legal:
            if len(action) == 4 and all(isinstance(x, CrazyCard) for x in action):
                ranks = [x.rank for x in action]
                suits = [x.suit for x in action]
                if ranks == [7, 7, 8, 9] and suits == ['Diamond', 'Heart', 'Heart', 'Heart']:
                    found = True
                    break
        assert found, "Combo 7D + 7H + 8H + 9H should be legal on top of Diamond"

    def test_complex_7_club_stack(self):
        """Test sequence 7 H + 7 S + 7 C + 8 C + 9 C is valid on top of Heart."""
        top = make_card(4, 'Heart')
        c7h = make_card(7, 'Heart')
        c7s = make_card(7, 'Spade')
        c7c = make_card(7, 'Club')
        c8c = make_card(8, 'Club')
        c9c = make_card(9, 'Club')
        
        state = make_state(
            p1_hand=[c7h, c7s, c7c, c8c, c9c],
            p2_hand=[make_card(3, 'Club')],
            discard_top=top,
            current_player=1
        )
        legal = state.get_legal_actions()
        found = False
        for action in legal:
            if len(action) == 5 and all(isinstance(x, CrazyCard) for x in action):
                ranks = [x.rank for x in action]
                suits = [x.suit for x in action]
                if ranks == [7, 7, 7, 8, 9] and suits == ['Heart', 'Spade', 'Club', 'Club', 'Club']:
                    found = True
                    break
        assert found, "Combo 7H + 7S + 7C + 8C + 9C should be legal on top of Heart"

    def test_four_2s_draw_8(self):
        """Test rank combo 2C + 2H + 2S + 2D causes draw penalty of exactly 8."""
        top = make_card(2, 'Club')
        c2c = make_card(2, 'Club')
        c2h = make_card(2, 'Heart')
        c2s = make_card(2, 'Spade')
        c2d = make_card(2, 'Diamond')
        
        state = make_state([c2c, c2h, c2s, c2d], [make_card(3, 'Club')], top, current_player=1)
        res = state.apply_action((c2c, c2h, c2s, c2d))
        assert res.pending_draws == 8, f"Expected 8, got {res.pending_draws}"

    def test_same_suit_wild_no_lock(self):
        """If a wild card is played but chooses the SAME suit as active before, the next wild immediately can change it."""
        top = make_card(4, 'Club') # Active suit is Club
        state = CrazyState([make_card('J', 'Club')], [make_card(8, 'Heart')], {}, [top], current_player=1, active_suit='Club')
        
        # P1 plays J and chooses Club (same suit).
        state_after_j = state.apply_action((make_card('J', 'Club'), 'Club'))
        assert state_after_j.active_suit == 'Club'
        assert state_after_j.wild_suit_change_allowed is True, "Chose same suit so wildcard is NOT locked!"
        
        # P2 plays 8 immediately and CAN change the suit to Heart
        legal_2 = state_after_j.get_legal_actions()
        assert (make_card(8, 'Heart'), 'Heart') in legal_2

    def test_complex_7_wild_stack(self):
        """Test sequence 7 C + 7 H + J H is valid when top card is J with active suit Club."""
        top = make_card('J', 'Spade') # Top is J, active_suit is Club
        c7c = make_card(7, 'Club')
        c7h = make_card(7, 'Heart')
        cjh = make_card('J', 'Heart')
        
        state = CrazyState(
            p1_hand=[c7c, c7h, cjh],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={},
            discard_pile=[top],
            current_player=1,
            active_suit='Club'
        )
        legal = state.get_legal_actions()
        # Combo (c7c, c7h, cjh) should be in legal
        found = False
        for action in legal:
            if len(action) == 3 and all(isinstance(x, CrazyCard) for x in action):
                ranks = [x.rank for x in action]
                suits = [x.suit for x in action]
                if ranks == [7, 7, 'J'] and suits == ['Club', 'Heart', 'Heart']:
                    found = True
                    break
        assert found, "Combo 7C + 7H + JH should be valid when J changed game to Club"

    def test_mixed_wild_combo_no_suit_change(self):
        """A mixed combo starting with a wildcard (e.g. 8 of Clubs + 9 of Clubs) played on top of a wildcard inherits the active suit instead of changing to Club."""
        top = make_card('J', 'Spade') # Active suit is Diamond (changed by previous player's J)
        c8c = make_card(8, 'Club')
        c9c = make_card(9, 'Club')
        
        state = CrazyState(
            p1_hand=[c8c, c9c],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={},
            discard_pile=[top],
            current_player=1,
            active_suit='Diamond',
            wild_suit_change_allowed=False # Already locked!
        )
        
        # P1 plays 8 of Clubs + 9 of Clubs
        res = state.apply_action((c8c, c9c))
        assert res.active_suit == 'Diamond', f"Expected active suit to remain Diamond, but got {res.active_suit}"

    def test_joker_play_chooses_suit(self):
        """Test playing Joker at the start (empty discard) chooses a valid active suit (Diamond) or defaults to Spade (never Joker)."""
        joker1 = make_card(0, 'Joker')
        joker2 = make_card(0, 'Joker')
        
        # Start game: P1 has Joker. Discard is empty.
        state = CrazyState([joker1], [make_card(3, 'Club')], {}, [], current_player=1)
        
        # 1. P1 plays Joker and chooses Diamond
        res1 = state.apply_action((joker1, 'Diamond'))
        assert res1.active_suit == 'Diamond'
        
        # 2. P1 plays double Joker (which prevents suit change due to stacking).
        # It must fallback to Spade instead of 'Joker'
        state_double = CrazyState([joker1, joker2], [make_card(3, 'Club')], {}, [], current_player=1)
        res2 = state_double.apply_action((joker1, joker2))
        assert res2.active_suit == 'Spade'

class TestDeckReshuffle:
    def test_reshuffle_possible_when_discard_gt_1(self):
        top   = make_card(4, 'Spade')
        state = CrazyState(
            p1_hand=[make_card(9, 'Heart')],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={},  # Empty deck
            discard_pile=[make_card(7, 'Spade'), top],
            current_player=0,
            player_to_draw=1
        )
        assert state._can_reshuffle()

    def test_reshuffle_not_possible_when_only_one_card_in_discard(self):
        top   = make_card(4, 'Spade')
        state = CrazyState(
            p1_hand=[make_card(9, 'Heart')],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={},
            discard_pile=[top],  # Only the top card
            current_player=0,
            player_to_draw=1
        )
        assert not state._can_reshuffle()

    def test_reshuffle_happens_on_draw_when_deck_empty(self):
        discard = [make_card(7, 'Heart'), make_card(4, 'Spade')]
        state = CrazyState(
            p1_hand=[make_card(9, 'Heart')],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={},
            discard_pile=discard,
            current_player=0,
            player_to_draw=1
        )
        outcomes = state.get_chance_outcomes()
        # The discard 7♥ should be the only card available
        assert len(outcomes) > 0
        assert any(c is not None for c, p in outcomes)

    def test_is_not_terminal_when_reshuffle_possible(self):
        top   = make_card(4, 'Spade')
        other = make_card(7, 'Heart')
        state = CrazyState(
            p1_hand=[make_card(9, 'Heart')],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={},
            discard_pile=[other, top],
            current_player=0,
            player_to_draw=1
        )
        assert not state.is_terminal()

class TestTerminal:
    def test_p1_wins_when_hand_empty(self):
        top = make_card(4, 'Spade')
        state = make_state([], [make_card(3, 'Club')], top)
        assert state.is_terminal()
        assert state.get_utility(1) == 1000.0
        assert state.get_utility(2) == -1000.0

    def test_p2_wins_when_hand_empty(self):
        top = make_card(4, 'Spade')
        state = make_state([make_card(9, 'Heart')], [], top)
        assert state.is_terminal()
        assert state.get_utility(2) == 1000.0
        assert state.get_utility(1) == -1000.0

    def test_not_terminal_with_cards(self):
        top = make_card(4, 'Spade')
        state = make_state([make_card(4, 'Heart')], [make_card(3, 'Club')], top)
        assert not state.is_terminal()


class TestJustDrew:
    def test_after_draw_player_can_play_or_pass(self):
        """After drawing a card, the player should get a chance to play it."""
        top     = make_card(4, 'Spade')
        new_4h  = make_card(4, 'Heart')  # A card that matches the top card
        state = CrazyState(
            p1_hand=[make_card(9, 'Club')],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={new_4h: 1},
            discard_pile=[top],
            current_player=0,
            player_to_draw=1
        )
        # Apply the draw action
        new_state = state.apply_action(new_4h)
        # Should still be P1's turn with just_drew=True
        assert new_state.current_player == 1
        assert getattr(new_state, 'just_drew', False) is True
        legal = new_state.get_legal_actions()
        assert ('PASS_TURN',) in legal, "Player should be able to pass after drawing"

    def test_pass_turn_ends_turn(self):
        top   = make_card(4, 'Spade')
        state = CrazyState(
            p1_hand=[make_card(9, 'Club')],
            p2_hand=[make_card(3, 'Club')],
            deck_counts={},
            discard_pile=[top],
            current_player=1,
        )
        state.just_drew = True
        new_state = state.apply_action(('PASS_TURN',))
        assert new_state.current_player == 2
        assert not getattr(new_state, 'just_drew', False)
