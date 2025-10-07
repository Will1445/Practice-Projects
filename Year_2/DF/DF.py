import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doppler DF Simulation")

clock = pygame.time.Clock()
FPS = 60

# RF Source
source_pos = [WIDTH // 2 + 200, HEIGHT // 2]
source_radius = 10
dragging = False

# Base frequency and wave speed
f0 = 1000.0  # Hz
c = 343.0

# Receiver orbit
center = (WIDTH // 2, HEIGHT // 2)
orbit_radius = 20
angle = 0
angular_speed = 0.05  # radians per frame

# Frequency history for one full orbit approximation
history_length = 180  # roughly one orbit at 60 FPS, angular_speed 0.05 rad/frame
frequency_history = [f0] * history_length
idx = 0

# Graph settings
graph_width, graph_height = 240, 140
graph_rect = pygame.Rect(WIDTH - graph_width - 20, 20, graph_width, graph_height)
padding_x = 15
padding_y = 15
dot_radius = 6

# Slider
slider_rect = pygame.Rect(50, 550, 200, 10)
slider_knob = pygame.Rect(50 + 100, 545, 10, 20)
slider_dragging = False
min_speed, max_speed = 0.003, 0.1

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
SOURCE_COLOR = (0, 200, 255)
RECEIVER_COLOR = (255, 100, 100)
SLIDER_COLOR = (180, 180, 180)
KNOB_COLOR = (100, 255, 100)
GRAPH_LINE_COLOR = GREEN
GRAPH_DOT_COLOR = (255, 255, 0)
CIRCLE_COLOR = (0, 150, 255)

prev_pos = None
prev_time = None

# Font for text
font = pygame.font.SysFont(None, 24)

# RF circle animation variables
max_circle_radius = 200
num_circles = 5
circle_spacing = max_circle_radius / num_circles
circle_phase = 0
circle_speed = 1.5  # pixels per frame

running = True
while running:
    screen.fill(BLACK)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if math.hypot(event.pos[0] - source_pos[0], event.pos[1] - source_pos[1]) < source_radius + 5:
                dragging = True
            if slider_knob.collidepoint(event.pos):
                slider_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            slider_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                source_pos[0], source_pos[1] = event.pos
            if slider_dragging:
                slider_knob.centerx = max(slider_rect.left, min(slider_rect.right, event.pos[0]))
                relative_pos = (slider_knob.centerx - slider_rect.left) / slider_rect.width
                angular_speed = min_speed + (max_speed - min_speed) * relative_pos

    # Draw RF emission circles
    circle_phase = (circle_phase + circle_speed) % circle_spacing
    for i in range(num_circles):
        radius = circle_phase + i * circle_spacing
        alpha = max(0, 255 * (1 - radius / max_circle_radius))
        if alpha > 0:
            circle_surface = pygame.Surface((max_circle_radius*2, max_circle_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (CIRCLE_COLOR[0], CIRCLE_COLOR[1], CIRCLE_COLOR[2], int(alpha)), (max_circle_radius, max_circle_radius), int(radius), 2)
            screen.blit(circle_surface, (source_pos[0] - max_circle_radius, source_pos[1] - max_circle_radius))

    # Draw RF source
    pygame.draw.circle(screen, SOURCE_COLOR, source_pos, source_radius)

    # Calculate receiver position
    angle += angular_speed
    receiver_x = center[0] + orbit_radius * math.cos(angle)
    receiver_y = center[1] + orbit_radius * math.sin(angle)
    receiver_pos = (receiver_x, receiver_y)

    # Calculate radial velocity (receiver relative to source)
    if prev_pos is not None and prev_time is not None:
        dt = (now - prev_time) / 1000  # seconds
        dx = receiver_x - prev_pos[0]
        dy = receiver_y - prev_pos[1]
        vx = dx / dt
        vy = dy / dt

        rx, ry = source_pos[0] - receiver_x, source_pos[1] - receiver_y
        r_mag = math.hypot(rx, ry)
        if r_mag != 0:
            ux, uy = rx / r_mag, ry / r_mag
            vr = vx * ux + vy * uy
        else:
            vr = 0
    else:
        vr = 0

    prev_pos = receiver_pos
    prev_time = now

    observed_freq = f0 * (1 + vr / c)

    idx = (idx + 1) % history_length
    frequency_history[idx] = observed_freq

    pygame.draw.circle(screen, RECEIVER_COLOR, (int(receiver_x), int(receiver_y)), 8)
    pygame.draw.circle(screen, (50, 50, 50), center, orbit_radius, 1)
    pygame.draw.rect(screen, SLIDER_COLOR, slider_rect)
    pygame.draw.rect(screen, KNOB_COLOR, slider_knob)
    pygame.draw.rect(screen, (40, 40, 40), graph_rect)
    pygame.draw.rect(screen, WHITE, graph_rect, 2)

    # Compute min and max freq dynamically over history
    min_freq = min(frequency_history)
    max_freq = max(frequency_history)
    freq_range = max_freq - min_freq
    if freq_range < 1e-5:
        freq_range = 1e-5

    y_min = min_freq - 0.1 * freq_range
    y_max = max_freq + 0.1 * freq_range

    x_min = - (padding_x / graph_width) * (history_length - 1)
    x_max = (history_length - 1) + (padding_x / graph_width) * (history_length - 1)

    usable_width = graph_width - 2 * padding_x
    usable_height = graph_height - 2 * padding_y

    points = []
    for i in range(history_length):
        j = (idx + 1 + i) % history_length
        freq = frequency_history[j]

        x = graph_rect.x + padding_x + ((i - x_min) / (x_max - x_min)) * usable_width
        y = graph_rect.y + graph_height - padding_y - ((freq - y_min) / (y_max - y_min)) * usable_height

        points.append((x, y))

    pygame.draw.lines(screen, GRAPH_LINE_COLOR, False, points, 2)

    dot_x, dot_y = points[-1]
    pygame.draw.circle(screen, GRAPH_DOT_COLOR, (int(dot_x), int(dot_y)), dot_radius)

    # Slider label
    label = font.render("Rotation Speed", True, WHITE)
    screen.blit(label, (slider_rect.left, slider_rect.top - 25))

    # Frequency readout below graph
    freq_text = font.render(f"Frequency: {observed_freq:.2f} Hz", True, WHITE)
    text_rect = freq_text.get_rect(midtop=(graph_rect.centerx, graph_rect.bottom + 5))
    screen.blit(freq_text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
