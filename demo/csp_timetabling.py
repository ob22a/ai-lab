import time
from domains.timetabling.Timetabling import TimetablingCSP
from csp.Backtracking import BacktrackingSolver, unassigned_variable_default, order_domain_values_default
from csp.heuristics.MRV import mrv
from csp.heuristics.DegreeHeuristic import mrv_with_degree_heuristic
from csp.inference.MAC import mac


def solve_timetabling():
    print("\n--- University Timetabling CSP ---")
    
    # 10 Courses
    classes = [
        {'id': 'CS101', 'instructor': 'Alice', 'capacity': 50},
        {'id': 'CS102', 'instructor': 'Bob', 'capacity': 30},
        {'id': 'CS201', 'instructor': 'Alice', 'capacity': 40},
        {'id': 'MATH101', 'instructor': 'Charlie', 'capacity': 100},
        {'id': 'MATH201', 'instructor': 'Charlie', 'capacity': 20},
        {'id': 'PHYS101', 'instructor': 'Dave', 'capacity': 60},
        {'id': 'PHYS201', 'instructor': 'Eve', 'capacity': 30},
        {'id': 'ENG101', 'instructor': 'Frank', 'capacity': 25},
        {'id': 'ENG102', 'instructor': 'Frank', 'capacity': 25},
        {'id': 'ART101', 'instructor': 'Grace', 'capacity': 15},
    ]
    
    # 5 Rooms
    rooms = [
        {'id': 'RoomA', 'capacity': 100}, # Large lecture hall
        {'id': 'RoomB', 'capacity': 60},
        {'id': 'RoomC', 'capacity': 40},
        {'id': 'RoomD', 'capacity': 30},
        {'id': 'RoomE', 'capacity': 20},
    ]
    
    # 5 Timeslots (simplified)
    timeslots = ['Mon 9AM', 'Mon 11AM', 'Wed 9AM', 'Wed 11AM', 'Fri 9AM']
    
    try:
        problem = TimetablingCSP(classes, rooms, timeslots)
    except ValueError as e:
        print(f"Error: {e}")
        return
        
    print(f"Scheduling {len(classes)} classes into {len(rooms)} rooms and {len(timeslots)} timeslots...")
    
    solver = BacktrackingSolver(
        problem,
        select_unassigned_variable=mrv_with_degree_heuristic,
        order_domain_values=order_domain_values_default,
        inference=mac
    )
    
    start = time.time()
    solution = solver.solve()
    duration = time.time() - start
    
    if solver.status == "SUCCESS":
        print(f"Solution found in {duration:.4f} seconds! (Nodes expanded: {solver.nodes_expanded})")
        print("\nSchedule:")
        
        # Group by timeslot for nice printing
        schedule_by_time = {t: [] for t in timeslots}
        for cls_id, (room, timeslot) in solution.items():
            schedule_by_time[timeslot].append(f"{cls_id:8} (Room: {room:6})")
            
        for t in timeslots:
            print(f"\n[{t}]")
            for item in schedule_by_time[t]:
                print(f"  {item}")
    else:
        print(f"NO SOLUTION EXISTS. Searched in {duration:.4f} seconds.")


def main():
    solve_timetabling()


if __name__ == "__main__":
    main()
