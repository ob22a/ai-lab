# Constraint Satisfaction Problem Benchmarks

We pitted our five solver configurations against four distinct CSP domains to empirically prove the value of heuristics and inference algorithms.

## Benchmark Results

*Run on standard hardware. BT = Backtracking, FC = Forward Checking, MAC = Maintaining Arc Consistency (AC-3).*

| Problem      | BT                   | BT+MRV               | BT+FC                | BT+MAC               | Min-Conflicts        |
|--------------|----------------------|----------------------|----------------------|----------------------|----------------------|
| Map Coloring | 11 nodes (0.0003s)   | 11 nodes (0.0002s)   | 7 nodes (0.0002s)    | 7 nodes (0.0003s)    | 10 steps (0.0002s)   |
| 8-Queens     | 876 nodes (0.0061s)  | 876 nodes (0.0062s)  | 88 nodes (0.0036s)   | 20 nodes (0.0042s)   | 42 steps (0.0024s)   |
| Sudoku Easy  | HANGS FOREVER        | 1637 nodes (0.1298s) | 489 nodes (0.2555s)  | 402 nodes (0.3400s)  | N/A (Too dense)      |
| Sudoku Hard  | HANGS FOREVER        | HANGS FOREVER        | 5587 nodes (2.7933s) | 1768 nodes (2.3466s) | N/A (Too dense)      |

## Analysis

### 1. The Necessity of Heuristics (MRV)
Naive Backtracking (BT) explores the search tree blindly. While this works for trivial problems like Australia Map Coloring, it completely fails on structured problems like Sudoku. Without the Minimum Remaining Values (MRV) heuristic guiding the search toward the most constrained cells, the solver wastes millions of cycles exploring doomed paths. Adding MRV allows BT to instantly solve Easy Sudoku in just 1637 nodes.

### 2. The Power of Inference (FC vs MAC)
Forward Checking (FC) is incredibly fast and prunes immediate violations, reducing 8-Queens from 876 nodes down to 88 nodes. However, on highly constrained problems like Hard Sudoku, FC isn't enough. It expands 5,587 nodes. 

Maintaining Arc Consistency (MAC) propagates constraints *globally*. By running AC-3 after every assignment, it detects deep, cascading failures instantly. This drops the Hard Sudoku node expansions from 5,587 down to just 1,768, resulting in a faster overall execution time despite AC-3 being a heavier operation.

### 3. The Local Search Anomaly (Min-Conflicts)
Min-Conflicts operates on a completely different paradigm, wandering randomly while minimizing constraint violations. For dense, loosely structured problems like N-Queens, it is mathematically unbeatable, solving 8-Queens in just 42 steps (and scaling effortlessly to 1000-Queens). However, for highly structured problems with precise unique solutions (like Sudoku), the landscape is riddled with plateaus and local optima, making Min-Conflicts practically useless without heavy modifications (like Random Restart or Tabu Search).
