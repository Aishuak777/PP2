import pygame
import math

# -----------------------------
# INITIAL SETTINGS
# -----------------------------
pygame.init()

WIDTH, HEIGHT = 1200, 800          # Window size
TOOLBAR_HEIGHT = 160               # Top area for colors and tools
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Program")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# -----------------------------
# COLORS
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
DARK_GRAY = (80, 80, 80)
LIGHT_BLUE = (173, 216, 230)

PALETTE = [
    (0, 0, 0),        # black
    (255, 0, 0),      # red
    (0, 180, 0),      # green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (255, 165, 0),    # orange
    (128, 0, 128),    # purple
    (255, 105, 180),  # pink
]

current_color = BLACK

# -----------------------------
# TOOLS
# -----------------------------
TOOLS = [
    ("Brush", "brush"),
    ("Rectangle", "rectangle"),
    ("Circle", "circle"),
    ("Square", "square"),
    ("Right Tri", "right_triangle"),
    ("Equi Tri", "equilateral_triangle"),
    ("Rhombus", "rhombus"),
    ("Eraser", "eraser"),
]

current_tool = "brush"

BRUSH_SIZE = 6
ERASER_SIZE = 20
SHAPE_WIDTH = 3

# -----------------------------
# DRAWING SURFACE
# Separate canvas so toolbar stays clean
# -----------------------------
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# -----------------------------
# UI ELEMENTS
# -----------------------------
palette_rects = []
tool_rects = {}

# Create color palette buttons
x = 20
for color in PALETTE:
    rect = pygame.Rect(x, 20, 40, 40)
    palette_rects.append((color, rect))
    x += 50

# Create tool buttons in 2 rows
start_x = 20
start_y = 70
button_w = 130
button_h = 35
gap = 10

for i, (label, tool_name) in enumerate(TOOLS):
    row = i // 4
    col = i % 4
    rect = pygame.Rect(
        start_x + col * (button_w + gap),
        start_y + row * (button_h + 10),
        button_w,
        button_h
    )
    tool_rects[tool_name] = (label, rect)

# Clear button
clear_button = pygame.Rect(980, 30, 150, 40)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def inside_canvas(pos):
    """Check if mouse is inside the drawing area."""
    return pos[1] >= TOOLBAR_HEIGHT

def to_canvas_pos(pos):
    """Convert screen coordinates to canvas coordinates."""
    return (pos[0], pos[1] - TOOLBAR_HEIGHT)

def clamp_mouse(pos):
    """Keep mouse position inside the drawing area."""
    x = max(0, min(WIDTH - 1, pos[0]))
    y = max(TOOLBAR_HEIGHT, min(HEIGHT - 1, pos[1]))
    return (x, y)

def normalize_rect(start, end):
    """Return a rectangle no matter which direction the user drags."""
    x1, y1 = start
    x2, y2 = end
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return pygame.Rect(left, top, width, height)

def square_rect(start, end):
    """
    Create a square using drag direction.
    Side is based on the smaller distance so it stays a square.
    """
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 >= x1:
        left = x1
    else:
        left = x1 - side

    if y2 >= y1:
        top = y1
    else:
        top = y1 - side

    return pygame.Rect(left, top, side, side)

def right_triangle_points(start, end):
    """
    Right triangle aligned to the axes.
    Vertices:
    - start point
    - point directly below/above start
    - current mouse point
    """
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]

def equilateral_triangle_points(start, end):
    """
    Build an equilateral triangle.
    We use start and end as one side,
    then rotate that side by 60 degrees to get the third point.
    """
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1

    # Rotate vector (dx, dy) by +60 degrees
    cos60 = 0.5
    sin60 = math.sqrt(3) / 2

    x3 = x1 + dx * cos60 - dy * sin60
    y3 = y1 + dx * sin60 + dy * cos60

    return [(x1, y1), (x2, y2), (x3, y3)]

def rhombus_points(start, end):
    """
    Draw a rhombus (diamond shape) inside the dragged rectangle.
    """
    rect = normalize_rect(start, end)
    left = rect.left
    right = rect.right
    top = rect.top
    bottom = rect.bottom
    cx = rect.centerx
    cy = rect.centery

    return [(cx, top), (right, cy), (cx, bottom), (left, cy)]

