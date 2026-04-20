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
GRAY = (80, 80, 80)
YELLOW = (255, 255, 0)

# Level settings
FOODS_PER_LEVEL = 4       # after every 4 foods -> next level
BASE_SPEED = 8            # speed at level 1
SPEED_INCREASE = 2        # speed increase each level

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)


# -------------------- FUNCTIONS --------------------
def draw_text(text, font, color, x, y):
    """Draw text on the screen."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def create_walls():
    """
    Create border walls around the playing field.
    Food must not spawn on these cells.
    """
    walls = []

    # Top and bottom borders
    for x in range(GRID_WIDTH):
        walls.append((x, 0))
        walls.append((x, GRID_HEIGHT - 1))

    # Left and right borders
    for y in range(GRID_HEIGHT):
        walls.append((0, y))
        walls.append((GRID_WIDTH - 1, y))

    return walls


def generate_food(snake, walls):
    """
    Generate food in a random position.
    Food must not appear on:
    1. walls
    2. snake body
    """
    while True:
        food = (
            random.randint(1, GRID_WIDTH - 2),
            random.randint(1, GRID_HEIGHT - 2)
        )

        if food not in snake and food not in walls:
            return food


def draw_cell(position, color):
    """Draw one square cell."""
    x, y = position
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 1)  # black border for better look


def show_game_over(score, level):
    """Display game over screen."""
    screen.fill(BLACK)
    draw_text("GAME OVER", big_font, RED, WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 80)
    draw_text(f"Score: {score}", font, WHITE, WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 20)
    draw_text(f"Level: {level}", font, WHITE, WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 20)
    draw_text("Press R to restart or Q to quit", font, YELLOW, WINDOW_WIDTH // 2 - 170, WINDOW_HEIGHT // 2 + 70)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# -------------------- MAIN GAME LOOP --------------------
def game():
    # Snake starts with length 3
    snake = [(5, 5), (4, 5), (3, 5)]

    # Initial movement direction
    direction = (1, 0)  # moving right

    # Create border walls
    walls = create_walls()

    # Generate first food
    food = generate_food(snake, walls)

    # Score and level
    score = 0
    level = 1

    running = True
    while running:
        # Current speed depends on level
        current_speed = BASE_SPEED + (level - 1) * SPEED_INCREASE

        # -------------------- EVENTS --------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Prevent snake from moving directly backwards
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

        # 1. Check if snake leaves the playing area
        if (
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT
        ):
            running = False

        # 2. Check collision with wall border
        elif new_head in walls:
            running = False

        # 3. Check collision with itself
        elif new_head in snake:
            running = False

        else:
            # Add new head
            snake.insert(0, new_head)

            # -------------------- FOOD CHECK --------------------
            if new_head == food:
                score += 1

                # 4. Level up after every FOODS_PER_LEVEL foods
                level = (score // FOODS_PER_LEVEL) + 1

                # 5. Generate new food in safe position
                food = generate_food(snake, walls)
            else:
                # Remove last segment if food not eaten
                snake.pop()

        # -------------------- DRAW --------------------
        screen.fill(BLACK)

        # Draw walls
        for wall in walls:
            draw_cell(wall, GRAY)

        # Draw snake head
        draw_cell(snake[0], DARK_GREEN)

        # Draw snake body
        for segment in snake[1:]:
            draw_cell(segment, GREEN)

        # Draw food
        draw_cell(food, RED)

        # Draw score and level
        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"Level: {level}", font, WHITE, 10, 40)
        draw_text(f"Speed: {current_speed}", font, WHITE, 10, 70)

        pygame.display.flip()
        clock.tick(current_speed)

    show_game_over(score, level)


# -------------------- START GAME --------------------
while True:
    game()