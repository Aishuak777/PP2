import json
import math
import os
import random
import sys

import pygame

# -------------------------------------------------
# Basic setup
# -------------------------------------------------
pygame.init()
pygame.font.init()

WIDTH = 520
HEIGHT = 760
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Racer")
CLOCK = pygame.time.Clock()

# Folder where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Save JSON files in the same folder as main.py
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

# -------------------------------------------------
# Colors
# -------------------------------------------------
WHITE = (245, 245, 245)
BLACK = (18, 18, 18)
DARK = (24, 28, 36)
GRAY = (95, 103, 117)
LIGHT_GRAY = (185, 190, 198)
ROAD_GRAY = (70, 74, 82)
GREEN = (38, 120, 55)
RED = (225, 70, 70)
BLUE = (70, 140, 255)
YELLOW = (255, 215, 0)
ORANGE = (255, 150, 50)
PURPLE = (176, 100, 255)
CYAN = (70, 220, 255)
GOLD = (255, 200, 70)
PINK = (255, 95, 180)

ROAD_LEFT = 90
ROAD_RIGHT = WIDTH - 90
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANES = 3
LANE_WIDTH = ROAD_WIDTH / LANES

CAR_COLORS = {
    "blue": (70, 140, 255),
    "red": (225, 70, 70),
    "green": (40, 195, 95),
    "gold": (255, 190, 50),
}

DIFFICULTY_PRESETS = {
    "easy": {
        "world_speed": 290,
        "traffic_interval": 1.20,
        "obstacle_interval": 1.80,
        "coin_interval": 0.85,
        "event_interval": 4.20,
        "powerup_interval": 7.50,
    },
    "normal": {
        "world_speed": 325,
        "traffic_interval": 1.00,
        "obstacle_interval": 1.55,
        "coin_interval": 0.80,
        "event_interval": 3.80,
        "powerup_interval": 7.00,
    },
    "hard": {
        "world_speed": 360,
        "traffic_interval": 0.82,
        "obstacle_interval": 1.35,
        "coin_interval": 0.75,
        "event_interval": 3.30,
        "powerup_interval": 6.50,
    },
}

BIG_FONT = pygame.font.SysFont("arial", 40, bold=True)
FONT = pygame.font.SysFont("arial", 24)
SMALL_FONT = pygame.font.SysFont("arial", 18)
TINY_FONT = pygame.font.SysFont("arial", 15)


# -------------------------------------------------
# Utility helpers
# -------------------------------------------------
def lane_center(index: int) -> float:
    return ROAD_LEFT + index * LANE_WIDTH + LANE_WIDTH / 2


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def draw_text(surface, text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_surface, rect)
    return rect


def load_json(path, default_data):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=2)
        return default_data

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=2)
        return default_data


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def difficulty_scale(distance_meters: float) -> float:
    """Increase spawn pressure as the player drives further."""
    return clamp(1.0 + distance_meters / 1800.0, 1.0, 2.25)


# -------------------------------------------------
# UI elements
# -------------------------------------------------
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        fill = (52, 60, 78) if hovered else (38, 44, 58)
        pygame.draw.rect(surface, fill, self.rect, border_radius=14)
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 2, border_radius=14)
        draw_text(surface, self.text, FONT, WHITE, self.rect.centerx, self.rect.centery, center=True)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class TextInput:
    def __init__(self, rect, text=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.active = False
        self.max_len = 12

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if len(self.text) < self.max_len and event.unicode.isprintable() and event.unicode not in "\t\r\n":
                    self.text += event.unicode

    def draw(self, surface, label):
        border = CYAN if self.active else LIGHT_GRAY
        pygame.draw.rect(surface, (34, 38, 46), self.rect, border_radius=12)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=12)
        draw_text(surface, label, SMALL_FONT, LIGHT_GRAY, self.rect.x, self.rect.y - 24)
        shown_text = self.text if self.text else "Type your name"
        shown_color = WHITE if self.text else GRAY
        draw_text(surface, shown_text, FONT, shown_color, self.rect.x + 12, self.rect.y + 10)


