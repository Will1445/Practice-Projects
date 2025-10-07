import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DF Simulation Menu")

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont(None, 36)

# Mode control
MODE_MENU = 0
MODE_DOPPLER = 1
MODE_WATTSON_WATT = 2
mode = MODE_MENU

# Shared RF Source
source_pos = [WIDTH // 2 + 200, HEIGHT // 2]
source_radius = 10

def draw_menu():
    screen.fill((0, 0, 0))
    title = font.render("Select DF Mode", True, (255, 255, 255))
    doppler_button = font.render("1 - Doppler DF", True, (0, 255, 0))
    wattson_button = font.render("2 - Wattson-Watt DF", True, (0, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
    screen.blit(doppler_button, (WIDTH // 2 - doppler_button.get_width() // 2, 250))
    screen.blit(wattson_button, (WIDTH // 2 - wattson_button.get_width() // 2, 320))
    pygame.display.flip()

def run_doppler_mode():
    global mode
    dragging = False
    f0 = 1000.0
    c = 343.0
    center = (WIDTH // 2, HEIGHT // 2)
    orbit_radius = 20
    angle = 0
    angular_speed = 0.05

    history_length = 180
    frequency_history = [f0] * history_length
    idx = 0

    graph_width, graph_height = 240, 140
    graph_rect = pygame.Rect(WIDTH - graph_width - 20, 20, graph_width, graph_height)
    padding_x = 15
    padding_y = 15
    dot_radius = 6

    slider_rect = pygame.Rect(50, 550, 200, 10)
    slider_knob = pygame.Rect(50 + 100, 545, 10, 20)
    slider_dragging = False
    min_speed, max_speed = 0.003, 0.1

    CIRCLE_COLOR = (0, 150, 255)
    max_circle_radius = 200
    num_circles = 5
    circle_spacing = max_circle_radius / num_circles
    circle_phase = 0
    circle_speed = 1.5

    prev_pos = None
    prev_time = None

    font_small = pygame.font.SysFont(None, 24)

    while mode == MODE_DOPPLER:
        screen.fill((0, 0, 0))
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                mode = MODE_MENU
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
                    rel_pos = (slider_knob.centerx - slider_rect.left) / slider_rect.width
                    angular_speed = min_speed + (max_speed - min_speed) * rel_pos

        circle_phase = (circle_phase + circle_speed) % circle_spacing
        for i in range(num_circles):
            radius = circle_phase + i * circle_spacing
            alpha = max(0, 255 * (1 - radius / max_circle_radius))
            if alpha > 0:
                surf = pygame.Surface((max_circle_radius*2, max_circle_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (CIRCLE_COLOR[0], CIRCLE_COLOR[1], CIRCLE_COLOR[2], int(alpha)), (max_circle_radius, max_circle_radius), int(radius), 2)
                screen.blit(surf, (source_pos[0] - max_circle_radius, source_pos[1] - max_circle_radius))

        pygame.draw.circle(screen, (0, 200, 255), source_pos, source_radius)

        angle += angular_speed
        receiver_x = center[0] + orbit_radius * math.cos(angle)
        receiver_y = center[1] + orbit_radius * math.sin(angle)
        receiver_pos = (receiver_x, receiver_y)

        if prev_pos is not None and prev_time is not None:
            dt = (now - prev_time) / 1000
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

        pygame.draw.circle(screen, (255, 100, 100), (int(receiver_x), int(receiver_y)), 8)
        pygame.draw.circle(screen, (50, 50, 50), center, orbit_radius, 1)
        pygame.draw.rect(screen, (180,180,180), slider_rect)
        pygame.draw.rect(screen, (100,255,100), slider_knob)
        pygame.draw.rect(screen, (40,40,40), graph_rect)
        pygame.draw.rect(screen, (255,255,255), graph_rect, 2)

        min_freq = min(frequency_history)
        max_freq = max(frequency_history)
        freq_range = max(1e-5, max_freq - min_freq)
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

        pygame.draw.lines(screen, (0, 255, 0), False, points, 2)
        dot_x, dot_y = points[-1]
        pygame.draw.circle(screen, (255, 255, 0), (int(dot_x), int(dot_y)), dot_radius)

        label = font_small.render("Rotation Speed", True, (255,255,255))
        screen.blit(label, (slider_rect.left, slider_rect.top - 25))
        freq_text = font_small.render(f"Frequency: {observed_freq:.2f} Hz", True, (255,255,255))
        screen.blit(freq_text, freq_text.get_rect(midtop=(graph_rect.centerx, graph_rect.bottom + 5)))

        pygame.display.flip()
        clock.tick(FPS)

def run_wattson_watt_mode():
    global mode
    dragging = False
    center = (WIDTH // 2, HEIGHT // 2)
    max_amp = 100
    font_small = pygame.font.SysFont(None, 24)

    # RF wave effect variables (similar to Doppler mode)
    CIRCLE_COLOR = (0, 150, 255)
    max_circle_radius = 200
    num_circles = 5
    circle_spacing = max_circle_radius / num_circles
    circle_phase = 0
    circle_speed = 1.5

    while mode == MODE_WATTSON_WATT:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                mode = MODE_MENU
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if math.hypot(event.pos[0] - source_pos[0], event.pos[1] - source_pos[1]) < source_radius + 5:
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                source_pos[0], source_pos[1] = event.pos

        # Update the RF wave phase
        circle_phase = (circle_phase + circle_speed) % circle_spacing

        # Draw fading RF waves around source_pos
        for i in range(num_circles):
            radius = circle_phase + i * circle_spacing
            alpha = max(0, 255 * (1 - radius / max_circle_radius))
            if alpha > 0:
                surf = pygame.Surface((max_circle_radius*2, max_circle_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (CIRCLE_COLOR[0], CIRCLE_COLOR[1], CIRCLE_COLOR[2], int(alpha)),
                                   (max_circle_radius, max_circle_radius), int(radius), 2)
                screen.blit(surf, (source_pos[0] - max_circle_radius, source_pos[1] - max_circle_radius))

        # Draw source and receiver
        pygame.draw.circle(screen, (0, 200, 255), source_pos, source_radius)
        pygame.draw.circle(screen, (255, 100, 100), center, 10)

        dx = source_pos[0] - center[0]
        dy = source_pos[1] - center[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            amp_x = amp_y = 0
        else:
            amp_x = max_amp * dx / distance
            amp_y = max_amp * dy / distance

        pygame.draw.line(screen, (255, 255, 0), center, (center[0] + amp_x, center[1]), 3)
        pygame.draw.line(screen, (0, 255, 0), center, (center[0], center[1] + amp_y), 3)

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        angle_text = font_small.render(f"Bearing: {angle_deg:.1f} deg", True, (255, 255, 255))
        screen.blit(angle_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


while True:
    if mode == MODE_MENU:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = MODE_DOPPLER
                elif event.key == pygame.K_2:
                    mode = MODE_WATTSON_WATT
    elif mode == MODE_DOPPLER:
        run_doppler_mode()
    elif mode == MODE_WATTSON_WATT:
        run_wattson_watt_mode()
