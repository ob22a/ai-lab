"""
demo/games_demo.py
Unified Adversarial Board Game AI Demo (Tic-Tac-Toe, Connect Four, Othello, Checkers).

Features:
  - Game selection: Tic-Tac-Toe, Connect Four, Othello (Reversi), Checkers
  - Agent selection: Human vs AI, AI vs AI, Human vs Human
  - Solvers: AlphaBeta, MCTS (Monte Carlo Tree Search), Random
  - Pygame interactive board game visualizer

Usage:
  python -m demo.games_demo [--vis] [--game tictactoe|connect_four|othello|checkers] [--p1 human|alphabeta|mcts|random] [--p2 human|alphabeta|mcts|random]
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Game State Domain Classes
from domains.tic_tac_toe.TicTacToe import TicTacToeState
from domains.connect_four.ConnectFour import ConnectFourState
from domains.othello.Othello import OthelloState
from domains.checkers.Checkers import CheckersState

# Solvers & Heuristics
from games.AlphaBeta import AlphaBetaSolver
from games.MCTS import MCTSSolver
from games.RandomSolver import RandomSolver
from visualization.BoardGameVisualizer import BoardGameVisualizer


def make_agent(agent_str, game_name):
    agent_str = agent_str.lower()
    if agent_str == "human":
        return "HUMAN"
    elif agent_str == "alphabeta":
        return AlphaBetaSolver()
    elif agent_str == "mcts":
        sims = 300 if game_name == "connect_four" else 500
        return MCTSSolver(num_simulations=sims)
    else:
        return RandomSolver()


def main():
    parser = argparse.ArgumentParser(description="Unified Board Game AI Demo")
    parser.add_argument("--vis", action="store_true", help="Launch interactive Pygame visualizer")
    parser.add_argument("--game", type=str, default="tictactoe", choices=["tictactoe", "connect_four", "othello", "checkers"],
                        help="Game domain (tictactoe, connect_four, othello, checkers)")
    parser.add_argument("--p1", type=str, default="human", choices=["human", "alphabeta", "mcts", "random"],
                        help="Player 1 agent type")
    parser.add_argument("--p2", type=str, default="mcts", choices=["human", "alphabeta", "mcts", "random"],
                        help="Player 2 agent type")
    args = parser.parse_args()

    print("=" * 65)
    print(f"         ADVERSARIAL BOARD GAME AI DEMO ({args.game.upper()})")
    print("=" * 65)

    # 1. Select Game State
    if args.game == "connect_four":
        initial_state = ConnectFourState()
        cell_size = 90
    elif args.game == "othello":
        initial_state = OthelloState()
        cell_size = 75
    elif args.game == "checkers":
        initial_state = CheckersState()
        cell_size = 75
    else:
        initial_state = TicTacToeState()
        cell_size = 110

    # 2. Select Players
    p1 = make_agent(args.p1, args.game)
    p2 = make_agent(args.p2, args.game)

    p1_name = "HUMAN" if p1 == "HUMAN" else p1.__class__.__name__
    p2_name = "HUMAN" if p2 == "HUMAN" else p2.__class__.__name__

    print(f"Game Chosen: {args.game.title()}")
    print(f"Player 1:    {p1_name}")
    print(f"Player 2:    {p2_name}\n")

    print("Launching Pygame Window! Click board or press SPACE for AI moves.")
    vis = BoardGameVisualizer(
        initial_state=initial_state,
        player1=p1,
        player2=p2,
        cell_size=cell_size
    )
    vis.run()
    
    try:
        from utils.auto_logger import auto_log_game
        if vis.state.is_terminal():
            winner = vis.state.get_winner()
            auto_log_game(args.game, p1_name, p2_name, winner, getattr(vis, "elapsed_time", 0.0))
    except Exception:
        pass


if __name__ == "__main__":
    main()