# -------------------------------------------------
# Game objects
# -------------------------------------------------
class WorldObject(pygame.sprite.Sprite):
    def __init__(self, lane, y, width, height):
        super().__init__()
        self.lane = lane
        self.width = width
        self.height = height
        self.x = lane_center(lane) - width / 2
        self.y = y
        self.rect = pygame.Rect(int(self.x), int(self.y), width, height)

    def sync_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


class Player(pygame.sprite.Sprite):
    def __init__(self, color_name):
        super().__init__()
        self.width = 50
        self.height = 92
        self.x = lane_center(1) - self.width / 2
        self.y = HEIGHT - 130
        self.base_move_speed = 300
        self.move_speed = self.base_move_speed
        self.color_name = color_name
        self.color = CAR_COLORS.get(color_name, BLUE)
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

        self.active_powerup = None
        self.active_powerup_time = 0.0
        self.repair_ready = False
        self.shield_ready = False
        self.invincible_time = 0.0
        self.slip_time = 0.0
        self.slowdown_time = 0.0
        self.strip_boost_time = 0.0

    def rebuild_color(self, color_name):
        self.color_name = color_name
        self.color = CAR_COLORS.get(color_name, BLUE)

    def update(self, dt, keys):
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1

        # Oil spill effect: temporarily invert controls.
        if self.slip_time > 0:
            direction *= -1

        current_move_speed = self.base_move_speed
        if self.slowdown_time > 0:
            current_move_speed *= 0.55
        if self.active_powerup == "nitro":
            current_move_speed *= 1.35
        if self.strip_boost_time > 0:
            current_move_speed *= 1.20

        self.x += direction * current_move_speed * dt
        self.x = clamp(self.x, ROAD_LEFT + 8, ROAD_RIGHT - self.width - 8)

        # Update timers.
        self.invincible_time = max(0.0, self.invincible_time - dt)
        self.slip_time = max(0.0, self.slip_time - dt)
        self.slowdown_time = max(0.0, self.slowdown_time - dt)
        self.strip_boost_time = max(0.0, self.strip_boost_time - dt)

        if self.active_powerup == "nitro":
            self.active_powerup_time = max(0.0, self.active_powerup_time - dt)
            if self.active_powerup_time <= 0:
                self.active_powerup = None
        elif self.active_powerup in {"shield", "repair"}:
            # These stay ready until used.
            self.active_powerup_time = 0.0

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface):
        body = self.rect.copy()
        roof = pygame.Rect(self.rect.x + 10, self.rect.y + 8, 30, 22)
        windshield = pygame.Rect(self.rect.x + 12, self.rect.y + 12, 26, 10)

        # Small flicker when shield or invincibility is active.
        visible = True
        if self.invincible_time > 0:
            visible = int(self.invincible_time * 20) % 2 == 0

        if visible:
            pygame.draw.rect(surface, self.color, body, border_radius=10)
            pygame.draw.rect(surface, BLACK, roof, border_radius=6)
            pygame.draw.rect(surface, CYAN, windshield, border_radius=4)
            pygame.draw.rect(surface, BLACK, (self.rect.x - 1, self.rect.y + 14, 7, 18), border_radius=2)
            pygame.draw.rect(surface, BLACK, (self.rect.right - 6, self.rect.y + 14, 7, 18), border_radius=2)
            pygame.draw.rect(surface, BLACK, (self.rect.x - 1, self.rect.y + 58, 7, 18), border_radius=2)
            pygame.draw.rect(surface, BLACK, (self.rect.right - 6, self.rect.y + 58, 7, 18), border_radius=2)

        if self.shield_ready:
            pygame.draw.ellipse(surface, CYAN, self.rect.inflate(18, 14), 3)

    def activate_powerup(self, kind):
        if self.active_powerup is not None:
            return False

        self.active_powerup = kind
        if kind == "nitro":
            self.active_powerup_time = 4.0
        elif kind == "shield":
            self.shield_ready = True
        elif kind == "repair":
            self.repair_ready = True
        return True

    def on_hard_collision(self):
        """Return True if the player survives the hit."""
        if self.invincible_time > 0:
            return True

        if self.shield_ready:
            self.shield_ready = False
            self.active_powerup = None
            self.invincible_time = 1.1
            return True

        if self.repair_ready:
            self.repair_ready = False
            self.active_powerup = None
            self.invincible_time = 1.1
            return True

        return False

    def powerup_label(self):
        if self.active_powerup == "nitro":
            return f"Nitro: {self.active_powerup_time:0.1f}s"
        if self.shield_ready:
            return "Shield: until hit"
        if self.repair_ready:
            return "Repair: ready"
        return "None"


