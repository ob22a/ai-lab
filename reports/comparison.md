# Algorithm Comparison & Advanced Theoretical Analysis

This document provides a deep-dive analysis into the performance tradeoffs observed in the benchmark results. Rather than focusing on standard textbook definitions, we explore the nuanced, advanced architectural behaviors of these AI paradigms.

## 1. Classical Search & Memory-Time Tradeoffs

### Defining Difficulty (Easy, Medium, Hard)
In our sliding-tile benchmarks (8-Puzzle and 15-Puzzle), difficulty is defined by the number of random valid moves applied to the solved goal state to generate the initial state:
- **Easy:** ~10-14 random moves.
- **Medium:** 18 moves (8-puzzle) or 25 moves (15-puzzle).
- **Hard:** 26 moves (8-puzzle) or 45 moves (15-puzzle).

*Note on the "Hard vs Medium" Anomaly:* You may notice in the `15-Puzzle Scaling` charts that some algorithms unexpectedly solved the "Hard" (45-move) instances faster than the "Medium" (25-move) instances. This happens for two reasons:
1. **Random Walk Cancellation:** Generating puzzles via purely random moves means a 45-move walk can backtrack on itself (e.g., UP then DOWN), resulting in an actual optimal solution depth that is much shorter than 45. 
2. **Heuristic Plateaus:** A Medium puzzle might land the board in a state space "plateau" where the heuristic values of all neighboring states are identical. The search algorithm is forced to explore a massive, dense tree to break the tie. A Hard puzzle might land in a state where the Pattern Database heuristic has a steep, perfect gradient pointing directly back to the goal, requiring zero tie-breaking and resulting in instant solves.

### A* vs IDA* (The Priority Queue Overhead)
A common misconception is that A* is universally faster than Iterative Deepening A* (IDA*) because IDA* redundantly explores upper levels of the search tree. However, our benchmarks on the **8-Puzzle** vs **15-Puzzle** reveal a fascinating inflection point:
- **8-Puzzle (Small State Space):** A* is slightly faster than IDA*. The total state space is small enough ($3.6 \times 10^5$) that A*'s `OpenSet` (a Priority Queue) remains relatively small. The overhead of $O(\log N)$ insertions is minimal, making A*'s single-pass exploration highly efficient.
- **15-Puzzle (Massive State Space):** IDA* entirely dominates A*. The 15-puzzle has over $10^{13}$ states. As A* searches, the Priority Queue and Closed Set (Hash Map) grow exponentially. The memory allocation overhead, cache misses, and massive $O(\log N)$ queue balancing operations slow A* to a crawl, often leading to RAM exhaustion. **IDA***, conversely, acts as a bounded Depth-First Search. It requires *zero* complex data structures—just a recursive call stack. Its memory footprint is strictly $O(d)$ (linear). Because the heuristic (Pattern Database) is so strong, the number of redundant expansions in IDA* is vastly outweighed by the sheer speed of raw call-stack traversal without Priority Queue overhead.

### The IDDFS Redundancy Trap
Iterative Deepening DFS (IDDFS) theoretically combines the optimality of BFS with the memory efficiency of DFS. It is the only way to do uninformed search on deep trees. However, **the memory vs. time tradeoff in IDDFS is highly sensitive to the branching factor ($b$)**. 
- In games or puzzles with high branching factors (e.g., $b \ge 3$), the bottom layer of the tree contains more nodes than all previous layers combined. The redundant regeneration of the upper tree is a negligible constant factor overhead (e.g., ~30% slower).
- **In Mazes (Low Branching Factor):** Mazes often consist of long, narrow corridors where $b \approx 1$. In these domains, the tree does not grow exponentially. IDDFS is forced to repeatedly re-traverse the exact same long paths from scratch for every depth increment $d$. This causes the time complexity to degrade to $O(d^2)$, making IDDFS catastrophically slow on Mazes compared to BFS, which just pays the linear memory cost.

---

## 2. The Power of Pattern Databases (PDBs)

