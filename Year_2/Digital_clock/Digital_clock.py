import pygame
import math
import time
import numpy as np

# Initialize pygame
pygame.init()

# Grid parameters
GRID_ROWS = 3
GRID_COLS = 8
CLOCK_RADIUS = 50
WIDTH = GRID_COLS * 2 * CLOCK_RADIUS
HEIGHT = GRID_ROWS * 2 * CLOCK_RADIUS
FPS = 60

# Timing parameters
acceleration_time = 5  # seconds
hold_time = 10         # seconds

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clock Grid")
clock = pygame.time.Clock()

def shortest_delta(a, b):
    """Calculate shortest angular difference between two angles"""
    d = b - a
    while d > math.pi:
        d -= 2 * math.pi
    while d <= -math.pi:
        d += 2 * math.pi
    return d

def draw_hand(surface, center, angle, length, color, thickness=3):
    """Draw a clock hand with validation"""
    if angle is None or np.isnan(angle):
        return
    end_x = center[0] + length * math.cos(angle)
    end_y = center[1] - length * math.sin(angle)
    pygame.draw.line(surface, color, center, (end_x, end_y), thickness)

def draw_clock(surface, center, hour, minute):
    """Draw static clock with number positions"""
    pygame.draw.circle(surface, (150, 150, 150), center, CLOCK_RADIUS, 3)
    if hour is not None:
        hour_angle = math.radians(90 - (hour % 12) * 30)
        draw_hand(surface, center, hour_angle, CLOCK_RADIUS*0.9, (255,255,255), 4)
    if minute is not None:
        minute_angle = math.radians(90 - minute * 6)
        draw_hand(surface, center, minute_angle, CLOCK_RADIUS*0.95, (255,255,255), 3)

def draw_clock_angle(surface, center, hour_angle, minute_angle):
    """Draw animated clock with direct angles"""
    pygame.draw.circle(surface, (150, 150, 150), center, CLOCK_RADIUS, 3)
    if hour_angle is not None and not np.isnan(hour_angle):
        draw_hand(surface, center, hour_angle, CLOCK_RADIUS*0.9, (255,255,255), 4)
    if minute_angle is not None and not np.isnan(minute_angle):
        draw_hand(surface, center, minute_angle, CLOCK_RADIUS*0.95, (255,255,255), 3)

def get_clock_positions(number):
    positions = {
        0: [[6,15], [6,45], [6,0], [6,0], [0,15], [0,45]],
        1: [[None,None], [6,30], [None,None], [6,0], [None,None], [0,0]],
        2: [[3,15], [6,45], [6,15], [0,45], [0,15], [9,45]],
        3: [[3,15], [6,45], [3,15], [0,45], [3,15], [9,0]],
        4: [[6,30], [6,30], [0,15], [0,45], [None,None], [0,0]],
        5: [[6,15], [9,45], [0,15], [6,45], [3,15], [0,45]],
        6: [[6,15], [9,45], [0,15], [9,30], [3,0], [9,0]],
        7: [[3,15], [9,30], [None,None], [0,30], [None,None], [0,0]],
        8: [[3,30], [9,30], [3,0], [9,0], [3,0], [9,0]],
        9: [[3,30], [9,30], [3,0], [9,0], [3,15], [9,0]]
    }
    return positions[number]

def display_number(segment, number):
    columns = [2*segment-1, 2*segment]
    positions = get_clock_positions(number)
    i = 0
    for col in columns:
        col -= 1  # 0-based indexing
        for row in range(3):
            pos = positions[2*row + i]
            center = (col*2*CLOCK_RADIUS + CLOCK_RADIUS,
                      row*2*CLOCK_RADIUS + CLOCK_RADIUS)
            draw_clock(screen, center, pos[0], pos[1])
        i += 1

