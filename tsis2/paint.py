import os
import math
from datetime import datetime
from collections import deque

import pygame


# =========================================================
# INITIAL SETUP
# =========================================================
pygame.init()

WIDTH, HEIGHT = 1300, 850
TOOLBAR_HEIGHT = 190
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 - Paint Application")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 16)
text_font = pygame.font.SysFont("arial", 32)

# Separate drawing surface for the canvas area only
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill((255, 255, 255))


# =========================================================
# COLORS
# =========================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (225, 225, 225)
DARK_GRAY = (80, 80, 80)
LIGHT_BLUE = (180, 220, 255)
LIGHT_GREEN = (200, 245, 200)
RED = (220, 50, 50)

PALETTE = [
    (0, 0, 0),         # black
    (255, 0, 0),       # red
    (0, 180, 0),       # green
    (0, 0, 255),       # blue
    (255, 255, 0),     # yellow
    (255, 165, 0),     # orange
    (128, 0, 128),     # purple
    (255, 105, 180),   # pink
    (0, 255, 255),     # cyan
    (139, 69, 19),     # brown
]

current_color = BLACK


# =========================================================
# TOOLS AND SIZES
# =========================================================
TOOLS = [
    ("Pencil", "pencil"),
    ("Line", "line"),
    ("Rectangle", "rectangle"),
    ("Circle", "circle"),
    ("Square", "square"),
    ("Right Tri", "right_triangle"),
    ("Equi Tri", "equilateral_triangle"),
    ("Rhombus", "rhombus"),
    ("Eraser", "eraser"),
    ("Fill", "fill"),
    ("Text", "text"),
    ("Picker", "picker"),
]

SIZE_OPTIONS = [
    ("Small", 2),
    ("Medium", 5),
    ("Large", 10),
]

current_tool = "pencil"
brush_size = 5


# =========================================================
# UI ELEMENTS
# =========================================================
palette_rects = []
tool_rects = {}
size_rects = {}

# Color palette buttons
px = 20
for color in PALETTE:
    rect = pygame.Rect(px, 20, 36, 36)
    palette_rects.append((color, rect))
    px += 44

# Tool buttons (2 rows)
tool_start_x = 20
tool_start_y = 70
tool_w = 120
tool_h = 34
tool_gap_x = 10
tool_gap_y = 10

for i, (label, tool_name) in enumerate(TOOLS):
    row = i // 6
    col = i % 6
    rect = pygame.Rect(
        tool_start_x + col * (tool_w + tool_gap_x),
        tool_start_y + row * (tool_h + tool_gap_y),
        tool_w,
        tool_h
    )
    tool_rects[tool_name] = (label, rect)

# Size buttons
size_start_x = 820
size_y = 25
size_w = 100
size_h = 34
size_gap = 10

for i, (label, value) in enumerate(SIZE_OPTIONS):
    rect = pygame.Rect(size_start_x + i * (size_w + size_gap), size_y, size_w, size_h)
    size_rects[value] = (label, rect)

# Save and clear buttons
save_button = pygame.Rect(820, 80, 150, 38)
clear_button = pygame.Rect(990, 80, 150, 38)


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def inside_canvas(pos):
    """Check whether a screen position is inside the drawing canvas."""
    return pos[1] >= TOOLBAR_HEIGHT


def screen_to_canvas(pos):
    """Convert screen coordinates to canvas coordinates."""
    return pos[0], pos[1] - TOOLBAR_HEIGHT


def clamp_to_canvas(pos):
    """Keep mouse position inside the canvas boundaries."""
    x = max(0, min(WIDTH - 1, pos[0]))
    y = max(TOOLBAR_HEIGHT, min(HEIGHT - 1, pos[1]))
    return x, y


def normalize_rect(start, end):
    """Return a proper pygame.Rect regardless of drag direction."""
    x1, y1 = start
    x2, y2 = end
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return pygame.Rect(left, top, width, height)


def square_rect(start, end):
    """Create a square based on the drag direction."""
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))

    left = x1 if x2 >= x1 else x1 - side
    top = y1 if y2 >= y1 else y1 - side

    return pygame.Rect(left, top, side, side)


def right_triangle_points(start, end):
    """
    Right triangle aligned with horizontal and vertical edges.
    Points:
    - start point
    - point vertically under/above start
    - end point
    """
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]


def equilateral_triangle_points(start, end):
    """
    Build an equilateral triangle using the segment start->end as one side.
    The third point is found by rotating the segment by 60 degrees.
    """
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1

    cos60 = 0.5
    sin60 = math.sqrt(3) / 2

    x3 = x1 + dx * cos60 - dy * sin60
    y3 = y1 + dx * sin60 + dy * cos60

    return [(x1, y1), (x2, y2), (x3, y3)]


def rhombus_points(start, end):
    """Draw a rhombus inside the dragged rectangle."""
    rect = normalize_rect(start, end)
    left = rect.left
    right = rect.right
    top = rect.top
    bottom = rect.bottom
    cx = rect.centerx
    cy = rect.centery

    return [(cx, top), (right, cy), (cx, bottom), (left, cy)]


