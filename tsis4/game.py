from __future__ import annotations

import random
from typing import Dict, List, Optional, Set, Tuple

import pygame

# -------------------- WINDOW / GRID --------------------
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
HUD_HEIGHT = 110
TOTAL_HEIGHT = WINDOW_HEIGHT + HUD_HEIGHT

# -------------------- COLORS --------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (110, 110, 110)
DARK_GRAY = (50, 50, 50)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
YELLOW = (255, 210, 0)
BLUE = (0, 120, 255)
CYAN = (0, 210, 255)
PURPLE = (160, 40, 220)
ORANGE = (255, 140, 0)
SILVER = (210, 210, 210)

# -------------------- GAME RULES --------------------
BASE_SPEED = 8
SPEED_INCREASE_PER_LEVEL = 2
SCORE_PER_LEVEL = 4

NORMAL_FOOD_TYPES = [
    {'name': 'Apple', 'color': RED, 'score': 1, 'grow': 1, 'chance': 60, 'lifetime': 8000},
    {'name': 'Banana', 'color': YELLOW, 'score': 2, 'grow': 2, 'chance': 30, 'lifetime': 6500},
    {'name': 'Berry', 'color': PURPLE, 'score': 3, 'grow': 3, 'chance': 10, 'lifetime': 5000},
]

POWER_UP_TYPES = {
    'speed_boost': {
        'label': 'Speed boost',
        'color': CYAN,
        'duration': 5000,
        'speed_delta': 4,
    },
    'slow_motion': {
        'label': 'Slow motion',
        'color': BLUE,
        'duration': 5000,
        'speed_delta': -3,
    },
    'shield': {
        'label': 'Shield',
        'color': SILVER,
        'duration': None,
        'speed_delta': 0,
    },
}

Position = Tuple[int, int]


