import pygame
import random
import sys

# -------------------- SETTINGS --------------------
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20

WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
GRAY = (90, 90, 90)

# Level settings
BASE_SPEED = 8
SPEED_INCREASE = 2
SCORE_PER_LEVEL = 4  # next level every 4 score points

# Food types
# "chance" means probability to appear
# "score" means how many points player gets
# "grow" means how many cells snake grows
# "lifetime" is how long food stays on screen in milliseconds
FOOD_TYPES = [
    {"name": "Apple",  "color": RED,    "score": 1, "grow": 1, "chance": 60, "lifetime": 8000},
    {"name": "Banana", "color": YELLOW, "score": 2, "grow": 2, "chance": 30, "lifetime": 6000},
    {"name": "Berry",  "color": PURPLE, "score": 3, "grow": 3, "chance": 10, "lifetime": 4000},
]

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)


# -------------------- HELPER FUNCTIONS --------------------
def draw_text(text, font_obj, color, x, y):
    """Draw text on the screen."""
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))


def draw_cell(position, color):
    """Draw one square cell at a grid position."""
    x, y = position
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 1)


def create_walls():
    """
    Create walls around the border of the playing field.
    Snake dies if it hits these walls.
    """
    walls = []

    # Top and bottom walls
    for x in range(GRID_WIDTH):
        walls.append((x, 0))
        walls.append((x, GRID_HEIGHT - 1))

    # Left and right walls
    for y in range(GRID_HEIGHT):
        walls.append((0, y))
        walls.append((GRID_WIDTH - 1, y))

    return walls


def choose_food_type():
    """
    Randomly choose a food type using different weights.
    Food with bigger 'chance' value appears more often.
    """
    chances = [food["chance"] for food in FOOD_TYPES]
    chosen = random.choices(FOOD_TYPES, weights=chances, k=1)[0]
    return chosen


def generate_food(snake, walls):
    """
    Generate food in a random safe position.
    Food cannot appear on:
    1. snake body
    2. wall cells
    """
    while True:
        position = (
            random.randint(1, GRID_WIDTH - 2),
            random.randint(1, GRID_HEIGHT - 2)
        )

        if position not in snake and position not in walls:
            food_type = choose_food_type()
            return {
                "pos": position,
                "type": food_type,
                "spawn_time": pygame.time.get_ticks()
            }


def show_game_over(score, level):
    """Display the game over screen."""
    screen.fill(BLACK)
    draw_text("GAME OVER", big_font, RED, WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 80)
    draw_text(f"Score: {score}", font, WHITE, WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 20)
    draw_text(f"Level: {level}", font, WHITE, WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 15)
    draw_text("Press R to restart or Q to quit", font, YELLOW, WINDOW_WIDTH // 2 - 170, WINDOW_HEIGHT // 2 + 60)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# -------------------- MAIN GAME FUNCTION --------------------
def game():
    # Snake initial position
    snake = [(5, 5), (4, 5), (3, 5)]

    # Initial direction: moving right
    direction = (1, 0)

    # Create border walls
    walls = create_walls()

    # Generate first food
    food = generate_food(snake, walls)

    # Game stats
    score = 0
    level = 1
    foods_eaten = 0

    # pending_growth is used when food should grow snake by more than 1 cell
    pending_growth = 0

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        current_speed = BASE_SPEED + (level - 1) * SPEED_INCREASE

        # -------------------- HANDLE FOOD TIMER --------------------
        # If food stayed too long, remove it and generate a new one
        food_lifetime = food["type"]["lifetime"]
        if current_time - food["spawn_time"] >= food_lifetime:
            food = generate_food(snake, walls)

        # -------------------- EVENTS --------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Prevent the snake from reversing into itself
                if event.key == pygame.K_UP and direction != (0, 1):
                    direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    direction = (1, 0)

        # -------------------- MOVE SNAKE --------------------
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Check if snake leaves the grid
        if (
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT
        ):
            running = False

        # Check collision with wall
        elif new_head in walls:
            running = False

        # Check collision with itself
        elif new_head in snake:
            running = False

        else:
            # Add new head
            snake.insert(0, new_head)

            # -------------------- CHECK IF FOOD IS EATEN --------------------
            if new_head == food["pos"]:
                foods_eaten += 1
                score += food["type"]["score"]

                # Snake already grows by 1 this move because we do not remove tail.
                # So we add only extra growth here.
                pending_growth += food["type"]["grow"] - 1

                # Increase level depending on score
                level = (score // SCORE_PER_LEVEL) + 1

                # Generate new food
                food = generate_food(snake, walls)

            else:
                # If snake still has extra growth stored, keep tail
                if pending_growth > 0:
                    pending_growth -= 1
                else:
                    # Normal movement: remove last segment
                    snake.pop()

        # -------------------- DRAW EVERYTHING --------------------
        screen.fill(BLACK)

        # Draw walls
        for wall in walls:
            draw_cell(wall, GRAY)

        # Draw snake
        draw_cell(snake[0], DARK_GREEN)  # head
        for segment in snake[1:]:
            draw_cell(segment, GREEN)

        # Draw food
        draw_cell(food["pos"], food["type"]["color"])

        # Calculate remaining food time
        time_left_ms = food["type"]["lifetime"] - (current_time - food["spawn_time"])
        if time_left_ms < 0:
            time_left_ms = 0
        time_left_sec = (time_left_ms + 999) // 1000  # round up to next second

        # Draw info text
        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"Level: {level}", font, WHITE, 10, 40)
        draw_text(f"Speed: {current_speed}", font, WHITE, 10, 70)
        draw_text(f"Food: {food['type']['name']}", font, WHITE, 10, 100)
        draw_text(f"Food Timer: {time_left_sec}s", font, WHITE, 10, 130)

        pygame.display.flip()
        clock.tick(current_speed)

    show_game_over(score, level)


# -------------------- START GAME --------------------
while True:
    game()