class TrafficCar(WorldObject):
    def __init__(self, lane, y, speed):
        super().__init__(lane, y, 46, 86)
        self.speed = speed
        self.color = random.choice([RED, ORANGE, PURPLE, BLUE])

    def update(self, dt, world_speed):
        self.y += (world_speed + self.speed) * dt
        self.sync_rect()
        if self.y > HEIGHT + 120:
            self.kill()

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, (self.rect.x + 10, self.rect.y + 10, 26, 20), border_radius=6)
        pygame.draw.rect(surface, BLACK, (self.rect.x - 1, self.rect.y + 14, 7, 16), border_radius=2)
        pygame.draw.rect(surface, BLACK, (self.rect.right - 6, self.rect.y + 14, 7, 16), border_radius=2)
        pygame.draw.rect(surface, BLACK, (self.rect.x - 1, self.rect.y + 56, 7, 16), border_radius=2)
        pygame.draw.rect(surface, BLACK, (self.rect.right - 6, self.rect.y + 56, 7, 16), border_radius=2)


class OilSpill(WorldObject):
    def __init__(self, lane, y):
        super().__init__(lane, y, 58, 20)

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.sync_rect()
        if self.y > HEIGHT + 80:
            self.kill()

    def draw(self, surface):
        pygame.draw.ellipse(surface, BLACK, self.rect)
        pygame.draw.ellipse(surface, (40, 40, 50), self.rect.inflate(-14, -6))


class Pothole(WorldObject):
    def __init__(self, lane, y):
        super().__init__(lane, y, 52, 24)

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.sync_rect()
        if self.y > HEIGHT + 80:
            self.kill()

    def draw(self, surface):
        pygame.draw.ellipse(surface, (54, 33, 22), self.rect)
        pygame.draw.ellipse(surface, BLACK, self.rect, 2)


class MovingBarrier(WorldObject):
    def __init__(self, lane, y):
        super().__init__(lane, y, 82, 20)
        self.vx = random.choice([-120, 120])

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.x += self.vx * dt

        if self.x < ROAD_LEFT + 6:
            self.x = ROAD_LEFT + 6
            self.vx *= -1
        if self.x + self.width > ROAD_RIGHT - 6:
            self.x = ROAD_RIGHT - 6 - self.width
            self.vx *= -1

        self.sync_rect()
        if self.y > HEIGHT + 80:
            self.kill()

    def draw(self, surface):
        pygame.draw.rect(surface, ORANGE, self.rect, border_radius=6)
        for offset in range(0, self.rect.width, 18):
            pygame.draw.line(surface, BLACK, (self.rect.x + offset, self.rect.y), (self.rect.x + offset + 10, self.rect.bottom), 3)


class SpeedBump(WorldObject):
    def __init__(self, lane, y):
        super().__init__(lane, y, int(LANE_WIDTH - 26), 14)

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.sync_rect()
        if self.y > HEIGHT + 50:
            self.kill()

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect, border_radius=6)
        pygame.draw.rect(surface, YELLOW, self.rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=6)


class NitroStrip(WorldObject):
    def __init__(self, lane, y):
        super().__init__(lane, y, int(LANE_WIDTH - 26), 18)

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.sync_rect()
        if self.y > HEIGHT + 50:
            self.kill()

    def draw(self, surface):
        pygame.draw.rect(surface, PINK, self.rect, border_radius=6)
        for i in range(5):
            pygame.draw.line(surface, WHITE, (self.rect.x + 12 + i * 18, self.rect.y + 2), (self.rect.x + 4 + i * 18, self.rect.bottom - 2), 2)


class Coin(WorldObject):
    def __init__(self, lane, y, value, color, radius):
        super().__init__(lane, y, radius * 2 + 8, radius * 2 + 8)
        self.value = value
        self.color = color
        self.radius = radius

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.sync_rect()
        if self.y > HEIGHT + 50:
            self.kill()

    def draw(self, surface):
        center = self.rect.center
        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, BLACK, center, self.radius, 2)
        draw_text(surface, str(self.value), TINY_FONT, BLACK, center[0], center[1], center=True)


