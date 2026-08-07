"""
Genetic Algorithm Evolution Demo for N-Queens Optimization.

Showcases:
  - Generation-by-generation evolution with selection, crossover, and mutation.
  - Live fitness progression chart (Best vs Average population fitness over time).
  - Elite genotype cards and chromosome inspector.
  - Hero board showing the fittest individual with conflict detection.
"""

from domains.n_queens.NQueensProblem import NQueensProblem
from search.local.GeneticAlgorithm import GeneticAlgorithm
from visualization.GeneticAlgorithmVisualizer import GeneticAlgorithmVisualizer


def main():
    print("=" * 60)
    print("  GENETIC ALGORITHM - N-QUEENS EVOLUTION DEMO")
    print("=" * 60)
    print("Controls:")
    print("  [SPACE]     Play / Pause generation evolution")
    print("  [RIGHT]     Step forward 1 generation")
    print("  [LEFT]      Step backward in generation history")
    print("  [1..4]      Inspect elite genotype on hero board")
    print("  [A]         Toggle continuous auto-evolution")
    print("  [R]         Restart with new initial population")
    print("  [UP / DOWN] Adjust evolution speed (FPS)")
    print("  [ESC]       Exit")
    print("=" * 60)

    n = 8
    pop_size = 40
    mutation_rate = 0.12
    max_generations = 300

    problem = NQueensProblem(n=n)
    solver = GeneticAlgorithm(
        problem=problem,
        pop_size=pop_size,
        mutation_rate=mutation_rate,
        max_generations=max_generations
    )

    visualizer = GeneticAlgorithmVisualizer(
        problem=problem,
        solver=solver,
        cell_size=55,
        fps=12,
        auto_run=False
    )
    visualizer.run()


if __name__ == "__main__":
    main()
