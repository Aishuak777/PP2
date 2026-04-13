from __future__ import annotations

from datetime import datetime
from pathlib import Path
import math
import pygame


class MickeyClock:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.width, self.height = self.screen.get_size()

        self.bg_color = (230, 230, 230)
        self.black = (20, 20, 20)
        self.white = (255, 255, 255)
        self.red = (210, 40, 40)
        self.yellow = (245, 220, 90)
        self.gray = (140, 140, 140)

        self.title_font = pygame.font.SysFont("arial", 30, bold=True)
        self.time_font = pygame.font.SysFont("consolas", 42, bold=True)
        self.number_font = pygame.font.SysFont("arial", 34, bold=True)

        self.center = (self.width // 2, self.height // 2 + 30)
        self.clock_radius = 250

        self.face_image = self._load_optional_image("clock_face.png", (560, 560))
        base_hand = self._load_optional_image("mickey_hand.png")

        self.hour_hand = None
        self.minute_hand = None
        self.second_hand = None

        if base_hand is not None:
            self.hour_hand = pygame.transform.smoothscale(base_hand, (80, 140))
            self.minute_hand = pygame.transform.smoothscale(base_hand, (70, 210))
            self.second_hand = pygame.transform.smoothscale(base_hand, (55, 240))

        self.current_hour = 0
        self.current_hour_12 = 0
        self.current_minute = 0
        self.current_second = 0

        self.hour_angle = 0.0
        self.minute_angle = 0.0
        self.second_angle = 0.0

    def _load_optional_image(
        self,
        filename: str,
        size: tuple[int, int] | None = None,
    ) -> pygame.Surface | None:
        path = Path(__file__).parent / "images" / filename
        if not path.exists():
            return None

        image = pygame.image.load(str(path)).convert_alpha()
        if size is not None:
            image = pygame.transform.smoothscale(image, size)
        return image

    def update(self) -> None:
        now = datetime.now()

        self.current_hour = now.hour
        self.current_hour_12 = now.hour % 12
        self.current_minute = now.minute
        self.current_second = now.second

        self.second_angle = self.current_second * 6
        self.minute_angle = self.current_minute * 6 + self.current_second * 0.1
        self.hour_angle = (
            self.current_hour_12 * 30
            + self.current_minute * 0.5
            + self.current_second * (0.5 / 60)
        )

    def draw(self) -> None:
        self.screen.fill(self.bg_color)

        self._draw_title()
        self._draw_digital_time()

        if self.face_image is not None:
            self._draw_background_face()
        else:
            self._draw_generated_face()

        self._draw_hands()
        self._draw_center_cap()

    def _draw_title(self) -> None:
        title = self.title_font.render("Mickey Mouse Clock", True, self.black)
        rect = title.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title, rect)

    def _draw_digital_time(self) -> None:
        text = f"{self.current_hour:02d}:{self.current_minute:02d}:{self.current_second:02d}"
        surface = self.time_font.render(text, True, self.black)
        rect = surface.get_rect(center=(self.width // 2, 80))
        self.screen.blit(surface, rect)

    def _draw_background_face(self) -> None:
        rect = self.face_image.get_rect(center=self.center)
        self.screen.blit(self.face_image, rect)

    def _draw_generated_face(self) -> None:
        cx, cy = self.center

        pygame.draw.circle(self.screen, self.red, self.center, self.clock_radius + 28)
        pygame.draw.circle(self.screen, self.black, self.center, self.clock_radius + 10)
        pygame.draw.circle(self.screen, self.white, self.center, self.clock_radius - 8)

        for hour in range(1, 13):
            angle_deg = hour * 30
            angle_rad = math.radians(angle_deg - 90)

            num_radius = self.clock_radius - 42
            x = cx + num_radius * math.cos(angle_rad)
            y = cy + num_radius * math.sin(angle_rad)

            text = self.number_font.render(str(hour), True, self.gray)
            rect = text.get_rect(center=(int(x), int(y)))
            self.screen.blit(text, rect)

        for i in range(60):
            angle_deg = i * 6
            angle_rad = math.radians(angle_deg - 90)

            outer_r = self.clock_radius - 10
            inner_r = self.clock_radius - 28 if i % 5 == 0 else self.clock_radius - 20

            x1 = cx + outer_r * math.cos(angle_rad)
            y1 = cy + outer_r * math.sin(angle_rad)
            x2 = cx + inner_r * math.cos(angle_rad)
            y2 = cy + inner_r * math.sin(angle_rad)

            width = 3 if i % 5 == 0 else 1
            pygame.draw.line(
                self.screen,
                self.black,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                width,
            )

        self._draw_small_mickey()

    def _draw_small_mickey(self) -> None:
        cx, cy = self.center

        pygame.draw.circle(self.screen, self.black, (cx - 55, cy - 85), 32)
        pygame.draw.circle(self.screen, self.black, (cx + 55, cy - 85), 32)

        pygame.draw.circle(self.screen, self.black, (cx, cy - 40), 50)

        pygame.draw.ellipse(self.screen, self.white, (cx - 32, cy - 48, 64, 42))
        pygame.draw.circle(self.screen, self.black, (cx - 12, cy - 58), 4)
        pygame.draw.circle(self.screen, self.black, (cx + 12, cy - 58), 4)
        pygame.draw.ellipse(self.screen, self.black, (cx - 10, cy - 42, 20, 12))

        pygame.draw.ellipse(self.screen, self.black, (cx - 38, cy + 5, 76, 95))
        pygame.draw.ellipse(self.screen, self.red, (cx - 34, cy + 35, 68, 46))

        pygame.draw.circle(self.screen, self.white, (cx - 12, cy + 58), 5)
        pygame.draw.circle(self.screen, self.white, (cx + 12, cy + 58), 5)

        pygame.draw.line(self.screen, self.black, (cx - 10, cy + 98), (cx - 25, cy + 135), 5)
        pygame.draw.line(self.screen, self.black, (cx + 10, cy + 98), (cx + 28, cy + 135), 5)

        pygame.draw.ellipse(self.screen, self.yellow, (cx - 52, cy + 128, 38, 20))
        pygame.draw.ellipse(self.screen, self.yellow, (cx + 12, cy + 128, 38, 20))

    def _draw_hands(self) -> None:
        pivot = self.center

        if self.hour_hand is not None:
            self._blit_rotated_from_bottom_center(self.hour_hand, pivot, self.hour_angle)
        else:
            self._draw_line_hand(pivot, self.hour_angle, 120, 10, self.black)

        if self.minute_hand is not None:
            self._blit_rotated_from_bottom_center(self.minute_hand, pivot, self.minute_angle)
        else:
            self._draw_line_hand(pivot, self.minute_angle, 165, 8, self.black)

        if self.second_hand is not None:
            self._blit_rotated_from_bottom_center(self.second_hand, pivot, self.second_angle)
        else:
            self._draw_line_hand(pivot, self.second_angle, 200, 4, self.red)

    def _blit_rotated_from_bottom_center(
        self,
        image: pygame.Surface,
        pivot: tuple[int, int],
        angle_clockwise: float,
    ) -> None:
        rotation = -angle_clockwise

        base_rect = image.get_rect(midbottom=pivot)
        offset = pygame.math.Vector2(pivot) - pygame.math.Vector2(base_rect.center)
        rotated_offset = offset.rotate(rotation)
        rotated_center = (pivot[0] - rotated_offset.x, pivot[1] - rotated_offset.y)

        rotated_image = pygame.transform.rotate(image, rotation)
        rotated_rect = rotated_image.get_rect(center=rotated_center)

        self.screen.blit(rotated_image, rotated_rect)

    def _draw_line_hand(
        self,
        pivot: tuple[int, int],
        angle_clockwise: float,
        length: int,
        width: int,
        color: tuple[int, int, int],
    ) -> None:
        rad = math.radians(angle_clockwise - 90)

        end_x = pivot[0] + length * math.cos(rad)
        end_y = pivot[1] + length * math.sin(rad)

        pygame.draw.line(
            self.screen,
            color,
            pivot,
            (int(end_x), int(end_y)),
            width,
        )

    def _draw_center_cap(self) -> None:
        pygame.draw.circle(self.screen, self.red, self.center, 12)
        pygame.draw.circle(self.screen, self.black, self.center, 12, 2)