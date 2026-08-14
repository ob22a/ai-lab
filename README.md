# 🚀 Advanced Agentic AI Framework & Interactive Lab

A state-of-the-art, highly modular Object-Oriented AI framework implemented from scratch in Python. Crafted specifically for **Visual Learners**, researchers, and developers, this repository provides unified abstractions, pluggable solver engines, 100% transparent visualizers, automated benchmarking pipelines, and an interactive **CLI Launcher** (`main.py`) across a vast array of artificial intelligence paradigms.

---

## ⚡ Quick Start

```bash
# Install dependencies
pip install pygame matplotlib numpy

# Launch the interactive CLI menu
python main.py

# Or run any demo directly
python -m demo.maze --algo AStar --vis
python -m demo.local_search_tsp --algo GeneticAlgorithm --vis
python -m demo.crazy_demo
```

---

## 🎮 Unified Interactive Launcher Hub (`main.py`)

Launch the interactive CLI menu to browse and run all **18 supported AI demos**:

```bash
python main.py
```

### Features of the Launcher Hub:
* **Categorized Menu**: Browse demos across **Search**, **Optimization**, **CSP**, and **Adversarial Games** categories.
* **Algorithm Selector**: Each demo supports CLI flags to pick algorithms (A*, BFS, DFS, UCS, IDA*, Hill Climbing, Simulated Annealing, Genetic Algorithm, Backtracking + MRV/MAC, Minimax, AlphaBeta, MCTS, IS-MCTS).
* **Game Modes**: Human vs AI, AI vs AI, Human vs Human.
* **Visualizer Support**: All demos with `--vis` flag launch interactive Pygame visualizers.
* **Dynamic Window Resizing**: Full `pygame.RESIZABLE` support across all visualizers.

---

## 📸 Interactive Visualizer Gallery & Screenshot Showcase

### 🧩 Constraint Satisfaction & Graph Decomposition
| Tree Decomposition (Junction Tree & Separators) | Cycle Cutset Conditioning (Acyclic Tree Subproblem) |
|:---:|:---:|
| ![Tree Decomposition](screenshots/tree_decomposition.png) | ![Cycle Cutset](screenshots/cycle_cutset.png) |

| Sudoku CSP (Backtracking + MRV + MAC) | N-Queens CSP Symmetry Breaking |
|:---:|:---:|
| ![Sudoku CSP](screenshots/sudoku.png) | ![N-Queens CSP](screenshots/n-queens_csp.png) |

### 🧭 Graph & Pathfinding Search
| Maze A* Search (Manhattan / Euclidean) | Online Maze Search (LRTA* Real-Time Learning) |
|:---:|:---:|
| ![Maze A* Search](screenshots/maze-astar.png) | ![LRTA* Online Maze](screenshots/maze_online_lrtastar.png) |

| 8-Puzzle Sliding Tile Search (Disjoint PDBs) | Romanian Map City Routing |
|:---:|:---:|
| ![8-Puzzle Search](screenshots/8-puzzle.png) | ![Romanian Map](screenshots/romanian_map.png) |

| Sokoban Box Pushing Search | Sokoban Solved State |
|:---:|:---:|
| ![Sokoban Search](screenshots/sokoban.png) | ![Sokoban Solved](screenshots/sokoban_solved.png) |

### 📈 Continuous Optimization & Population Solvers
| TSP Genetic Algorithm (Elite Population Inspector) | TSP Simulated Annealing (Distance Progression Curve) |
|:---:|:---:|
| ![TSP Genetic Algorithm](screenshots/tsp_genetic_algorithm.png) | ![TSP Simulated Annealing](screenshots/tsp_simulated_annealing.png) |

| N-Queens Genetic Algorithm (Top Chromosomes) | N-Queens Local Beam Search (k Parallel Beams) |
|:---:|:---:|
| ![N-Queens GA](screenshots/n-queens_genetic_algorithm.png) | ![N-Queens Beam Search](screenshots/n-queens_local_beam_search.png) |

| N-Queens Simulated Annealing | N-Queens Hill Climbing |
|:---:|:---:|
| ![N-Queens SA](screenshots/n-queens_simulated_annealing.png) | ![N-Queens HC](screenshots/n_queens_hill_climbing.png) |

