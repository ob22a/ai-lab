"""
benchmarks/game_benchmark.py — Game agent tournament benchmarker.

Covers: Tic-Tac-Toe, Connect Four, Othello, Checkers, Crazy Card Game.
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
from games.AlphaBetaOrdered import AlphaBetaOrderedSolver
from games.IterativeDeepening import IterativeDeepeningSolver

from domains.tic_tac_toe.TicTacToe import TicTacToeState
from domains.connect_four.ConnectFour import ConnectFourState
from domains.crazy.CrazyState import determinize_crazy_state
from demo.crazy_demo import make_full_deck_state
from domains.othello.Othello import OthelloState
from domains.othello.OthelloEval import othello_evaluation
from domains.checkers.Checkers import CheckersState
from domains.checkers.CheckersEval import checkers_evaluation


def play_game(state, agent1, agent2, max_moves: int = 100) -> int:
    curr_state = state
    p1_id = curr_state.get_current_player()
    move_count = 0

    while not curr_state.is_terminal() and move_count < max_moves:
        move_count += 1
        cp = curr_state.get_current_player()
        if cp == 0:
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
    if u1 < 0:
        return 2
    return 0


def _all_matchups():
    return [
        ("tic_tac_toe", "Tic-Tac-Toe", lambda: TicTacToeState(), [
            ("Minimax", MinimaxSolver()),
            ("AlphaBeta", AlphaBetaSolver()),
            ("AlphaBetaOrdered", AlphaBetaOrderedSolver(max_depth=5)),
            ("MCTS(n=30)", MCTSSolver(num_simulations=30)),
            ("IterativeDeepening", IterativeDeepeningSolver(time_limit_seconds=0.5)),
            ("Random", RandomSolver()),
        ]),
        ("connect_four", "Connect Four", lambda: ConnectFourState(), [
            ("AlphaBeta(d=4)", AlphaBetaSolver(max_depth=4)),
            ("MCTS(n=30)", MCTSSolver(num_simulations=30)),
            ("Random", RandomSolver()),
        ]),
        ("othello", "Othello (Reversi)", lambda: OthelloState(), [
            ("AlphaBeta(d=3)", AlphaBetaOrderedSolver(max_depth=3, evaluation_function=othello_evaluation)),
            ("MCTS(n=30)", MCTSSolver(num_simulations=30)),
            ("Random", RandomSolver()),
        ]),
        ("checkers", "Checkers", lambda: CheckersState(), [
            ("AlphaBeta(d=4)", AlphaBetaOrderedSolver(max_depth=4, evaluation_function=checkers_evaluation)),
            ("AlphaBeta(d=6)", AlphaBetaOrderedSolver(max_depth=6, evaluation_function=checkers_evaluation)),
            ("MCTS(n=100)", MCTSSolver(num_simulations=100)),
            ("Random", RandomSolver()),
        ]),
        ("crazy", "Crazy Card Game", lambda: make_full_deck_state(), [
            ("Obssa Heuristic", ObssaHeuristicSolver()),
            ("IS-MCTS(n=30)", InformationSetMCTSSolver(determinize_crazy_state, num_simulations=30)),
            ("Random", RandomSolver()),
        ]),
    ]


def run_game_tournament(num_runs=30, target_games=None, agent_filter=None, reset=False):
    if target_games is None:
        target_games = ["tic_tac_toe", "connect_four", "othello", "checkers", "crazy"]

    print("=" * 70)
    print(f"  RUNNING GAME AGENT TOURNAMENT BENCHMARK ({num_runs} RUNS PER PAIRING)")
    print("=" * 70)

    matchups = [m for m in _all_matchups() if m[0] in target_games or any(t.lower() in m[0].lower() for t in target_games)]
    if not matchups:
        matchups = _all_matchups()

    from benchmarks.benchmark import append_game_result_to_csv

    csv_path = "results/game_tournament.csv"
    first_write = reset

    for key, game_name, state_factory, agents in matchups:
        if agent_filter:
            filt = {a.strip().lower() for a in agent_filter}
            agents = [(n, ag) for n, ag in agents if any(x in n.lower() for x in filt)]
        if len(agents) < 2:
            continue

        print(f"\n--- Tournament: {game_name} ---")
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                name1, a1 = agents[i]
                name2, a2 = agents[j]
                p1_wins = p2_wins = draws = 0
                t0 = time.perf_counter()
                for _ in range(num_runs):
                    winner = play_game(state_factory(), a1, a2)
                    if winner == 1:
                        p1_wins += 1
                    elif winner == 2 or winner == -1:
                        p2_wins += 1
                    else:
                        draws += 1
                elapsed = time.perf_counter() - t0
                avg_time = elapsed / num_runs
                print(f"  {name1:<20} vs {name2:<20} | W1:{p1_wins:2d} W2:{p2_wins:2d} D:{draws:2d} | {avg_time:.3f}s")
                append_game_result_to_csv(csv_path, game_name, name1, name2, p1_wins, p2_wins, draws, avg_time, reset=first_write)
                first_write = False

    print(f"\nSaved Game Tournament Results -> {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--games", "--domains", dest="games", type=str, default="tic_tac_toe,connect_four,othello,checkers,crazy")
    parser.add_argument("--agents", type=str, default="", help="Comma-separated agent name filter")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    games_list = [g.strip() for g in args.games.split(",") if g.strip()]
    agent_list = [a.strip() for a in args.agents.split(",") if a.strip()] or None
    run_game_tournament(num_runs=args.runs, target_games=games_list, agent_filter=agent_list, reset=args.reset)
