"""
generate_report.py
Automated benchmark report & figure generator using Matplotlib.

Reads directly from populated CSV files in results/:
  - results/search_8puzzle.csv
  - results/search_15puzzle.csv
  - results/search_maze.csv
  - results/local_search_tsp.csv
  - results/local_search_nqueens.csv
  - results/csp_benchmarks.csv
  - results/game_tournament.csv

Generates comprehensive high-resolution charts in reports/figures/:
  - search_nodes_expanded.png        (8-Puzzle Node Expansions with PDB Heuristics)
  - search_runtime_comparison.png     (8-Puzzle Execution Time in ms)
  - 8puzzle_all_instances.png        (8-Puzzle Easy vs Medium vs Hard Multi-Instance)
  - puzzles_15_comparison.png        (15-Puzzle Informed Search Performance with PDB)
  - 15puzzle_all_instances.png       (15-Puzzle Medium vs Hard Multi-Instance)
  - maze_all_algos_comparison.png    (50x50 Maze Pathfinding Comparison)
  - maze_scaling_comparison.png      (Maze 10x10 vs 30x30 vs 50x50 Node Scaling)
  - maze_runtime_scaling.png         (Maze 10x10 vs 30x30 vs 50x50 Runtime Scaling in ms)
  - local_search_comparison.png      (TSP 20-City Local Search & Optimization)
  - nqueens_local_comparison.png     (8-Queens Local Search Comparison)
  - csp_benchmark_summary.png        (CSP Solvers Pruning Comparison)
  - csp_runtime_summary.png          (CSP Solvers Execution Time in ms)
  - game_tournament_winrates.png     (Adversarial Game Tournament Win Rates)
"""

import csv
import os
import matplotlib.pyplot as plt
import numpy as np