class SnakeGame:
    """Contains all gameplay logic. The menu and other screens live in main.py."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, settings: Dict, username: str, personal_best: Optional[int]):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.username = username
        self.personal_best = personal_best

        self.font = pygame.font.SysFont('Arial', 22)
        self.small_font = pygame.font.SysFont('Arial', 18)

        # Initial snake state.
        self.snake: List[Position] = [(5, 5), (4, 5), (3, 5)]
        self.direction: Position = (1, 0)
        self.pending_growth = 0

        # Walls always exist around the border.
        self.walls = self.create_border_walls()
        self.obstacles: Set[Position] = set()

        # Score / level / status values.
        self.score = 0
        self.level = 1
        self.running = True
        self.game_over_reason = 'collision'

        # Foods and power-ups.
        # Initialize these attributes before generating the first food,
        # because random_empty_cell() -> occupied_cells() checks them.
        self.normal_food = None
        self.poison_food = None
        self.power_up = None
        self.normal_food = self.generate_normal_food()
        self.next_poison_spawn_check = 0
        self.next_power_up_check = 0

        # Power-up effect state.
        self.active_timed_effect = None
        self.active_timed_effect_end = 0
        self.shield_ready = False

    # -------------------- BASIC HELPERS --------------------
    def create_border_walls(self) -> Set[Position]:
        """Create static walls around the outer border."""
        walls: Set[Position] = set()
        for x in range(GRID_WIDTH):
            walls.add((x, 0))
            walls.add((x, GRID_HEIGHT - 1))
        for y in range(GRID_HEIGHT):
            walls.add((0, y))
            walls.add((GRID_WIDTH - 1, y))
        return walls

    def occupied_cells(self) -> Set[Position]:
        """Cells that new items are not allowed to use."""
        occupied = set(self.walls)
        occupied.update(self.snake)
        occupied.update(self.obstacles)
        if self.normal_food:
            occupied.add(self.normal_food['pos'])
        if self.poison_food:
            occupied.add(self.poison_food['pos'])
        if self.power_up:
            occupied.add(self.power_up['pos'])
        return occupied

    def random_empty_cell(self, extra_blocked: Optional[Set[Position]] = None) -> Optional[Position]:
        """Pick a free position for food, poison, power-ups, or obstacles."""
        blocked = self.occupied_cells()
        if extra_blocked:
            blocked.update(extra_blocked)

        free_cells = [
            (x, y)
            for x in range(1, GRID_WIDTH - 1)
            for y in range(1, GRID_HEIGHT - 1)
            if (x, y) not in blocked
        ]
        if not free_cells:
            return None
        return random.choice(free_cells)

    def choose_food_type(self) -> Dict:
        """Weighted random selection for normal foods."""
        weights = [item['chance'] for item in NORMAL_FOOD_TYPES]
        return random.choices(NORMAL_FOOD_TYPES, weights=weights, k=1)[0]

    def generate_normal_food(self) -> Dict:
        """Create a normal food item with lifetime and weighted type."""
        pos = self.random_empty_cell()
        food_type = self.choose_food_type()
        return {
            'pos': pos,
            'type': food_type,
            'spawn_time': pygame.time.get_ticks(),
        }

    def spawn_poison_food(self):
        """Spawn poison food as a second item on the field."""
        pos = self.random_empty_cell()
        if pos is None:
            return
        self.poison_food = {
            'pos': pos,
            'color': DARK_RED,
            'spawn_time': pygame.time.get_ticks(),
            'lifetime': 7000,
        }

    def maybe_spawn_poison_food(self, now: int):
        """Poison food appears randomly alongside normal food."""
        if self.poison_food is not None:
            return
        if now < self.next_poison_spawn_check:
            return

        self.next_poison_spawn_check = now + 2000
        if random.random() < 0.40:
            self.spawn_poison_food()

    def maybe_spawn_power_up(self, now: int):
        """Only one power-up item can exist on the field at a time."""
        if self.power_up is not None:
            return
        if now < self.next_power_up_check:
            return

        self.next_power_up_check = now + 3000
        if random.random() < 0.30:
            pos = self.random_empty_cell()
            if pos is None:
                return
            power_name = random.choice(list(POWER_UP_TYPES.keys()))
            self.power_up = {
                'name': power_name,
                'pos': pos,
                'spawn_time': now,
                'lifetime': 8000,
            }

    def build_obstacles_for_level(self):
        """Starting from level 3, create interior static wall blocks."""
        if self.level < 3:
            self.obstacles = set()
            return

        obstacle_count = min(3 + (self.level - 3), 8)
        head_x, head_y = self.snake[0]

        # Keep the area around the snake head clear, so the new walls do not trap it.
        safe_zone = {
            (x, y)
            for x in range(head_x - 2, head_x + 3)
            for y in range(head_y - 2, head_y + 3)
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT
        }

        new_obstacles: Set[Position] = set()
        for _ in range(obstacle_count):
            extra_blocked = set(new_obstacles)
            extra_blocked.update(safe_zone)
            pos = self.random_empty_cell(extra_blocked)
            if pos is not None:
                new_obstacles.add(pos)

        self.obstacles = new_obstacles

        # Reposition food or power-up if something went wrong and an item ended up inside obstacles.
        if self.normal_food and self.normal_food['pos'] in self.obstacles:
            self.normal_food = self.generate_normal_food()
        if self.poison_food and self.poison_food['pos'] in self.obstacles:
            self.poison_food = None
        if self.power_up and self.power_up['pos'] in self.obstacles:
            self.power_up = None

    def activate_power_up(self, power_name: str, now: int):
        """Apply the power-up effect after the snake collects the item."""
        if power_name == 'shield':
            self.shield_ready = True
            self.active_timed_effect = None
            self.active_timed_effect_end = 0
            return

        self.active_timed_effect = power_name
        self.active_timed_effect_end = now + POWER_UP_TYPES[power_name]['duration']

    def update_timed_effects(self, now: int):
        """Stop speed boost / slow motion when their timer ends."""
        if self.active_timed_effect and now >= self.active_timed_effect_end:
            self.active_timed_effect = None
            self.active_timed_effect_end = 0

    def current_speed(self) -> int:
        """Speed grows with level and may change because of power-ups."""
        speed = BASE_SPEED + (self.level - 1) * SPEED_INCREASE_PER_LEVEL
        if self.active_timed_effect:
            speed += POWER_UP_TYPES[self.active_timed_effect]['speed_delta']
        return max(4, speed)

    def level_from_score(self) -> int:
        return (self.score // SCORE_PER_LEVEL) + 1

    def will_tail_move(self, normal_food_hit: bool) -> bool:
        """Used for correct self-collision logic when the tail leaves its cell."""
        if normal_food_hit:
            return False
        if self.pending_growth > 0:
            return False
        return True

    # -------------------- GAMEPLAY --------------------
    def handle_food_timers(self, now: int):
        """Normal food, poison food, and power-ups disappear after some time."""
        if self.normal_food and now - self.normal_food['spawn_time'] >= self.normal_food['type']['lifetime']:
            self.normal_food = self.generate_normal_food()

        if self.poison_food and now - self.poison_food['spawn_time'] >= self.poison_food['lifetime']:
            self.poison_food = None

        if self.power_up and now - self.power_up['spawn_time'] >= self.power_up['lifetime']:
            self.power_up = None

    def consume_poison_food(self):
        """Poison food shortens the snake by 2 segments."""
        self.poison_food = None

        for _ in range(2):
            if len(self.snake) > 1:
                self.snake.pop()

        if len(self.snake) <= 1:
            self.game_over_reason = 'poison'
            self.running = False

    def update_level_and_obstacles(self):
        """Increase level using score and regenerate level-based obstacles."""
        new_level = self.level_from_score()
        if new_level != self.level:
            self.level = new_level
            self.build_obstacles_for_level()

    def process_collision(self, collision_happened: bool) -> bool:
        """Shield ignores one wall / self / obstacle collision once."""
        if not collision_happened:
            return False
        if self.shield_ready:
            self.shield_ready = False
            return True
        self.running = False
        self.game_over_reason = 'collision'
        return False

    def step(self):
        """Move the snake by one cell and handle all interactions."""
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        normal_food_hit = self.normal_food and new_head == self.normal_food['pos']
        poison_food_hit = self.poison_food and new_head == self.poison_food['pos']
        power_up_hit = self.power_up and new_head == self.power_up['pos']

        wall_hit = (
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.walls
        )
        obstacle_hit = new_head in self.obstacles

        # Moving into the tail is allowed if the tail will move away on this same step.
        tail_moves = self.will_tail_move(normal_food_hit=bool(normal_food_hit))
        body_to_check = self.snake[:-1] if tail_moves else self.snake
        self_hit = new_head in body_to_check

        if self.process_collision(wall_hit or obstacle_hit or self_hit):
            return
        if not self.running:
            return

        # Safe move: add the new head.
        self.snake.insert(0, new_head)

        if normal_food_hit:
            self.score += self.normal_food['type']['score']
            self.pending_growth += self.normal_food['type']['grow'] - 1
            self.normal_food = self.generate_normal_food()
            self.update_level_and_obstacles()
        elif poison_food_hit:
            self.consume_poison_food()
            if not self.running:
                return
        else:
            if self.pending_growth > 0:
                self.pending_growth -= 1
            else:
                self.snake.pop()

        if power_up_hit and self.power_up:
            self.activate_power_up(self.power_up['name'], pygame.time.get_ticks())
            self.power_up = None

    # -------------------- DRAWING --------------------
    def draw_cell(self, pos: Position, color: Tuple[int, int, int]):
        rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE + HUD_HEIGHT, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_grid(self):
        if not self.settings.get('grid', True):
            return
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x, HUD_HEIGHT), (x, TOTAL_HEIGHT))
        for y in range(HUD_HEIGHT, TOTAL_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y))

    def draw_hud(self, now: int):
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))

        food_seconds = 0
        if self.normal_food:
            left = self.normal_food['type']['lifetime'] - (now - self.normal_food['spawn_time'])
            food_seconds = max(0, (left + 999) // 1000)

        pb_text = '-' if self.personal_best is None else str(self.personal_best)
        power_text = 'None'
        if self.active_timed_effect:
            remaining = max(0, (self.active_timed_effect_end - now + 999) // 1000)
            power_text = f"{POWER_UP_TYPES[self.active_timed_effect]['label']} ({remaining}s)"
        elif self.shield_ready:
            power_text = 'Shield ready'

        self.screen.blit(self.font.render(f'User: {self.username}', True, WHITE), (12, 8))
        self.screen.blit(self.font.render(f'Score: {self.score}', True, WHITE), (12, 35))
        self.screen.blit(self.font.render(f'Level: {self.level}', True, WHITE), (150, 35))
        self.screen.blit(self.font.render(f'Speed: {self.current_speed()}', True, WHITE), (260, 35))
        self.screen.blit(self.small_font.render(f'Personal best: {pb_text}', True, WHITE), (12, 65))
        self.screen.blit(self.small_font.render(f'Food timer: {food_seconds}s', True, WHITE), (210, 65))
        self.screen.blit(self.small_font.render(f'Power-up: {power_text}', True, WHITE), (360, 65))

    def draw(self, now: int):
        self.screen.fill(BLACK)
        self.draw_hud(now)
        self.draw_grid()

        # Draw border walls and inner obstacles.
        for wall in self.walls:
            self.draw_cell(wall, GRAY)
        for block in self.obstacles:
            self.draw_cell(block, ORANGE)

        # Draw snake using the saved color from settings.
        snake_color = tuple(self.settings.get('snake_color', [0, 200, 0]))
        head_color = tuple(max(0, min(255, c - 50)) for c in snake_color)
        self.draw_cell(self.snake[0], head_color)
        for segment in self.snake[1:]:
            self.draw_cell(segment, snake_color)

        # Normal weighted food.
        if self.normal_food and self.normal_food['pos']:
            self.draw_cell(self.normal_food['pos'], self.normal_food['type']['color'])

        # Poison food.
        if self.poison_food:
            self.draw_cell(self.poison_food['pos'], self.poison_food['color'])

        # Power-up item.
        if self.power_up:
            item_color = POWER_UP_TYPES[self.power_up['name']]['color']
            self.draw_cell(self.power_up['pos'], item_color)

        pygame.display.flip()

    # -------------------- MAIN LOOP --------------------
    def run(self) -> Dict:
        """Run the snake game and return score / level when it ends."""
        move_event = pygame.USEREVENT + 1

        # IMPORTANT:
        # Do not reset the timer every frame, otherwise the event may never fire
        # and the snake will look frozen. Update it only when the speed changes.
        last_speed = self.current_speed()
        pygame.time.set_timer(move_event, int(1000 / last_speed))

        while self.running:
            now = pygame.time.get_ticks()
            self.handle_food_timers(now)
            self.maybe_spawn_poison_food(now)
            self.maybe_spawn_power_up(now)
            self.update_timed_effects(now)

            # Update movement timer only when speed really changes.
            current_speed = self.current_speed()
            if current_speed != last_speed:
                last_speed = current_speed
                pygame.time.set_timer(move_event, int(1000 / last_speed))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.time.set_timer(move_event, 0)
                    return {'quit_app': True}

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.direction = (1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        pygame.time.set_timer(move_event, 0)
                        return {'back_to_menu': True}

                if event.type == move_event:
                    self.step()

            self.draw(now)
            self.clock.tick(60)

        pygame.time.set_timer(move_event, 0)
        return {
            'score': self.score,
            'level': self.level,
            'reason': self.game_over_reason,
        }