The quality of an informed search is entirely bottlenecked by its heuristic function $h(n)$. The benchmarks on the sliding tile puzzles demonstrate the dramatic scalability differences between heuristic architectures:
- **Misplaced Tile:** Extremely weak. It considers tiles independently and ignores the distance they must travel. It fails to prune the search tree effectively, resulting in massive node expansions.
- **Manhattan Distance:** Better, as it calculates the $x/y$ distance for each tile. However, it still assumes tiles can move through each other (ignores tile collisions).
- **Disjoint Pattern Databases (PDB):** PDBs represent a paradigm shift. Instead of a mathematical formula, we run a pre-computation step (using reverse BFS from the goal) to find the *exact* optimal cost to align a specific subset of tiles (e.g., tiles 1-7). By storing these exact costs in a massive lookup table, and adding disjoint subsets together, we get an incredibly tight admissible bound. The benchmarks show that PDBs reduce the nodes expanded by **orders of magnitude**, shrinking the effective branching factor to near $1.0$ and allowing complex 15-puzzle instances to be solved in milliseconds.

---

## 3. Constraint Satisfaction (CSP) Advanced Inference

In CSPs, the goal is to fail as fast as possible. 
- **MRV (Minimum Remaining Values):** This dynamic variable ordering heuristic always selects the most constrained variable. If a variable has only 1 legal value left, MRV forces the solver to assign it immediately, cascading constraints to neighbors.
- **Forward Checking (FC) vs MAC (Maintaining Arc Consistency):**
  - **FC** only looks one step ahead, removing illegal values from unassigned neighbors.
  - **MAC** (using the AC-3 algorithm) runs a full graph consistency check after *every* assignment. While MAC detects unsolvable sub-trees much earlier than FC, the overhead of managing the AC-3 queue at every node is high. Our benchmarks on Sudoku show that for **Easy** puzzles, FC is faster because the overhead of MAC isn't justified. But for **Hard** Sudoku with sparse clues, MAC is strictly required to prevent the solver from thrashing for hours in invalid states.

---

## 4. Adversarial Game Search

- **Alpha-Beta Pruning & Move Ordering:** Alpha-Beta is only as good as its move ordering. If the best move is evaluated first, Alpha-Beta prunes the remaining branches, doubling the effective search depth. Our engines use Iterative Deepening to seed the next depth's move order, combined with a History Heuristic, ensuring near-optimal $O(b^{d/2})$ performance.
## 5. Summary: Which Algorithm Should I Use?

Based on the empirical evidence in our benchmark reports, here is the definitive guide to algorithm selection within this framework:

- **For Small/Medium Puzzles (8-Puzzle):** Use **A*** with a Pattern Database. The priority queue overhead is negligible, and it avoids IDA*'s redundant expansions.
- **For Massive Puzzles (15-Puzzle):** Use **IDA*** with a Pattern Database. The strict linear memory requirement completely bypasses the catastrophic RAM and Priority Queue slowdowns that cripple standard A*.
- **For Mazes / Pathfinding:** Use **BFS** or **Bidirectional BFS** if uniformed, or **A*** (Manhattan) if informed. Avoid IDDFS entirely, as the low branching factor of mazes ($b \approx 1$) causes IDDFS to thrash in $O(d^2)$ time.
- **For TSP / N-Queens:** Use **Simulated Annealing (SA)** or **Genetic Algorithms (GA)**. Standard Hill Climbing gets trapped in local optima too easily. GA is particularly powerful for TSP when using edge-recombination (OX1) crossover.
- **For Sudoku / CSPs:** Use **Backtracking + MRV + MAC (AC-3)**. While MAC adds overhead per node, it drastically reduces the overall tree size, making it the only algorithm capable of solving "Hard" Sudoku instances in a reasonable time.
- **For Zero-Sum Games:** Use **Alpha-Beta Pruning** with Iterative Deepening move-ordering. For games with massive branching factors or complex evaluations (like Connect Four), **MCTS** provides a robust alternative that doesn't rely on handcrafted heuristics.
- **For Hidden-Information Games (Crazy):** Use **IS-MCTS** (Information-Set MCTS), as it elegantly handles hidden state by determinizing hands during simulations.
