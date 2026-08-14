"""
crazy_demo.py
Demo runner for the 'Crazy' card game visualizer.

Usage:
    python -m demo.crazy_demo

Controls (in-game):
    Click cards in your hand  → select / deselect for a combo
    PLAY SELECTED button      → play the selected cards
    DRAW FROM DECK button     → draw a card
    LEFT / RIGHT              → step through move history
    SPACE                     → toggle AI auto-play
    R                         → restart
    ESC                       → exit
"""

import random
from domains.crazy.CrazyCard import create_deck, CrazyCard
from domains.crazy.CrazyState import CrazyState
from games.MCTS import InformationSetMCTSSolver
from domains.crazy.CrazyState import determinize_crazy_state
from games.RandomSolver import RandomSolver
from games.heuristics.ObssaHeuristic import ObssaHeuristicSolver
from visualization.CrazyVisualizer import CrazyVisualizer


# ─────────────────────────────────────────────────────────────────────────────
# Deck helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_full_deck_state(p1_cards: int = 5, p2_cards: int = 6) -> CrazyState:
    """Standard 54-card deck (52 + 2 Jokers). P2 starts with 6 cards and goes first.
    The game starts with an EMPTY discard pile – P2 must play any card to open.
    """
    deck = create_deck()
    random.shuffle(deck)

    p1_hand = [deck.pop() for _ in range(p1_cards)]
    p2_hand = [deck.pop() for _ in range(p2_cards)]

    deck_counts: dict = {}
    for c in deck:
        deck_counts[c] = deck_counts.get(c, 0) + 1

    # P2 has 6 cards and goes first; empty discard – any card is a valid opening play
    return CrazyState(p1_hand, p2_hand, deck_counts, [], current_player=2)


def make_simplified_deck_state(p1_cards: int = 5, p2_cards: int = 6) -> CrazyState:
    """
    Reduced deck (only ranks 7–A for 2 suits: Spade and Heart, plus both Jokers).
    Produces a smaller deck faster for AlphaBeta / deep search.
    P2 goes first with an empty discard – any card is valid as the opening play.
    """
    suits = ['Spade', 'Heart']
    ranks = [7, 8, 9, 10, 'J', 'Q', 'K', 'A']
    deck  = [CrazyCard(r, s) for s in suits for r in ranks]
    deck += [CrazyCard(0, 'Joker'), CrazyCard(0, 'Joker')]
    deck += [CrazyCard(2, 'Spade'), CrazyCard(2, 'Heart')]
    deck += [CrazyCard(5, 'Spade'), CrazyCard(5, 'Heart')]
    random.shuffle(deck)

    p1_hand = [deck.pop() for _ in range(p1_cards)]
    p2_hand = [deck.pop() for _ in range(p2_cards)]

    deck_counts: dict = {}
    for c in deck:
        deck_counts[c] = deck_counts.get(c, 0) + 1

    # P2 goes first with empty discard
    return CrazyState(p1_hand, p2_hand, deck_counts, [], current_player=2)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  CRAZY CARD GAME  –  AI Lab")
    print("=" * 60)

    # ── Choose agents ─────────────────────────────────────────────────────
    # Player 1 is YOU (human).  Change to MCTSSolver() to watch AI vs AI.
    # p1 = "HUMAN"
    p1 = ObssaHeuristicSolver()

    # Player 2 is the AI.  Change num_simulations / algorithm as desired.
    # IS-MCTS required: Crazy has hidden information (opponent's hand is unknown)
    p2 = InformationSetMCTSSolver(determinize_crazy_state, num_simulations=200)
    # For a weaker / faster AI:
    # p2 = RandomSolver()

    # ── Choose deck ───────────────────────────────────────────────────────
    # Full 54-card deck (standard game)
    initial_state = make_full_deck_state()  # p1=5 cards, p2=6 cards, p2 goes first

    # Simplified deck (faster for strong AI like AlphaBeta):
    # initial_state = make_simplified_deck_state()  # p1=5, p2=6

    # ── Human side (1 = bottom, 2 = top) ─────────────────────────────────
    human_player = 1

    print(f"P1: {'YOU' if p1 == 'HUMAN' else p1.__class__.__name__}")
    print(f"P2: {p2.__class__.__name__}")
    print(f"Deck size: {sum(initial_state.deck_counts.values())} cards in deck")
    print(f"P1 hand: {len(initial_state.p1_hand)} cards")
    print(f"P2 hand: {len(initial_state.p2_hand)} cards")
    print()

    vis = CrazyVisualizer(
        initial_state=initial_state,
        player1=p1,
        player2=p2,
        human_player=human_player,
        fps=30
    )
    vis.run()
    
    try:
        from utils.auto_logger import auto_log_game
        if vis.state.is_terminal():
            winner = vis.state.get_winner()
            p1_name = "HUMAN" if p1 == "HUMAN" else p1.__class__.__name__
            p2_name = "HUMAN" if p2 == "HUMAN" else p2.__class__.__name__
            auto_log_game("crazy", p1_name, p2_name, winner, getattr(vis, "elapsed_time", 0.0))
    except Exception:
        pass


if __name__ == "__main__":
    main()