def main():
    running = True
    just_started_moving = True

    # Animation state
    hour_angles = minute_angles = None
    acceleration_factor = 0.1
    acceleration_random_factors = None
    current_velocity_h = current_velocity_m = None
    decel_start_time = None
    decel_start_angles_h = decel_start_angles_m = None
    target_hour_angles = target_minute_angles = None

    while running:
        screen.fill((0, 0, 0))
        current_time = time.localtime()
        hour, minute = current_time.tm_hour, current_time.tm_min
        current_sec = time.time() % 60

        if current_sec <= hold_time:
            # Static display phase
            just_started_moving = True
            hour_angles = minute_angles = None
            acceleration_factor = 0.1
            acceleration_random_factors = None
            current_velocity_h = current_velocity_m = None
            decel_start_time = decel_start_angles_h = decel_start_angles_m = None
            target_hour_angles = target_minute_angles = None

            # Display current time
            hour_str = f"{hour:02d}"
            minute_str = f"{minute:02d}"
            display_number(1, int(hour_str[0]))
            display_number(2, int(hour_str[1]))
            display_number(3, int(minute_str[0]))
            display_number(4, int(minute_str[1]))
        else:
            # Animation phase
            if just_started_moving:
                # Initialize angles and velocities
                ha_list, ma_list = [], []
                digits = [int(d) for d in f"{hour:02d}{minute:02d}"]
                for digit in digits:
                    positions = get_clock_positions(digit)
                    for pos in positions:
                        h_angle = math.radians(90 - (pos[0]%12*30)) if pos[0] is not None else 0
                        m_angle = math.radians(90 - pos[1]*6) if pos[1] is not None else 0
                        ha_list.append(h_angle)
                        ma_list.append(m_angle)
                hour_angles = np.array(ha_list, dtype=float)
                minute_angles = np.array(ma_list, dtype=float)
                just_started_moving = False

                # Initialize velocity factors
                acceleration_random_factors = np.random.uniform(1, 1.1, hour_angles.shape)
                current_velocity_h = np.pi/256 * acceleration_factor * acceleration_random_factors * FPS
                current_velocity_m = np.pi/128 * acceleration_factor * acceleration_random_factors * FPS

            # Phase calculations
            if hold_time < current_sec <= hold_time+acceleration_time:
                # Acceleration phase
                acceleration_factor *= 1.01
                current_velocity_h = np.pi/256 * acceleration_factor * acceleration_random_factors * FPS
                current_velocity_m = np.pi/128 * acceleration_factor * acceleration_random_factors * FPS
                
                # Update angles
                hour_angles += current_velocity_h / FPS
                minute_angles += current_velocity_m / FPS

            elif 60-acceleration_time <= current_sec < 60:
                # Deceleration phase
                if decel_start_time is None:
                    decel_start_time = time.time()
                    decel_start_angles_h = hour_angles.copy()
                    decel_start_angles_m = minute_angles.copy()

                    # Calculate next minute's targets
                    next_min = (minute + 1) % 60
                    next_hr = (hour + 1) % 24 if next_min == 0 else hour
                    next_digits = [int(d) for d in f"{next_hr:02d}{next_min:02d}"]
                    target_ha, target_ma = [], []
                    for digit in next_digits:
                        for pos in get_clock_positions(digit):
                            h = math.radians(90 - (pos[0]%12*30)) if pos[0] is not None else None
                            m = math.radians(90 - pos[1]*6) if pos[1] is not None else None
                            target_ha.append(h)
                            target_ma.append(m)
                    target_hour_angles = np.array(target_ha, dtype=object)
                    target_minute_angles = np.array(target_ma, dtype=object)

                # Cubic easing function for smooth deceleration
                t_elapsed = time.time() - decel_start_time
                u = min(t_elapsed / acceleration_time, 1.0)
                
                new_ha, new_ma = [], []
                for i in range(len(hour_angles)):
                    # Hour hand calculation
                    if target_hour_angles[i] is None:
                        new_ha.append(None)
                    else:
                        S = decel_start_angles_h[i]
                        d = shortest_delta(S, target_hour_angles[i])
                        V0 = current_velocity_h[i]
                        new_ha.append(S + (u**3 - 2*u**2 + u)*acceleration_time*V0 + (-2*u**3 + 3*u**2)*d)
                    
                    # Minute hand calculation
                    if target_minute_angles[i] is None:
                        new_ma.append(None)
                    else:
                        S = decel_start_angles_m[i]
                        d = shortest_delta(S, target_minute_angles[i])
                        V0 = current_velocity_m[i]
                        new_ma.append(S + (u**3 - 2*u**2 + u)*acceleration_time*V0 + (-2*u**3 + 3*u**2)*d)
                
                hour_angles = np.array(new_ha, dtype=object)
                minute_angles = np.array(new_ma, dtype=object)

            else:
                # Constant velocity phase
                hour_angles += current_velocity_h / FPS
                minute_angles += current_velocity_m / FPS

            # Draw all clocks
            idx = 0
            for segment in range(4):
                for clock_num in range(6):
                    col = clock_num % 2
                    row = clock_num // 2
                    center = ((2*segment + col)*2*CLOCK_RADIUS + CLOCK_RADIUS,
                             row*2*CLOCK_RADIUS + CLOCK_RADIUS)
                    draw_clock_angle(screen, center, 
                                   hour_angles[idx] if hour_angles is not None else None,
                                   minute_angles[idx] if minute_angles is not None else None)
                    idx += 1

        pygame.display.flip()
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()