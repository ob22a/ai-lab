import random
from typing import Tuple, Set

class RandomizedSokobanGenerator:
    """
    Procedurally generates guaranteed solvable Sokoban levels using Reverse Play!
    
    Instead of placing boxes randomly (which almost always creates unsolvable boards),
    we start with a SOLVED board (boxes on targets), and the player "pulls" the boxes 
    backwards through the maze for N random steps. 
    
    The resulting board is guaranteed to be solvable, because the solution is simply 
    the reverse of the pull-moves we just made!
    """
    def __init__(self, width: int = 8, height: int = 8, num_boxes: int = 3, num_pulls: int = 50):
        self.width = width
        self.height = height
        self.num_boxes = num_boxes
        self.num_pulls = num_pulls
        
        self.walls: Set[Tuple[int, int]] = set()
        self.targets: Set[Tuple[int, int]] = set()
        self.boxes: Set[Tuple[int, int]] = set()
        self.player: Tuple[int, int] = (0, 0)

    def _generate_empty_room(self):
        self.walls.clear()
        self.targets.clear()
        self.boxes.clear()

        # Create outer walls
        for r in range(self.height):
            for c in range(self.width):
                if r == 0 or r == self.height - 1 or c == 0 or c == self.width - 1:
                    self.walls.add((r, c))
                    
        # Add some random internal obstacles to make it interesting
        for _ in range((self.width * self.height) // 8):
            r, c = random.randint(2, self.height - 3), random.randint(2, self.width - 3)
            self.walls.add((r, c))

    def _perform_step(self, directions):
        random.shuffle(directions)
        moved = False
        
        for dr, dc in directions:
            pr, pc = self.player
            new_pr, new_pc = pr + dr, pc + dc
            box_r, box_c = pr - dr, pc - dc
            
            # Check if we can move backwards (must be empty space)
            if (new_pr, new_pc) in self.walls or (new_pr, new_pc) in self.boxes:
                continue
                
            # Check if there is a box in front of us to pull
            if (box_r, box_c) in self.boxes:
                # Execute Pull
                self.boxes.remove((box_r, box_c))
                self.boxes.add((pr, pc))
                self.player = (new_pr, new_pc)
                moved = True
                break
                
        if not moved:
            # If we couldn't pull any box, take a standard random step
            for dr, dc in directions:
                new_pr, new_pc = self.player[0] + dr, self.player[1] + dc
                if (new_pr, new_pc) not in self.walls and (new_pr, new_pc) not in self.boxes:
                    self.player = (new_pr, new_pc)
                    break

    def generate(self) -> str:
        # Loop until a level is successfully generated with 0 boxes on target
        while True:
            self._generate_empty_room()
            
            # 1. Place targets randomly in valid empty spaces
            available_spaces = [
                (r, c) for r in range(1, self.height - 1) 
                for c in range(1, self.width - 1) 
                if (r, c) not in self.walls
            ]
            
            if len(available_spaces) < self.num_boxes:
                continue

            target_positions = random.sample(available_spaces, self.num_boxes)
            for pos in target_positions:
                self.targets.add(pos)
                self.boxes.add(pos) # Start with boxes ON the targets (Solved State)
                
            # Place player next to one of the boxes
            tr, tc = target_positions[0]
            neighbors = [(tr-1, tc), (tr+1, tc), (tr, tc-1), (tr, tc+1)]
            valid_neighbors = [n for n in neighbors if n not in self.walls and n not in self.boxes]
            if valid_neighbors:
                self.player = random.choice(valid_neighbors)
            else:
                self.player = (1, 1) # Fallback

            # 2. Reverse Play (Pulling)
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            
            # Minimum pulls loop
            for _ in range(self.num_pulls):
                self._perform_step(directions)

            # Continue pulling extra steps until no box is on any target spot
            extra_steps = 0
            max_extra_steps = 100
            while not self.boxes.isdisjoint(self.targets) and extra_steps < max_extra_steps:
                self._perform_step(directions)
                extra_steps += 1

            # If all boxes successfully moved off targets, break out of retry loop
            if self.boxes.isdisjoint(self.targets):
                break

        # 3. Convert generated state to ASCII String
        lines = []
        for r in range(self.height):
            row = []
            for c in range(self.width):
                pos = (r, c)
                if pos in self.walls:
                    row.append('#')
                elif pos in self.boxes and pos in self.targets:
                    row.append('*')
                elif pos in self.boxes:
                    row.append('$')
                elif pos == self.player and pos in self.targets:
                    row.append('+')
                elif pos == self.player:
                    row.append('@')
                elif pos in self.targets:
                    row.append('.')
                else:
                    row.append(' ')
            lines.append("".join(row))
            
        return "\n".join(lines)