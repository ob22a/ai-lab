import random
from domains.crazy.CrazyCard import create_deck
from domains.crazy.CrazyState import CrazyState
from games.MCTS import InformationSetMCTSSolver

def determinize_crazy(state: CrazyState) -> CrazyState:
    """
    Creates a Determinized Universe from a hidden state.
    We know: our hand (p1), the discard pile, and the deck counts.
    We do NOT know: the exact cards in the opponent's hand.
    We shuffle all unknown cards, deal the correct number to the opponent,
    and leave the rest in the deck counts.
    """
    unknown_cards = []
    
    # In a real game, the AI would track exactly what cards it has seen.
    # For this demo, we extract the unknown cards directly from the deck_counts
    # because deck_counts currently holds the entire remaining universe of cards.
    for card, count in state.deck_counts.items():
        for _ in range(count):
            unknown_cards.append(card)
            
    # The opponent's true hand is technically hidden, but we know HOW MANY cards they have.
    opp_hand_size = len(state.p2_hand)
    
    # Also add the true opponent hand to the unknown pool (since the AI doesn't know them)
    for c in state.p2_hand:
        unknown_cards.append(c)
        
    random.shuffle(unknown_cards)
    
    guessed_opp_hand = unknown_cards[:opp_hand_size]
    guessed_deck = unknown_cards[opp_hand_size:]
    
    # Rebuild the deck counts
    new_deck_counts = {}
    for c in guessed_deck:
        new_deck_counts[c] = new_deck_counts.get(c, 0) + 1
        
    return CrazyState(
        p1_hand=list(state.p1_hand),
        p2_hand=guessed_opp_hand,
        deck_counts=new_deck_counts,
        discard_pile=list(state.discard_pile),
        current_player=state.current_player,
        active_suit=state.active_suit,
        player_to_draw=state.player_to_draw,
        pending_draws=state.pending_draws,
        turn_skipped=state.turn_skipped
    )

def test_mcts_crazy():
    print("=== 'Crazy' Card Game: Information Set MCTS ===\n")
    
    full_deck = create_deck()
    random.shuffle(full_deck)
    
    p1_hand = [full_deck.pop() for _ in range(5)]
    p2_hand = [full_deck.pop() for _ in range(6)]
    discard = [full_deck.pop()]
    
    deck_counts = {}
    for c in full_deck:
        deck_counts[c] = deck_counts.get(c, 0) + 1
        
    state = CrazyState(p1_hand, p2_hand, deck_counts, discard, current_player=1)
    
    print("AI's Hand:", state.p1_hand)
    print("Top Card:", state.discard_pile[-1])
    print("\nRunning MCTS (1000 Simulations)...")
    
    # Use IS-MCTS to run 1000 simulations across random determinized worlds
    solver = InformationSetMCTSSolver(determinize_crazy, num_simulations=1000)
    best_move = solver.get_best_action(state)
    
    print(f"Nodes expanded (Simulations): {solver.nodes_expanded}")
    print(f"MCTS chose to play: {best_move}")

def main():
    test_mcts_crazy()

if __name__ == "__main__":
    main()
