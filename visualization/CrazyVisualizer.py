"""
CrazyVisualizer.py
Pygame-based interactive visualizer for the 'Crazy' card game.

Controls:
  Click cards in YOUR hand  -> Select / deselect cards for a combo
  Click 'PLAY SELECTED'     -> Play the selected combo
  Click 'DRAW FROM DECK'    -> Draw a card from the deck
  LEFT / RIGHT arrows       -> Step backward / forward through move history
  SPACE                     -> Toggle AI auto-play
  R                         -> Restart
  ESC                       -> Exit
"""

import pygame
import threading
import time
import random
from domains.crazy.CrazyState import CrazyState
from domains.crazy.CrazyCard import CrazyCard

# ─── Colour palette ────────────────────────────────────────────────────────────
BG           = (15,  20,  35)
FELT         = (24,  90,  45)
CARD_WHITE   = (250, 248, 240)
CARD_RED     = (196,  40,  40)
CARD_SHADOW  = ( 10,  10,  10)
GOLD         = (255, 200,  60)
SILVER       = (180, 180, 200)
HUD_BG       = ( 30,  35,  55)
HUD_LINE     = ( 70,  80, 120)
TEXT_BRIGHT  = (230, 235, 255)
TEXT_DIM     = (120, 130, 170)
GREEN_BTN    = ( 40, 160,  80)
RED_BTN      = (160,  40,  40)
BLUE_BTN     = ( 40,  80, 160)
YELLOW_HL    = (255, 230,  60)
SELECT_GLOW  = ( 80, 200, 255)
SKIP_ORANGE  = (255, 140,  30)

SUIT_SYMBOLS = {'Spade': '♠', 'Heart': '♥', 'Diamond': '♦', 'Club': '♣', 'Joker': '★'}
SUIT_COLORS  = {'Spade': CARD_SHADOW, 'Heart': CARD_RED, 'Diamond': CARD_RED,
                'Club': CARD_SHADOW, 'Joker': (160, 40, 200)}

def rank_str(rank):
    return str(rank) if rank != 0 else 'JK'

def suit_symbol(suit):
    return SUIT_SYMBOLS.get(suit, suit)