def draw_toolbar():
    """Draw the toolbar, color buttons, tool buttons, and labels."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    # Title
    title = font.render("Paint Program", True, BLACK)
    screen.blit(title, (20, 130))

    # Draw color buttons
    for color, rect in palette_rects:
        pygame.draw.rect(screen, color, rect)
        border = 3 if color == current_color else 1
        pygame.draw.rect(screen, BLACK, rect, border)

    # Draw tool buttons
    for tool_name, (label, rect) in tool_rects.items():
        fill_color = LIGHT_BLUE if tool_name == current_tool else WHITE
        pygame.draw.rect(screen, fill_color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        text = font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # Clear button
    pygame.draw.rect(screen, WHITE, clear_button)
    pygame.draw.rect(screen, BLACK, clear_button, 2)
    clear_text = font.render("Clear Canvas", True, BLACK)
    clear_text_rect = clear_text.get_rect(center=clear_button.center)
    screen.blit(clear_text, clear_text_rect)

    # Show current tool and color
    info = font.render(f"Current tool: {current_tool}   Current color: {current_color}", True, BLACK)
    screen.blit(info, (650, 90))

# -----------------------------
# MAIN LOOP VARIABLES
# -----------------------------
running = True
drawing = False
start_pos = None
last_pos = None
canvas_copy = None

# -----------------------------
# MAIN LOOP
# -----------------------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -----------------------------
        # MOUSE BUTTON DOWN
        # -----------------------------
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            clicked_ui = False

            # Check color selection
            for color, rect in palette_rects:
                if rect.collidepoint(mouse_pos):
                    current_color = color
                    clicked_ui = True
                    break

            # Check tool selection
            if not clicked_ui:
                for tool_name, (label, rect) in tool_rects.items():
                    if rect.collidepoint(mouse_pos):
                        current_tool = tool_name
                        clicked_ui = True
                        break

            # Check clear button
            if not clicked_ui and clear_button.collidepoint(mouse_pos):
                canvas.fill(WHITE)
                clicked_ui = True

            # Start drawing if mouse is on canvas
            if not clicked_ui and inside_canvas(mouse_pos):
                drawing = True
                start_pos = to_canvas_pos(clamp_mouse(mouse_pos))
                last_pos = start_pos

                # Save current canvas for preview shapes
                if current_tool in ["rectangle", "circle", "square", "right_triangle", "equilateral_triangle", "rhombus"]:
                    canvas_copy = canvas.copy()

                # Draw a dot immediately for brush/eraser
                if current_tool == "brush":
                    pygame.draw.circle(canvas, current_color, start_pos, BRUSH_SIZE // 2)
                elif current_tool == "eraser":
                    pygame.draw.circle(canvas, WHITE, start_pos, ERASER_SIZE // 2)

        # -----------------------------
        # MOUSE MOTION
        # -----------------------------
        elif event.type == pygame.MOUSEMOTION and drawing:
            mouse_pos = clamp_mouse(event.pos)
            current_pos = to_canvas_pos(mouse_pos)

            # Freehand brush
            if current_tool == "brush":
                pygame.draw.line(canvas, current_color, last_pos, current_pos, BRUSH_SIZE)
                last_pos = current_pos

            # Eraser
            elif current_tool == "eraser":
                pygame.draw.line(canvas, WHITE, last_pos, current_pos, ERASER_SIZE)
                last_pos = current_pos

            # Preview rectangle
            elif current_tool == "rectangle":
                canvas.blit(canvas_copy, (0, 0))
                rect = normalize_rect(start_pos, current_pos)
                pygame.draw.rect(canvas, current_color, rect, SHAPE_WIDTH)

            # Preview circle
            elif current_tool == "circle":
                canvas.blit(canvas_copy, (0, 0))
                radius = int(math.hypot(current_pos[0] - start_pos[0], current_pos[1] - start_pos[1]))
                if radius > 0:
                    pygame.draw.circle(canvas, current_color, start_pos, radius, SHAPE_WIDTH)

            # Preview square
            elif current_tool == "square":
                canvas.blit(canvas_copy, (0, 0))
                rect = square_rect(start_pos, current_pos)
                pygame.draw.rect(canvas, current_color, rect, SHAPE_WIDTH)

            # Preview right triangle
            elif current_tool == "right_triangle":
                canvas.blit(canvas_copy, (0, 0))
                points = right_triangle_points(start_pos, current_pos)
                pygame.draw.polygon(canvas, current_color, points, SHAPE_WIDTH)

            # Preview equilateral triangle
            elif current_tool == "equilateral_triangle":
                canvas.blit(canvas_copy, (0, 0))
                points = equilateral_triangle_points(start_pos, current_pos)
                pygame.draw.polygon(canvas, current_color, points, SHAPE_WIDTH)

            # Preview rhombus
            elif current_tool == "rhombus":
                canvas.blit(canvas_copy, (0, 0))
                points = rhombus_points(start_pos, current_pos)
                pygame.draw.polygon(canvas, current_color, points, SHAPE_WIDTH)

        # -----------------------------
        # MOUSE BUTTON UP
        # -----------------------------
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            drawing = False
            start_pos = None
            last_pos = None
            canvas_copy = None

    # -----------------------------
    # DRAW EVERYTHING
    # -----------------------------
    screen.fill(WHITE)
    draw_toolbar()
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()