class PowerUp(WorldObject):
    def __init__(self, lane, y, kind):
        super().__init__(lane, y, 34, 34)
        self.kind = kind
        self.life_time = 6.0

    def update(self, dt, world_speed):
        self.y += world_speed * dt
        self.life_time -= dt
        self.sync_rect()
        if self.y > HEIGHT + 60 or self.life_time <= 0:
            self.kill()

    def draw(self, surface):
        color_map = {
            "nitro": PINK,
            "shield": CYAN,
            "repair": GREEN,
        }
        label_map = {
            "nitro": "N",
            "shield": "S",
            "repair": "R",
        }
        pygame.draw.circle(surface, color_map[self.kind], self.rect.center, 18)
        pygame.draw.circle(surface, BLACK, self.rect.center, 18, 2)
        draw_text(surface, label_map[self.kind], FONT, BLACK, self.rect.centerx, self.rect.centery - 1, center=True)


# -------------------------------------------------
# Main application
# -------------------------------------------------
class RacerApp:
    def __init__(self):
        default_settings = {
            "sound": True,
            "car_color": "blue",
            "difficulty": "normal",
            "username": "Player",
        }
        self.settings = load_json(SETTINGS_FILE, default_settings)
        self.leaderboard = load_json(LEADERBOARD_FILE, [])

        self.state = "menu"
        self.running = True

        self.username_input = TextInput((160, 145, 200, 44), self.settings.get("username", "Player"))

        self.menu_buttons = {
            "start": Button((180, 230, 160, 50), "Start Game"),
            "settings": Button((180, 295, 160, 50), "Settings"),
            "leaderboard": Button((180, 360, 160, 50), "Leaderboard"),
            "quit": Button((180, 425, 160, 50), "Quit"),
        }

        self.settings_buttons = {
            "sound": Button((160, 210, 200, 50), "Sound"),
            "difficulty": Button((160, 280, 200, 50), "Difficulty"),
            "car_color": Button((160, 350, 200, 50), "Car Color"),
            "back": Button((180, 450, 160, 50), "Back"),
        }

        self.over_buttons = {
            "retry": Button((145, 420, 100, 48), "Retry"),
            "menu": Button((275, 420, 100, 48), "Menu"),
        }

        self.leaderboard_back = Button((180, 650, 160, 48), "Back")

        self.reset_run_state()

    # ---------------------------------------------
    # Save / load helpers
    # ---------------------------------------------
    def save_settings(self):
        self.settings["username"] = self.username_input.text.strip() or "Player"
        save_json(SETTINGS_FILE, self.settings)

    def save_leaderboard(self):
        self.leaderboard = sorted(self.leaderboard, key=lambda item: item["score"], reverse=True)[:10]
        save_json(LEADERBOARD_FILE, self.leaderboard)

    # ---------------------------------------------
    # Run state
    # ---------------------------------------------
    def reset_run_state(self):
        preset = DIFFICULTY_PRESETS[self.settings.get("difficulty", "normal")]
        self.player = Player(self.settings.get("car_color", "blue"))

        self.traffic = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.events = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.distance_m = 0.0
        self.coin_count = 0
        self.coin_value = 0
        self.bonus_score = 0
        self.speed_level = 0
        self.game_over_saved = False
        self.flash_message = ""
        self.flash_timer = 0.0

        self.traffic_timer = 0.0
        self.obstacle_timer = 0.0
        self.coin_timer = 0.0
        self.event_timer = 0.0
        self.powerup_timer = 0.0
        self.road_offset = 0.0

        self.base_world_speed = preset["world_speed"]
        self.current_world_speed = self.base_world_speed
        self.run_over = False

    def start_new_game(self):
        self.username_input.text = self.username_input.text.strip() or "Player"
        self.settings["username"] = self.username_input.text
        self.save_settings()
        self.reset_run_state()
        self.state = "game"

    def current_score(self):
        return int(self.distance_m + self.coin_value * 25 + self.bonus_score)

    def add_flash(self, message):
        self.flash_message = message
        self.flash_timer = 1.3

    # ---------------------------------------------
    # Spawning helpers
    # ---------------------------------------------
    def free_spawn_lanes(self):
        blocked = set()
        for group in (self.traffic, self.obstacles, self.events, self.coins, self.powerups):
            for sprite in group:
                if sprite.y < 150:
                    blocked.add(getattr(sprite, "lane", -1))
        lanes = [lane for lane in range(LANES) if lane not in blocked]
        return lanes if lanes else list(range(LANES))

    def spawn_traffic(self, amount=1):
        lanes = self.free_spawn_lanes()
        random.shuffle(lanes)
        for lane in lanes[:amount]:
            extra_speed = random.randint(35, 110)
            self.traffic.add(TrafficCar(lane, -120, extra_speed))

    def spawn_obstacle(self):
        lane = random.choice(self.free_spawn_lanes())
        kind = random.choice(["oil", "pothole", "pothole"])
        if kind == "oil":
            self.obstacles.add(OilSpill(lane, -80))
        else:
            self.obstacles.add(Pothole(lane, -80))

    def spawn_event(self):
        lane = random.choice(self.free_spawn_lanes())
        kind = random.choice(["barrier", "speed_bump", "nitro_strip"])
        if kind == "barrier":
            self.events.add(MovingBarrier(lane, -90))
        elif kind == "speed_bump":
            self.events.add(SpeedBump(lane, -50))
        else:
            self.events.add(NitroStrip(lane, -50))

    def spawn_coin(self):
        lane = random.choice(self.free_spawn_lanes())
        coin_types = [
            (1, YELLOW, 11),
            (2, ORANGE, 12),
            (5, PURPLE, 13),
        ]
        value, color, radius = random.choices(coin_types, weights=[0.60, 0.28, 0.12], k=1)[0]
        self.coins.add(Coin(lane, -60, value, color, radius))

    def spawn_powerup(self):
        lane = random.choice(self.free_spawn_lanes())
        kind = random.choice(["nitro", "shield", "repair"])
        self.powerups.add(PowerUp(lane, -60, kind))

    # ---------------------------------------------
    # Event handling by screen
    # ---------------------------------------------
    def handle_menu_event(self, event):
        self.username_input.handle_event(event)

        if self.menu_buttons["start"].is_clicked(event):
            self.start_new_game()
        elif self.menu_buttons["settings"].is_clicked(event):
            self.state = "settings"
        elif self.menu_buttons["leaderboard"].is_clicked(event):
            self.state = "leaderboard"
        elif self.menu_buttons["quit"].is_clicked(event):
            self.running = False

    def handle_settings_event(self, event):
        if self.settings_buttons["sound"].is_clicked(event):
            self.settings["sound"] = not self.settings.get("sound", True)
            self.save_settings()
        elif self.settings_buttons["difficulty"].is_clicked(event):
            order = ["easy", "normal", "hard"]
            current = self.settings.get("difficulty", "normal")
            next_index = (order.index(current) + 1) % len(order)
            self.settings["difficulty"] = order[next_index]
            self.save_settings()
        elif self.settings_buttons["car_color"].is_clicked(event):
            order = list(CAR_COLORS.keys())
            current = self.settings.get("car_color", "blue")
            next_index = (order.index(current) + 1) % len(order)
            self.settings["car_color"] = order[next_index]
            self.save_settings()
        elif self.settings_buttons["back"].is_clicked(event):
            self.state = "menu"

    def handle_game_over_event(self, event):
        if self.over_buttons["retry"].is_clicked(event):
            self.start_new_game()
        elif self.over_buttons["menu"].is_clicked(event):
            self.state = "menu"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.start_new_game()

    def handle_leaderboard_event(self, event):
        if self.leaderboard_back.is_clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.state = "menu"

    def handle_global_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state == "menu":
                self.handle_menu_event(event)
            elif self.state == "settings":
                self.handle_settings_event(event)
            elif self.state == "game_over":
                self.handle_game_over_event(event)
            elif self.state == "leaderboard":
                self.handle_leaderboard_event(event)

    # ---------------------------------------------
    # Game update logic
    # ---------------------------------------------
    def update_game(self, dt):
        if self.run_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)

        # Distance increases with road speed.
        scale = difficulty_scale(self.distance_m)
        self.speed_level = self.coin_count // 2

        bonus_world_speed = self.speed_level * 18
        if self.player.active_powerup == "nitro":
            bonus_world_speed += 55
        if self.player.strip_boost_time > 0:
            bonus_world_speed += 28
        if self.player.slowdown_time > 0:
            bonus_world_speed -= 45

        self.current_world_speed = max(230, self.base_world_speed * scale + bonus_world_speed)
        self.distance_m += self.current_world_speed * dt * 0.05
        self.road_offset = (self.road_offset + self.current_world_speed * dt) % 70

        preset = DIFFICULTY_PRESETS[self.settings.get("difficulty", "normal")]

        self.traffic_timer += dt
        self.obstacle_timer += dt
        self.coin_timer += dt
        self.event_timer += dt
        self.powerup_timer += dt

        traffic_interval = max(0.42, preset["traffic_interval"] / scale)
        obstacle_interval = max(0.70, preset["obstacle_interval"] / scale)
        coin_interval = max(0.42, preset["coin_interval"] / min(scale, 1.35))
        event_interval = max(1.80, preset["event_interval"] / min(scale, 1.55))
        powerup_interval = preset["powerup_interval"]

        if self.traffic_timer >= traffic_interval:
            self.traffic_timer = 0.0
            amount = 2 if random.random() < min(0.18 + self.distance_m / 5000.0, 0.45) else 1
            self.spawn_traffic(amount=amount)

        if self.obstacle_timer >= obstacle_interval:
            self.obstacle_timer = 0.0
            self.spawn_obstacle()

        if self.coin_timer >= coin_interval:
            self.coin_timer = 0.0
            self.spawn_coin()

        if self.event_timer >= event_interval:
            self.event_timer = 0.0
            self.spawn_event()

        if self.powerup_timer >= powerup_interval:
            self.powerup_timer = 0.0
            if len(self.powerups) == 0:
                self.spawn_powerup()

        for group in (self.traffic, self.obstacles, self.events, self.coins, self.powerups):
            for sprite in group:
                sprite.update(dt, self.current_world_speed)

        # Handle collisions with traffic cars.
        traffic_hits = pygame.sprite.spritecollide(self.player, self.traffic, True)
        if traffic_hits:
            survived = self.player.on_hard_collision()
            if survived:
                self.bonus_score += 25
                self.add_flash("Saved by a power-up")
            else:
                self.end_run()
                return

        # Handle collisions with obstacles.
        obstacle_hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        for obstacle in obstacle_hits:
            if isinstance(obstacle, OilSpill):
                self.player.slip_time = 1.25
                obstacle.kill()
                self.add_flash("Oil spill - controls reversed")
            elif isinstance(obstacle, Pothole):
                survived = self.player.on_hard_collision()
                obstacle.kill()
                if survived:
                    self.bonus_score += 20
                    self.add_flash("Repair/Shield saved you")
                else:
                    self.end_run()
                    return

        # Handle dynamic road events.
        event_hits = pygame.sprite.spritecollide(self.player, self.events, False)
        for event_sprite in event_hits:
            if isinstance(event_sprite, MovingBarrier):
                survived = self.player.on_hard_collision()
                event_sprite.kill()
                if survived:
                    self.bonus_score += 20
                    self.add_flash("Barrier blocked by power-up")
                else:
                    self.end_run()
                    return
            elif isinstance(event_sprite, SpeedBump):
                self.player.slowdown_time = 1.3
                event_sprite.kill()
                self.add_flash("Speed bump - slowed down")
            elif isinstance(event_sprite, NitroStrip):
                self.player.strip_boost_time = 1.6
                event_sprite.kill()
                self.bonus_score += 10
                self.add_flash("Nitro strip boost")

        # Collect coins.
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_hits:
            self.coin_count += 1
            self.coin_value += coin.value
            self.bonus_score += coin.value * 2

        # Collect power-ups only if no power-up is currently active.
        for powerup in pygame.sprite.spritecollide(self.player, self.powerups, False):
            if self.player.activate_powerup(powerup.kind):
                self.bonus_score += 30
                self.add_flash(f"Collected {powerup.kind.title()}")
                powerup.kill()

        self.flash_timer = max(0.0, self.flash_timer - dt)

    def end_run(self):
        self.run_over = True
        if not self.game_over_saved:
            entry = {
                "name": self.settings.get("username", "Player") or "Player",
                "score": self.current_score(),
                "coins": self.coin_count,
                "distance": round(self.distance_m, 1),
            }
            self.leaderboard.append(entry)
            self.save_leaderboard()
            self.game_over_saved = True
        self.state = "game_over"

    # ---------------------------------------------
    # Drawing
    # ---------------------------------------------
    def draw_background(self):
        SCREEN.fill(GREEN)
        pygame.draw.rect(SCREEN, ROAD_GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.line(SCREEN, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
        pygame.draw.line(SCREEN, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

        # Dashed lane lines
        for lane in range(1, LANES):
            x = ROAD_LEFT + lane * LANE_WIDTH
            for y in range(-70, HEIGHT + 70, 70):
                pygame.draw.rect(SCREEN, LIGHT_GRAY, (x - 4, y + self.road_offset, 8, 38), border_radius=4)

    def draw_menu(self):
        SCREEN.fill(DARK)
        draw_text(SCREEN, "ADVANCED RACER", BIG_FONT, WHITE, WIDTH // 2, 82, center=True)
        draw_text(SCREEN, "Type your name, then start the run.", SMALL_FONT, LIGHT_GRAY, WIDTH // 2, 112, center=True)

        self.username_input.draw(SCREEN, "Username")

        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons.values():
            button.draw(SCREEN, mouse_pos)

        draw_text(SCREEN, f"Current difficulty: {self.settings['difficulty'].title()}", SMALL_FONT, CYAN, WIDTH // 2, 525, center=True)
        draw_text(SCREEN, f"Car color: {self.settings['car_color'].title()}", SMALL_FONT, CYAN, WIDTH // 2, 555, center=True)
        draw_text(SCREEN, f"Sound: {'On' if self.settings['sound'] else 'Off'}", SMALL_FONT, CYAN, WIDTH // 2, 585, center=True)
        draw_text(SCREEN, "Power-ups: Nitro, Shield, Repair", TINY_FONT, LIGHT_GRAY, WIDTH // 2, 645, center=True)
        draw_text(SCREEN, "Only one power-up can be active at a time.", TINY_FONT, LIGHT_GRAY, WIDTH // 2, 665, center=True)

    def draw_settings(self):
        SCREEN.fill(DARK)
        draw_text(SCREEN, "SETTINGS", BIG_FONT, WHITE, WIDTH // 2, 82, center=True)
        draw_text(SCREEN, "Click a button to cycle values.", SMALL_FONT, LIGHT_GRAY, WIDTH // 2, 116, center=True)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.settings_buttons.values():
            button.draw(SCREEN, mouse_pos)

        draw_text(SCREEN, f"Sound: {'On' if self.settings['sound'] else 'Off'}", FONT, WHITE, WIDTH // 2, 236, center=True)
        draw_text(SCREEN, f"Difficulty: {self.settings['difficulty'].title()}", FONT, WHITE, WIDTH // 2, 306, center=True)
        draw_text(SCREEN, f"Car Color: {self.settings['car_color'].title()}", FONT, WHITE, WIDTH // 2, 376, center=True)

        preview_rect = pygame.Rect(WIDTH // 2 - 25, 555, 50, 92)
        pygame.draw.rect(SCREEN, CAR_COLORS[self.settings['car_color']], preview_rect, border_radius=10)
        pygame.draw.rect(SCREEN, BLACK, (preview_rect.x + 10, preview_rect.y + 10, 30, 22), border_radius=6)
        draw_text(SCREEN, "Car preview", SMALL_FONT, LIGHT_GRAY, WIDTH // 2, 530, center=True)

    def draw_leaderboard(self):
        SCREEN.fill(DARK)
        draw_text(SCREEN, "TOP 10 LEADERBOARD", BIG_FONT, WHITE, WIDTH // 2, 72, center=True)

        header_y = 140
        draw_text(SCREEN, "Rank", SMALL_FONT, CYAN, 55, header_y)
        draw_text(SCREEN, "Name", SMALL_FONT, CYAN, 125, header_y)
        draw_text(SCREEN, "Score", SMALL_FONT, CYAN, 245, header_y)
        draw_text(SCREEN, "Coins", SMALL_FONT, CYAN, 335, header_y)
        draw_text(SCREEN, "Distance", SMALL_FONT, CYAN, 405, header_y)

        for index, row in enumerate(self.leaderboard[:10], start=1):
            y = 170 + (index - 1) * 42
            pygame.draw.rect(SCREEN, (36, 40, 48), (40, y - 6, 440, 34), border_radius=10)
            draw_text(SCREEN, str(index), SMALL_FONT, WHITE, 58, y)
            draw_text(SCREEN, row.get("name", "Player"), SMALL_FONT, WHITE, 120, y)
            draw_text(SCREEN, str(row.get("score", 0)), SMALL_FONT, WHITE, 245, y)
            draw_text(SCREEN, str(row.get("coins", 0)), SMALL_FONT, WHITE, 345, y)
            draw_text(SCREEN, str(row.get("distance", 0)), SMALL_FONT, WHITE, 410, y)

        if not self.leaderboard:
            draw_text(SCREEN, "No saved scores yet.", FONT, LIGHT_GRAY, WIDTH // 2, 290, center=True)

        self.leaderboard_back.draw(SCREEN, pygame.mouse.get_pos())

    def draw_game(self):
        self.draw_background()

        for group in (self.coins, self.powerups, self.obstacles, self.events, self.traffic):
            for sprite in group:
                sprite.draw(SCREEN)
        self.player.draw(SCREEN)

        # HUD panel
        hud = pygame.Rect(12, 10, 496, 88)
        pygame.draw.rect(SCREEN, (18, 20, 28), hud, border_radius=16)
        pygame.draw.rect(SCREEN, LIGHT_GRAY, hud, 2, border_radius=16)

        draw_text(SCREEN, f"Score: {self.current_score()}", SMALL_FONT, WHITE, 24, 22)
        draw_text(SCREEN, f"Distance: {self.distance_m:0.1f} m", SMALL_FONT, WHITE, 24, 48)

        draw_text(SCREEN, f"Coins: {self.coin_count}", SMALL_FONT, YELLOW, 190, 22)
        draw_text(SCREEN, f"Coin Value: {self.coin_value}", SMALL_FONT, WHITE, 190, 48)

        draw_text(SCREEN, f"Speed Lv: {self.speed_level}", SMALL_FONT, CYAN, 350, 22)
        draw_text(SCREEN, f"Power-up: {self.player.powerup_label()}", SMALL_FONT, WHITE, 350, 48)

        if self.flash_timer > 0:
            draw_text(SCREEN, self.flash_message, FONT, WHITE, WIDTH // 2, 124, center=True)

    def draw_game_over(self):
        SCREEN.fill(DARK)
        draw_text(SCREEN, "GAME OVER", BIG_FONT, WHITE, WIDTH // 2, 130, center=True)
        draw_text(SCREEN, f"Player: {self.settings.get('username', 'Player')}", FONT, LIGHT_GRAY, WIDTH // 2, 190, center=True)
        draw_text(SCREEN, f"Final Score: {self.current_score()}", FONT, WHITE, WIDTH // 2, 240, center=True)
        draw_text(SCREEN, f"Distance: {self.distance_m:0.1f} m", FONT, WHITE, WIDTH // 2, 275, center=True)
        draw_text(SCREEN, f"Coins: {self.coin_count}  |  Value: {self.coin_value}", FONT, YELLOW, WIDTH // 2, 310, center=True)
        draw_text(SCREEN, f"Difficulty: {self.settings['difficulty'].title()}", FONT, CYAN, WIDTH // 2, 345, center=True)
        draw_text(SCREEN, "Your result was saved to leaderboard.json", SMALL_FONT, LIGHT_GRAY, WIDTH // 2, 380, center=True)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.over_buttons.values():
            button.draw(SCREEN, mouse_pos)

        draw_text(SCREEN, "Press Enter to start again.", SMALL_FONT, LIGHT_GRAY, WIDTH // 2, 510, center=True)

    # ---------------------------------------------
    # Main loop
    # ---------------------------------------------
    def run(self):
        while self.running:
            dt = CLOCK.tick(FPS) / 1000.0
            self.handle_global_events()

            if self.state == "game":
                self.update_game(dt)

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "settings":
                self.draw_settings()
            elif self.state == "leaderboard":
                self.draw_leaderboard()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.flip()

        self.save_settings()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = RacerApp()
    app.run()