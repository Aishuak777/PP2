import os
import pygame
from player import MusicPlayer


pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player with Keyboard Controller")

font_title = pygame.font.SysFont("Arial", 30, bold=True)
font_text = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 20)

WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
BLUE = (70, 130, 180)
GREEN = (60, 180, 120)
RED = (200, 80, 80)

music_folder = os.path.join(os.path.dirname(__file__), "music")
player = MusicPlayer(music_folder)

TRACK_END_EVENT = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(TRACK_END_EVENT)

clock = pygame.time.Clock()
running = True


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_progress_bar(x, y, w, h, progress):
    pygame.draw.rect(screen, LIGHT_GRAY, (x, y, w, h), border_radius=8)
    fill_width = int(w * progress)
    pygame.draw.rect(screen, BLUE, (x, y, fill_width, h), border_radius=8)
    pygame.draw.rect(screen, BLACK, (x, y, w, h), 2, border_radius=8)


while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == TRACK_END_EVENT:
            if player.has_tracks() and not player.is_paused_or_stopped:
                player.next_track()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()

            elif event.key == pygame.K_s:
                player.stop()

            elif event.key == pygame.K_n:
                player.next_track()

            elif event.key == pygame.K_b:
                player.previous_track()

            elif event.key == pygame.K_q:
                running = False

    title = "Music Player"
    draw_text(title, font_title, BLACK, 300, 40)

    draw_text("Controls:", font_text, BLACK, 50, 110)
    draw_text("P = Play", font_small, BLACK, 70, 150)
    draw_text("S = Stop", font_small, BLACK, 70, 180)
    draw_text("N = Next", font_small, BLACK, 70, 210)
    draw_text("B = Previous", font_small, BLACK, 70, 240)
    draw_text("Q = Quit", font_small, BLACK, 70, 270)

    draw_text("Current Track:", font_text, BLACK, 50, 340)
    draw_text(player.get_current_track_name(), font_small, BLUE, 70, 380)

    progress = player.get_progress()
    draw_progress_bar(400, 180, 300, 30, progress)

    draw_text("Playback Progress", font_text, BLACK, 430, 130)
    draw_text(player.get_time_text(), font_small, BLACK, 500, 230)

    if not player.has_tracks():
        draw_text("Put .wav or .mp3 files into the music folder", font_small, RED, 250, 450)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()