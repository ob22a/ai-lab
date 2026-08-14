"""
demo/csp_timetabling.py
University Timetabling CSP Demo.

Solvers available:   BacktrackingSolver, MinConflictsSolver
Heuristics available: mrv, mrv_with_degree_heuristic, lcv, None
Inferences available: mac, forward_checking, None

Usage:
  python -m demo.csp_timetabling [--algo Backtracking|MinConflicts]
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.timetabling.Timetabling import TimetablingCSP, DEFAULT_CLASSES, DEFAULT_ROOMS, DEFAULT_TIMESLOTS
from csp.Backtracking import BacktrackingSolver, order_domain_values_default
from csp.MinConflicts import MinConflictsSolver
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.MAC import mac
from csp.inference.ForwardChecking import forward_checking


def main():
    parser = argparse.ArgumentParser(description="University Timetabling CSP Demo")
    parser.add_argument("--algo", type=str, default="Backtracking", choices=["Backtracking", "MinConflicts"], help="CSP solver class")
    args = parser.parse_args()

    print("=" * 65)
    print("         UNIVERSITY TIMETABLING CSP DEMO")
    print("=" * 65)

    classes = DEFAULT_CLASSES
    rooms = DEFAULT_ROOMS
    timeslots = DEFAULT_TIMESLOTS

    try:
        problem = TimetablingCSP(classes, rooms, timeslots)
    except ValueError as e:
        print(f"Error initializing timetabling problem: {e}")
        return

    print(f"Scheduling {len(classes)} classes into {len(rooms)} rooms and {len(timeslots)} timeslots...")

    if args.algo == "MinConflicts":
        solver = MinConflictsSolver(problem, max_steps=1000)
    else:
        solver = BacktrackingSolver(
            problem,
            select_unassigned_variable=mrv_with_degree_heuristic,
            order_domain_values=order_domain_values_default,
            inference=mac
        )

    t0 = time.time()
    solution = solver.solve()
    duration = time.time() - t0

    if solver.status == "SUCCESS" and solution:
        print(f"\nSolution Found in {duration:.4f}s! (Nodes expanded: {solver.nodes_expanded})")
        print("\nSchedule Grid:")
        schedule_by_time = {t: [] for t in timeslots}
        for cls_id, (room, timeslot) in solution.items():
            schedule_by_time[timeslot].append(f"{cls_id:6s} (Room: {room:8s})")

        for t in timeslots:
            print(f"\n[{t}]")
            for item in schedule_by_time[t]:
                print(f"  {item}")
    else:
        print(f"\nNo valid timetable schedule found. Searched in {duration:.4f}s.")
    print("=" * 65)


if __name__ == "__main__":
    main()

