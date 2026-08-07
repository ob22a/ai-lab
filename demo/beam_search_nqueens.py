"""
Local Beam Search Demo for N-Queens Optimization.

Showcases:
  - Multi-beam candidate boards running in parallel (k beams).
  - Main hero board with attacking pair visualizer.
  - Interactive beam card selection and real-time diversity metrics.
  - Step-by-step history scrubbing and auto-run.
"""

from domains.n_queens.NQueensProblem import NQueensProblem
from search.local.LocalBeamSearch import LocalBeamSearch
from visualization.BeamSearchVisualizer import BeamSearchVisualizer


def main():
    print("=" * 60)
    print("  LOCAL BEAM SEARCH - N-QUEENS OPTIMIZATION DEMO")
    print("=" * 60)
    print("Controls:")
    print("  [SPACE]     Play / Pause auto-stepping")
    print("  [RIGHT]     Step forward 1 iteration")
    print("  [LEFT]      Step backward in history")
    print("  [1..k]      Inspect candidate beam on hero board")
    print("  [A]         Toggle continuous auto-run")
    print("  [R]         Restart with new initial random beams")
    print("  [UP / DOWN] Adjust playback speed (FPS)")
    print("  [ESC]       Exit")
    print("=" * 60)

    # 8-Queens is classic (can be set to 4, 8, 10, etc.)
    n = 8
    k = 5  # Number of parallel beams
    problem = NQueensProblem(n=n)
    solver = LocalBeamSearch(problem, k=k)

    visualizer = BeamSearchVisualizer(
        problem=problem,
        solver=solver,
        cell_size=55,
        fps=8,
        auto_run=False
    )
    visualizer.run()


if __name__ == "__main__":
    main()
