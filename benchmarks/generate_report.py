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

    # 1. 8-Puzzle Hard Nodes & Runtime Chart (Dual Axis)
    csv_8p = read_csv_data("results/search_8puzzle.csv")
    if csv_8p:
        hard_rows = [r for r in csv_8p if "8pzl hard" in r[0] and r[2].strip().lower() in ("true", "1")]
        if not hard_rows:
            hard_rows = [r for r in csv_8p if "8pzl medium" in r[0] and r[2].strip().lower() in ("true", "1")] or csv_8p
        from collections import defaultdict
        groups = defaultdict(list)
        # Filter out Misplaced_Tile and Manhattan so the chart isn't too cluttered
        for r in hard_rows:
            algo = r[0].split("/")[0].strip()
            if "Misplaced" not in algo and "Manhattan" not in algo:
                groups[algo].append(r)
        algos_8p = list(groups.keys())
        nodes_8p_hard = [sum(int(float(r[4])) for r in groups[a])/len(groups[a]) for a in algos_8p]
        times_8p_ms = [sum(float(r[6])*1000.0 for r in groups[a])/len(groups[a]) for a in algos_8p]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        x = np.arange(len(algos_8p))
        
        bars1 = ax1.bar(x, nodes_8p_hard, color=['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#CCB974'][:len(algos_8p)], alpha=0.8)
        bars2 = ax2.bar(x, times_8p_ms, color=['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#CCB974'][:len(algos_8p)], alpha=0.8)
        
        ax1.set_yscale('log')
        ax2.set_yscale('log')
        ax1.set_ylabel('Nodes Expanded (Log Scale)')
        ax2.set_ylabel('Execution Time (ms) (Log Scale)')
        ax1.set_title('8-Puzzle Instance: Nodes')
        ax2.set_title('8-Puzzle Instance: Time')
        
        for ax in (ax1, ax2):
            ax.set_xticks(x)
            ax.set_xticklabels(algos_8p, rotation=45, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
        annotate_bars(ax1, bars1, fontsize=8)
        annotate_bars(ax2, bars2, fontsize=8)
        
        plt.tight_layout(pad=2.0)
        plt.savefig("reports/figures/search_nodes_expanded.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/search_nodes_expanded.png")

        # 1b. 8-Puzzle Multi-Difficulty Scaling (Easy vs Medium vs Hard)
        diffs = ["8pzl easy", "8pzl medium", "8pzl hard"]
        all_algos = sorted(list(set(r[0].split("/")[0].strip() for r in csv_8p if "Misplaced" not in r[0] and "Manhattan" not in r[0])))
        if len(all_algos) > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 8))
            x = np.arange(len(all_algos))
            width = 0.25
            colors_bar = ['#55A868', '#DD8452', '#C44E52']

            for i, diff in enumerate(diffs):
                diff_nodes = []
                diff_times = []
                for algo in all_algos:
                    matches = [r for r in csv_8p if algo in r[0] and diff in r[0] and r[2].strip().lower() in ("true", "1")]
                    diff_nodes.append(sum(int(float(m[4])) for m in matches)/len(matches) if matches else 0)
                    diff_times.append(sum(float(m[6])*1000.0 for m in matches)/len(matches) if matches else 0)
                
                offset = (i - 1) * width
                ax1.bar(x + offset, diff_nodes, width, label=f'{diff.upper()}', color=colors_bar[i], alpha=0.8)
                ax2.bar(x + offset, diff_times, width, label=f'{diff.upper()}', color=colors_bar[i], alpha=0.8)

            ax1.set_yscale('log')
            ax2.set_yscale('log')
            ax1.set_ylabel('Nodes Expanded (Log Scale)')
            ax2.set_ylabel('Execution Time (ms) (Log Scale)')
            ax1.set_title('8-Puzzle Scaling: Nodes')
            ax2.set_title('8-Puzzle Scaling: Time')
            
            for ax in (ax1, ax2):
                ax.set_xticks(x)
                ax.set_xticklabels(all_algos, rotation=45, ha='right')
                ax.legend()
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                
            plt.tight_layout(pad=2.0)
            plt.savefig("reports/figures/8puzzle_all_instances.png", dpi=300, bbox_inches='tight')
            plt.close()
            print("  [OK] Saved reports/figures/8puzzle_all_instances.png")

    # 2. 15-Puzzle Informed Search Comparison Chart (Dual Axis)
    csv_15p = read_csv_data("results/search_15puzzle.csv")
    if csv_15p:
        hard_15p_rows = [r for r in csv_15p if "15pzl hard" in r[0] and r[2].strip().lower() in ("true", "1")] or csv_15p
        groups = defaultdict(list)
        for r in hard_15p_rows: 
            groups[r[0].split("/")[0].strip()].append(r)
        algos_15p = list(groups.keys())
        nodes_15p = [sum(int(float(r[4])) for r in groups[a])/len(groups[a]) for a in algos_15p]
        times_15p = [sum(float(r[6])*1000.0 for r in groups[a])/len(groups[a]) for a in algos_15p]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        x = np.arange(len(algos_15p))
        
        bars1 = ax1.bar(x, nodes_15p, color=['#55A868', '#C44E52', '#4C72B0', '#DD8452', '#8172B3', '#CCB974'][:len(algos_15p)], alpha=0.8)
        bars2 = ax2.bar(x, times_15p, color=['#55A868', '#C44E52', '#4C72B0', '#DD8452', '#8172B3', '#CCB974'][:len(algos_15p)], alpha=0.8)
        
        ax1.set_yscale('log')
        ax2.set_yscale('log')
        ax1.set_ylabel('Nodes Expanded (Log Scale)')
        ax2.set_ylabel('Execution Time (ms) (Log Scale)')
        ax1.set_title('15-Puzzle Hard Instance: Nodes')
        ax2.set_title('15-Puzzle Hard Instance: Time')
        
        for ax in (ax1, ax2):
            ax.set_xticks(x)
            ax.set_xticklabels(algos_15p, rotation=45, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
        annotate_bars(ax1, bars1, fontsize=8)
        annotate_bars(ax2, bars2, fontsize=8)
        
        plt.tight_layout(pad=2.0)
        plt.savefig("reports/figures/puzzles_15_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/puzzles_15_comparison.png")

        # 2b. 15-Puzzle Medium vs Hard Multi-Instance
        diffs_15 = ["15pzl medium", "15pzl hard"]
        algos_15_list = sorted(list(set(r[0].split("/")[0].strip() for r in csv_15p)))
        if len(algos_15_list) > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 8))
            x = np.arange(len(algos_15_list))
            width = 0.35
            colors_bar = ['#4C72B0', '#C44E52']

            for i, diff in enumerate(diffs_15):
                nodes_list = []
                times_list = []
                for algo in algos_15_list:
                    matches = [r for r in csv_15p if algo in r[0] and diff in r[0] and r[2].strip().lower() in ("true", "1")]
                    nodes_list.append(sum(int(float(m[4])) for m in matches)/len(matches) if matches else 0)
                    times_list.append(sum(float(m[6])*1000.0 for m in matches)/len(matches) if matches else 0)
                
                offset = (i - 0.5) * width
                ax1.bar(x + offset, nodes_list, width, label=f'{diff.upper()}', color=colors_bar[i], alpha=0.8)
                ax2.bar(x + offset, times_list, width, label=f'{diff.upper()}', color=colors_bar[i], alpha=0.8)

            ax1.set_yscale('log')
            ax2.set_yscale('log')
            ax1.set_ylabel('Nodes Expanded (Log Scale)')
            ax2.set_ylabel('Execution Time (ms) (Log Scale)')
            ax1.set_title('15-Puzzle Scaling: Nodes')
            ax2.set_title('15-Puzzle Scaling: Time')
            
            for ax in (ax1, ax2):
                ax.set_xticks(x)
                ax.set_xticklabels(algos_15_list, rotation=45, ha='right')
                ax.legend()
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                
            plt.tight_layout(pad=2.0)
            plt.savefig("reports/figures/15puzzle_all_instances.png", dpi=300, bbox_inches='tight')
            plt.close()
            print("  [OK] Saved reports/figures/15puzzle_all_instances.png")

    # 3. Maze Pathfinding Across ALL Search Algorithms & Runtime Scaling
    csv_maze = read_csv_data("results/search_maze.csv")
    if csv_maze:
        maze_50_rows = [r for r in csv_maze if "maze 50x50" in r[0] and r[2].strip().lower() in ("true", "1")] or csv_maze
        groups = defaultdict(list)
        for r in maze_50_rows: groups[r[0].split("/")[0].strip()].append(r)
        all_search_algos = list(groups.keys())
        nodes_maze_50 = [sum(int(float(r[4])) for r in groups[a])/len(groups[a]) for a in all_search_algos]

        fig, ax = plt.subplots(figsize=(16, 8))
        x = np.arange(len(all_search_algos))
        bars = ax.bar(x, nodes_maze_50, color=['#C44E52']*5 + ['#55A868']*6)
        ax.set_yscale('log')
        ax.set_ylabel('Nodes Expanded (Log Scale)')
        ax.set_title('50×50 Maze Pathfinding: ALL Search Algorithms Comparison (Manhattan Heuristic)')
        ax.set_xticks(x)
        ax.set_xticklabels(all_search_algos, rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        annotate_bars(ax, bars, fontsize=8)
        plt.tight_layout(pad=2.0)
        plt.savefig("reports/figures/maze_all_algos_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/maze_all_algos_comparison.png")

        # 3b. Maze Node & Runtime Scaling (Uninformed vs Informed)
        maze_sizes = ["maze 10x10", "maze 30x30", "maze 50x50"]
        unique_algos = sorted(list(set(r[0].split("/")[0].strip() for r in csv_maze)))
        uninformed_algos = [a for a in unique_algos if "(" not in a and "GBFS" not in a]
        informed_algos = [a for a in unique_algos if "(" in a or "GBFS" in a]

        def plot_maze_scaling(algo_subset, filename_prefix, title_suffix):
            if not algo_subset: return
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 8))
            x = np.arange(len(algo_subset))
            width = 0.25
            colors_bar = ['#55A868', '#DD8452', '#C44E52']

            for i, sz in enumerate(maze_sizes):
                sz_nodes = []
                sz_times = []
                for algo in algo_subset:
                    matches = [r for r in csv_maze if algo in r[0] and sz in r[0] and r[2].strip().lower() in ("true", "1")]
                    sz_nodes.append(sum(int(float(m[4])) for m in matches)/len(matches) if matches else 0)
                    sz_times.append(sum(float(m[6])*1000.0 for m in matches)/len(matches) if matches else 0)
                
                offset = (i - 1) * width
                ax1.bar(x + offset, sz_nodes, width, label=f'{sz.upper()}', color=colors_bar[i], alpha=0.8)
                ax2.bar(x + offset, sz_times, width, label=f'{sz.upper()}', color=colors_bar[i], alpha=0.8)

            ax1.set_yscale('log')
            ax2.set_yscale('log')
            ax1.set_ylabel('Nodes Expanded (Log Scale)')
            ax2.set_ylabel('Execution Time (ms) (Log Scale)')
            ax1.set_title(f'Maze Grid Scaling {title_suffix}: Nodes')
            ax2.set_title(f'Maze Grid Scaling {title_suffix}: Time')
            
            for ax in (ax1, ax2):
                ax.set_xticks(x)
                ax.set_xticklabels(algo_subset, rotation=45, ha='right')
                ax.legend()
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                
            plt.tight_layout(pad=2.0)
            plt.savefig(f"reports/figures/{filename_prefix}.png", dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  [OK] Saved reports/figures/{filename_prefix}.png")

        plot_maze_scaling(uninformed_algos, "maze_scaling_uninformed", "(Uninformed)")
        plot_maze_scaling(informed_algos, "maze_scaling_informed", "(Informed)")

    # 4. Local Search & Optimization Comparison (TSP & N-Queens)
    csv_tsp = read_csv_data("results/local_search_tsp.csv")
    if csv_tsp:
        from collections import defaultdict
        tsp_groups = defaultdict(list)
        for r in csv_tsp:
            if len(r) > 3 and r[2].strip().lower() in ("true", "1"):
                tsp_groups[r[0].split("/")[0].strip()].append(abs(float(r[3])))
                
        opt_algos = list(tsp_groups.keys())
        tsp_tour_costs = [sum(v)/len(v) for v in tsp_groups.values()]
        fig, ax = plt.subplots(figsize=(16, 8))
        x = np.arange(len(opt_algos))
        bars = ax.bar(x, tsp_tour_costs, color=['#C44E52', '#55A868', '#4C72B0', '#8172B3'][:len(opt_algos)], width=0.5)
        ax.set_ylabel('Optimal Tour Distance (2-Opt Distance, Lower is Better)')
        ax.set_title('TSP Optimization: Genetic Algorithm vs Local Search (20 Cities)')
        ax.set_xticks(x)
        ax.set_xticklabels(opt_algos, rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout(pad=2.0)
        plt.savefig("reports/figures/local_search_comparison.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/local_search_comparison.png")

    csv_nq = read_csv_data("results/local_search_nqueens.csv")
    if csv_nq:
        from collections import defaultdict
        nq_groups = defaultdict(list)
        for r in csv_nq:
            if len(r) > 3 and r[2].strip().lower() in ("true", "1"):
                nq_groups[r[0].split("/")[0].strip()].append(float(r[3]))
                
        nq_algos = list(nq_groups.keys())
        nq_scores = [sum(v)/len(v) for v in nq_groups.values()]

        fig, ax = plt.subplots(figsize=(16, 8))
        x = np.arange(len(nq_algos))
        bars = ax.bar(x, nq_scores, color=['#55A868', '#4C72B0', '#DD8452', '#8172B3'][:len(nq_algos)], width=0.5)
        ax.set_ylabel('Non-Attacking Queen Pairs (Higher is Better, Max=28)')
        ax.set_title('8-Queens Optimization: Local Search & Genetic Algorithm')
        ax.set_ylim(20, 30)
        ax.set_xticks(x)
        ax.set_xticklabels(nq_algos, rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout(pad=2.0)
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
            fig, ax = plt.subplots(figsize=(16, 8))
            x = np.arange(len(csp_labels))
            colors = ['#C44E52', '#DD8452', '#4C72B0', '#55A868', '#8172B3', '#CCB974',
                       '#64B5CD', '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF', '#AEC7E8']
            bars = ax.bar(x, csp_nodes, color=colors[:len(csp_labels)])
            ax.set_ylabel('Avg Nodes Expanded')
            ax.set_title('8-Queens CSP Solver Comparison: Nodes Expanded')
            ax.set_xticks(x)
            ax.set_xticklabels(csp_labels, rotation=45, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            annotate_bars(ax, bars, fontsize=8)
            plt.tight_layout(pad=2.0)
            plt.savefig("reports/figures/csp_benchmark_summary.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/csp_benchmark_summary.png")

            # Runtime Chart
            fig, ax = plt.subplots(figsize=(16, 8))
            bars = ax.bar(x, csp_times_ms, color=colors[:len(csp_labels)])
            ax.set_ylabel('Avg Execution Time (ms)')
            ax.set_title('8-Queens CSP Solver Execution Speed (ms)')
            ax.set_xticks(x)
            ax.set_xticklabels(csp_labels, rotation=45, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.annotate(f"{h:.2f}ms", xy=(bar.get_x() + bar.get_width() / 2, h),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')
            plt.tight_layout(pad=2.0)
            plt.savefig("reports/figures/csp_runtime_summary.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/csp_runtime_summary.png")

        # CSP Cross-Domain Grouped Bar Chart
        csp_domains_set = sorted(set(label.split("/")[1].strip() for label in csp_groups.keys() if "/" in label))
        csp_solvers_set = sorted(set(label.split("/")[0].strip() for label in csp_groups.keys() if "/" in label))
        if len(csp_domains_set) > 1 and len(csp_solvers_set) > 1:
            fig, ax = plt.subplots(figsize=(16, 8))
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
            ax.set_xticklabels(csp_solvers_set, rotation=45, ha='right')
            ax.legend(fontsize=8)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout(pad=2.0)
            plt.savefig("reports/figures/csp_cross_domain.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/csp_cross_domain.png")

    # 5b. Heuristic Comparison Chart (A* on 8-puzzle: misplaced vs manhattan vs pattern_db)
    if csv_8p:
        heuristic_rows = [r for r in csv_8p if "(" in r[0] and "SMA*" not in r[0] and "8pzl medium" in r[0]]
        if heuristic_rows:
            from collections import defaultdict
            h_nodes_map = defaultdict(list)
            h_times_map = defaultdict(list)
            for r in heuristic_rows:
                label = r[0].split("/")[0].strip()
                h_nodes_map[label].append(int(float(r[4])))
                h_times_map[label].append(float(r[6]) * 1000.0)
                
            h_labels = list(h_nodes_map.keys())
            h_nodes = [sum(v)/len(v) for v in h_nodes_map.values()]
            h_times = [sum(v)/len(v) for v in h_times_map.values()]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            x = np.arange(len(h_labels))
            colors_h = ['#C44E52', '#DD8452', '#55A868', '#4C72B0', '#8172B3', '#CCB974']

            bars1 = ax1.bar(x, h_nodes, color=colors_h[:len(h_labels)])
            ax1.set_ylabel('Nodes Expanded')
            ax1.set_title('Heuristic Comparison: Nodes Expanded (8-Puzzle Medium)')
            ax1.set_xticks(x)
            ax1.set_xticklabels(h_labels, rotation=45, ha='right')
            ax1.grid(axis='y', linestyle='--', alpha=0.7)
            annotate_bars(ax1, bars1, fontsize=8)

            bars2 = ax2.bar(x, h_times, color=colors_h[:len(h_labels)])
            ax2.set_ylabel('Runtime (ms)')
            ax2.set_title('Heuristic Comparison: Runtime (8-Puzzle Medium)')
            ax2.set_xticks(x)
            ax2.set_xticklabels(h_labels, rotation=45, ha='right')
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
            for bar in bars2:
                h = bar.get_height()
                if h > 0:
                    ax2.annotate(f"{h:.2f}ms", xy=(bar.get_x() + bar.get_width() / 2, h),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')

            plt.tight_layout(pad=2.0)
            plt.savefig("reports/figures/heuristic_comparison_8puzzle.png", dpi=300)
            plt.close()
            print("  [OK] Saved reports/figures/heuristic_comparison_8puzzle.png")

    # 6. Game Tournament Winrates Chart
    csv_game = read_csv_data("results/game_tournament.csv")
    if csv_game:
        matchups = [f"[{r[0]}]\n{r[1]} vs {r[2]}" for r in csv_game]
        p1_rates = []
        p2_rates = []
        draw_rates = []
        for r in csv_game:
            w1 = float(r[3])
            w2 = float(r[4])
            d = float(r[5])
            total = w1 + w2 + d
            if total > 0:
                p1_rates.append(w1 / total * 100)
                p2_rates.append(w2 / total * 100)
                draw_rates.append(d / total * 100)
            else:
                p1_rates.append(0)
                p2_rates.append(0)
                draw_rates.append(0)

        fig, ax = plt.subplots(figsize=(14, max(6, len(matchups) * 0.5)))
        y = np.arange(len(matchups))
        
        # P1 Wins (Green)
        b1 = ax.barh(y, p1_rates, color='#55A868', label='Agent 1 Wins')
        # Draws (Gray)
        b2 = ax.barh(y, draw_rates, left=p1_rates, color='#7F7F7F', label='Draws')
        # P2 Wins (Red)
        b3 = ax.barh(y, p2_rates, left=np.array(p1_rates)+np.array(draw_rates), color='#C44E52', label='Agent 2 Wins')
        
        ax.set_xlabel('Outcome Percentage (%)')
        ax.set_title('Adversarial Game Tournament Performance (100% Stacked)')
        ax.set_xlim(0, 100)
        ax.set_yticks(y)
        ax.set_yticklabels(matchups, fontsize=9)
        ax.invert_yaxis()
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.05))
        
        # Annotate
        for bars, rates in zip([b1, b2, b3], [p1_rates, draw_rates, p2_rates]):
            for bar, rate in zip(bars, rates):
                if rate > 5:
                    ax.annotate(f"{rate:.0f}%",
                                xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2),
                                xytext=(0, 0), textcoords="offset points",
                                ha='center', va='center', color='white', fontweight='bold', fontsize=8)

        plt.tight_layout(pad=2.0)
        plt.savefig("reports/figures/game_tournament_winrates.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("  [OK] Saved reports/figures/game_tournament_winrates.png")

    csv_online = read_csv_data("results/online_search_maze.csv")
    if csv_online and len(csv_online) > 1:
        fig, ax = plt.subplots(figsize=(12, 7))
        
        mazes = {}
        for r in csv_online:
            maze_id = r[0]
            trial = int(r[1])
            cost = int(r[2])
            if maze_id not in mazes:
                mazes[maze_id] = {'trials': [], 'costs': []}
            mazes[maze_id]['trials'].append(trial)
            mazes[maze_id]['costs'].append(cost)
            
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, (maze_id, data) in enumerate(mazes.items()):
            c = colors[i % len(colors)]
            ax.plot(data['trials'], data['costs'], marker='o', linestyle='-', color=c, label=maze_id, linewidth=2.5, markersize=6)
            
        ax.set_xlabel('Trial Number', fontweight='bold', fontsize=11)
        ax.set_ylabel('Path Cost (Steps)', fontweight='bold', fontsize=11)
        ax.set_title('LRTA* Learning Curve across 5 Unknown Mazes (20x20)', fontweight='bold', fontsize=14)
        ax.set_xticks(range(1, 21))
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(title='Random Mazes', loc='upper right')
        
        plt.tight_layout(pad=2.0)
        plt.savefig("reports/figures/online_search_learning_curve.png", dpi=300)
        plt.close()
        print("  [OK] Saved reports/figures/online_search_learning_curve.png")

    print("\nReport figure generation complete.")


if __name__ == "__main__":
    generate_reports_and_charts()