### 🎮 Adversarial Game Theory & Card Games
| Crazy Card Game (Information Set MCTS vs Obssa's Heuristic) | Othello / Reversi (Alpha-Beta Pruning) |
|:---:|:---:|
| ![Crazy Card Game](screenshots/crazy_card_game.png) | ![Othello Reversi](screenshots/othello.png) |

| Connect Four (Alpha-Beta Search) | Tic-Tac-Toe (Minimax Search) |
|:---:|:---:|
| ![Connect Four](screenshots/connect_four.png) | ![Tic-Tac-Toe](screenshots/tic-tac-toe.png) |

---

## 🛠️ Educational Modules, Standalone Demos & CLI Execution

This Lab is built for hands-on learning, experimentation, and research. Run any demo directly from your terminal:

```bash
# 1. Graph & Pathfinding Search
python -m demo.maze --algo AStar --vis
python -m demo.maze --algo IGBFS --vis
python -m demo.n-puzzle --size 4 --algo AStar --vis
python -m demo.romanian_map_demo --start Arad --goal Bucharest --algo AStar --vis
python -m demo.sokoban_demo --vis

# 2. Local Search & Continuous Optimization
python -m demo.local_search_tsp --algo GeneticAlgorithm --vis
python -m demo.local_search_tsp --algo LocalBeamSearch --vis
python -m demo.local_search_nqueens --algo GeneticAlgorithm --vis

# 3. Constraint Satisfaction Problems (CSP)
python -m demo.csp_tree_decomposition --vis
python -m demo.csp_cycle_cutset --vis
python -m demo.csp_sudoku --difficulty hard --inference mac --vis
python -m demo.csp_map_coloring --vis
python -m demo.csp_cryptarithmetic --vis

# 4. Board Games & Imperfect Information Card Games
python -m demo.games_demo --game othello --p1 human --p2 alphabeta --vis
python -m demo.games_demo --game connect_four --p1 mcts --p2 random --vis
python -m demo.crazy_demo
```

---

## 🏗 Architecture & Design System

The core design philosophy of this Lab revolves around clean **separation of concerns** between **Domains (State Representations)** and **Solvers (Algorithms)**.

```mermaid
classDiagram
    class SearchProblem {
        +start
        +goal
        +get_actions(state)
        +get_result(state, action)
        +get_cost(state, action, next_state)
        +heuristic(state)
    }

    class OptimizationProblem {
        +initial_state
        +value(state)
        +get_all_neighbors(state)
        +get_random_neighbor(state)
        +crossover(state1, state2)
        +mutate(state)
    }

    class CSPProblem {
        +variables
        +domains
        +constraints
        +add_constraint(constraint)
    }

    class GameState {
        +current_player
        +get_legal_actions()
        +apply_action(action)
        +is_terminal()
        +get_utility(player)
    }

    class MazeSearchProblem
    class NPuzzleProblem
    class RomanianMapProblem
    class WordLadderProblem
    class SokobanProblem
    class VacuumWorldProblem

    class NQueensProblem
    class TSPProblem

    class MapColoringCSP
    class NQueensCSP
    class SudokuCSP
    class CryptarithmeticCSP
    class TimetablingCSP

    class TicTacToeState
    class ConnectFourState
    class CheckersState
    class OthelloState
    class CrazyState

    SearchProblem <|-- MazeSearchProblem
    SearchProblem <|-- NPuzzleProblem
    SearchProblem <|-- RomanianMapProblem
    SearchProblem <|-- WordLadderProblem
    SearchProblem <|-- SokobanProblem
    SearchProblem <|-- VacuumWorldProblem

    OptimizationProblem <|-- NQueensProblem
    OptimizationProblem <|-- TSPProblem

    CSPProblem <|-- MapColoringCSP
    CSPProblem <|-- NQueensCSP
    CSPProblem <|-- SudokuCSP
    CSPProblem <|-- CryptarithmeticCSP
    CSPProblem <|-- TimetablingCSP

    GameState <|-- TicTacToeState
    GameState <|-- ConnectFourState
    GameState <|-- CheckersState
    GameState <|-- OthelloState
    GameState <|-- CrazyState
```

---

## 📊 Performance Benchmarks & Report Generation

Benchmark evaluation results and performance comparison reports are saved directly in markdown and high-resolution chart format.

### Running Benchmarks

```bash
# Run all benchmarks (30 iterations per algorithm)
python -m benchmarks.run_all_benchmarks --runs 30

# Run individual benchmark suites with filters
python -m benchmarks.search_benchmark --runs 10 --domains 8pzl --algos "A*,IDA*"
python -m benchmarks.csp_benchmark --runs 10 --algos "BT+MAC,BT+MRV"
python -m benchmarks.game_benchmark --runs 5 --games tic_tac_toe
python -m benchmarks.local_search_benchmark --runs 10 --domains tsp

# Use --reset to clear existing CSV data before writing
python -m benchmarks.search_benchmark --runs 30 --reset
```

### Generating Reports

```bash
# Generate performance charts (saved to reports/figures/)
python -m benchmarks.generate_report

# Generate markdown summary tables (updates reports/benchmark_report.md)
python -m utils.generate_markdown_tables
```

* **Reports**: See `reports/benchmark_report.md` and `reports/comparison.md`.
* **CSV Results**: Raw per-run data in `results/*.csv`.
* **Charts**: High-resolution figures in `reports/figures/`.

---

## 🤝 Open Source Contribution Guidelines

We welcome open-source contributions! Adding a new search algorithm, heuristic, or domain is straightforward:

1. **Add a New Search Algorithm**: Inherit from `SearchAlgorithm` in `search/SearchAlgorithm.py` and implement `search_step()`.
2. **Add a New CSP Heuristic / Inference**: Implement a function receiving `(csp, assignment)` inside `csp/heuristics/` or `csp/inference/`.
3. **Add a New Game Domain**: Inherit from `GameState` in `games/GameState.py` and define `get_legal_actions()`, `apply_action()`, and `is_terminal()`.
4. **Add a Custom Visualizer**: Create a Pygame visualizer class in `visualization/` with standardized HUD controls (`SPACE` auto-play, `+`/`-` speed, `LEFT`/`RIGHT` step, `R` restart).

---

## 📜 License

Licensed under the MIT License. Developed for educational research, visual learning, and advanced AI algorithm exploration.