def flood_fill(surface, start_pos, fill_color):
    """
    Flood fill using exact color match.
    It fills all neighboring pixels that have the same color as the clicked pixel.
    """
    w, h = surface.get_size()
    x0, y0 = start_pos

    if not (0 <= x0 < w and 0 <= y0 < h):
        return

    target_color = surface.get_at((x0, y0))
    replacement = pygame.Color(fill_color[0], fill_color[1], fill_color[2], 255)

    if target_color == replacement:
        return

    q = deque()
    q.append((x0, y0))

    while q:
        x, y = q.popleft()

        if x < 0 or x >= w or y < 0 or y >= h:
            continue

        if surface.get_at((x, y)) != target_color:
            continue

        surface.set_at((x, y), replacement)

        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))


def save_canvas(surface):
    """Save the canvas in the same folder where paint.py is located."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{timestamp}.png"

    folder = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(folder, filename)

    pygame.image.save(surface, full_path)
    return filename


def draw_toolbar(status_text):
    """Draw the entire toolbar area."""
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    # Title
    title = font.render("TSIS 2 - Paint Application", True, BLACK)
    screen.blit(title, (20, 150))

    # Color palette
    palette_title = small_font.render("Colors", True, BLACK)
    screen.blit(palette_title, (20, 2))

    for color, rect in palette_rects:
        pygame.draw.rect(screen, color, rect)
        border_width = 3 if color == current_color else 1
        pygame.draw.rect(screen, BLACK, rect, border_width)

    # Tool buttons
    tools_title = small_font.render("Tools", True, BLACK)
    screen.blit(tools_title, (20, 48))

    for tool_name, (label, rect) in tool_rects.items():
        fill = LIGHT_BLUE if current_tool == tool_name else WHITE
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        text = small_font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # Size buttons
    size_title = small_font.render("Brush Size (1/2/3)", True, BLACK)
    screen.blit(size_title, (820, 2))

    for value, (label, rect) in size_rects.items():
        fill = LIGHT_GREEN if brush_size == value else WHITE
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        text = small_font.render(f"{label} ({value})", True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # Save button
    pygame.draw.rect(screen, WHITE, save_button)
    pygame.draw.rect(screen, BLACK, save_button, 2)
    save_text = font.render("Save", True, BLACK)
    screen.blit(save_text, save_text.get_rect(center=save_button.center))

    # Clear button
    pygame.draw.rect(screen, WHITE, clear_button)
    pygame.draw.rect(screen, BLACK, clear_button, 2)
    clear_text = font.render("Clear", True, BLACK)
    screen.blit(clear_text, clear_text.get_rect(center=clear_button.center))

    # Information line
    info = font.render(
        f"Tool: {current_tool}   Color: {current_color}   Size: {brush_size}",
        True,
        BLACK
    )
    screen.blit(info, (820, 130))

    status_surface = small_font.render(
        status_text,
        True,
        RED if "saved" not in status_text.lower() else (0, 120, 0)
    )
    screen.blit(status_surface, (820, 158))


def draw_text_preview(text_buffer, text_pos):
    """Draw text preview while typing. It is not permanent until Enter is pressed."""
    if text_buffer and text_pos is not None:
        preview = text_font.render(text_buffer, True, current_color)
        screen.blit(preview, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))


def commit_text(surface, text_buffer, text_pos, color):
    """Permanently draw typed text onto the canvas."""
    if text_buffer and text_pos is not None:
        rendered = text_font.render(text_buffer, True, color)
        surface.blit(rendered, text_pos)


# =========================================================
# MAIN STATE VARIABLES
# =========================================================
running = True

drawing = False
start_pos = None
last_pos = None
canvas_copy = None

typing_active = False
text_buffer = ""
text_pos = None

status_text = "Ready"


# =========================================================
# MAIN LOOP
# =========================================================
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -------------------------------------------------
        # KEYBOARD INPUT
        # -------------------------------------------------
        elif event.type == pygame.KEYDOWN:
            # Brush size shortcuts
            if event.key == pygame.K_1:
                brush_size = 2
                status_text = "Brush size set to Small"
            elif event.key == pygame.K_2:
                brush_size = 5
                status_text = "Brush size set to Medium"
            elif event.key == pygame.K_3:
                brush_size = 10
                status_text = "Brush size set to Large"

            # Text tool typing
            if typing_active:
                if event.key == pygame.K_RETURN:
                    commit_text(canvas, text_buffer, text_pos, current_color)
                    typing_active = False
                    text_buffer = ""
                    text_pos = None
                    status_text = "Text placed on canvas"

                elif event.key == pygame.K_ESCAPE:
                    typing_active = False
                    text_buffer = ""
                    text_pos = None
                    status_text = "Text canceled"

                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]

                else:
                    if event.unicode and event.unicode.isprintable():
                        text_buffer += event.unicode

        # -------------------------------------------------
        # MOUSE BUTTON DOWN
        # -------------------------------------------------
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            clicked_ui = False

            # Color palette click
            for color, rect in palette_rects:
                if rect.collidepoint(mouse_pos):
                    current_color = color
                    clicked_ui = True
                    status_text = f"Color changed to {current_color}"
                    break

            # Tool button click
            if not clicked_ui:
                for tool_name, (label, rect) in tool_rects.items():
                    if rect.collidepoint(mouse_pos):
                        current_tool = tool_name
                        clicked_ui = True
                        status_text = f"Tool changed to {label}"

                        if typing_active:
                            typing_active = False
                            text_buffer = ""
                            text_pos = None
                        break

            # Size button click
            if not clicked_ui:
                for value, (label, rect) in size_rects.items():
                    if rect.collidepoint(mouse_pos):
                        brush_size = value
                        clicked_ui = True
                        status_text = f"Brush size set to {label}"
                        break

            # Save button click
            if not clicked_ui and save_button.collidepoint(mouse_pos):
                if typing_active and text_buffer:
                    commit_text(canvas, text_buffer, text_pos, current_color)
                    typing_active = False
                    text_buffer = ""
                    text_pos = None

                filename = save_canvas(canvas)
                status_text = f"Canvas saved as {filename}"
                clicked_ui = True

            # Clear button click
            if not clicked_ui and clear_button.collidepoint(mouse_pos):
                canvas.fill(WHITE)
                typing_active = False
                text_buffer = ""
                text_pos = None
                status_text = "Canvas cleared"
                clicked_ui = True

            # Canvas click
            if not clicked_ui and inside_canvas(mouse_pos):
                canvas_pos = screen_to_canvas(clamp_to_canvas(mouse_pos))

                if current_tool == "picker":
                    sampled = canvas.get_at(canvas_pos)
                    current_color = (sampled.r, sampled.g, sampled.b)
                    status_text = f"Picked color {current_color}"

                elif current_tool == "fill":
                    flood_fill(canvas, canvas_pos, current_color)
                    status_text = "Area filled"

                elif current_tool == "text":
                    typing_active = True
                    text_buffer = ""
                    text_pos = canvas_pos
                    status_text = "Typing mode: Enter = place, Esc = cancel"

                else:
                    drawing = True
                    start_pos = canvas_pos
                    last_pos = canvas_pos

                    if current_tool in [
                        "line",
                        "rectangle",
                        "circle",
                        "square",
                        "right_triangle",
                        "equilateral_triangle",
                        "rhombus",
                    ]:
                        canvas_copy = canvas.copy()

                    if current_tool == "pencil":
                        pygame.draw.circle(canvas, current_color, start_pos, max(1, brush_size // 2))

                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, start_pos, max(4, brush_size))

        # -------------------------------------------------
        # MOUSE MOTION
        # -------------------------------------------------
        elif event.type == pygame.MOUSEMOTION and drawing:
            mouse_pos = clamp_to_canvas(event.pos)
            current_pos = screen_to_canvas(mouse_pos)

            if current_tool == "pencil":
                pygame.draw.line(canvas, current_color, last_pos, current_pos, brush_size)
                last_pos = current_pos

            elif current_tool == "eraser":
                pygame.draw.line(canvas, WHITE, last_pos, current_pos, brush_size * 2)
                last_pos = current_pos

            elif current_tool == "line":
                canvas.blit(canvas_copy, (0, 0))
                pygame.draw.line(canvas, current_color, start_pos, current_pos, brush_size)

            elif current_tool == "rectangle":
                canvas.blit(canvas_copy, (0, 0))
                rect = normalize_rect(start_pos, current_pos)
                pygame.draw.rect(canvas, current_color, rect, brush_size)

            elif current_tool == "circle":
                canvas.blit(canvas_copy, (0, 0))
                radius = int(math.hypot(current_pos[0] - start_pos[0], current_pos[1] - start_pos[1]))
                if radius > 0:
                    pygame.draw.circle(canvas, current_color, start_pos, radius, brush_size)

            elif current_tool == "square":
                canvas.blit(canvas_copy, (0, 0))
                rect = square_rect(start_pos, current_pos)
                pygame.draw.rect(canvas, current_color, rect, brush_size)

            elif current_tool == "right_triangle":
                canvas.blit(canvas_copy, (0, 0))
                points = right_triangle_points(start_pos, current_pos)
                pygame.draw.polygon(canvas, current_color, points, brush_size)

            elif current_tool == "equilateral_triangle":
                canvas.blit(canvas_copy, (0, 0))
                points = equilateral_triangle_points(start_pos, current_pos)
                pygame.draw.polygon(canvas, current_color, points, brush_size)

            elif current_tool == "rhombus":
                canvas.blit(canvas_copy, (0, 0))
                points = rhombus_points(start_pos, current_pos)
                pygame.draw.polygon(canvas, current_color, points, brush_size)

        # -------------------------------------------------
        # MOUSE BUTTON UP
        # -------------------------------------------------
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing:
                drawing = False
                start_pos = None
                last_pos = None
                canvas_copy = None

    # -----------------------------------------------------
    # DRAW EVERYTHING TO THE SCREEN
    # -----------------------------------------------------
    draw_toolbar(status_text)
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    draw_text_preview(text_buffer, text_pos)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()