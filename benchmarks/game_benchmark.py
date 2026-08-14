"""
benchmarks/game_benchmark.py

Automated Game Agent Tournament Benchmarker.

Runs tournament matchups between adversarial search & heuristic agents:
  - AlphaBeta, MCTS, Random, Obssa Heuristic
Across game domains:
  - Tic-Tac-Toe
  - Connect Four
  - Crazy

Outputs saved to results/game_tournament.csv
"""

import argparse
import csv
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from games.AlphaBeta import AlphaBetaSolver
from games.MCTS import MCTSSolver, InformationSetMCTSSolver
from games.Minimax import MinimaxSolver
from games.RandomSolver import RandomSolver
from games.heuristics.ObssaHeuristic import ObssaHeuristicSolver

from domains.tic_tac_toe.TicTacToe import TicTacToeState
from domains.connect_four.ConnectFour import ConnectFourState
from domains.crazy.CrazyState import determinize_crazy_state
from demo.crazy_demo import make_full_deck_state
from domains.othello.Othello import OthelloState
from domains.othello.OthelloEval import othello_evaluation
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver


def play_game(state, agent1, agent2, max_moves: int = 100) -> int:
    """Plays a single game between agent1 (P1) and agent2 (P2). Returns winner ID (1, 2, or 0 for draw).
    Uses full 54-card deck for Crazy card game and caps maximum turns at max_moves to prevent infinite loops.
    """
    curr_state = state
    p1_id = curr_state.get_current_player()

    move_count = 0

    while not curr_state.is_terminal() and move_count < max_moves:
        move_count += 1
        cp = curr_state.get_current_player()
        if cp == 0:
            # Chance node
            outcomes = curr_state.get_chance_outcomes()
            if not outcomes:
                break
            cards = [c for c, p in outcomes]
            probs = [p for c, p in outcomes]
            drawn = random.choices(cards, weights=probs, k=1)[0]
            curr_state = curr_state.apply_action(drawn)
        else:
            agent = agent1 if cp == p1_id else agent2
            action = agent.get_best_action(curr_state)
            if action is None:
                break
            curr_state = curr_state.apply_action(action)

    u1 = curr_state.get_utility(p1_id)
    if u1 > 0:
        return 1
    elif u1 < 0:
        return 2
    return 0


def run_game_tournament(num_runs=30, target_games=None):
    if target_games is None:
        target_games = ["tic_tac_toe", "connect_four", "othello", "crazy"]

    print("=" * 70)
    print(f"  RUNNING GAME AGENT TOURNAMENT BENCHMARK ({num_runs} RUNS PER PAIRING)")
    print("=" * 70)

    all_matchups = [
        ("tic_tac_toe", "Tic-Tac-Toe", lambda: TicTacToeState(), [
            ("AlphaBeta", AlphaBetaSolver()),
            ("MCTS(n=30)", MCTSSolver(num_simulations=30)),
            ("Random", RandomSolver())
        ]),
        ("connect_four", "Connect Four", lambda: ConnectFourState(), [
            ("AlphaBeta(d=4)", AlphaBetaSolver(max_depth=4)),
            ("MCTS(n=30)", MCTSSolver(num_simulations=30)),
            ("Random", RandomSolver())
        ]),
        ("othello", "Othello (Reversi)", lambda: OthelloState(), [
            ("AlphaBeta(d=3)", AlphaBetaOrderedSolver(max_depth=3, evaluation_function=othello_evaluation)),
            ("MCTS(n=30)", MCTSSolver(num_simulations=30)),
            ("Random", RandomSolver())
        ]),
        ("crazy", "Crazy Card Game", lambda: make_full_deck_state(), [
            ("Obssa Heuristic", ObssaHeuristicSolver()),
            ("IS-MCTS(n=30)", InformationSetMCTSSolver(determinize_crazy_state, num_simulations=30)),
            ("Random", RandomSolver())
        ])
    ]

    # Filter by target_games
    matchups = [m for m in all_matchups if m[0] in target_games or any(t.lower() in m[0].lower() for t in target_games)]
    if not matchups:
        matchups = all_matchups

    results = []

    for key, game_name, state_factory, agents in matchups:
        print(f"\n--- Tournament: {game_name} ---")
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                name1, a1 = agents[i]
                name2, a2 = agents[j]
                
                p1_wins = 0
                p2_wins = 0
                draws = 0
                t0 = time.perf_counter()

                for run_idx in range(num_runs):
                    st = state_factory()
                    winner = play_game(st, a1, a2)
                    if winner == 1:
                        p1_wins += 1
                    elif winner == 2:
                        p2_wins += 1
                    else:
                        draws += 1

                elapsed = time.perf_counter() - t0
                avg_time = elapsed / num_runs

                print(f"  {name1:<18} vs {name2:<18} | P1 Wins: {p1_wins:2d} | P2 Wins: {p2_wins:2d} | Draws: {draws:2d} | Avg Time: {avg_time:.3f}s")
                results.append([game_name, name1, name2, p1_wins, p2_wins, draws, round(avg_time, 4)])

    csv_path = "results/game_tournament.csv"
    os.makedirs("results", exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Game", "Agent 1", "Agent 2", "Agent 1 Wins", "Agent 2 Wins", "Draws", "Avg Game Time (s)"])
        writer.writerows(results)

    print(f"\nSaved Game Tournament Results -> {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30, help="Number of runs per matchup (default: 30)")
    parser.add_argument("--games", "--domains", type=str, default="tic_tac_toe,connect_four,crazy", help="Comma-separated games to run")
    args = parser.parse_args()
    games_list = [g.strip() for g in args.games.split(",") if g.strip()]
    run_game_tournament(num_runs=args.runs, target_games=games_list)
