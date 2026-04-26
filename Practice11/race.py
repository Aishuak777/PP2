import pygame
import random
import sys

# ---------------------------------
# Initialize pygame
# ---------------------------------
pygame.init()

# ---------------------------------
# Game window settings
# ---------------------------------
WIDTH = 400
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer with Coins")
clock = pygame.time.Clock()

# ---------------------------------
# Colors
# ---------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (70, 70, 70)
GREEN = (20, 120, 20)
BLUE = (50, 120, 255)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (170, 80, 255)
LIGHT_GRAY = (220, 220, 220)

# ---------------------------------
# Road settings
# ---------------------------------
ROAD_LEFT = 80
ROAD_RIGHT = WIDTH - 80
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANES = 3
LANE_WIDTH = ROAD_WIDTH // LANES

# ---------------------------------
# Fonts
# ---------------------------------
font_small = pygame.font.SysFont("Arial", 24)
font_big = pygame.font.SysFont("Arial", 42)

# ---------------------------------
# Game tuning
# ---------------------------------
# Speed level increases every 2 collected coins
COINS_NEEDED_FOR_SPEED_UP = 2

# Initial enemy speed
enemy_base_speed = 5

# Road animation
road_line_speed = 6
road_line_offset = 0

# ---------------------------------
# Helper functions
# ---------------------------------
def lane_center(lane_index):
    """Return x-coordinate of the center of the selected lane."""
    return ROAD_LEFT + lane_index * LANE_WIDTH + LANE_WIDTH // 2


def draw_text(surface, text, font, color, x, y):
    """Draw text on the screen."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


def draw_road():
    """Draw grass, road, borders, and moving dashed lane lines."""
    global road_line_offset

    # Grass background
    screen.fill(GREEN)

    # Road
    pygame.draw.rect(screen, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

    # Road borders
    pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    # Dashed lane lines
    for lane in range(1, LANES):
        x = ROAD_LEFT + lane * LANE_WIDTH
        for y in range(-40, HEIGHT, 60):
            pygame.draw.rect(screen, LIGHT_GRAY, (x - 3, y + road_line_offset, 6, 30))

    # Move dashed lines down
    road_line_offset += road_line_speed
    if road_line_offset >= 60:
        road_line_offset = 0


# ---------------------------------
# Player class
# ---------------------------------
class Player(pygame.sprite.Sprite):
    """Player car controlled by arrow keys."""

    def __init__(self):
        super().__init__()

        # Transparent surface for the player's car
        self.image = pygame.Surface((40, 70), pygame.SRCALPHA)

        # Car body
        pygame.draw.rect(self.image, BLUE, (5, 10, 30, 50), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (10, 0, 20, 15), border_radius=4)

        # Wheels
        pygame.draw.rect(self.image, BLACK, (0, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (0, 45, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 45, 5, 12), border_radius=2)

        # Starting position
        self.rect = self.image.get_rect()
        self.rect.centerx = lane_center(1)
        self.rect.bottom = HEIGHT - 20

        self.speed = 6

    def update(self):
        """Move player left or right and keep it inside the road."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Prevent leaving the road
        if self.rect.left < ROAD_LEFT + 5:
            self.rect.left = ROAD_LEFT + 5
        if self.rect.right > ROAD_RIGHT - 5:
            self.rect.right = ROAD_RIGHT - 5


