"""
utils/generate_markdown_tables.py

Automated Table & Markdown Report Generator.
Reads benchmark CSV results from `results/*.csv`, aggregates raw per-run data,
and generates clean GitHub Markdown tables for:
  - reports/benchmark_report.md
  - reports/comparison.md

Usage:
  python -m utils.generate_markdown_tables
"""

import os
import csv
import glob
from collections import defaultdict
from typing import List, Dict, Any, Tuple


def read_csv_rows(csv_filepath: str) -> List[List[str]]:
    """Reads a CSV file and returns all rows (excluding header)."""
    if not os.path.exists(csv_filepath):
        return []
    with open(csv_filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        return [r for r in reader if r]


def aggregate_search_csv(csv_filepath: str) -> str:
    """Aggregates raw per-run search/local-search CSV into a summary markdown table."""
    rows = read_csv_rows(csv_filepath)
    if not rows:
        return f"*No data found in `{csv_filepath}`.*\n"

    # Group by Label (column 0)
    groups = defaultdict(list)
    for r in rows:
        if len(r) >= 8:
            groups[r[0]].append(r)

    # Build summary table
    md = []
    md.append("| Algorithm / Instance | Success Rate | Avg Path Cost | Avg Nodes Expanded | Avg Runtime (s) | Runs |")
    md.append("| --- | --- | --- | --- | --- | --- |")

    for label in groups:
        runs = groups[label]
        total = len(runs)
        successes = [r for r in runs if r[2].strip().lower() in ("true", "1")]
        sr = f"{len(successes)}/{total}"
        if successes:
            avg_cost = sum(float(r[3]) for r in successes) / len(successes)
            avg_nodes = sum(int(float(r[4])) for r in successes) / len(successes)
            avg_time = sum(float(r[6]) for r in successes) / len(successes)
            md.append(f"| {label} | {sr} | {avg_cost:.1f} | {int(avg_nodes):,} | {avg_time:.6f} | {total} |")
        else:
            md.append(f"| {label} | {sr} | — | — | — | {total} |")

    return "\n".join(md) + "\n"


def aggregate_csp_csv(csv_filepath: str) -> str:
    """Aggregates raw per-run CSP CSV into a summary markdown table."""
    rows = read_csv_rows(csv_filepath)
    if not rows:
        return f"*No data found in `{csv_filepath}`.*\n"

    groups = defaultdict(list)
    for r in rows:
        if len(r) >= 7:
            groups[r[0]].append(r)

    md = []
    md.append("| Solver / Problem | Success Rate | Avg Nodes | Avg Runtime (s) | Runs |")
    md.append("| --- | --- | --- | --- | --- |")

    for label in sorted(groups.keys()):
        runs = groups[label]
        total = len(runs)
        successes = [r for r in runs if r[2].strip().lower() in ("true", "1")]
        sr = f"{len(successes)}/{total}"
        if successes:
            avg_nodes = sum(int(float(r[4])) for r in successes) / len(successes)
            avg_time = sum(float(r[6]) for r in successes) / len(successes)
            md.append(f"| {label} | {sr} | {int(avg_nodes):,} | {avg_time:.6f} | {total} |")
        else:
            md.append(f"| {label} | {sr} | — | — | {total} |")

    return "\n".join(md) + "\n"


def game_tournament_table(csv_filepath: str) -> str:
    """Converts game tournament CSV directly to markdown (already aggregated)."""
    rows = read_csv_rows(csv_filepath)
    if not rows:
        return f"*No data found in `{csv_filepath}`.*\n"

    md = []
    md.append("| Game | Agent 1 | Agent 2 | Agent 1 Wins | Agent 2 Wins | Draws | Avg Time (s) |")
    md.append("| --- | --- | --- | --- | --- | --- | --- |")

    for r in rows:
        if len(r) >= 7:
            md.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |")

    return "\n".join(md) + "\n"


def generate_all_reports():
    print("=" * 65)
    print("      AUTOMATED MARKDOWN TABLE & REPORT GENERATOR")
    print("=" * 65)

    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in `{results_dir}/`. Please run benchmarks first.")
        return

    print(f"\nFound {len(csv_files)} CSV files in `{results_dir}/`:")
    for f in csv_files:
        print(f"  - {f}")

    # === 1. Generate benchmark_report.md ===
    bm_report_path = "reports/benchmark_report.md"
    sections = []
    sections.append("# AI Lab — Automated Benchmark Report\n")
    sections.append("This report is automatically generated from raw benchmark CSV files in `results/`.\n")
    sections.append("To regenerate: `python -m utils.generate_markdown_tables`\n")
    sections.append("For performance charts: `python -m benchmarks.generate_report`\n")

    # 8-Puzzle
    sections.append("---\n\n## 1. N-Puzzle Search Performance\n")
    sections.append("### 1a. 8-Puzzle\n")
    sections.append(aggregate_search_csv("results/search_8puzzle.csv"))
    if os.path.exists("reports/figures/search_nodes_expanded.png"):
        sections.append("\n![8-Puzzle Nodes Expanded](figures/search_nodes_expanded.png)\n")
    if os.path.exists("reports/figures/8puzzle_all_instances.png"):
        sections.append("\n![8-Puzzle Multi-Difficulty](figures/8puzzle_all_instances.png)\n")

    # 15-Puzzle
    sections.append("\n### 1b. 15-Puzzle\n")
    sections.append(aggregate_search_csv("results/search_15puzzle.csv"))
    if os.path.exists("reports/figures/puzzles_15_comparison.png"):
        sections.append("\n![15-Puzzle Performance](figures/puzzles_15_comparison.png)\n")

    # Maze
    sections.append("\n---\n\n## 2. Maze Pathfinding\n")
    sections.append(aggregate_search_csv("results/search_maze.csv"))
    if os.path.exists("reports/figures/maze_all_algos_comparison.png"):
        sections.append("\n![Maze Algorithms](figures/maze_all_algos_comparison.png)\n")
    if os.path.exists("reports/figures/maze_scaling_comparison.png"):
        sections.append("\n![Maze Scaling](figures/maze_scaling_comparison.png)\n")

    # Local Search - TSP
    sections.append("\n---\n\n## 3. Local Search & Optimization\n")
    sections.append("### 3a. TSP (20 Cities)\n")
    sections.append(aggregate_search_csv("results/local_search_tsp.csv"))
    if os.path.exists("reports/figures/local_search_comparison.png"):
        sections.append("\n![TSP Comparison](figures/local_search_comparison.png)\n")

    # Local Search - N-Queens
    sections.append("\n### 3b. N-Queens Local Search\n")
    sections.append(aggregate_search_csv("results/local_search_nqueens.csv"))
    if os.path.exists("reports/figures/nqueens_local_comparison.png"):
        sections.append("\n![N-Queens Local Search](figures/nqueens_local_comparison.png)\n")

    # CSP
    sections.append("\n---\n\n## 4. Constraint Satisfaction Problems (CSP)\n")
    sections.append(aggregate_csp_csv("results/csp_benchmarks.csv"))
    if os.path.exists("reports/figures/csp_benchmark_summary.png"):
        sections.append("\n![CSP Nodes](figures/csp_benchmark_summary.png)\n")
    if os.path.exists("reports/figures/csp_runtime_summary.png"):
        sections.append("\n![CSP Runtime](figures/csp_runtime_summary.png)\n")
    if os.path.exists("reports/figures/csp_cross_domain.png"):
        sections.append("\n![CSP Cross-Domain](figures/csp_cross_domain.png)\n")

    # Games
    sections.append("\n---\n\n## 5. Adversarial Game Tournament\n")
    sections.append(game_tournament_table("results/game_tournament.csv"))
    if os.path.exists("reports/figures/game_tournament_winrates.png"):
        sections.append("\n![Game Tournament](figures/game_tournament_winrates.png)\n")

    # Heuristic Comparison
    sections.append("\n---\n\n## 6. Heuristic Comparison\n")
    sections.append("### A* and IDA* on 8-Puzzle (Misplaced vs Manhattan vs Pattern Database)\n")
    if os.path.exists("reports/figures/heuristic_comparison_8puzzle.png"):
        sections.append("\n![Heuristic Comparison](figures/heuristic_comparison_8puzzle.png)\n")
    else:
        sections.append("*Run `python -m benchmarks.generate_report` to generate heuristic comparison charts.*\n")

    with open(bm_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sections))

    print(f"\nSuccessfully generated -> `{bm_report_path}`")
    print("=" * 65)


if __name__ == "__main__":
    generate_all_reports()