def read_csv_data(filepath):
    if not os.path.exists(filepath):
        return None
    rows = []
    with open(filepath, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for r in reader:
            if r:
                rows.append(r)
    return rows


def annotate_bars(ax, bars, fmt="{:,}", fontsize=8, is_float=False):
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            val_str = f"{height:.4f}" if is_float else f"{int(height):,}"
            ax.annotate(val_str,
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=fontsize, fontweight='bold')


def generate_reports_and_charts():
    os.makedirs("reports/figures", exist_ok=True)
    print("Generating Comprehensive Performance Figures directly from CSV files in results/...\n")

    # Helper to append (PDB) to informed puzzle algos
    def pdb_label(algo_name):
        informed = ["A*", "IDA*", "RBFS", "SMA*", "Bidir-A*", "GBFS"]
        clean = algo_name.split("(")[0].strip()
        if any(clean == inf for inf in informed):
            return f"{algo_name} (PDB)"
        return algo_name

    # 1. 8-Puzzle Hard Node Expansions & Runtime Chart
    csv_8p = read_csv_data("results/search_8puzzle.csv")
    if csv_8p:
        hard_rows = [r for r in csv_8p if "8pzl hard" in r[0]]
        if not hard_rows:
            hard_rows = [r for r in csv_8p if "8pzl medium" in r[0]] or csv_8p
        algos_8p = [pdb_label(r[0].split("/")[0].strip()) for r in hard_rows]
        nodes_8p_hard = [int(float(r[3])) for r in hard_rows]
        times_8p_ms = [float(r[5]) * 1000.0 for r in hard_rows] # Convert to ms

        # Nodes Expanded Chart
        fig, ax = plt.subplots(figsize=(11, 6))
        x = np.arange(len(algos_8p))
        bars = ax.bar(x, nodes_8p_hard, color=['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#CCB974'][:len(algos_8p)])
        ax.set_yscale('log')
        ax.set_ylabel('Nodes Expanded (Log Scale)')
        ax.set_title('8-Puzzle Instance: Nodes Expanded (Disjoint Pattern Database Heuristics)')
        ax.set_xticks(x)
        ax.set_xticklabels(algos_8p, rotation=20)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        annotate_bars(ax, bars, fontsize=8)
        plt.tight_layout()
        plt.savefig("reports/figures/search_nodes_expanded.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/search_nodes_expanded.png")

        # Runtime Execution Speed Chart (in ms)
        fig, ax = plt.subplots(figsize=(11, 6))
        bars = ax.bar(x, times_8p_ms, color=['#55A868', '#4C72B0', '#DD8452', '#C44E52', '#8172B3', '#CCB974'][:len(algos_8p)])
        ax.set_yscale('log')
        ax.set_ylabel('Execution Time (ms, Log Scale)')
        ax.set_title('8-Puzzle Execution Time (ms): Pattern Database Heuristic Acceleration')
        ax.set_xticks(x)
        ax.set_xticklabels(algos_8p, rotation=20)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.annotate(f"{h:.2f}ms", xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')
        plt.tight_layout()
        plt.savefig("reports/figures/search_runtime_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/search_runtime_comparison.png")

        # 1b. 8-Puzzle Multi-Difficulty Scaling (Easy vs Medium vs Hard)
        diffs = ["8pzl easy", "8pzl medium", "8pzl hard"]
        all_algos = sorted(list(set(r[0].split("/")[0].strip() for r in csv_8p)))
        all_algos_lbl = [pdb_label(a) for a in all_algos]
        if len(all_algos) > 0:
            fig, ax = plt.subplots(figsize=(13, 6))
            x = np.arange(len(all_algos))
            width = 0.25
            colors = ['#55A868', '#DD8452', '#C44E52']

            for i, diff in enumerate(diffs):
                diff_nodes = []
                for algo in all_algos:
                    match = next((r for r in csv_8p if algo in r[0] and diff in r[0]), None)
                    diff_nodes.append(int(float(match[3])) if match else 0)
                offset = (i - 1) * width
                ax.bar(x + offset, diff_nodes, width, label=diff.upper(), color=colors[i])

            ax.set_yscale('log')
            ax.set_ylabel('Nodes Expanded (Log Scale)')
            ax.set_title('8-Puzzle Scaling Across Difficulties (PDB Heuristics vs Uninformed)')
            ax.set_xticks(x)
            ax.set_xticklabels(all_algos_lbl, rotation=20)
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("reports/figures/8puzzle_all_instances.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/8puzzle_all_instances.png")

    # 2. 15-Puzzle Informed Search Comparison Chart (PDB Heuristics)
    csv_15p = read_csv_data("results/search_15puzzle.csv")
    if csv_15p:
        hard_15p_rows = [r for r in csv_15p if "15pzl hard" in r[0]] or csv_15p
        algos_15p = [pdb_label(r[0].split("/")[0].strip()) for r in hard_15p_rows]
        nodes_15p = [int(float(r[3])) for r in hard_15p_rows]

        fig, ax = plt.subplots(figsize=(11, 6))
        x = np.arange(len(algos_15p))
        bars = ax.bar(x, nodes_15p, color=['#55A868', '#C44E52', '#4C72B0', '#DD8452', '#8172B3', '#CCB974'][:len(algos_15p)])
        ax.set_yscale('log')
        ax.set_ylabel('Nodes Expanded (Log Scale)')
        ax.set_title('15-Puzzle Hard Instance: Disjoint Pattern Database (PDB) Performance')
        ax.set_xticks(x)
        ax.set_xticklabels(algos_15p, rotation=20)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        annotate_bars(ax, bars, fontsize=8)
        plt.tight_layout()
        plt.savefig("reports/figures/puzzles_15_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/puzzles_15_comparison.png")

        # 2b. 15-Puzzle Medium vs Hard Multi-Instance
        diffs_15 = ["15pzl medium", "15pzl hard"]
        algos_15_list = sorted(list(set(r[0].split("/")[0].strip() for r in csv_15p)))
        algos_15_lbl = [pdb_label(a) for a in algos_15_list]
        if len(algos_15_list) > 0:
            fig, ax = plt.subplots(figsize=(11, 6))
            x = np.arange(len(algos_15_list))
            width = 0.35
            colors = ['#4C72B0', '#C44E52']

            for i, diff in enumerate(diffs_15):
                nodes_list = []
                for algo in algos_15_list:
                    match = next((r for r in csv_15p if algo in r[0] and diff in r[0]), None)
                    nodes_list.append(int(float(match[3])) if match else 0)
                offset = (i - 0.5) * width
                ax.bar(x + offset, nodes_list, width, label=diff.upper(), color=colors[i])

            ax.set_yscale('log')
            ax.set_ylabel('Nodes Expanded (Log Scale)')
            ax.set_title('15-Puzzle Scaling: Medium vs Hard Instance (PDB Heuristic)')
            ax.set_xticks(x)
            ax.set_xticklabels(algos_15_lbl, rotation=15)
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("reports/figures/15puzzle_all_instances.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/15puzzle_all_instances.png")

    # 3. Maze Pathfinding Across ALL Search Algorithms & Runtime Scaling
    csv_maze = read_csv_data("results/search_maze.csv")
    if csv_maze:
        maze_50_rows = [r for r in csv_maze if "maze 50x50" in r[0]] or csv_maze
        all_search_algos = [r[0].split("/")[0].strip() for r in maze_50_rows]
        nodes_maze_50 = [int(float(r[3])) for r in maze_50_rows]

        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(all_search_algos))
        bars = ax.bar(x, nodes_maze_50, color=['#C44E52']*5 + ['#55A868']*6)
        ax.set_yscale('log')
        ax.set_ylabel('Nodes Expanded (Log Scale)')
        ax.set_title('50×50 Maze Pathfinding: ALL Search Algorithms Comparison (Manhattan Heuristic)')
        ax.set_xticks(x)
        ax.set_xticklabels(all_search_algos, rotation=25)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        annotate_bars(ax, bars, fontsize=8)
        plt.tight_layout()
        plt.savefig("reports/figures/maze_all_algos_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/maze_all_algos_comparison.png")

        # 3b. Maze Node Scaling (10x10 vs 30x30 vs 50x50)
        maze_sizes = ["maze 10x10", "maze 30x30", "maze 50x50"]
        unique_algos = sorted(list(set(r[0].split("/")[0].strip() for r in csv_maze)))
        if len(unique_algos) > 0:
            fig, ax = plt.subplots(figsize=(14, 6))
            x = np.arange(len(unique_algos))
            width = 0.25
            colors = ['#55A868', '#DD8452', '#C44E52']

            for i, sz in enumerate(maze_sizes):
                sz_nodes = []
                for algo in unique_algos:
                    match = next((r for r in csv_maze if algo in r[0] and sz in r[0]), None)
                    sz_nodes.append(int(float(match[3])) if match else 0)
                offset = (i - 1) * width
                ax.bar(x + offset, sz_nodes, width, label=sz.upper(), color=colors[i])

            ax.set_yscale('log')
            ax.set_ylabel('Nodes Expanded (Log Scale)')
            ax.set_title('Maze Pathfinding Grid Scaling (10×10 vs 30×30 vs 50×50 Grid)')
            ax.set_xticks(x)
            ax.set_xticklabels(unique_algos, rotation=25)
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("reports/figures/maze_scaling_comparison.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/maze_scaling_comparison.png")

        # 3c. Maze Runtime Execution Time Scaling (in ms)
        if len(unique_algos) > 0:
            fig, ax = plt.subplots(figsize=(14, 6))
            x = np.arange(len(unique_algos))
            width = 0.25
            colors = ['#4C72B0', '#55A868', '#C44E52']

            for i, sz in enumerate(maze_sizes):
                sz_times = []
                for algo in unique_algos:
                    match = next((r for r in csv_maze if algo in r[0] and sz in r[0]), None)
                    sz_times.append(float(match[5]) * 1000.0 if match else 0.0) # Convert to ms
                offset = (i - 1) * width
                ax.bar(x + offset, sz_times, width, label=sz.upper(), color=colors[i])

            ax.set_yscale('log')
            ax.set_ylabel('Runtime (ms, Log Scale)')
            ax.set_title('Maze Pathfinding Execution Time (ms) Scaling Across Grid Sizes')
            ax.set_xticks(x)
            ax.set_xticklabels(unique_algos, rotation=25)
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("reports/figures/maze_runtime_scaling.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/maze_runtime_scaling.png")

    # 4. Local Search & Optimization Comparison (TSP & N-Queens)
    csv_tsp = read_csv_data("results/local_search_tsp.csv")
    if csv_tsp:
        opt_algos = [r[0].split("/")[0].strip() for r in csv_tsp]
        tsp_tour_costs = [float(r[2]) for r in csv_tsp]

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(opt_algos))
        bars = ax.bar(x, tsp_tour_costs, color=['#C44E52', '#55A868', '#4C72B0', '#8172B3'][:len(opt_algos)], width=0.5)
        ax.set_ylabel('Optimal Tour Distance (2-Opt Distance, Lower is Better)')
        ax.set_title('TSP Optimization: Genetic Algorithm vs Local Search (20 Cities)')
        ax.set_xticks(x)
        ax.set_xticklabels(opt_algos, rotation=15)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig("reports/figures/local_search_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/local_search_comparison.png")

    csv_nq = read_csv_data("results/local_search_nqueens.csv")
    if csv_nq:
        nq_algos = [r[0].split("/")[0].strip() for r in csv_nq]
        nq_scores = [float(r[2]) for r in csv_nq]

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(nq_algos))
        bars = ax.bar(x, nq_scores, color=['#55A868', '#4C72B0', '#DD8452', '#8172B3'][:len(nq_algos)], width=0.5)
        ax.set_ylabel('Non-Attacking Queen Pairs (Higher is Better, Max=28)')
        ax.set_title('8-Queens Optimization: Local Search & Genetic Algorithm')
        ax.set_ylim(20, 30)
        ax.set_xticks(x)
        ax.set_xticklabels(nq_algos, rotation=15)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig("reports/figures/nqueens_local_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/nqueens_local_comparison.png")

    # 5. CSP Benchmark Comparison Chart (from raw per-run CSV format)
    csv_csp = read_csv_data("results/csp_benchmarks.csv")
    if csv_csp:
        # Aggregate raw rows by label: group by Label, compute mean nodes and mean runtime
        from collections import defaultdict
        csp_groups = defaultdict(list)
        for r in csv_csp:
            if len(r) >= 7:
                csp_groups[r[0]].append(r)

        # Extract 8-Queens entries for the main chart
        csp_labels = []
        csp_nodes = []
        csp_times_ms = []
        for label, rows in sorted(csp_groups.items()):
            if "8-Queens" in label:
                solver_name = label.split("/")[0].strip()
                successful_rows = [r for r in rows if r[2].strip().lower() in ("true", "1")]
                if successful_rows:
                    avg_nodes = sum(int(float(r[4])) for r in successful_rows) / len(successful_rows)
                    avg_time = sum(float(r[6]) for r in successful_rows) / len(successful_rows) * 1000.0
                else:
                    avg_nodes = 0
                    avg_time = 0
                csp_labels.append(solver_name)
                csp_nodes.append(avg_nodes)
                csp_times_ms.append(avg_time)

        if csp_labels:
            # Nodes Chart
            fig, ax = plt.subplots(figsize=(12, 6))
            x = np.arange(len(csp_labels))
            colors = ['#C44E52', '#DD8452', '#4C72B0', '#55A868', '#8172B3', '#CCB974',
                       '#64B5CD', '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF', '#AEC7E8']
            bars = ax.bar(x, csp_nodes, color=colors[:len(csp_labels)])
            ax.set_ylabel('Avg Nodes Expanded')
            ax.set_title('8-Queens CSP Solver Comparison: Nodes Expanded')
            ax.set_xticks(x)
            ax.set_xticklabels(csp_labels, rotation=25, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            annotate_bars(ax, bars, fontsize=8)
            plt.tight_layout()
            plt.savefig("reports/figures/csp_benchmark_summary.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/csp_benchmark_summary.png")

            # Runtime Chart
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(x, csp_times_ms, color=colors[:len(csp_labels)])
            ax.set_ylabel('Avg Execution Time (ms)')
            ax.set_title('8-Queens CSP Solver Execution Speed (ms)')
            ax.set_xticks(x)
            ax.set_xticklabels(csp_labels, rotation=25, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.annotate(f"{h:.2f}ms", xy=(bar.get_x() + bar.get_width() / 2, h),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')
            plt.tight_layout()
            plt.savefig("reports/figures/csp_runtime_summary.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/csp_runtime_summary.png")

        # CSP Cross-Domain Grouped Bar Chart
        csp_domains_set = sorted(set(label.split("/")[1].strip() for label in csp_groups.keys() if "/" in label))
        csp_solvers_set = sorted(set(label.split("/")[0].strip() for label in csp_groups.keys() if "/" in label))
        if len(csp_domains_set) > 1 and len(csp_solvers_set) > 1:
            fig, ax = plt.subplots(figsize=(14, 7))
            x = np.arange(len(csp_solvers_set))
            width = 0.8 / max(1, len(csp_domains_set))
            domain_colors = ['#4C72B0', '#55A868', '#DD8452', '#C44E52', '#8172B3']

            for i, domain in enumerate(csp_domains_set):
                nodes_list = []
                for solver in csp_solvers_set:
                    label_key = f"{solver} / {domain}"
                    if label_key in csp_groups:
                        successful = [r for r in csp_groups[label_key] if r[2].strip().lower() in ("true", "1")]
                        avg_n = sum(int(float(r[4])) for r in successful) / len(successful) if successful else 0
                    else:
                        avg_n = 0
                    nodes_list.append(avg_n)
                offset = (i - len(csp_domains_set) / 2 + 0.5) * width
                ax.bar(x + offset, nodes_list, width, label=domain, color=domain_colors[i % len(domain_colors)])

            ax.set_yscale('log')
            ax.set_ylabel('Avg Nodes Expanded (Log Scale)')
            ax.set_title('CSP Solver Comparison Across All Domains')
            ax.set_xticks(x)
            ax.set_xticklabels(csp_solvers_set, rotation=30, ha='right')
            ax.legend(fontsize=8)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("reports/figures/csp_cross_domain.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/csp_cross_domain.png")

    # 5b. Heuristic Comparison Chart (A* on 8-puzzle: misplaced vs manhattan vs pattern_db)
    if csv_8p:
        heuristic_rows = [r for r in csv_8p if "(" in r[0] and "8pzl medium" in r[0]]
        if heuristic_rows:
            h_labels = [r[0].split("/")[0].strip() for r in heuristic_rows]
            h_nodes = [int(float(r[4])) for r in heuristic_rows]
            h_times = [float(r[6]) * 1000.0 for r in heuristic_rows]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            x = np.arange(len(h_labels))
            colors_h = ['#C44E52', '#DD8452', '#55A868', '#4C72B0', '#8172B3', '#CCB974']

            bars1 = ax1.bar(x, h_nodes, color=colors_h[:len(h_labels)])
            ax1.set_ylabel('Nodes Expanded')
            ax1.set_title('Heuristic Comparison: Nodes Expanded (8-Puzzle Medium)')
            ax1.set_xticks(x)
            ax1.set_xticklabels(h_labels, rotation=20, ha='right')
            ax1.grid(axis='y', linestyle='--', alpha=0.7)
            annotate_bars(ax1, bars1, fontsize=8)

            bars2 = ax2.bar(x, h_times, color=colors_h[:len(h_labels)])
            ax2.set_ylabel('Runtime (ms)')
            ax2.set_title('Heuristic Comparison: Runtime (8-Puzzle Medium)')
            ax2.set_xticks(x)
            ax2.set_xticklabels(h_labels, rotation=20, ha='right')
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
            for bar in bars2:
                h = bar.get_height()
                if h > 0:
                    ax2.annotate(f"{h:.2f}ms", xy=(bar.get_x() + bar.get_width() / 2, h),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')

            plt.tight_layout()
            plt.savefig("reports/figures/heuristic_comparison_8puzzle.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/heuristic_comparison_8puzzle.png")

    # 6. Game Tournament Winrates Chart
    csv_game = read_csv_data("results/game_tournament.csv")
    if csv_game:
        matchups = [f"{r[1]}\nvs\n{r[2]}" for r in csv_game]
        game_names = [r[0] for r in csv_game]
        winrates_p1 = []
        for r in csv_game:
            w1 = float(r[3])
            w2 = float(r[4])
            d = float(r[5])
            total = w1 + w2 + d
            rate = (w1 / total * 100) if total > 0 else 0
            winrates_p1.append(rate)

        fig, ax = plt.subplots(figsize=(12, 6.5))
        x = np.arange(len(matchups))
        colors_g = ['#55A868', '#4C72B0', '#DD8452', '#8172B3', '#CCB974', '#C44E52',
                     '#64B5CD', '#E377C2', '#7F7F7F', '#BCBD22']
        bars = ax.bar(x, winrates_p1, color=[colors_g[i % len(colors_g)] for i in range(len(matchups))], width=0.45)
        ax.set_ylabel('Agent 1 Win Rate (%)')
        ax.set_title('Adversarial Game Tournament Performance & Win Rates')
        ax.set_ylim(0, 125)
        ax.set_xticks(x)
        ax.set_xticklabels(matchups, rotation=0, fontsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for i, bar in enumerate(bars):
            height = bar.get_height()
            g_name = game_names[i] if i < len(game_names) else ""
            ax.annotate(f'[{g_name}]\n{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=7, fontweight='bold')

        plt.tight_layout()
        plt.savefig("reports/figures/game_tournament_winrates.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/game_tournament_winrates.png")

    print("\nReport figure generation complete.")


if __name__ == "__main__":
    generate_reports_and_charts()
