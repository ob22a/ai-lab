"""
utils/generate_markdown_tables.py

Automated Table & Markdown Report Generator.
Reads benchmark CSV results from `results/*.csv` and generates clean GitHub Markdown tables
to update reports/benchmark_report.md, reports/csp_comparison.md, and README.md.

Usage:
  python -m utils.generate_markdown_tables
"""

import os
import csv
import glob
from typing import List, Dict, Any


def csv_to_markdown(csv_filepath: str) -> str:
    """Reads a CSV file and converts it to a clean GitHub Markdown table."""
    if not os.path.exists(csv_filepath):
        return f"*CSV file not found: `{csv_filepath}`*\n"

    with open(csv_filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return "*CSV file is empty.*\n"

    header = rows[0]
    data = rows[1:]

    # Format Markdown Table
    md = []
    md.append("| " + " | ".join(header) + " |")
    md.append("| " + " | ".join(["---"] * len(header)) + " |")

    for row in data:
        md.append("| " + " | ".join(row) + " |")

    return "\n".join(md) + "\n"


def generate_all_reports():
    print("=" * 65)
    print("      AUTOMATED MARKDOWN TABLE GENERATOR")
    print("=" * 65)

    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in `{results_dir}/`. Please run benchmarks first.")
        return

    print(f"\nFound {len(csv_files)} CSV files in `{results_dir}/`:")
    for f in csv_files:
        print(f"  - {f}")

    # 1. Update benchmark_report.md
    bm_report_path = "reports/benchmark_report.md"
    os.makedirs("reports", exist_ok=True)

    report_lines = [
        "# Automated AI Search & CSP Performance Benchmark Report\n",
        "This document is automatically generated from benchmark CSV output files.\n",
        "## 1. N-Puzzle Search Performance\n",
        "### 8-Puzzle Benchmark",
        csv_to_markdown("results/search_8puzzle.csv"),
        "### 15-Puzzle Benchmark",
        csv_to_markdown("results/search_15puzzle.csv"),
        "## 2. Maze Pathfinding Performance",
        csv_to_markdown("results/search_maze.csv"),
        "## 3. Game Agent Tournament Benchmark",
        csv_to_markdown("results/game_tournament.csv"),
    ]

    with open(bm_report_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(report_lines))

    print(f"\nSuccessfully updated -> `{bm_report_path}`")

    # 2. Update csp_comparison.md
    csp_report_path = "reports/csp_comparison.md"
    csp_lines = [
        "# Constraint Satisfaction Problem (CSP) Benchmark Comparison\n",
        "This document presents automated benchmark results across CSP domains (Sudoku, N-Queens, Map Coloring, Cryptarithmetic).\n",
        "## CSP Solver Performance Table\n",
        csv_to_markdown("results/csp_benchmark.csv"),
    ]

    with open(csp_report_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(csp_lines))

    print(f"Successfully updated -> `{csp_report_path}`")
    print("=" * 65)


if __name__ == "__main__":
    generate_all_reports()
