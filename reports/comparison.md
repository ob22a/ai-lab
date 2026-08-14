
# Algorithm Comparison & Theoretical Analysis

This document provides a theoretical explanation of the performance tradeoffs between different AI paradigms implemented in the framework, referencing the empirical data generated in `benchmark_report.md`.

## 1. Classical Search Algorithms (Pathfinding & Puzzles)

When comparing search algorithms on deterministic, fully observable environments like Mazes or N-Puzzle, performance hinges on **completeness**, **optimality**, and **informedness**.

### Uninformed Search Tradeoffs
- **Breadth-First Search (BFS)** vs. **Depth-First Search (DFS)**: 
  BFS is optimal (finds the shortest path) but its memory footprint grows exponentially, often exhausting RAM on large domains like the 15-Puzzle. DFS is memory-efficient (linear space) but frequently dives into deep sub-optimal paths, resulting in significantly higher path costs.
- **Iterative Deepening DFS (IDDFS)**:
  Combines the memory efficiency of DFS with the optimality of BFS. However, the redundant regeneration of upper tree levels creates a massive runtime overhead, making it slower than BFS in shallow graphs but strictly necessary for deep, wide graphs. **Optimized IDDFS** mitigates this overhead by avoiding full frontier resets across depth limits, acting effectively as a memory-bounded breadth-first exploration, drastically improving times on standard problems like Mazes or 8-puzzle.
- **Bidirectional Search**:
  By searching simultaneously from start to goal, the time complexity drops from $O(b^d)$ to $O(b^{d/2})$. The benchmarks show this is vastly superior to standard BFS on large mazes, though implementing the frontier intersection correctly is complex.

### Informed Search & Heuristics
- **A* vs Greedy Best-First Search (GBFS)**:
  GBFS relies entirely on the heuristic $f(n) = h(n)$, expanding nodes extremely quickly toward the goal but often getting trapped by obstacles, resulting in sub-optimal paths. A* balances path cost and heuristic $f(n) = g(n) + h(n)$, guaranteeing the optimal path at the cost of significantly higher node expansion (memory overhead).
- **Heuristic Quality (Misplaced vs Manhattan vs Pattern Database)**:
  The 8-Puzzle benchmarks clearly demonstrate the value of informed heuristics. **Misplaced Tiles** provides a weak bound, resulting in huge tree expansions. **Manhattan Distance** tightens the bound significantly. **Disjoint Pattern Databases (PDB)** provide the tightest admissible bound by precomputing sub-problem costs, drastically reducing A* node expansion to near-linear times at the cost of precomputation memory.
- **Memory-Bounded Variants (IDA*, SMA*)**:
  A* struggles with memory exhaustion on the 15-Puzzle. IDA* relies on depth limits derived from the f-cost rather than tree depth, allowing optimal search with linear memory. SMA* limits the frontier queue size and drops the worst nodes, making it practical for massive state spaces.

---

## 2. Local Search & Optimization (TSP & N-Queens)

Local search discards systematic exploration in favor of iterative improvement, making it the only viable choice for massive, continuous, or un-navigable state spaces.

- **Hill Climbing**:
  Highly susceptible to local optima. On N-Queens and TSP, standard hill climbing frequently stalls at a sub-optimal plateau. Random restarts (Stochastic Hill Climbing) alleviate this but don't guarantee optimality.
- **Simulated Annealing (SA)**:
  By allowing "worse" moves early in the search (controlled by the temperature parameter), SA successfully escapes the local minima that trap Hill Climbing. The benchmarks show SA reliably finding optimal or near-optimal solutions, provided the cooling schedule is slow enough.
- **Genetic Algorithms (GA) vs Local Beam Search**:
  GA relies on recombination (crossover) to jump across the state space, maintaining diversity. Local Beam Search maintains $k$ parallel states but doesn't recombine them. GA generally outperforms Beam Search on TSP because edge-recombination (OX1 crossover) preserves sub-tours effectively, whereas Beam Search often collapses to $k$ variations of the same local optimum.

---

## 3. Constraint Satisfaction Problems (CSP)

CSP solvers focus on assignment validity rather than path-finding, making inference and variable ordering critical.

- **Naive Backtracking**:
  Explores the state space blindly, failing catastrophically on dense problems like Hard Sudoku or the 8-Queens puzzle due to extreme thrashing.
- **Variable Ordering (MRV & Degree Heuristic)**:
  The **Minimum Remaining Values (MRV)** heuristic dynamically selects the most constrained variable, forcing failures early and pruning massive branches of the search tree. The Degree Heuristic breaks MRV ties by selecting variables involved in the most constraints, further improving early failure detection.
- **Inference (Forward Checking vs MAC)**:
  **Forward Checking (FC)** removes illegal values from unassigned neighbors after an assignment, catching failures one step ahead. **Maintaining Arc Consistency (MAC)** enforces full graph consistency (AC-3) after every step. While MAC prunes the most nodes (often solving Easy Sudoku without any backtracking), the computational overhead of running AC-3 at every node makes it slower than FC on simpler or sparse graphs.
- **Advanced Solvers (Cycle Cutset & Tree Decomposition)**:
  For nearly tree-structured graphs, Cycle Cutset isolates the cycles, reducing the problem to an acyclic graph solvable in $O(n d^2)$ time. This is vastly superior to standard backtracking for sparsely connected map coloring domains.

---

## 4. Adversarial Games

In zero-sum games, the challenge is modeling the opponent's optimal play within strict time bounds.

- **Minimax vs Alpha-Beta Pruning**:
  Minimax explores the entire game tree, which is impossible for anything beyond Tic-Tac-Toe. Alpha-Beta pruning eliminates branches that cannot affect the final decision, effectively doubling the solvable search depth in the same time frame.
- **Move Ordering**:
  Alpha-Beta's efficiency depends entirely on move ordering. By employing iterative deepening and history heuristics, `AlphaBetaOrderedSolver` evaluates the strongest moves first, maximizing cutoffs and achieving significantly deeper searches than naive Alpha-Beta.
- **Monte Carlo Tree Search (MCTS)**:
  Unlike Alpha-Beta, which requires a handcrafted evaluation function, MCTS relies on stochastic playouts. This makes it highly effective for games with massive branching factors or complex state evaluations (like Connect Four or Othello). However, without depth penalties, pure MCTS can struggle to prioritize immediate wins over guaranteed delayed wins, requiring careful tuning of the exploration constant and simulation counts.
- **Information-Set MCTS (IS-MCTS)**:
  For hidden-information games like the Crazy card game, standard solvers fail because they assume perfect information. IS-MCTS addresses this by determinizing (randomly guessing) the opponent's hidden cards at each simulation step, allowing MCTS to reason probabilistically about the opponent's hand.
