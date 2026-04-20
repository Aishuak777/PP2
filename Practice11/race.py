import pygame
import random
import sys

# Initialize pygame
pygame.init()

# -----------------------------
# Game settings
# -----------------------------
WIDTH = 400
HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
YELLOW = (255, 215, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GREEN = (34, 177, 76)
ROAD_LINE_COLOR = (240, 240, 240)
GRASS = (30, 120, 30)

# Road settings
ROAD_LEFT = 80
ROAD_RIGHT = WIDTH - 80
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANES = 3
LANE_WIDTH = ROAD_WIDTH // LANES

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont("Arial", 24)
font_big = pygame.font.SysFont("Arial", 42)

# -----------------------------
# Helper functions
# -----------------------------
def lane_center(lane_index):
    """Return x-coordinate of the center of a lane."""
    return ROAD_LEFT + lane_index * LANE_WIDTH + LANE_WIDTH // 2

def draw_text(surface, text, font, color, x, y):
    """Draw text on the screen."""
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

# -----------------------------
# Player class
# -----------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Create player's car as a simple rectangle surface
        self.image = pygame.Surface((40, 70), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        # Draw body of the car
        pygame.draw.rect(self.image, BLUE, (5, 10, 30, 50), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (10, 0, 20, 15), border_radius=5)

        # Wheels
        pygame.draw.rect(self.image, BLACK, (0, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (0, 45, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 45, 5, 12), border_radius=2)

        self.rect = self.image.get_rect()
        self.rect.centerx = lane_center(1)  # Start in middle lane
        self.rect.bottom = HEIGHT - 20
        self.speed = 6

    def update(self):
        keys = pygame.key.get_pressed()

        # Move left
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        # Move right
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Prevent player from leaving the road
        if self.rect.left < ROAD_LEFT + 5:
            self.rect.left = ROAD_LEFT + 5
        if self.rect.right > ROAD_RIGHT - 5:
            self.rect.right = ROAD_RIGHT - 5

# -----------------------------
# Enemy class
# -----------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Create enemy car surface
        self.image = pygame.Surface((40, 70), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        # Draw enemy car
        pygame.draw.rect(self.image, RED, (5, 10, 30, 50), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (10, 0, 20, 15), border_radius=5)

        # Wheels
        pygame.draw.rect(self.image, BLACK, (0, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (0, 45, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 45, 5, 12), border_radius=2)

        self.rect = self.image.get_rect()
        self.rect.centerx = lane_center(random.randint(0, 2))
        self.rect.y = -80
        self.speed = random.randint(5, 8)

    def update(self):
        # Move enemy downward
        self.rect.y += self.speed

        # Delete enemy when it leaves the screen
        if self.rect.top > HEIGHT:
            self.kill()

# -----------------------------
# Coin class
# -----------------------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Create coin surface
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        # Draw a yellow coin
        pygame.draw.circle(self.image, YELLOW, (11, 11), 10)
        pygame.draw.circle(self.image, BLACK, (11, 11), 10, 2)

        self.rect = self.image.get_rect()
        self.rect.centerx = lane_center(random.randint(0, 2))
        self.rect.y = -30
        self.speed = 5

    def update(self):
        # Move coin downward
        self.rect.y += self.speed

        # Delete coin when it leaves the screen
        if self.rect.top > HEIGHT:
            self.kill()

# -----------------------------
# Road line animation
# -----------------------------
line_y = 0
line_speed = 6

def draw_road():
    """Draw the road, grass, and moving lane lines."""
    global line_y

    # Grass
    screen.fill(GRASS)

    # Road
    pygame.draw.rect(screen, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

    # Road borders
    pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    # Lane divider lines
    for lane in range(1, LANES):
        x = ROAD_LEFT + lane * LANE_WIDTH
        for y in range(-40, HEIGHT, 60):
            pygame.draw.rect(screen, ROAD_LINE_COLOR, (x - 3, y + line_y, 6, 30))

    # Animate lane lines
    line_y += line_speed
    if line_y >= 60:
        line_y = 0

# -----------------------------
# Sprite groups
# -----------------------------
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# -----------------------------
# Timed events
# -----------------------------
ADD_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_ENEMY, 1200)

ADD_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(ADD_COIN, 1500)

# -----------------------------
# Score variables
# -----------------------------
score = 0
coin_count = 0
game_over = False

# -----------------------------
# Main game loop
# -----------------------------
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Spawn enemies regularly
        if event.type == ADD_ENEMY and not game_over:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Spawn coins regularly
        if event.type == ADD_COIN and not game_over:
            coin = Coin()
            all_sprites.add(coin)
            coins.add(coin)

        # Restart game after game over
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                # Reset everything
                all_sprites.empty()
                enemies.empty()
                coins.empty()

                player = Player()
                all_sprites.add(player)

                score = 0
                coin_count = 0
                game_over = False

    if not game_over:
        # Update all sprites
        all_sprites.update()

        # Increase score over time
        score += 1

        # Check collision with enemy cars
        if pygame.sprite.spritecollideany(player, enemies):
            game_over = True

        # Check collision with coins
        collected = pygame.sprite.spritecollide(player, coins, True)
        if collected:
            coin_count += len(collected)

    # Draw everything
    draw_road()
    all_sprites.draw(screen)

    # Show score in top left
    draw_text(screen, f"Score: {score}", font_small, WHITE, 10, 10)

    # Show collected coins in top right
    coin_text = font_small.render(f"Coins: {coin_count}", True, YELLOW)
    coin_rect = coin_text.get_rect(topright=(WIDTH - 10, 10))
    screen.blit(coin_text, coin_rect)

    # Game over screen
    if game_over:
        game_over_text = font_big.render("GAME OVER", True, WHITE)
        restart_text = font_small.render("Press R to Restart", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()