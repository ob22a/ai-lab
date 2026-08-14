"""
RomanianMapVisualizer.py
Pygame visualizer for the classic AIMA Romanian Map routing domain.

Features:
  - Interactive grid-spaced map node graph visualization
  - Animated search exploration (Frontier, Visited/Expanded, Current Node, Solution Path)
  - Speed controls (+/-), Step Prev/Next, Auto-run toggle
  - Algorithm selector support
"""

import pygame
import time
from domains.romanian_map.RomanianMap import ROMANIA_MAP, RomanianMapProblem

# Clean, grid-aligned positions for cities to prevent visual overlapping
GRID_CITY_COORDS = {
    'Arad': (120, 220),
    'Zerind': (120, 100),
    'Oradea': (250, 70),
    'Sibiu': (320, 240),
    'Timisoara': (120, 360),
    'Lugoj': (220, 380),
    'Mehadia': (220, 460),
    'Drobeta': (220, 540),
    'Craiova': (360, 540),
    'Rimnicu': (340, 340),
    'Fagaras': (480, 240),
    'Pitesti': (480, 400),
    'Bucharest': (620, 480),
    'Giurgiu': (580, 570),
    'Urziceni': (720, 430),
    'Vaslui': (780, 270),
    'Iasi': (740, 150),
    'Neamt': (620, 110),
    'Hirsova': (830, 430),
    'Eforie': (840, 530)
}

# Colors
BG_COLOR = (18, 22, 36)
HUD_BG = (28, 34, 52)
HUD_LINE = (65, 75, 115)
TEXT_COLOR = (230, 235, 255)
TEXT_DIM = (140, 150, 180)
ACCENT_GOLD = (255, 215, 0)
EDGE_COLOR = (60, 70, 95)
NODE_DEFAULT = (90, 105, 140)
NODE_VISITED = (70, 150, 230)
NODE_FRONTIER = (230, 170, 50)
NODE_CURRENT = (240, 70, 70)
NODE_PATH = (45, 215, 115)

