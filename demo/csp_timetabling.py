# =====================================================================
# TWEAKABLE CONFIGURATION - Modify these variables to test variations!
# =====================================================================
# Solvers available:   BacktrackingSolver, MinConflictsSolver
# Heuristics available: mrv, mrv_with_degree_heuristic, lcv, None
# Inferences available: mac, forward_checking, None
# =====================================================================

import sys
import time
from domains.timetabling.Timetabling import TimetablingCSP
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.MAC import mac
from csp.inference.ForwardChecking import forward_checking
from visualization.TimetablingVisualizer import TimetablingVisualizer, DEFAULT_CLASSES, DEFAULT_ROOMS, DEFAULT_TIMESLOTS

# ── User Configuration ────────────────────────────────────────────────
CHOSEN_SOLVER = BacktrackingSolver
CHOSEN_HEURISTIC = mrv_with_degree_heuristic  # Options: mrv, mrv_with_degree_heuristic, None
CHOSEN_INFERENCE = mac                        # Options: mac, forward_checking, None
VISUALIZE = True                              # Set to False for text-only output


def solve_timetabling(visualize=True):
    print("\n--- University Timetabling CSP Demo ---")
    
    classes = DEFAULT_CLASSES
    rooms = DEFAULT_ROOMS
    timeslots = DEFAULT_TIMESLOTS
    
    try:
        problem = TimetablingCSP(classes, rooms, timeslots)
    except ValueError as e:
        print(f"Error: {e}")
        return
        
    print(f"Scheduling {len(classes)} classes into {len(rooms)} rooms and {len(timeslots)} timeslots...")
    
    solver = CHOSEN_SOLVER(
        problem,
        select_unassigned_variable=CHOSEN_HEURISTIC,
        order_domain_values=order_domain_values_default,
        inference=CHOSEN_INFERENCE
    )
    
    start = time.time()
    solution = solver.solve()
    duration = time.time() - start
    
    if solver.status == "SUCCESS":
        print(f"Solution found in {duration:.4f} seconds! (Nodes expanded: {solver.nodes_expanded})")
        print("\nSchedule:")
        schedule_by_time = {t: [] for t in timeslots}
        for cls_id, (room, timeslot) in solution.items():
            schedule_by_time[timeslot].append(f"{cls_id:8} (Room: {room:6})")
            
        for t in timeslots:
            print(f"\n[{t}]")
            for item in schedule_by_time[t]:
                print(f"  {item}")
    else:
        print(f"NO SOLUTION EXISTS. Searched in {duration:.4f} seconds.")

    if visualize:
        print("\nLaunching Pygame Timetabling Visualizer...")
        vis = TimetablingVisualizer(problem=problem, solver_class=CHOSEN_SOLVER)
        vis.run()


def main():
    visualize = VISUALIZE and ("--no-vis" not in sys.argv)
    solve_timetabling(visualize=visualize)


if __name__ == "__main__":
    main()
