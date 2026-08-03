import pygame
import time
from games.GameState import GameState
from games.GameSolver import GameSolver
import threading

class BoardGameVisualizer:
    def __init__(self, initial_state: GameState, player1, player2, cell_size=80):
        self.initial_state = initial_state
        self.state = initial_state
        self.player1 = player1  # Can be GameSolver or "HUMAN"
        self.player2 = player2  # Can be GameSolver or "HUMAN"
        
        self.p1_id = self.state.get_current_player()
        
        # Test applying a move to see what next player id is
        legal = self.state.get_legal_actions()
        if legal:
            self.p2_id = self.state.apply_action(legal[0]).get_current_player()
        else:
            self.p2_id = -1
            
        self.players = {
            self.p1_id: self.player1,
            self.p2_id: self.player2
        }
        
        self.cell_size = cell_size
        self.rows = len(self.state.board)
        self.cols = len(self.state.board[0])
        
        self.board_width = self.cols * self.cell_size
        self.board_height = self.rows * self.cell_size
        self.hud_width = 300
        
        self.width = self.board_width + self.hud_width
        self.height = max(self.board_height, 400)

        self.COLORS = {
            "background": (20, 20, 20),
            "hud": (40, 40, 40),
            "hud_line": (100, 100, 100),
            "hud_text": (200, 200, 200),
            "hud_title": (255, 200, 100),
            "board_bg": (30, 144, 255) if self.rows == 6 and self.cols == 7 else (34, 139, 34) if self.rows == 8 else (240, 217, 181),
            "grid_lines": (0, 0, 0),
            "p1": (255, 0, 0) if self.rows == 6 else (0, 0, 0) if self.rows == 8 else (80, 80, 80),
            "p2": (255, 255, 0) if self.rows == 6 else (255, 255, 255) if self.rows == 8 else (240, 240, 240),
            "empty": (20, 20, 20) if self.rows == 6 else None
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        game_name = "Connect Four" if self.rows == 6 else "Othello" if self.rows == 8 else "Tic-Tac-Toe"
        pygame.display.set_caption(f"AI Lab - {game_name}")

        self.font = pygame.font.SysFont("consolas", 14)
        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_piece = pygame.font.SysFont("consolas", int(self.cell_size * 0.7), bold=True)

        self.running = True
        self.ai_thinking = False
        self.game_over = False
        self.auto_run = True

        self.history = [self.state]
        self.history_index = 0
        self.ai_thread = None
        self.ai_turn_id = 0

    def restart(self):
        self.state = self.initial_state
        self.history = [self.state]
        self.history_index = 0
        self.ai_thinking = False
        self.ai_turn_id += 1

    def draw_board(self):
        # Draw background
        board_rect = pygame.Rect(0, 0, self.board_width, self.board_height)
        pygame.draw.rect(self.screen, self.COLORS["board_bg"], board_rect)
        
        # Draw grid
        for r in range(self.rows + 1):
            pygame.draw.line(self.screen, self.COLORS["grid_lines"], (0, r * self.cell_size), (self.board_width, r * self.cell_size), 2)
        for c in range(self.cols + 1):
            pygame.draw.line(self.screen, self.COLORS["grid_lines"], (c * self.cell_size, 0), (c * self.cell_size, self.board_height), 2)
            
        # Draw pieces
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.history[self.history_index].board[r][c]
                center = (c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2)
                
                if self.rows == 6: # Connect Four
                    if val == self.p1_id:
                        pygame.draw.circle(self.screen, self.COLORS["p1"], center, self.cell_size // 2 - 5)
                    elif val == self.p2_id:
                        pygame.draw.circle(self.screen, self.COLORS["p2"], center, self.cell_size // 2 - 5)
                    else:
                        pygame.draw.circle(self.screen, self.COLORS["empty"], center, self.cell_size // 2 - 5)
                elif self.rows == 8: # Othello
                    if val == self.p1_id:
                        pygame.draw.circle(self.screen, self.COLORS["p1"], center, self.cell_size // 2 - 5)
                    elif val == self.p2_id:
                        pygame.draw.circle(self.screen, self.COLORS["p2"], center, self.cell_size // 2 - 5)
                else: # Tic-Tac-Toe
                    if val == self.p1_id or val == 'X':
                        text = self.font_piece.render("X", True, (0, 0, 0))
                        rect = text.get_rect(center=center)
                        self.screen.blit(text, rect)
                    elif val == self.p2_id or val == 'O':
                        text = self.font_piece.render("O", True, (200, 0, 0))
                        rect = text.get_rect(center=center)
                        self.screen.blit(text, rect)

    def draw_hud(self):
        hud_rect = pygame.Rect(self.board_width, 0, self.hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLORS["hud"], hud_rect)
        pygame.draw.line(self.screen, self.COLORS["hud_line"], (self.board_width, 0), (self.board_width, self.height), 2)

        x = self.board_width + 20
        y = 20

        def draw(text, font=None, color=None, gap=8):
            nonlocal y
            f = font or self.font
            c = color or self.COLORS["hud_text"]
            surface = f.render(str(text), True, c)
            self.screen.blit(surface, (x, y))
            y += surface.get_height() + gap

        draw("BOARD GAME ENGINE", self.font_title, self.COLORS["hud_title"], 20)
        
        p1_name = "HUMAN" if self.player1 == "HUMAN" else self.player1.__class__.__name__
        p2_name = "HUMAN" if self.player2 == "HUMAN" else self.player2.__class__.__name__
        
        draw(f"Player 1: {p1_name}")
        draw(f"Player 2: {p2_name}")
        
        y += 20
        
        state_to_draw = self.history[self.history_index]
        
        if state_to_draw.is_terminal():
            u1 = state_to_draw.get_utility(self.p1_id)
            u2 = state_to_draw.get_utility(self.p2_id)
            if u1 > u2:
                winner = self.p1_id
            elif u2 > u1:
                winner = self.p2_id
            else:
                winner = "DRAW"
                
            draw("GAME OVER!", self.font_title, (255, 100, 100))
            if winner == self.p1_id:
                draw("Player 1 Wins!", color=(100, 255, 100))
            elif winner == self.p2_id:
                draw("Player 2 Wins!", color=(100, 255, 100))
            else:
                draw("It's a Draw!", color=(200, 200, 200))
        else:
            curr_p = state_to_draw.get_current_player()
            curr_name = p1_name if curr_p == self.p1_id else p2_name
            draw(f"Turn: Player {1 if curr_p == self.p1_id else 2}")
            draw(f"({curr_name})")
            
            if self.ai_thinking and self.history_index == len(self.history) - 1:
                draw("AI is thinking...", color=(255, 255, 100))
                
        y += 20
        draw("CONTROLS:", self.font_title, self.COLORS["hud_title"])
        draw("[RIGHT] Step Forward")
        draw("[LEFT]  Step Backward")
        draw("[SPACE] Toggle Auto-Play")
        draw("[R]     Restart")
        draw("[ESC]   Exit")
        
        y += 20
        draw(f"Auto-Play: {'ON' if self.auto_run else 'OFF'}")
        draw(f"Move: {self.history_index} / {len(self.history)-1}")

    def render(self):
        self.draw_board()
        self.draw_hud()
        pygame.display.flip()

    def process_ai_turn(self, turn_id):
        self.render()
        
        current_player_agent = self.players[self.state.get_current_player()]
        # Get best action (this might take a few seconds)
        action = current_player_agent.get_best_action(self.state)
        
        if not self.running: return
        
        # Discard the result if a restart or time-travel occurred
        if turn_id != self.ai_turn_id:
            return

        new_state = self.state.apply_action(action)
        self.state = new_state
        self.history.append(self.state)
        self.history_index += 1
        self.ai_thinking = False
        
    def _step_backward(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.state = self.history[self.history_index]
            self.auto_run = False
            self.ai_turn_id += 1
            self.ai_thinking = False
            
    def _step_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.state = self.history[self.history_index]

    def handle_human_click(self, pos):
        if self.state.is_terminal() or self.ai_thinking:
            return
            
        current_player_agent = self.players[self.state.get_current_player()]
        if current_player_agent != "HUMAN":
            return
            
        x, y = pos
        if x >= self.board_width or y >= self.board_height:
            return
            
        c = x // self.cell_size
        r = y // self.cell_size
        
        # If user clicks while we are viewing history, truncate the future
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            self.state = self.history[-1]
            
        legal_actions = self.state.get_legal_actions()
        
        if self.rows == 6: # Connect Four actions are just column indices (if that's how it's implemented)
            # Actually, ConnectFourState returns column indices, let's check
            # We'll just allow any action that matches (r, c) or c
            action = None
            if c in legal_actions:
                action = c
            elif (r, c) in legal_actions:
                action = (r, c)
        else:
            action = (r, c)
            
        if action in legal_actions:
            self.state = self.state.apply_action(action)
            self.history.append(self.state)
            self.history_index += 1
            
    def run(self):
        self.render()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_SPACE:
                        self.auto_run = not self.auto_run
                    elif event.key == pygame.K_LEFT:
                        self._step_backward()
                    elif event.key == pygame.K_RIGHT:
                        self._step_forward()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        self.handle_human_click(event.pos)
                        
            self.render()
            
            if self.auto_run and not self.state.is_terminal() and not self.ai_thinking and self.history_index == len(self.history) - 1:
                current_player_agent = self.players[self.state.get_current_player()]
                if current_player_agent != "HUMAN":
                    # Start AI in a thread so it doesn't freeze the Pygame event loop
                    self.ai_thinking = True
                    self.ai_turn_id += 1
                    self.ai_thread = threading.Thread(target=self.process_ai_turn, args=(self.ai_turn_id,), daemon=True)
                    self.ai_thread.start()
                    
            time.sleep(0.05)
            
        pygame.quit()
