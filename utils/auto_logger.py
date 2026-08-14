import sys
import os

def auto_log_result(solver, result):
    """
    Automatically logs a solver's result to the correct CSV file.
    Does not log if it's running via benchmark scripts to avoid double-logging.
    """
    # Don't double-log if running from benchmarks
    if any("benchmark" in arg for arg in sys.argv):
        return

    try:
        from core.result import Result
        if not isinstance(result, Result):
            return

        from benchmarks.benchmark import append_result_to_csv
        csv_path = None
        label = f"{solver.__class__.__name__}"
        
        if hasattr(solver, 'problem'):
            prob_name = type(solver.problem).__name__
            if 'TSP' in prob_name:
                csv_path = "results/local_search_tsp.csv"
                cities = len(getattr(solver.problem, 'cities', []))
                label += f" / TSP {cities} (Demo)"
                if result.solution:
                    result.path_cost = -solver.problem.value(result.solution.state)
            elif 'NQueens' in prob_name:
                csv_path = "results/local_search_nqueens.csv"
                n = getattr(solver.problem, 'n', 8)
                label += f" / N-Queens {n} (Demo)"
                if result.solution:
                    result.path_cost = solver.problem.value(result.solution.state)
            elif 'Maze' in prob_name:
                csv_path = "results/search_maze.csv"
                grid = getattr(solver.problem, 'grid', [])
                w = len(grid[0]) if grid else 0
                h = len(grid) if grid else 0
                label += f" / Maze {w}x{h} (Demo)"
            elif 'NPuzzle' in prob_name:
                n = getattr(solver.problem, 'n', 3)
                if n == 3:
                    csv_path = "results/search_8puzzle.csv"
                    label += f" / 8-puzzle (Demo)"
                else:
                    csv_path = "results/search_15puzzle.csv"
                    label += f" / 15-puzzle (Demo)"
            else:
                csv_path = "results/other_search.csv"
                label += f" / {prob_name} (Demo)"

        if csv_path:
            append_result_to_csv(csv_path, label, 1, result)
    except Exception as e:
        print(f"[Warning] Auto-logging failed: {e}")

def auto_log_csp(solver, assignment, runtime):
    if any("benchmark" in arg for arg in sys.argv):
        return
    try:
        from core.result import Result
        from benchmarks.benchmark import append_result_to_csv
        
        success = assignment is not None and len(assignment) > 0
        res = Result(
            success=success,
            runtime=runtime,
            nodes_expanded=getattr(solver, "nodes_expanded", 0),
            nodes_generated=getattr(solver, "nodes_generated", 0),
            path_cost=1.0 if success else 0.0,
        )
        
        prob_name = type(solver.problem).__name__ if hasattr(solver, 'problem') else "CSP"
        label = f"{solver.__class__.__name__} / {prob_name} (Demo)"
        
        append_result_to_csv("results/csp_benchmarks.csv", label, 1, res)
    except Exception as e:
        print(f"[Warning] CSP Auto-logging failed: {e}")

def auto_log_game(game_name, p1_name, p2_name, winner, runtime):
    if any("benchmark" in arg for arg in sys.argv):
        return
    try:
        from benchmarks.benchmark import append_result_to_csv, _timestamp
        import csv
        import os
        
        csv_path = "results/game_tournament.csv"
        os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
        write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
        
        p1_wins = 1 if winner == 1 else 0
        p2_wins = 1 if winner == -1 else 0
        draws = 1 if winner == 0 else 0
        
        row = [game_name, p1_name, p2_name, p1_wins, p2_wins, draws, round(runtime, 6)]
        
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["Game", "Agent 1", "Agent 2", "Agent 1 Wins", "Agent 2 Wins", "Draws", "Avg Game Time (s)"])
            writer.writerow(row)
    except Exception as e:
        print(f"[Warning] Game Auto-logging failed: {e}")

