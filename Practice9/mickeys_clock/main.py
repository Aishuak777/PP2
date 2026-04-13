import sys
import pygame

from clock import MickeyClock


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Mickey's Clock Application")

    app = MickeyClock(screen)
    fps_clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        app.update()
        app.draw()

        pygame.display.flip()
        fps_clock.tick(60)


if __name__ == "__main__":
    main()