class CrazyVisualizer:
    CARD_W = 60
    CARD_H = 88
    CARD_R = 6   # corner radius

    def __init__(self, initial_state: CrazyState, player1, player2,
                 human_player: int = 1, fps: int = 30):
        """
        player1 / player2 : a GameSolver instance OR the string "HUMAN"
        human_player       : which side the human is (1 or 2)
        """
        self.initial_state  = initial_state
        self.state          = initial_state
        self.human_player   = human_player
        self.player1        = player1
        self.player2        = player2
        self.players        = {1: player1, 2: player2}

        self.fps = fps

        # Window geometry
        self.W, self.H = 1100, 700
        self.HUD_X     = self.W - 280

        # History for time-travel
        self.history       = [self.state]
        self.history_index = 0
        self.ai_thinking   = False
        self.ai_turn_id    = 0
        self.auto_run      = True

        # Human interaction state
        self.selected_cards   = []   # list of CrazyCard objects chosen by human
        self.suit_picker      = None # None or the wild combo pending suit selection

        # Move log for tracking last moves
        self.move_log: list = []  # list of (player_num, action_str) tuples

        # Status message
        self.message     = "Game started!"
        self.message_clr = TEXT_BRIGHT

        # ── Pygame init ──────────────────────────────────────────────────────
        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("AI Lab – Crazy Card Game")

        self.clock       = pygame.time.Clock()
        self.font_lg     = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_md     = pygame.font.SysFont("consolas", 16)
        self.font_sm     = pygame.font.SysFont("consolas", 13)
        self.font_card   = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_card_s = pygame.font.SysFont("consolas", 14)

        self.running = True

    # ─────────────────────────────────────────────────────────────────────────
    # Card drawing helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _draw_card(self, surf, x, y, card: CrazyCard,
                   face_up=True, selected=False, small=False):
        w, h = (self.CARD_W, self.CARD_H) if not small else (44, 64)
        r = self.CARD_R

        # Shadow
        shadow = pygame.Rect(x+3, y+3, w, h)
        pygame.draw.rect(surf, CARD_SHADOW, shadow, border_radius=r)

        # Card body
        col = SELECT_GLOW if selected else CARD_WHITE
        pygame.draw.rect(surf, col, pygame.Rect(x, y, w, h), border_radius=r)

        if not face_up:
            # Card back pattern
            inner = pygame.Rect(x+4, y+4, w-8, h-8)
            pygame.draw.rect(surf, (30, 60, 120), inner, border_radius=r-2)
            pygame.draw.rect(surf, (20, 40, 100), inner, width=2, border_radius=r-2)
            return pygame.Rect(x, y, w, h)

        if card is None:
            return pygame.Rect(x, y, w, h)

        suit_col = SUIT_COLORS.get(card.suit, CARD_SHADOW)
        rank_s   = rank_str(card.rank)
        suit_s   = suit_symbol(card.suit)

        f = self.font_card if not small else self.font_card_s

        # Top-left rank + suit
        t = f.render(rank_s, True, suit_col)
        surf.blit(t, (x+4, y+3))
        t2 = f.render(suit_s, True, suit_col)
        surf.blit(t2, (x+4, y+3+t.get_height()))

        # Centre big suit
        big = self.font_lg.render(suit_s, True, suit_col)
        bx = x + w//2 - big.get_width()//2
        by = y + h//2 - big.get_height()//2
        surf.blit(big, (bx, by))

        # Special badges
        badges = []
        dp = card.get_draw_penalty()
        if dp > 0:
            badges.append(f"+{dp}")
        if card.skips_turn():
            badges.append("SKP")
        if card.is_wild() and card.rank != 0:
            badges.append("WLD")
        if card.rank == 0:
            badges.append("JOKER")
        for i, b in enumerate(badges):
            bt = self.font_sm.render(b, True, SKIP_ORANGE)
            surf.blit(bt, (x+4, y+h-14-i*12))

        return pygame.Rect(x, y, w, h)

    def _draw_card_back(self, surf, x, y):
        return self._draw_card(surf, x, y, None, face_up=False)

    # ─────────────────────────────────────────────────────────────────────────
    # Render sections
    # ─────────────────────────────────────────────────────────────────────────

    def _render_hand(self, surf, hand, y_center, face_up, is_human_hand):
        """Draw a row of cards centred on y_center. Returns list of (rect, card)."""
        if not hand:
            return []
        n     = len(hand)
        gap   = min(self.CARD_W + 8, (self.HUD_X - 20) // max(n, 1))
        total = gap * (n-1) + self.CARD_W
        x0    = max(8, (self.HUD_X - total) // 2)
        y0    = y_center - self.CARD_H // 2

        rects = []
        for i, card in enumerate(hand):
            x = x0 + i * gap
            sel = is_human_hand and any(c is card for c in self.selected_cards)
            r = self._draw_card(surf, x, y0, card, face_up=face_up, selected=sel)
            rects.append((r, card))
        return rects

    def _render_center(self, surf):
        cx = self.HUD_X // 2
        cy = self.H // 2

        # Felt table circle
        pygame.draw.circle(surf, FELT, (cx, cy), 200)
        pygame.draw.circle(surf, (20, 70, 35), (cx, cy), 200, 3)

        # Discard pile
        state = self.history[self.history_index]
        if state.discard_pile:
            top_card = state.discard_pile[-1]
            dc_x, dc_y = cx - self.CARD_W - 10, cy - self.CARD_H // 2
            self._draw_card(surf, dc_x, dc_y, top_card, face_up=True)
            # "Discard" label
            lbl = self.font_sm.render("DISCARD", True, SILVER)
            surf.blit(lbl, (dc_x + self.CARD_W//2 - lbl.get_width()//2,
                            dc_y - 18))
        else:
            # Empty discard — game opening
            dc_x, dc_y = cx - self.CARD_W - 10, cy - self.CARD_H // 2
            # Draw an empty card outline
            pygame.draw.rect(surf, (40, 70, 50),
                             pygame.Rect(dc_x, dc_y, self.CARD_W, self.CARD_H),
                             border_radius=self.CARD_R)
            pygame.draw.rect(surf, SILVER,
                             pygame.Rect(dc_x, dc_y, self.CARD_W, self.CARD_H),
                             width=2, border_radius=self.CARD_R)
            ot = self.font_sm.render("EMPTY", True, SILVER)
            surf.blit(ot, (dc_x + self.CARD_W//2 - ot.get_width()//2,
                           dc_y + self.CARD_H//2 - ot.get_height()//2))
            open_t = self.font_sm.render("Play any card!", True, GOLD)
            surf.blit(open_t, (cx - open_t.get_width()//2, cy + 95))

        if state.active_suit:
            as_   = state.active_suit
            sym   = suit_symbol(as_)
            col   = SUIT_COLORS.get(as_, TEXT_BRIGHT)
            label = self.font_lg.render(f"Suit: {sym} {as_}", True, col)
            surf.blit(label, (cx - label.get_width()//2, cy + 90))

        # Deck (face-down stack)
        deck_size = sum(state.deck_counts.values())
        dk_x, dk_y = cx + 10, cy - self.CARD_H // 2
        for offset in range(min(4, deck_size)):
            self._draw_card_back(surf,
                                 dk_x + offset, dk_y - offset)
        deck_btn_rect = pygame.Rect(dk_x, dk_y - 3, self.CARD_W, self.CARD_H + 3)

        lbl = self.font_sm.render("DECK", True, SILVER)
        surf.blit(lbl, (dk_x + self.CARD_W//2 - lbl.get_width()//2, dk_y - 18))
        cnt = self.font_sm.render(f"{deck_size} cards", True, GOLD)
        surf.blit(cnt, (dk_x + self.CARD_W//2 - cnt.get_width()//2,
                        dk_y + self.CARD_H + 4))

        # Pending draws indicator
        if state.pending_draws > 0:
            txt = self.font_md.render(f"+{state.pending_draws} DRAWS PENDING", True, (255, 100, 60))
            surf.blit(txt, (cx - txt.get_width()//2, cy - 120))
        if getattr(state, 'just_drew', False):
            txt = self.font_md.render("▶ Play or PASS?", True, GOLD)
            surf.blit(txt, (cx - txt.get_width()//2, cy - 120))

        return deck_btn_rect

    def _render_buttons(self, surf):
        """Draw action buttons. Returns (play_rect, draw_rect, accept_rect, pass_rect)."""
        state    = self.history[self.history_index]
        is_live  = self.history_index == len(self.history) - 1
        # current_player can be 0 (CHANCE), so use .get()
        cp       = state.current_player
        is_human = (self.players.get(cp) == "HUMAN") if (not state.is_terminal() and cp != 0) else False
        active   = is_live and is_human and not self.ai_thinking and not state.is_terminal()

        just_drew   = getattr(state, 'just_drew', False)
        forced_draw = active and state.pending_draws > 0 and not just_drew
        can_play    = active and not forced_draw

        bw, bh = 155, 38
        # Four buttons: PLAY, DRAW, ACCEPT, PASS
        total_btn_w = bw * 4 + 10 * 3
        bx = (self.HUD_X - total_btn_w) // 2
        by = self.H - 70

        # PLAY SELECTED
        play_col  = GREEN_BTN if can_play and self.selected_cards else (40, 55, 40)
        play_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(surf, play_col, play_rect, border_radius=8)
        pt = self.font_md.render("▶ PLAY SELECTED", True, TEXT_BRIGHT)
        surf.blit(pt, (bx + bw//2 - pt.get_width()//2, by + bh//2 - pt.get_height()//2))

        # DRAW FROM DECK
        draw_col  = BLUE_BTN if (can_play and not just_drew) else (25, 35, 60)
        draw_rect = pygame.Rect(bx + bw + 10, by, bw, bh)
        pygame.draw.rect(surf, draw_col, draw_rect, border_radius=8)
        dt = self.font_md.render("⬇ DRAW FROM DECK", True, TEXT_BRIGHT)
        surf.blit(dt, (draw_rect.centerx - dt.get_width()//2,
                       draw_rect.centery - dt.get_height()//2))

        # ACCEPT button (only visible when forced)
        accept_col  = (150, 50, 50) if forced_draw else (35, 35, 35)
        accept_rect = pygame.Rect(bx + (bw + 10) * 2, by, bw, bh)
        pygame.draw.rect(surf, accept_col, accept_rect, border_radius=8)
        alabel = "⚠ DRAW PENALTIES" if forced_draw else "─"
        at = self.font_md.render(alabel, True, TEXT_BRIGHT if forced_draw else TEXT_DIM)
        surf.blit(at, (accept_rect.centerx - at.get_width()//2,
                       accept_rect.centery - at.get_height()//2))

        # PASS TURN button (visible after drawing)
        pass_col  = (120, 80, 30) if (active and just_drew) else (35, 35, 35)
        pass_rect = pygame.Rect(bx + (bw + 10) * 3, by, bw, bh)
        pygame.draw.rect(surf, pass_col, pass_rect, border_radius=8)
        plabel = "→ PASS TURN" if (active and just_drew) else "─"
        ptt = self.font_md.render(plabel, True, TEXT_BRIGHT if (active and just_drew) else TEXT_DIM)
        surf.blit(ptt, (pass_rect.centerx - ptt.get_width()//2,
                        pass_rect.centery - ptt.get_height()//2))

        return play_rect, draw_rect, accept_rect, pass_rect

    def _render_suit_picker(self, surf):
        """Overlay for choosing a suit when a wild card is played."""
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        suits  = ['Spade', 'Heart', 'Diamond', 'Club']
        bw, bh = 130, 130
        gap    = 20
        total  = len(suits) * (bw + gap) - gap
        x0     = self.W // 2 - total // 2
        y0     = self.H  // 2 - bh // 2

        title = self.font_lg.render("Choose a Suit:", True, GOLD)
        surf.blit(title, (self.W//2 - title.get_width()//2, y0 - 50))

        rects = {}
        for i, suit in enumerate(suits):
            x = x0 + i * (bw + gap)
            r = pygame.Rect(x, y0, bw, bh)
            col = (40, 50, 80)
            pygame.draw.rect(surf, col, r, border_radius=12)
            pygame.draw.rect(surf, HUD_LINE, r, width=2, border_radius=12)

            sym = suit_symbol(suit)
            sc  = SUIT_COLORS.get(suit, TEXT_BRIGHT)
            st  = self.font_lg.render(sym, True, sc)
            surf.blit(st, (r.centerx - st.get_width()//2, r.centery - st.get_height()//2 - 10))
            nt  = self.font_md.render(suit, True, TEXT_DIM)
            surf.blit(nt, (r.centerx - nt.get_width()//2, r.bottom - 30))

            rects[suit] = r

        # CANCEL button to return to hand card selection
        cancel_w, cancel_h = 160, 40
        cancel_rect = pygame.Rect(self.W // 2 - cancel_w // 2, y0 + bh + 40, cancel_w, cancel_h)
        pygame.draw.rect(surf, RED_BTN, cancel_rect, border_radius=8)
        ct = self.font_md.render("❌ CANCEL", True, TEXT_BRIGHT)
        surf.blit(ct, (cancel_rect.centerx - ct.get_width()//2, cancel_rect.centery - ct.get_height()//2))

        rects['CANCEL'] = cancel_rect
        return rects

    def _render_hud(self, surf):
        state = self.history[self.history_index]

        hud = pygame.Rect(self.HUD_X, 0, self.W - self.HUD_X, self.H)
        pygame.draw.rect(surf, HUD_BG, hud)
        pygame.draw.line(surf, HUD_LINE, (self.HUD_X, 0), (self.HUD_X, self.H), 2)

        x = self.HUD_X + 14
        y = 14

        def txt(s, font=None, col=None, gap=8):
            nonlocal y
            f = font or self.font_md
            c = col or TEXT_BRIGHT
            surf.blit(f.render(s, True, c), (x, y))
            y += f.size(s)[1] + gap

        def sep():
            nonlocal y
            y += 8
            pygame.draw.line(surf, HUD_LINE, (x, y), (self.W-12, y), 2)
            y += 18

        txt("CRAZY CARD GAME", self.font_lg, GOLD, 4)
        sep()

        # Player names
        p1_name = "YOU" if self.player1 == "HUMAN" else self.player1.__class__.__name__
        p2_name = "YOU" if self.player2 == "HUMAN" else self.player2.__class__.__name__
        txt(f"P1: {p1_name}")
        txt(f"P2: {p2_name}")
        sep()

        # Hand sizes
        txt(f"P1 cards:  {len(state.p1_hand)}")
        txt(f"P2 cards:  {len(state.p2_hand)}")
        txt(f"Deck left: {sum(state.deck_counts.values())}")
        txt(f"Discard:   {len(state.discard_pile)}")
        sep()

        # Turn / status
        if state.is_terminal():
            u1 = state.get_utility(1)
            u2 = state.get_utility(2)
            if u1 > u2:
                txt("PLAYER 1 WINS!", self.font_lg, GOLD)
            elif u2 > u1:
                txt("PLAYER 2 WINS!", self.font_lg, GOLD)
            else:
                txt("DRAW!", self.font_lg, SILVER)
        else:
            cp = state.current_player
            if cp == 0:
                whose = state.player_to_draw
                wname = p1_name if whose == 1 else p2_name
                txt(f"Drawing for P{whose} ({wname})", col=SILVER)
            else:
                cname = p1_name if cp == 1 else p2_name
                turn_col = YELLOW_HL if (self.players.get(cp) == "HUMAN") else SELECT_GLOW
                txt(f"Turn: P{cp} ({cname})", col=turn_col)

            if state.pending_draws > 0:
                txt(f"  ⚠ PENALTY: +{state.pending_draws} draws!", col=(255, 100, 60))
                is_human_cp = self.players.get(state.current_player) == "HUMAN"
                if is_human_cp and state.current_player != 0:
                    txt("  Counter: play a 2,7,A♠,Joker", col=(255, 180, 80), gap=3)
                    txt("  or click ⚠ DRAW PENALTIES", col=(255, 180, 80), gap=3)
            if self.ai_thinking and self.history_index == len(self.history)-1:
                txt("  AI is thinking...", col=SILVER)

        sep()

        # Status message
        msg_lines = self.message.split('\n')
        for line in msg_lines:
            txt(line, self.font_sm, self.message_clr, 3)

        sep()

        # Move log (last 5 moves visible)
        txt("MOVE LOG:", col=TEXT_DIM)
        log_slice = self.move_log[-5:] if len(self.move_log) >= 1 else []
        if not log_slice:
            txt("  (no moves yet)", self.font_sm, TEXT_DIM, 2)
        for (actor, astr) in reversed(log_slice):
            col = YELLOW_HL if actor == 1 else SELECT_GLOW
            # Privacy: Hide what opponent drew
            if actor != self.human_player and "Drew" in astr:
                astr = "Drew a card"
            
            # Wrap long move descriptions
            full_text = f"  P{actor}: {astr}"
            max_chars = max(15, (self.W - self.HUD_X - 25) // 8)
            if len(full_text) > max_chars:
                words = full_text.split()
                line = ""
                for word in words:
                    if len(line) + len(word) + 1 <= max_chars:
                        line += (" " if line else "") + word
                    else:
                        txt(line, self.font_sm, col, 1)
                        line = "    " + word
                if line:
                    txt(line, self.font_sm, col, 2)
            else:
                txt(full_text, self.font_sm, col, 2)

        sep()

        # Controls
        txt("CONTROLS:", col=TEXT_DIM)
        for ctrl in ["[SPACE]  Auto-play on/off",
                     "[RIGHT]  Step forward",
                     "[LEFT]   Step backward",
                     "[N]      New Game",
                     "[R]      Restart",
                     "[ESC]    Exit"]:
            txt(ctrl, self.font_sm, TEXT_DIM, 3)

        sep()
        txt(f"Auto-play: {'ON' if self.auto_run else 'OFF'}",
            col=GOLD if self.auto_run else SILVER)
        txt(f"Move {self.history_index} / {len(self.history)-1}", col=TEXT_DIM)

    def _render_player_labels(self, surf):
        state = self.history[self.history_index]
        p1_name = "YOU" if self.player1 == "HUMAN" else self.player1.__class__.__name__
        p2_name = "YOU" if self.player2 == "HUMAN" else self.player2.__class__.__name__

        lbl1 = self.font_md.render(
            f"Player 1 ({p1_name}) – {len(state.p1_hand)} cards", True,
            YELLOW_HL if state.current_player == 1 else TEXT_DIM)
        surf.blit(lbl1, (8, self.H - 160))

        lbl2 = self.font_md.render(
            f"Player 2 ({p2_name}) – {len(state.p2_hand)} cards", True,
            YELLOW_HL if state.current_player == 2 else TEXT_DIM)
        surf.blit(lbl2, (8, 8))

    # ─────────────────────────────────────────────────────────────────────────
    # Main render
    # ─────────────────────────────────────────────────────────────────────────

    def render(self):
        self.screen.fill(BG)
        state = self.history[self.history_index]

        # Player 2 hand at top (face-down unless AI debug)
        p2_face_up = (self.player2 == "HUMAN")
        self.p2_card_rects = self._render_hand(
            self.screen, state.p2_hand, 80, face_up=p2_face_up, is_human_hand=False)

        # Center table area
        self.deck_btn_rect = self._render_center(self.screen)

        # Player 1 hand at bottom (always face-up for human)
        is_human_hand = (self.player1 == "HUMAN" and
                         state.current_player == 1 and
                         self.history_index == len(self.history)-1 and
                         not self.ai_thinking)
        self.p1_card_rects = self._render_hand(
            self.screen, state.p1_hand, self.H - 100,
            face_up=True, is_human_hand=is_human_hand)

        # Labels
        self._render_player_labels(self.screen)

        # Buttons
        self.play_btn, self.draw_btn, self.accept_btn, self.pass_btn = self._render_buttons(self.screen)

        # HUD
        self._render_hud(self.screen)

        # Suit picker overlay
        self.suit_rects = None
        if self.suit_picker is not None:
            self.suit_rects = self._render_suit_picker(self.screen)

        pygame.display.flip()

    # ─────────────────────────────────────────────────────────────────────────
    # History helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _push_state(self, new_state: CrazyState, action=None, actor: int = None):
        # Truncate any forward history
        self.history = self.history[:self.history_index + 1]
        # Truncate move log too if we went back
        if action is not None and actor is not None:
            astr = _action_str(action) if not isinstance(action, str) else action
            self.move_log = self.move_log[:self.history_index]
            self.move_log.append((actor, astr))
        self.history.append(new_state)
        self.history_index += 1
        self.state = new_state

    def _step_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.state = self.history[self.history_index]
            self.ai_turn_id += 1
            self.ai_thinking = False
            self.selected_cards.clear()

    def _step_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.state = self.history[self.history_index]

    def restart(self):
        self.state          = self.initial_state
        self.history        = [self.state]
        self.history_index  = 0
        self.ai_thinking    = False
        self.ai_turn_id    += 1
        self.selected_cards.clear()
        self.suit_picker    = None
        self.move_log       = []
        self.message        = "Game restarted!"
        self.message_clr    = GOLD

    def new_game(self):
        from demo.crazy_demo import make_full_deck_state
        self.initial_state = make_full_deck_state()
        self.restart()
        self.message     = "New game started!"
        self.message_clr = GOLD

    # ─────────────────────────────────────────────────────────────────────────
    # AI thread
    # ─────────────────────────────────────────────────────────────────────────

    def _ai_turn(self, turn_id: int, delay: float):
        time.sleep(delay)
        if turn_id != self.ai_turn_id or not self.running:
            return

        agent = self.players[self.state.current_player]
        try:
            action = agent.get_best_action(self.state)
        except Exception as e:
            self.message     = f"AI error: {e}"
            self.message_clr = (255, 80, 80)
            self.ai_thinking = False
            return

        if turn_id != self.ai_turn_id or not self.running:
            return

        new_state = self.state.apply_action(action)
        actor = self.state.current_player
        self._push_state(new_state, action=action, actor=actor)
        self.ai_thinking = False

        aname = agent.__class__.__name__
        self.message     = f"P{actor} ({aname}): {_action_str(action)}"
        self.message_clr = SELECT_GLOW

    def _try_launch_ai(self):
        state = self.history[self.history_index]
        if (self.auto_run and
                not state.is_terminal() and
                not self.ai_thinking and
                self.history_index == len(self.history) - 1):

            cp = state.current_player
            if cp == 0:
                # Non-blocking pause for CHANCE node resolution
                if not hasattr(self, '_chance_timer'):
                    self._chance_timer = time.time()
                    return
                if time.time() - self._chance_timer < 0.25:
                    return
                delattr(self, '_chance_timer')

                outcomes = state.get_chance_outcomes()
                cards    = [c for c, p in outcomes]
                probs    = [p for c, p in outcomes]
                drawn    = random.choices(cards, weights=probs, k=1)[0]
                new_state = state.apply_action(drawn)
                actor = state.player_to_draw
                
                # Privacy: mask drawn card details if opponent drew
                if actor != self.human_player:
                    self._push_state(new_state, action="Drew a card", actor=actor)
                    self.message     = f"P{actor} drew a card"
                else:
                    self._push_state(new_state, action=f"Drew {drawn}", actor=actor)
                    dstr = str(drawn) if drawn else "nothing (deck empty)"
                    self.message     = f"You drew: {dstr}"
                self.message_clr = SILVER
            elif self.players.get(cp) != "HUMAN":
                self.ai_thinking = True
                self.ai_turn_id += 1
                # If game just started (empty discard), wait 1.8 seconds so user can see it. Otherwise wait 1.2 seconds.
                delay = 1.8 if not state.discard_pile else 1.2
                t = threading.Thread(
                    target=self._ai_turn, args=(self.ai_turn_id, delay), daemon=True)
                t.start()

    # ─────────────────────────────────────────────────────────────────────────
    # Human action helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _human_try_play(self):
        """Try to play the currently selected cards as a combo."""
        state = self.history[self.history_index]
        if not self.selected_cards or state.current_player != self.human_player:
            return

        legal = state.get_legal_actions()

        # Build raw card combo preserving selection order!
        raw_selection = tuple(self.selected_cards)
        raw_sorted = tuple(sorted(self.selected_cards, key=lambda c: (str(c.rank), c.suit)))

        # Check if the set of selected cards is valid (ignoring order)
        matched = None
        for action in legal:
            cards_in_action = tuple(sorted(
                [x for x in action if isinstance(x, CrazyCard)],
                key=lambda c: (str(c.rank), c.suit)))
            if cards_in_action == raw_sorted:
                matched = action
                break

        if matched is None:
            if state.pending_draws > 0:
                self.message     = "You must counter the penalty or accept it!"
                self.message_clr = (255, 80, 80)
            else:
                self.message     = "Invalid combo! Check the rules."
                self.message_clr = (255, 80, 80)
            return

        # Determine if it's a solo wild play that needs a suit picker
        cards_in_matched  = [x for x in matched if isinstance(x, CrazyCard)]
        is_solo_wild      = (len(cards_in_matched) == 1 and cards_in_matched[0].is_wild())
        suit_in_action    = any(isinstance(x, str) for x in matched)

        if is_solo_wild and suit_in_action:
            self.suit_picker = raw_selection   # store cards in selection order
            return

        # Apply action using the USER'S selection order instead of sorted order.
        # This ensures the last card selected is on top of the discard pile.
        user_ordered_action = raw_selection
        actor = state.current_player
        new_state = state.apply_action(user_ordered_action)
        self._push_state(new_state, action=user_ordered_action, actor=actor)
        self.selected_cards.clear()
        self.message     = f"You played: {_action_str(user_ordered_action)}"
        self.message_clr = GOLD

    def _human_draw(self):
        """Human draws from deck, or accepts forced penalty/skip."""
        state = self.history[self.history_index]
        if state.current_player != self.human_player:
            return
        legal = state.get_legal_actions()

        if state.pending_draws > 0:
            # Must draw penalty cards (opens CHANCE node)
            actor = state.current_player
            new_state = state.apply_action(("DRAW_PENALTY",))
            self._push_state(new_state, action=("DRAW_PENALTY",), actor=actor)
            self.message     = f"Drawing {state.pending_draws} penalty cards..."
            self.message_clr = (255, 100, 60)
        elif ("DRAW_FROM_DECK",) in state.get_legal_actions():
            actor = state.current_player
            new_state = state.apply_action(("DRAW_FROM_DECK",))
            self._push_state(new_state, action=("DRAW_FROM_DECK",), actor=actor)
            self.message     = "You drew from the deck."
            self.message_clr = SILVER
        else:
            self.message     = "Can't draw right now."
            self.message_clr = (255, 80, 80)
        self.selected_cards.clear()

    def _pick_suit(self, suit: str):
        """Called when human picks a suit for a wild-card play."""
        state = self.history[self.history_index]
        cards = self.suit_picker # selection order preserved
        self.suit_picker = None

        # Build action tuple: cards in selection order + chosen suit
        action = tuple(list(cards) + [suit])

        actor = state.current_player
        new_state = state.apply_action(action)
        self._push_state(new_state, action=action, actor=actor)
        self.selected_cards.clear()
        self.message     = f"You played wild → {suit}"
        self.message_clr = GOLD

    # ─────────────────────────────────────────────────────────────────────────
    # Event handling
    # ─────────────────────────────────────────────────────────────────────────

    def _handle_events(self):
        state    = self.history[self.history_index]
        is_live  = self.history_index == len(self.history) - 1
        cp       = state.current_player
        is_human = (self.players.get(cp) == "HUMAN") if (not state.is_terminal() and cp != 0) else False
        active   = is_live and is_human and not self.ai_thinking

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self.W, self.H = event.w, event.h
                self.HUD_X = self.W - 280
                self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.suit_picker is not None:
                        self.suit_picker = None
                    else:
                        self.running = False
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_n:
                    self.new_game()
                elif event.key == pygame.K_SPACE:
                    self.auto_run = not self.auto_run
                elif event.key == pygame.K_LEFT:
                    self._step_back()
                elif event.key == pygame.K_RIGHT:
                    self._step_forward()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                # Suit picker overlay takes priority
                if self.suit_rects:
                    for suit, r in self.suit_rects.items():
                        if r.collidepoint(pos):
                            if suit == 'CANCEL':
                                self.suit_picker = None
                            else:
                                self._pick_suit(suit)
                    continue

                # Action buttons
                if active:
                    if self.play_btn.collidepoint(pos):
                        self._human_try_play()
                        continue
                    if self.draw_btn.collidepoint(pos):
                        if not state.pending_draws:
                            self._human_draw()
                        continue
                    if self.accept_btn.collidepoint(pos):
                        if state.pending_draws > 0:
                            self._human_draw()
                        continue
                    if self.pass_btn.collidepoint(pos):
                        if getattr(state, 'just_drew', False):
                            actor = state.current_player
                            new_state = state.apply_action(("PASS_TURN",))
                            self._push_state(new_state, action=("PASS_TURN",), actor=actor)
                            self.selected_cards.clear()
                            self.message     = "You passed after drawing."
                            self.message_clr = TEXT_DIM
                        continue

                    # Deck click = draw (only when free)
                    if (self.deck_btn_rect.collidepoint(pos)
                            and not state.pending_draws):
                        self._human_draw()
                        continue

                    # Card selection
                    target_rects = []
                    if cp == 1 and self.player1 == "HUMAN":
                        target_rects = getattr(self, 'p1_card_rects', [])
                    elif cp == 2 and self.player2 == "HUMAN":
                        target_rects = getattr(self, 'p2_card_rects', [])

                    for rect, card in target_rects:
                        if rect.collidepoint(pos):
                            is_selected = any(c is card for c in self.selected_cards)
                            if is_selected:
                                self.selected_cards = [c for c in self.selected_cards if c is not card]
                            else:
                                self.selected_cards.append(card)
                            break

    # ─────────────────────────────────────────────────────────────────────────
    # Main loop
    # ─────────────────────────────────────────────────────────────────────────

    def run(self):
        while self.running:
            self._handle_events()
            self.render()
            self._try_launch_ai()
            self.clock.tick(self.fps)
        pygame.quit()


# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

def _action_str(action) -> str:
    parts = []
    for item in action:
        if isinstance(item, CrazyCard):
            parts.append(f"{rank_str(item.rank)}{suit_symbol(item.suit)}")
        elif isinstance(item, str):
            parts.append(f"→{item}")
        elif item in (("DRAW_FROM_DECK",), ("DRAW_PENALTY",), ("SKIP",)):
            parts.append(str(item[0]))
        else:
            parts.append(str(item))
    return " + ".join(parts) if parts else str(action)
