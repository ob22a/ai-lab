# Rules of 'Crazy' Card Game

Welcome to **Crazy**, a premium tactical card game played with a standard 54-card deck (52 cards + 2 Jokers).

---

## 1. Game Setup & Objective
* **Player 1**: Starts with **5 cards**.
* **Player 2 (AI)**: Starts with **6 cards** and goes first.
* **Objective**: Be the first player to empty your hand.
* **Game Start**: The discard pile is initially **empty**. The first player (P2) can play **any card** to open the game.

---

## 2. Basic Matching Rules
On your turn, you must play a card (or a combo of cards) matching the top card of the discard pile by:
1. **Rank** (e.g., playing a 4 on a 4)
2. **Suit** (e.g., playing a Spade on a Spade)
3. **Active Suit** (if the suit was changed by a Wildcard)

If you cannot make a valid move:
* You must **Draw** a card from the deck. The drawn card is placed at the rightmost end of your hand.
* **Post-Draw Play Option**: If the drawn card is a valid play, you can play it immediately. Otherwise, you must choose **Pass Turn** to yield.

---

## 3. Special Card Abilities

### ✦ Wildcards (`8`, `J`, `Joker`)
* Can be played on **any** card regardless of suit/rank as a solo move or at the start of a combo.
* Allows the player to choose a new **Active Suit** (Spade, Heart, Diamond, or Club).
* **Wildcard Chaining Restriction**: Wildcards cannot be played together on their own (e.g., `8 + J + Joker` without matching ranks or a 7 is illegal). Wildcards only gain "play anywhere" status when starting a move or when embedded inside a 7-suit chain.
* **Stacking Wildcards Exception**: If a wildcard is played immediately on top of another wildcard, it inherits the active suit and **cannot** change it, **unless** the first wildcard chose the *same* suit as the active suit before it was played.

### ✦ Draw Penalties
These cards force the opponent to draw cards:
* **`2`**: Opponent draws **2 cards**.
* **`7`**: Opponent draws **1 card** (only when played solo or in a rank combo of 7s).
* **`Ace of Spades` (A♠)**: Opponent draws **5 cards**.
* **`Joker`**: Opponent draws **7 cards**.

### ✦ Skips (`5`)
* Automatically forces the opponent to skip their turn.
* When played in a combo with penalty cards (e.g., `7C + 5C + AC + AS`), the draw penalty targets the opponent and forces them to draw cards. Upon finishing the draw, their turn is skipped and control returns to the attacker.

---

## 4. Multi-Card Combos & 7-Chain Rules

You can play multiple cards in a single turn in three ways:

### A. Rank Combos
Play multiple cards of the same rank:
* **Example**: Playing `4♠ + 4♥` on a Spade.
* **Example**: Playing `2♣ + 2♥ + 2♠ + 2♦` (draw penalty stacks to **8**!).
* **Illegal**: `4D + 4S + JS + JD` without a 7 bridging them is **illegal** (mismatched ranks).

### B. 7-Suit Combos & 7-Chains
A `7` at the start of a sequence opens a suit chain.
* **Rules for 7-Chains**:
  1. A 7 starts a suit run. Subsequent cards can match rank or match any 7's suit in the chain.
  2. **Suit Determination in 7-Chains**: When wildcards (`8`, `J`, `Joker`) are embedded in a 7-chain (e.g., `7S + 8C + JH`), they lose their suit-changing power. The game's active suit is determined by the **topmost non-special card** in the combo (e.g., `7S + 8C + JH` results in Spade; `7D + 3D + 3C + 8S + Joker` results in Club).
* **Example**: `7D + 7C + 3C + 3S + 8D + 8S + JC` is valid and results in suit **Spade**.
* **Illegal Sequences**: `6D + 8D` (no 7 to glue), `10S + 8D` (mismatched rank, no 7).

---

## 5. Defense & Penalty Stacking
If you are attacked by a draw penalty (e.g., +2 draws pending):
* You do **not** have to draw immediately.
* You can **Counter** by playing any valid combo that itself produces a net draw penalty target > 0 (e.g., `A♣ + A♠`, `7C + 5C + A♣ + A♠`, or same-rank penalty cards like `2♥ + 2♦`).
* Countering stacks the new penalty on top of the incoming penalty and redirects the combined total to your opponent.
