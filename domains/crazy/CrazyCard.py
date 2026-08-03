class CrazyCard:
    """
    Represents a playing card for the game 'Crazy'.
    Suits: 'Spade', 'Heart', 'Diamond', 'Club', 'Joker'
    Ranks: 2-10, 'J', 'Q', 'K', 'A', 0 (for Joker)
    """
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        if not isinstance(other, CrazyCard):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    def is_wild(self):
        """Returns True if the card can be played at any time and changes the suit."""
        return self.rank in {0, 8, 'J'}

    def get_draw_penalty(self):
        """Returns the number of cards this card forces the opponent to draw."""
        if self.rank == 0:
            return 7
        elif self.rank == 'A' and self.suit == 'Spade':
            return 5
        elif self.rank == 2:
            return 2
        elif self.rank == 7:
            return 1
        return 0

    def skips_turn(self):
        """Returns True if the card forces the opponent to skip their turn."""
        return self.rank == 5

    def __str__(self):
        return f"{self.rank} of {self.suit}"
        
    def __repr__(self):
        return self.__str__()

def create_deck():
    """Generates a standard 54-card deck (52 standard + 2 Jokers)."""
    suits = ['Spade', 'Heart', 'Diamond', 'Club']
    ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
    deck = []
    
    for suit in suits:
        for rank in ranks:
            deck.append(CrazyCard(rank, suit))
            
    deck.append(CrazyCard(0, 'Joker'))
    deck.append(CrazyCard(0, 'Joker'))
    
    return deck
