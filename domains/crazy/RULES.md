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
* You must **Draw** a card from the deck.
* **Post-Draw Play Option**: If the drawn card is a valid play, you can play it immediately. Otherwise, you must choose **Pass Turn** to yield.

---

## 3. Special Card Abilities

### ✦ Wildcards (`8`, `J`, `Joker`)
* Can be played on **any** card regardless of suit/rank.
* Allows the player to choose a new **Active Suit** (Spade, Heart, Diamond, or Club).
* **Stacking Wildcards Exception**: If a wildcard is played immediately on top of another wildcard, it inherits the active suit and **cannot** change it, **unless** the first wildcard chose the *same* suit as the active suit before it was played. If it didn't change the suit, the second wildcard CAN change the suit.

### ✦ Draw Penalties
These cards force the opponent to draw cards:
* **`2`**: Opponent draws **2 cards**.
* **`7`**: Opponent draws **1 card** (only when played solo or in a rank combo of 7s).
* **`Ace of Spades` (A♠)**: Opponent draws **5 cards**.
* **`Joker`**: Opponent draws **7 cards**.

### ✦ Skips (`5`)
* Automatically forces the opponent to skip their turn.
* **Non-cancelable**: The skipped player does not get a turn to react or draw; the turn automatically passes.

---

## 4. Multi-Card Combos & Stacking
You can play multiple cards in a single turn in three ways:

### A. Rank Combos
Play multiple cards of the same rank:
* **Example**: Playing `4♠ + 4♥` on a Spade.
* **Example**: Playing `2♣ + 2♥ + 2♠ + 2♦` (draw penalty stacks to **8**!).

### B. 7-Suit Combos
A `7` can start a suit run. Play a `7` first, followed by any other cards of that same suit:
* **Example**: Playing `7♥ + 8♥ + 9♥` on a Heart.
* **Example**: Playing `7♠ + 2♠` (causes opponent to draw **2** because 7 doesn't contribute penalty in suit combos).

### C. Transition Combos (7-Rank to 7-Suit)
A rank combo of 7s allows you to transition into a suit run of the last 7's suit:
* **Example**: playing `7♦ + 7♥ + 8♥ + 9♥` on a Diamond. The `7♦` is played on Diamond rank/suit, the `7♥` rank-matches it, and then starts a Hearts run!
* **Example**: playing `7♥ + 7♠ + 7♣ + 8♣ + 9♣` on a Heart.

---

## 5. Defense & Penalty Stacking
If you are attacked by a draw penalty (e.g., +2 draws pending):
* You do **not** have to draw immediately.
* You can **Counter** by playing your own draw-penalty card(s) to stack and pass the penalty to your opponent.
* **Defense Counter Restrictions**:
  * Only cards with draw penalties (`2`, `7`, `A♠`, and `Joker`) can be played as defense counters. Wildcards `8` and `J` **cannot** be used to counter since they have no draw penalty.
  * Counter combos must consist **entirely of cards of the same rank** (e.g., all `2`s, all `7`s, all `Jokers`, or a single `A♠`). Mixed/stacked suit combos (e.g., `7♥ + 2♥` or `7♥ + 3♥ + 4♥ + 6♥ + 2♥`) **cannot** be played as defense counters.
* The penalty of a played combo is calculated by summing the contiguous run of matching penalty cards starting from the top (last card played) of the sequence.

### Examples of Penalty Stacking:
* **`7♥ + 2♥`**: The top card is `2`. The penalty is **2** (the 7 does not contribute).
* **`7♥ + 2♥ + 2♦`**: The top card is `2` and the second card is `2`. Both are 2s. The penalty is **4**.
* **`7♠ + 4♠ + 2♠`**: The top card is `2`. The card before it is `4` (non-penalty), which stops the stack. The penalty is **2**.
* **`7♠ + 2♠ + 4♠`**: The top card is `4` (non-penalty). The penalty is **0**.
* **`Joker + Joker`**: The penalty is **14**.