# ---------------------------------
# Enemy class
# ---------------------------------
class Enemy(pygame.sprite.Sprite):
    """Enemy cars moving down the road."""

    def __init__(self, speed):
        super().__init__()

        # Transparent surface for enemy car
        self.image = pygame.Surface((40, 70), pygame.SRCALPHA)

        # Car body
        pygame.draw.rect(self.image, RED, (5, 10, 30, 50), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (10, 0, 20, 15), border_radius=4)

        # Wheels
        pygame.draw.rect(self.image, BLACK, (0, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 15, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (0, 45, 5, 12), border_radius=2)
        pygame.draw.rect(self.image, BLACK, (35, 45, 5, 12), border_radius=2)

        # Random lane position
        self.rect = self.image.get_rect()
        self.rect.centerx = lane_center(random.randint(0, 2))
        self.rect.y = -80

        # Enemy speed depends on current difficulty
        self.speed = speed + random.randint(0, 2)

    def update(self):
        """Move enemy downward and delete after leaving screen."""
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.kill()


# ---------------------------------
# Coin class
# ---------------------------------
class Coin(pygame.sprite.Sprite):
    """Coin with different value/weight."""

    def __init__(self):
        super().__init__()

        # Different coin types
        coin_types = [
            {"value": 1, "color": YELLOW, "radius": 10},
            {"value": 2, "color": ORANGE, "radius": 11},
            {"value": 5, "color": PURPLE, "radius": 12},
        ]

        # Spawn probabilities
        probabilities = [0.6, 0.3, 0.1]

        chosen = random.choices(coin_types, weights=probabilities, k=1)[0]

        self.value = chosen["value"]
        self.color = chosen["color"]
        self.radius = chosen["radius"]

        # Transparent surface for coin
        size = self.radius * 2 + 6
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Draw coin
        pygame.draw.circle(self.image, self.color, (size // 2, size // 2), self.radius)
        pygame.draw.circle(self.image, BLACK, (size // 2, size // 2), self.radius, 2)

        # Coin value text
        value_text = font_small.render(str(self.value), True, BLACK)
        value_rect = value_text.get_rect(center=(size // 2, size // 2))
        self.image.blit(value_text, value_rect)

        # Random lane position
        self.rect = self.image.get_rect()
        self.rect.centerx = lane_center(random.randint(0, 2))
        self.rect.y = -40

        self.speed = 5

    def update(self):
        """Move coin downward and delete after leaving screen."""
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.kill()


# ---------------------------------
# Create sprite groups
# ---------------------------------
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# ---------------------------------
# Timed events
# ---------------------------------
ADD_ENEMY = pygame.USEREVENT + 1
ADD_COIN = pygame.USEREVENT + 2

pygame.time.set_timer(ADD_ENEMY, 1200)
pygame.time.set_timer(ADD_COIN, 1500)

# ---------------------------------
# Game variables
# ---------------------------------
score = 0
coin_count = 0
coin_weight_sum = 0
game_over = False
speed_level = 0

# ---------------------------------
# Main loop
# ---------------------------------
while True:
    clock.tick(FPS)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Add enemy
        if event.type == ADD_ENEMY and not game_over:
            enemy = Enemy(enemy_base_speed)
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Add coin
        if event.type == ADD_COIN and not game_over:
            coin = Coin()
            all_sprites.add(coin)
            coins.add(coin)

        # Restart after game over
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                all_sprites.empty()
                enemies.empty()
                coins.empty()

                player = Player()
                all_sprites.add(player)

                score = 0
                coin_count = 0
                coin_weight_sum = 0
                game_over = False
                speed_level = 0
                enemy_base_speed = 5

    # Update game objects
    if not game_over:
        all_sprites.update()

        # Increase survival score
        score += 1

        # Collision with enemy = game over
        if pygame.sprite.spritecollideany(player, enemies):
            game_over = True

        # Collision with coins
        collected_coins = pygame.sprite.spritecollide(player, coins, True)

        if collected_coins:
            # Increase number of collected coins
            coin_count += len(collected_coins)

            # Add total value of collected coins
            for coin in collected_coins:
                coin_weight_sum += coin.value

            # Increase speed level every N coins
            new_speed_level = coin_count // COINS_NEEDED_FOR_SPEED_UP

            # Make speed level grow faster
            if new_speed_level > speed_level:
                speed_level = new_speed_level
                enemy_base_speed += 2

                # Increase speed of enemies already on screen too
                for enemy in enemies:
                    enemy.speed += 2

    # Draw scene
    draw_road()
    all_sprites.draw(screen)

    # Top left: score
    draw_text(screen, f"Score: {score}", font_small, WHITE, 10, 10)

    # Top left below score: speed level
    draw_text(screen, f"Speed Lv: {speed_level}", font_small, WHITE, 10, 40)

    # Top right: collected coins
    coin_count_surface = font_small.render(f"Coins: {coin_count}", True, YELLOW)
    coin_count_rect = coin_count_surface.get_rect(topright=(WIDTH - 10, 10))
    screen.blit(coin_count_surface, coin_count_rect)

    # Top right below: total value/weight
    value_surface = font_small.render(f"Value: {coin_weight_sum}", True, WHITE)
    value_rect = value_surface.get_rect(topright=(WIDTH - 10, 40))
    screen.blit(value_surface, value_rect)

    # Game over text
    if game_over:
        game_over_text = font_big.render("GAME OVER", True, WHITE)
        restart_text = font_small.render("Press R to Restart", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()