from typing import List, Tuple, Set, Any, FrozenSet
from core.problem import SearchProblem

class SokobanState:
    """
    State representation for Sokoban.
    We track the player's position and the boxes' positions.
    We pass a reference to the problem (which holds walls/targets) for easy visualization.
    """
    def __init__(self, player: Tuple[int, int], boxes: FrozenSet[Tuple[int, int]], problem_ref=None):
        self.player = player
        self.boxes = frozenset(boxes)
        self.problem_ref = problem_ref
        
    def __eq__(self, other):
        return isinstance(other, SokobanState) and self.player == other.player and self.boxes == other.boxes
        
    def __hash__(self):
        return hash((self.player, self.boxes))
        
    def __str__(self):
        if not self.problem_ref:
            return f"Player: {self.player}, Boxes: {self.boxes}"
            
        lines = []
        for r in range(self.problem_ref.height):
            row = []
            for c in range(self.problem_ref.width):
                pos = (r, c)
                if pos in self.problem_ref.walls:
                    row.append('#')
                elif pos in self.boxes and pos in self.problem_ref.targets:
                    row.append('*')
                elif pos in self.boxes:
                    row.append('$')
                elif pos == self.player and pos in self.problem_ref.targets:
                    row.append('+')
                elif pos == self.player:
                    row.append('@')
                elif pos in self.problem_ref.targets:
                    row.append('.')
                else:
                    row.append(' ')
            lines.append("".join(row))
        return "\n".join(lines)

class SokobanProblem(SearchProblem):
    """
    Finds the shortest path to push all boxes onto targets.
    """
    def __init__(self, layout_str: str):
        self.walls: Set[Tuple[int, int]] = set()
        self.targets: Set[Tuple[int, int]] = set()
        
        start_player = None
        start_boxes = set()
        
        lines = layout_str.strip('\n').split('\n')
        self.height = len(lines)
        self.width = max(len(line) for line in lines)
        
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                if char == '#':
                    self.walls.add((r, c))
                elif char == '.':
                    self.targets.add((r, c))
                elif char == '$':
                    start_boxes.add((r, c))
                elif char == '*':
                    self.targets.add((r, c))
                    start_boxes.add((r, c))
                elif char == '@':
                    start_player = (r, c)
                elif char == '+':
                    self.targets.add((r, c))
                    start_player = (r, c)
                    
        if start_player is None:
            raise ValueError("No player '@' found in layout!")
            
        start_state = SokobanState(start_player, frozenset(start_boxes), self)
        
        # Sokoban goal state is implicit (all boxes on targets) rather than a single explicit state
        super().__init__(start_state, None)

    def is_goal_state(self, state: SokobanState) -> bool:
        # State is goal if all boxes are on targets
        return state.boxes == self.targets

    def get_actions(self, state: SokobanState) -> List[str]:
        actions = []
        r, c = state.player
        
        # Directions: Up, Down, Left, Right
        directions = {
            'U': (-1, 0),
            'D': (1, 0),
            'L': (0, -1),
            'R': (0, 1)
        }
        
        for action, (dr, dc) in directions.items():
            nr, nc = r + dr, c + dc
            
            # 1. Check if moving into a wall
            if (nr, nc) in self.walls:
                continue
                
            # 2. Check if moving into a box
            if (nr, nc) in state.boxes:
                # Can we push the box? Check the space behind the box
                push_r, push_c = nr + dr, nc + dc
                
                if (push_r, push_c) in self.walls or (push_r, push_c) in state.boxes:
                    # Cannot push! Wall or another box is blocking it.
                    continue
                    
                # Check for simple deadlock (pushing a box into a corner without a target)
                if (push_r, push_c) not in self.targets and self._is_corner(push_r, push_c):
                    continue # Skip this state completely to prune the search tree!
                    
                actions.append(action.lower()) # lower case for push
                
            else:
                # Valid Move (Empty space)
                actions.append(action.upper()) # UPPER case for move
                
        return actions

    def get_result(self, state: SokobanState, action: str) -> SokobanState:
        r, c = state.player
        
        directions = {
            'u': (-1, 0), 'U': (-1, 0),
            'd': (1, 0), 'D': (1, 0),
            'l': (0, -1), 'L': (0, -1),
            'r': (0, 1), 'R': (0, 1)
        }
        dr, dc = directions[action]
        nr, nc = r + dr, c + dc
        
        # If it was a push (lowercase)
        if action.islower():
            push_r, push_c = nr + dr, nc + dc
            new_boxes = set(state.boxes)
            new_boxes.remove((nr, nc))
            new_boxes.add((push_r, push_c))
            return SokobanState((nr, nc), frozenset(new_boxes), self)
            
        # Standard move
        return SokobanState((nr, nc), state.boxes, self)

    def get_cost(self, state: SokobanState, action: str, next_state: SokobanState) -> float:
        return 1.0

    def _is_corner(self, r: int, c: int) -> bool:
        """Helper to detect if a square is a corner bounded by walls, leading to a deadlock."""
        up = (r - 1, c) in self.walls
        down = (r + 1, c) in self.walls
        left = (r, c - 1) in self.walls
        right = (r, c + 1) in self.walls
        
        return (up and left) or (up and right) or (down and left) or (down and right)

    def heuristic(self, state: SokobanState) -> float:
        """
        Admissible Heuristic: Minimum total Manhattan distance from each box to its nearest target.
        (A perfect admissible heuristic would use bipartite matching, but greedy is fast and decent).
        """
        if self.is_goal_state(state):
            return 0.0
            
        total_distance = 0.0
        available_targets = set(self.targets)
        
        for br, bc in state.boxes:
            min_dist = float('inf')
            best_target = None
            
            for tr, tc in available_targets:
                dist = abs(br - tr) + abs(bc - tc)
                if dist < min_dist:
                    min_dist = dist
                    best_target = (tr, tc)
                    
            if best_target:
                total_distance += min_dist
                # Remove target to ensure 1:1 mapping (greedy approach)
                available_targets.remove(best_target)
                
        return total_distance
