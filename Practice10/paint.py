import math
import pygame

# -------------------- SETTINGS --------------------
WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 90
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
DARK_GRAY = (90, 90, 90)
LIGHT_BLUE = (173, 216, 230)

PALETTE = [
    (0, 0, 0),        # black
    (255, 0, 0),      # red
    (0, 170, 0),      # green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (255, 165, 0),    # orange
    (128, 0, 128),    # purple
    (255, 105, 180),  # pink
]

BRUSH_SIZE = 6
SHAPE_WIDTH = 3

TOOLS = ["brush", "rectangle", "circle", "eraser"]

# -------------------- HELPERS --------------------
def inside_canvas(pos):
    return pos[1] >= TOOLBAR_HEIGHT

def to_canvas_pos(pos):
    return (pos[0], pos[1] - TOOLBAR_HEIGHT)

def clamp_to_canvas_screen(pos):
    x = max(0, min(WIDTH - 1, pos[0]))
    y = max(TOOLBAR_HEIGHT, min(HEIGHT - 1, pos[1]))
    return (x, y)

def make_ui():
    palette_rects = []
    x = 20
    y = 20
    size = 35
    gap = 10

    for color in PALETTE:
        palette_rects.append((color, pygame.Rect(x, y, size, size)))
        x += size + gap

    tool_rects = {}
    x = 420
    w = 120
    h = 40
    gap = 12

    for tool in TOOLS:
        tool_rects[tool] = pygame.Rect(x, 25, w, h)
        x += w + gap

    clear_rect = pygame.Rect(840, 25, 120, 40)

    return palette_rects, tool_rects, clear_rect

def draw_toolbar(screen, font, current_color, current_tool, palette_rects, tool_rects, clear_rect):
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    # Title
    title = font.render("PAINT", True, BLACK)
    screen.blit(title, (20, 60))

    # Colors
    for color, rect in palette_rects:
        pygame.draw.rect(screen, color, rect)
        border_color = BLACK if color == current_color else DARK_GRAY
        border_width = 3 if color == current_color else 1
        pygame.draw.rect(screen, border_color, rect, border_width)

    # Tools
    for tool, rect in tool_rects.items():
        fill = LIGHT_BLUE if tool == current_tool else WHITE
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        label = font.render(tool.capitalize(), True, BLACK)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    # Clear button
    pygame.draw.rect(screen, WHITE, clear_rect)
    pygame.draw.rect(screen, BLACK, clear_rect, 2)
    clear_label = font.render("Clear", True, BLACK)
    clear_label_rect = clear_label.get_rect(center=clear_rect.center)
    screen.blit(clear_label, clear_label_rect)

    # Current info
    info = font.render(f"Color: {current_color}   Tool: {current_tool}", True, BLACK)
    screen.blit(info, (20, 10))

def normalize_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return pygame.Rect(left, top, width, height)

# -------------------- MAIN --------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Paint")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    palette_rects, tool_rects, clear_rect = make_ui()

    # Separate canvas surface
    canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
    canvas.fill(WHITE)

    current_color = BLACK
    current_tool = "brush"

    drawing = False
    start_pos = None
    last_pos = None
    canvas_backup = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # Toolbar clicks
                clicked_ui = False

                for color, rect in palette_rects:
                    if rect.collidepoint(mouse_pos):
                        current_color = color
                        clicked_ui = True
                        break

                if not clicked_ui:
                    for tool, rect in tool_rects.items():
                        if rect.collidepoint(mouse_pos):
                            current_tool = tool
                            clicked_ui = True
                            break

                if not clicked_ui and clear_rect.collidepoint(mouse_pos):
                    canvas.fill(WHITE)
                    clicked_ui = True

                # Canvas clicks
                if not clicked_ui and inside_canvas(mouse_pos):
                    drawing = True
                    start_pos = to_canvas_pos(clamp_to_canvas_screen(mouse_pos))
                    last_pos = start_pos

                    if current_tool in ("rectangle", "circle"):
                        canvas_backup = canvas.copy()

                    elif current_tool == "brush":
                        pygame.draw.circle(canvas, current_color, start_pos, BRUSH_SIZE // 2)

                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, start_pos, 12)

            elif event.type == pygame.MOUSEMOTION and drawing:
                mouse_pos = clamp_to_canvas_screen(event.pos)
                if not inside_canvas(mouse_pos):
                    continue

                current_pos = to_canvas_pos(mouse_pos)

                if current_tool == "brush":
                    pygame.draw.line(canvas, current_color, last_pos, current_pos, BRUSH_SIZE)
                    last_pos = current_pos

                elif current_tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, current_pos, 24)
                    last_pos = current_pos

                elif current_tool == "rectangle":
                    canvas.blit(canvas_backup, (0, 0))
                    rect = normalize_rect(start_pos, current_pos)
                    pygame.draw.rect(canvas, current_color, rect, SHAPE_WIDTH)

                elif current_tool == "circle":
                    canvas.blit(canvas_backup, (0, 0))
                    radius = int(math.hypot(current_pos[0] - start_pos[0], current_pos[1] - start_pos[1]))
                    if radius > 0:
                        pygame.draw.circle(canvas, current_color, start_pos, radius, SHAPE_WIDTH)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drawing = False
                start_pos = None
                last_pos = None
                canvas_backup = None

        # Draw everything
        screen.fill(WHITE)
        draw_toolbar(screen, font, current_color, current_tool, palette_rects, tool_rects, clear_rect)
        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()