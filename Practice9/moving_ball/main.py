import pygame
from ball import Ball

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball Game")
    clock = pygame.time.Clock()

    ball = Ball(
        x=WIDTH // 2,
        y=HEIGHT // 2,
        radius=25,
        color=RED,
        step=20,
        screen_width=WIDTH,
        screen_height=HEIGHT
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ball.move(0, -20)
                elif event.key == pygame.K_DOWN:
                    ball.move(0, 20)
                elif event.key == pygame.K_LEFT:
                    ball.move(-20, 0)
                elif event.key == pygame.K_RIGHT:
                    ball.move(20, 0)

        screen.fill(WHITE)
        ball.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()