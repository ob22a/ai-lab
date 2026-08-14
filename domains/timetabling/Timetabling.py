from typing import Dict, Any, List, Tuple
from csp.CSPProblem import CSPProblem, Constraint

class RoomConflictConstraint(Constraint):
    """
    Ensures that no two classes are assigned the exact same (room, timeslot).
    """
    def __init__(self, class1: Any, class2: Any):
        super().__init__([class1, class2])
        self.class1 = class1
        self.class2 = class2

    def is_satisfied(self, assignment: Dict[Any, Any]) -> bool:
        if self.class1 not in assignment or self.class2 not in assignment:
            return True
            
        return assignment[self.class1] != assignment[self.class2]


class InstructorConflictConstraint(Constraint):
    """
    Ensures that if two classes share the same instructor, they are not 
    scheduled in the same timeslot.
    """
    def __init__(self, class1: Any, class2: Any):
        super().__init__([class1, class2])
        self.class1 = class1
        self.class2 = class2

    def is_satisfied(self, assignment: Dict[Any, Any]) -> bool:
        if self.class1 not in assignment or self.class2 not in assignment:
            return True
            
        # assignment[class] is a (room, timeslot) tuple
        timeslot1 = assignment[self.class1][1]
        timeslot2 = assignment[self.class2][1]
        
        return timeslot1 != timeslot2


DEFAULT_CLASSES = [
    {'id': 'CS101', 'instructor': 'Dr. Alan', 'capacity': 40},
    {'id': 'CS102', 'instructor': 'Dr. Alan', 'capacity': 30},
    {'id': 'CS201', 'instructor': 'Dr. Barbara', 'capacity': 50},
    {'id': 'CS202', 'instructor': 'Dr. Barbara', 'capacity': 60},
    {'id': 'CS301', 'instructor': 'Dr. Charlie', 'capacity': 45},
    {'id': 'CS302', 'instructor': 'Dr. Charlie', 'capacity': 35},
]

DEFAULT_ROOMS = [
    {'id': 'Room 101', 'capacity': 50},
    {'id': 'Room 102', 'capacity': 80},
    {'id': 'Lab 1', 'capacity': 40},
]

DEFAULT_TIMESLOTS = ['Mon 9AM', 'Mon 11AM', 'Tue 9AM', 'Tue 11AM', 'Wed 10AM']


class TimetablingCSP(CSPProblem):
    """
    University Timetabling CSP.
    classes: List of dicts, e.g., [{'id': 'CS101', 'instructor': 'Alice', 'capacity': 50}, ...]
    rooms: List of dicts, e.g., [{'id': 'RoomA', 'capacity': 100}, ...]
    timeslots: List of strings, e.g., ['Mon 9AM', 'Mon 10AM', ...]
    """
    def __init__(self, classes: List[Dict[str, Any]] = None, rooms: List[Dict[str, Any]] = None, timeslots: List[str] = None):
        classes = classes or DEFAULT_CLASSES
        rooms = rooms or DEFAULT_ROOMS
        timeslots = timeslots or DEFAULT_TIMESLOTS

        variables = [c['id'] for c in classes]
        
        # Build domains with capacity pre-filtering
        domains = {}
        for cls in classes:
            cls_domain = []
            for room in rooms:
                if room['capacity'] >= cls['capacity']:
                    for timeslot in timeslots:
                        cls_domain.append((room['id'], timeslot))
            domains[cls['id']] = cls_domain
            
            if not cls_domain:
                raise ValueError(f"Class {cls['id']} has no valid rooms due to capacity constraints!")
                
        super().__init__(variables, domains)
        
        # Add Constraints
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                cls1 = classes[i]
                cls2 = classes[j]
                
                # 1. Room Conflict: No two classes can be in the same room at the same time.
                self.add_constraint(RoomConflictConstraint(cls1['id'], cls2['id']))
                
                # 2. Instructor Conflict: Same instructor cannot be in two places at once.
                if cls1['instructor'] == cls2['instructor']:
                    self.add_constraint(InstructorConflictConstraint(cls1['id'], cls2['id']))