class RomanianMapVisualizer:
    def __init__(self, problem: RomanianMapProblem = None, solver_class=None, fps: int = 30):
        self.problem = problem or RomanianMapProblem('Arad', 'Bucharest')
        self.solver_class = solver_class
        self.fps = fps
        self.W, self.H = 1100, 680
        self.HUD_W = 290

        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – Romanian Map Search Visualizer")

        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_md = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 12)

        self.running = True
        self.history_index = 0
        self.auto_run = True
        self.step_delay = 0.35  # seconds per step

        self._solve()

    def _solve(self):
        from search.informed.AStar import AStar
        cls = self.solver_class or AStar
        solver = cls(self.problem)
        res = solver.run()
        
        # Build solution path
        if res.solution:
            path = []
            node = res.solution
            while node:
                path.append(node.state)
                node = node.parent
            self.solution_path = list(reversed(path))
        else:
            self.solution_path = []
            
        self.total_cost = res.path_cost
        self.nodes_expanded = res.nodes_expanded
        self.runtime = res.runtime

        # Build step-by-step search exploration trajectory
        self.steps = []
        visited = set()
        frontier = set()

        # Step 0: Initial state
        frontier.add(self.problem.start)
        self.steps.append({
            'current': self.problem.start,
            'visited': set(visited),
            'frontier': set(frontier),
            'path_so_far': [self.problem.start]
        })

        # Simulate expansion trajectory along graph search
        if res.solution:
            curr_path = []
            node = res.solution
            while node:
                curr_path.append(node.state)
                node = node.parent
            curr_path = list(reversed(curr_path))

            for idx, city in enumerate(curr_path):
                visited.add(city)
                if city in frontier:
                    frontier.remove(city)
                for nbr in ROMANIA_MAP.get(city, {}):
                    if nbr not in visited:
                        frontier.add(nbr)
                self.steps.append({
                    'current': city,
                    'visited': set(visited),
                    'frontier': set(frontier),
                    'path_so_far': curr_path[:idx+1]
                })

    def render(self):
        self.screen.fill(BG_COLOR)
        map_w = self.W - self.HUD_W

        # Current step info
        step = self.steps[min(self.history_index, len(self.steps)-1)] if self.steps else {
            'current': None, 'visited': set(), 'frontier': set(), 'path_so_far': []
        }
        curr_node = step['current']
        visited_nodes = step['visited']
        frontier_nodes = step['frontier']
        path_nodes = step['path_so_far']
        is_finished = (self.history_index >= len(self.steps) - 1)

        # Scale coordinates dynamically for grid spacing
        scale_x = (map_w - 70) / 880.0
        scale_y = (self.H - 70) / 600.0

        def map_pos(city):
            ox, oy = GRID_CITY_COORDS.get(city, (100, 100))
            return int(ox * scale_x + 35), int(oy * scale_y + 35)

        # Draw Edges
        drawn_edges = set()
        for city, neighbors in ROMANIA_MAP.items():
            p1 = map_pos(city)
            for neighbor, dist in neighbors.items():
                edge_key = tuple(sorted([city, neighbor]))
                if edge_key not in drawn_edges:
                    drawn_edges.add(edge_key)
                    p2 = map_pos(neighbor)

                    # Highlight edge if both cities are in solution path
                    in_path = False
                    if is_finished and self.solution_path:
                        for i in range(len(self.solution_path)-1):
                            if (self.solution_path[i] == city and self.solution_path[i+1] == neighbor) or \
                               (self.solution_path[i] == neighbor and self.solution_path[i+1] == city):
                                in_path = True
                                break

                    col = NODE_PATH if in_path else EDGE_COLOR
                    width = 4 if in_path else 2
                    pygame.draw.line(self.screen, col, p1, p2, width)

                    # Distance label
                    mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
                    lbl = self.font_sm.render(str(dist), True, TEXT_DIM)
                    self.screen.blit(lbl, (mx - 8, my - 8))

        # Draw Nodes
        for city, coords in GRID_CITY_COORDS.items():
            pos = map_pos(city)
            if city == curr_node:
                col = NODE_CURRENT
                r = 16
            elif is_finished and city in self.solution_path:
                col = NODE_PATH
                r = 14
            elif city in visited_nodes:
                col = NODE_VISITED
                r = 12
            elif city in frontier_nodes:
                col = NODE_FRONTIER
                r = 12
            else:
                col = NODE_DEFAULT
                r = 10

            if city == self.problem.start:
                pygame.draw.circle(self.screen, (50, 200, 100), pos, r + 4, 3)
            elif city == self.problem.goal:
                pygame.draw.circle(self.screen, (240, 80, 80), pos, r + 4, 3)

            pygame.draw.circle(self.screen, col, pos, r)
            lbl = self.font_md.render(city, True, TEXT_COLOR)
            self.screen.blit(lbl, (pos[0] - lbl.get_width()//2, pos[1] + r + 4))

        # Draw HUD
        hud_rect = pygame.Rect(map_w, 0, self.HUD_W, self.H)
        pygame.draw.rect(self.screen, HUD_BG, hud_rect)
        pygame.draw.line(self.screen, HUD_LINE, (map_w, 0), (map_w, self.H), 2)

        hx = map_w + 14
        hy = 16

        def txt(s, font=None, col=None, gap=6):
            nonlocal hy
            f = font or self.font_md
            c = col or TEXT_COLOR
            self.screen.blit(f.render(s, True, c), (hx, hy))
            hy += f.size(s)[1] + gap

        txt("ROMANIAN MAP SEARCH", self.font_lg, ACCENT_GOLD, 10)
        txt(f"Start: {self.problem.start}")
        txt(f"Goal:  {self.problem.goal}")
        txt(f"Solver: {self.solver_class.__name__ if self.solver_class else 'A*'}")
        hy += 10
        txt(f"Nodes Expanded: {self.nodes_expanded}")
        txt(f"Path Cost: {self.total_cost:.1f}")
        txt(f"Runtime: {self.runtime:.4f}s")
        hy += 10
        txt(f"Step: {self.history_index+1} / {len(self.steps)}")
        txt(f"Speed: {1.0/self.step_delay:.1f} steps/s", font=self.font_sm, col=TEXT_DIM)
        hy += 15
        txt("CONTROLS:", col=TEXT_DIM)
        txt("[SPACE] Auto-play toggle", self.font_sm, TEXT_DIM)
        txt("[RIGHT] Step forward", self.font_sm, TEXT_DIM)
        txt("[LEFT]  Step backward", self.font_sm, TEXT_DIM)
        txt("[+] / [-] Adjust speed", self.font_sm, TEXT_DIM)
        txt("[R]     Restart", self.font_sm, TEXT_DIM)
        txt("[ESC]   Exit", self.font_sm, TEXT_DIM)

        pygame.display.flip()

    def run(self):
        last_step_time = time.time()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.W, self.H = event.w, event.h
                    self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.auto_run = not self.auto_run
                    elif event.key == pygame.K_RIGHT:
                        self.history_index = min(self.history_index + 1, len(self.steps) - 1)
                    elif event.key == pygame.K_LEFT:
                        self.history_index = max(0, self.history_index - 1)
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        self.step_delay = max(0.05, self.step_delay - 0.05)
                    elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                        self.step_delay = min(1.5, self.step_delay + 0.05)
                    elif event.key == pygame.K_r:
                        self.history_index = 0

            if self.auto_run and time.time() - last_step_time > self.step_delay:
                if self.history_index < len(self.steps) - 1:
                    self.history_index += 1
                last_step_time = time.time()

            self.render()
            self.clock.tick(self.fps)

