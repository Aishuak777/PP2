from __future__ import annotations

import sys
from datetime import datetime
from typing import List, Tuple

import pygame

from db import DatabaseManager
from game import WINDOW_WIDTH, TOTAL_HEIGHT, SnakeGame
from settings import load_settings, save_settings

pygame.init()

SCREEN = pygame.display.set_mode((WINDOW_WIDTH, TOTAL_HEIGHT))
pygame.display.set_caption('Snake - Practice Project')
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont('Arial', 24)
SMALL_FONT = pygame.font.SysFont('Arial', 18)
BIG_FONT = pygame.font.SysFont('Arial', 40)

# Colors used by UI screens.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 130, 255)
RED = (220, 0, 0)
GREEN = (0, 180, 0)
YELLOW = (255, 210, 0)


class Button:
    """Simple clickable UI button drawn with pygame rectangles."""

    def __init__(self, x: int, y: int, w: int, h: int, text: str):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        color = BLUE if self.rect.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        label = FONT.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class SnakeApp:
    def __init__(self):
        self.settings = load_settings()
        self.db = DatabaseManager()

        self.username = ''
        self.state = 'menu'
        self.status_message = ''
        self.last_result = None
        self.last_personal_best = None

        # Menu / game over buttons.
        self.menu_buttons = {
            'play': Button(220, 250, 160, 45, 'Play'),
            'leaderboard': Button(220, 310, 160, 45, 'Leaderboard'),
            'settings': Button(220, 370, 160, 45, 'Settings'),
            'quit': Button(220, 430, 160, 45, 'Quit'),
        }
        self.game_over_buttons = {
            'retry': Button(170, 380, 120, 45, 'Retry'),
            'menu': Button(320, 380, 150, 45, 'Main Menu'),
        }
        self.back_button = Button(220, 520, 160, 45, 'Back')
        self.save_back_button = Button(210, 520, 180, 45, 'Save & Back')

        # Leaderboard data is loaded when the screen opens.
        self.leaderboard_rows: List[dict] = []

        # Settings UI state.
        self.color_step = 15

    # -------------------- GENERAL DRAW HELPERS --------------------
    def draw_title(self, text: str, y: int = 40):
        label = BIG_FONT.render(text, True, WHITE)
        SCREEN.blit(label, label.get_rect(center=(WINDOW_WIDTH // 2, y)))

    def draw_center_text(self, text: str, y: int, color=WHITE, small=False):
        font = SMALL_FONT if small else FONT
        label = font.render(text, True, color)
        SCREEN.blit(label, label.get_rect(center=(WINDOW_WIDTH // 2, y)))

    def draw_username_box(self):
        """Draw the username input field on the main menu."""
        box = pygame.Rect(160, 150, 280, 42)
        pygame.draw.rect(SCREEN, DARK_GRAY, box, border_radius=8)
        pygame.draw.rect(SCREEN, WHITE, box, 2, border_radius=8)

        label = FONT.render('Username:', True, WHITE)
        SCREEN.blit(label, (160, 118))

        text = self.username if self.username else 'Type username here'
        color = WHITE if self.username else GRAY
        text_surface = FONT.render(text, True, color)
        SCREEN.blit(text_surface, (box.x + 10, box.y + 8))

    def sanitize_username(self):
        self.username = self.username.strip()[:50]

    # -------------------- MENU --------------------
    def draw_menu(self):
        SCREEN.fill(BLACK)
        self.draw_title('Snake Game')
        self.draw_username_box()

        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons.values():
            button.draw(SCREEN, mouse_pos)

        self.draw_center_text('Type a username, then press Play', 215, small=True)
        if self.db.available:
            self.draw_center_text('Database: connected', 490, GREEN, small=True)
        else:
            message = self.db.error_message or 'Database: not available'
            self.draw_center_text(f'Database: {message}', 490, YELLOW, small=True)

        if self.status_message:
            self.draw_center_text(self.status_message, 560, YELLOW, small=True)

        pygame.display.flip()

    def handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN:
                self.start_game()
            else:
                if event.unicode.isprintable() and len(self.username) < 50:
                    self.username += event.unicode

        if self.menu_buttons['play'].clicked(event):
            self.start_game()
        elif self.menu_buttons['leaderboard'].clicked(event):
            self.open_leaderboard()
        elif self.menu_buttons['settings'].clicked(event):
            self.state = 'settings'
            self.status_message = ''
        elif self.menu_buttons['quit'].clicked(event):
            pygame.quit()
            sys.exit()

    def start_game(self):
        """Run one gameplay session and save the result after game over."""
        self.sanitize_username()
        if not self.username:
            self.status_message = 'Please enter a username first.'
            return

        self.status_message = ''
        personal_best_before = self.db.get_personal_best(self.username)
        self.last_personal_best = personal_best_before

        result = SnakeGame(
            screen=SCREEN,
            clock=CLOCK,
            settings=self.settings,
            username=self.username,
            personal_best=personal_best_before,
        ).run()

        if result.get('quit_app'):
            pygame.quit()
            sys.exit()
        if result.get('back_to_menu'):
            self.state = 'menu'
            return

        self.last_result = result
        self.db.save_session(self.username, result['score'], result['level'])
        self.last_personal_best = self.db.get_personal_best(self.username)
        self.state = 'game_over'

    # -------------------- GAME OVER --------------------
    def draw_game_over(self):
        SCREEN.fill(BLACK)
        self.draw_title('Game Over', 70)

        if self.last_result:
            self.draw_center_text(f"Username: {self.username}", 160)
            self.draw_center_text(f"Score: {self.last_result['score']}", 210)
            self.draw_center_text(f"Level reached: {self.last_result['level']}", 250)
            pb_text = '-' if self.last_personal_best is None else str(self.last_personal_best)
            self.draw_center_text(f"Personal best: {pb_text}", 290)
            reason = self.last_result.get('reason', 'collision').replace('_', ' ').title()
            self.draw_center_text(f"Reason: {reason}", 330, small=True)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_over_buttons.values():
            button.draw(SCREEN, mouse_pos)

        pygame.display.flip()

    def handle_game_over_event(self, event):
        if self.game_over_buttons['retry'].clicked(event):
            self.start_game()
        elif self.game_over_buttons['menu'].clicked(event):
            self.state = 'menu'

    # -------------------- LEADERBOARD --------------------
    def open_leaderboard(self):
        self.leaderboard_rows = self.db.get_top_scores(10)
        self.state = 'leaderboard'

    def draw_leaderboard(self):
        SCREEN.fill(BLACK)
        self.draw_title('Leaderboard', 60)

        headers = ['Rank', 'Username', 'Score', 'Level', 'Date']
        x_positions = [50, 110, 290, 380, 460]
        y_start = 120

        for header, x in zip(headers, x_positions):
            SCREEN.blit(FONT.render(header, True, YELLOW), (x, y_start))

        pygame.draw.line(SCREEN, WHITE, (40, y_start + 35), (WINDOW_WIDTH - 40, y_start + 35), 2)

        if not self.leaderboard_rows:
            self.draw_center_text('No records yet or database is unavailable.', 260, small=True)
        else:
            for index, row in enumerate(self.leaderboard_rows, start=1):
                y = y_start + 45 + (index - 1) * 34
                played_at = row['played_at']
                date_text = played_at.strftime('%Y-%m-%d') if isinstance(played_at, datetime) else str(played_at)[:10]
                values = [
                    str(index),
                    str(row['username']),
                    str(row['score']),
                    str(row['level_reached']),
                    date_text,
                ]
                for value, x in zip(values, x_positions):
                    SCREEN.blit(SMALL_FONT.render(value, True, WHITE), (x, y))

        self.back_button.draw(SCREEN, pygame.mouse.get_pos())
        pygame.display.flip()

    def handle_leaderboard_event(self, event):
        if self.back_button.clicked(event):
            self.state = 'menu'

    # -------------------- SETTINGS --------------------
    def draw_settings(self):
        SCREEN.fill(BLACK)
        self.draw_title('Settings', 60)

        # Grid and sound toggles.
        grid_text = f"Grid overlay: {'ON' if self.settings['grid'] else 'OFF'}"
        sound_text = f"Sound: {'ON' if self.settings['sound'] else 'OFF'}"
        SCREEN.blit(FONT.render(grid_text, True, WHITE), (110, 150))
        SCREEN.blit(FONT.render(sound_text, True, WHITE), (110, 210))

        # Snake color controls.
        SCREEN.blit(FONT.render('Snake color (RGB):', True, WHITE), (110, 285))
        r, g, b = self.settings['snake_color']
        SCREEN.blit(FONT.render(f'R: {r}', True, WHITE), (110, 340))
        SCREEN.blit(FONT.render(f'G: {g}', True, WHITE), (110, 390))
        SCREEN.blit(FONT.render(f'B: {b}', True, WHITE), (110, 440))

        preview_rect = pygame.Rect(390, 325, 90, 90)
        pygame.draw.rect(SCREEN, tuple(self.settings['snake_color']), preview_rect, border_radius=8)
        pygame.draw.rect(SCREEN, WHITE, preview_rect, 2, border_radius=8)

        mouse_pos = pygame.mouse.get_pos()

        # Buttons are recreated here because their labels depend on current values.
        self.grid_button = Button(380, 145, 110, 40, 'Toggle')
        self.sound_button = Button(380, 205, 110, 40, 'Toggle')

        self.r_minus = Button(220, 333, 45, 36, '-')
        self.r_plus = Button(275, 333, 45, 36, '+')
        self.g_minus = Button(220, 383, 45, 36, '-')
        self.g_plus = Button(275, 383, 45, 36, '+')
        self.b_minus = Button(220, 433, 45, 36, '-')
        self.b_plus = Button(275, 433, 45, 36, '+')

        for button in [
            self.grid_button, self.sound_button,
            self.r_minus, self.r_plus,
            self.g_minus, self.g_plus,
            self.b_minus, self.b_plus,
            self.save_back_button,
        ]:
            button.draw(SCREEN, mouse_pos)

        self.draw_center_text('Snake color can be any RGB value from 0 to 255', 490, small=True)
        pygame.display.flip()

    def clamp_color(self):
        self.settings['snake_color'] = [max(0, min(255, c)) for c in self.settings['snake_color']]

    def handle_settings_event(self, event):
        if self.grid_button.clicked(event):
            self.settings['grid'] = not self.settings['grid']
        elif self.sound_button.clicked(event):
            self.settings['sound'] = not self.settings['sound']
        elif self.r_minus.clicked(event):
            self.settings['snake_color'][0] -= self.color_step
        elif self.r_plus.clicked(event):
            self.settings['snake_color'][0] += self.color_step
        elif self.g_minus.clicked(event):
            self.settings['snake_color'][1] -= self.color_step
        elif self.g_plus.clicked(event):
            self.settings['snake_color'][1] += self.color_step
        elif self.b_minus.clicked(event):
            self.settings['snake_color'][2] -= self.color_step
        elif self.b_plus.clicked(event):
            self.settings['snake_color'][2] += self.color_step
        elif self.save_back_button.clicked(event):
            self.clamp_color()
            save_settings(self.settings)
            self.state = 'menu'
            return

        self.clamp_color()

    # -------------------- MAIN LOOP --------------------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == 'menu':
                    self.handle_menu_event(event)
                elif self.state == 'game_over':
                    self.handle_game_over_event(event)
                elif self.state == 'leaderboard':
                    self.handle_leaderboard_event(event)
                elif self.state == 'settings':
                    self.handle_settings_event(event)

            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'game_over':
                self.draw_game_over()
            elif self.state == 'leaderboard':
                self.draw_leaderboard()
            elif self.state == 'settings':
                self.draw_settings()

            CLOCK.tick(60)


if __name__ == '__main__':
    SnakeApp().run()
