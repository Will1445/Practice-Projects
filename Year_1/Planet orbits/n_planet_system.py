import pygame
import numpy as np
import math
import random

random.seed=14

width = 1300
height = 800
dt = 1
G = 1
m = 30

n=50

pygame.init()
screen = pygame.display.set_mode((width, height))
random_colours = []

for i in range(1,n+1):
    globals()[f'planet_{i}_pos_x'] = random.randint(0,1300)
    globals()[f'planet_{i}_pos_y'] = random.randint(0,800)
    globals()[f'planet_{i}_rad_vel_x'] = 0
    globals()[f'planet_{i}_rad_vel_y'] = 0
    globals()[f'planet_{i}_tan_vel_x'] = random.randint(-100,100) /100
    globals()[f'planet_{i}_tan_vel_y'] = random.randint(-100,100) /100
    colour = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    random_colours.append(colour)


# Creating dotted positions empty arrays 
for i in range(1,n+1):
    globals()[f'planet_{i}_dotted_positions'] = []


BLACK = (0, 0, 0)

font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK)
    
    # Seperation between # and # as a scalar
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            globals()[f'seperation_{i}and{j}'] = np.sqrt((globals()[f'planet_{i}_pos_x'] - globals()[f'planet_{j}_pos_x'])**2 + (globals()[f'planet_{i}_pos_y'] - globals()[f'planet_{j}_pos_y'])**2)
       
    # Angle from # to #                                                                                                                               
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            globals()[f'angle_{i}and{j}'] = math.atan2(-globals()[f'planet_{i}_pos_y'] + globals()[f'planet_{j}_pos_y'], globals()[f'planet_{i}_pos_x'] - globals()[f'planet_{j}_pos_x'])
            globals()[f'angle_{j}and{i}'] = globals()[f'angle_{i}and{j}'] + np.pi
    
    # Acceleration of # caused by #
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            globals()[f'planet_{i}_acceleration_{j}'] = (G*m)/globals()[f'seperation_{i}and{j}']**2
            globals()[f'planet_{j}_acceleration_{i}'] = (G*m)/globals()[f'seperation_{i}and{j}']**2
            
    # Summing accelerations from all other planets for planet # in the x direction        
    for i in range(1,n+1):
        temp = 0
        for j in range(1,n+1):
            if i != j:
                temp = temp + globals()[f'planet_{i}_acceleration_{j}'] * -np.cos(globals()[f'angle_{i}and{j}'])
        globals()[f'planet_{i}_acceleration_x'] = temp
    
    # Summing accelerations from all other planets for planet # in the y direction    
    for i in range(1,n+1):
        temp = 0
        for j in range(1,n+1):
            if i != j:
                temp = temp + globals()[f'planet_{i}_acceleration_{j}'] * np.sin(globals()[f'angle_{i}and{j}'])
        globals()[f'planet_{i}_acceleration_y'] = temp
    
    # Finding each planets new radial velocity
    for i in range(1,n+1):
        globals()[f'planet_{i}_rad_vel_x'] = globals()[f'planet_{i}_rad_vel_x'] + globals()[f'planet_{i}_acceleration_x'] * dt
        globals()[f'planet_{i}_rad_vel_y'] = globals()[f'planet_{i}_rad_vel_y'] + globals()[f'planet_{i}_acceleration_y'] * dt
   
    # Finding each planets new position
    for i in range(1,n+1):
        globals()[f'planet_{i}_pos_x'] = globals()[f'planet_{i}_pos_x'] + (globals()[f'planet_{i}_rad_vel_x'] + globals()[f'planet_{i}_tan_vel_x']) * dt
        globals()[f'planet_{i}_pos_y'] = globals()[f'planet_{i}_pos_y'] + (globals()[f'planet_{i}_rad_vel_y'] + globals()[f'planet_{i}_tan_vel_y']) * dt
    
    
    # Creating dotted line positions
    
    for i in range(1,n+1):
        globals()[f'planet_{i}_dotted_positions'].append((globals()[f'planet_{i}_pos_x'], globals()[f'planet_{i}_pos_y']))
    
    
    # Drawing objects at new positions
    
    for i in range(1,n+1):
        pygame.draw.circle(screen, random_colours[i-1], (globals()[f'planet_{i}_pos_x'], globals()[f'planet_{i}_pos_y']), 2.5)
    
    
    # Drawing the dotted lines
    
    for i in range(1,n+1):
        for j in range(0,len(globals()[f'planet_{i}_dotted_positions']), 3):
            pygame.draw.circle(screen, random_colours[i-1], globals()[f'planet_{i}_dotted_positions'][j][:2], 1)
   

    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()