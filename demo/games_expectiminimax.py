import random
from domains.crazy.CrazyCard import create_deck
from domains.crazy.CrazyState import CrazyState
from games.Expectiminimax import ExpectiminimaxSolver

def test_determinization():
    print("=== 'Crazy' Card Game: Expectiminimax via Determinization ===\n")
    
    # 1. Setup the true game state
    full_deck = create_deck()
    random.shuffle(full_deck)
    
    p1_hand = [full_deck.pop() for _ in range(5)]
    p2_hand = [full_deck.pop() for _ in range(6)] # P2 goes first
    discard = [full_deck.pop()]
    
    # Deck counts representation (what the AI knows)
    deck_counts = {}
    for c in full_deck:
        deck_counts[c] = deck_counts.get(c, 0) + 1
        
    state = CrazyState(p1_hand, p2_hand, deck_counts, discard, current_player=2)
    
    print("Opponent's True Hand (Hidden from AI):", state.p2_hand)
    print("AI's Hand:", state.p1_hand)
    print("Top Card:", state.discard_pile[-1])
    
    # AI wants to find the best move, but it doesn't know p2_hand.
    # We create a Deterministic World by sampling a random hand for P2 from the unknown cards.
    
    print("\nAI is determinizing the world by guessing the opponent's hand...")
    
    # All unknown cards: P2's hand + Deck
    unknown_cards = p2_hand + full_deck
    
    # Sample a hand
    random.shuffle(unknown_cards)
    guessed_p2_hand = unknown_cards[:6]
    guessed_deck = unknown_cards[6:]
    
    guessed_deck_counts = {}
    for c in guessed_deck:
        guessed_deck_counts[c] = guessed_deck_counts.get(c, 0) + 1
        
    guessed_state = CrazyState(p1_hand, guessed_p2_hand, guessed_deck_counts, discard, current_player=1) # AI is P1
    
    solver = ExpectiminimaxSolver(max_depth=3)
    best_move = solver.get_best_action(guessed_state)
    
    print(f"\nAI (Expectiminimax) explored {solver.nodes_expanded} nodes in the determinized world.")
    print(f"AI chose to play: {best_move}")
    
    if best_move == ["DRAW_FROM_DECK"]:
        print("AI had no valid moves and decided to draw from the CHANCE deck.")

def main():
    test_determinization()

if __name__ == "__main__":
    main()
