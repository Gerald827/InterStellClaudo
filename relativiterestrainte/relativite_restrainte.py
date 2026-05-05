
import sys
import math
import random
from turtle import width
import numpy as np

import pygame
import random

# Couleurs 
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 150, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (100, 100, 100)
PURPLE = (150, 15, 150)

pygame.init()
window = pygame.display.set_mode((1200, 900))
pygame.display.set_caption("Relativité Restreinte - Dilatation du Temps")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("arial", 40, bold=True)
big_font = pygame.font.SysFont("arial", 60, bold=True)
label_font = pygame.font.SysFont("arial", 24)
info_font = pygame.font.SysFont("arial", 18)

# Clock settings
clock_radius = 120
left_clock_center = (300, 350)
right_clock_center = (900, 350)

celerite = 299792458  # m/s aka vitesse de la lumière

# Counter variables
counter = 0.0
counter2 = 0.0
accumulator = 0.0
accumulator2 = 0.0
speed = 1.0
speed2 = 1.0
beta = 0.0  # v/c

# Slider variables
slider_y = 800
slider_x_min = 150
slider_x_max = 1050
dragging = False
min_beta = 0.0
max_beta = 0.99

def format_time(c):
    total_sec = int(c)
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def draw_analog_clock(center, color, total_seconds):
    """Draw a professional-looking analog clock"""
    # Circle border
    pygame.draw.circle(window, color, center, clock_radius, 3)
    pygame.draw.circle(window, DARK_GRAY, center, clock_radius - 5)
    
    # Hour numbers
    for hour in range(1, 13):
        angle = math.radians((hour - 3) * 30)
        x = center[0] + (clock_radius - 30) * math.cos(angle)
        y = center[1] + (clock_radius - 30) * math.sin(angle)
        hour_text = info_font.render(str(hour), True, WHITE)
        hour_rect = hour_text.get_rect(center=(x, y))
        window.blit(hour_text, hour_rect)
    
    # Hour marks (thicker at 12, 3, 6, 9)
    for i in range(60):
        angle = math.radians(i * 6)
        if i % 5 == 0:
            start_r = clock_radius - 20
            line_width = 3
        else:
            start_r = clock_radius - 12
            line_width = 1
        
        start_x = center[0] + start_r * math.cos(angle)
        start_y = center[1] + start_r * math.sin(angle)
        end_x = center[0] + clock_radius * math.cos(angle)
        end_y = center[1] + clock_radius * math.sin(angle)
        pygame.draw.line(window, WHITE, (start_x, start_y), (end_x, end_y), line_width)
    
    # Calculate hand positions
    total_sec = int(total_seconds)
    seconds = total_sec % 60
    minutes = (total_sec // 60) % 60
    hours = (total_sec // 3600) % 12
    
    # Hour hand
    hour_angle = math.radians((hours + minutes / 60.0 - 3) * 30)
    hour_length = clock_radius * 0.5
    hour_x = center[0] + hour_length * math.cos(hour_angle)
    hour_y = center[1] + hour_length * math.sin(hour_angle)
    pygame.draw.line(window, color, center, (hour_x, hour_y), 8)
    
    # Minute hand
    minute_angle = math.radians((minutes + seconds / 60.0 - 15) * 6)
    minute_length = clock_radius * 0.7
    minute_x = center[0] + minute_length * math.cos(minute_angle)
    minute_y = center[1] + minute_length * math.sin(minute_angle)
    pygame.draw.line(window, color, center, (minute_x, minute_y), 5)
    
    # Second hand
    second_angle = math.radians((seconds - 15) * 6)
    second_length = clock_radius * 0.8
    second_x = center[0] + second_length * math.cos(second_angle)
    second_y = center[1] + second_length * math.sin(second_angle)
    pygame.draw.line(window, BLUE, center, (second_x, second_y), 2)
    
    # Center dot
    pygame.draw.circle(window, WHITE, center, 6)

stars = [(random.randint(0, 1200), random.randint(0, 900)) for _ in range(200)]

run = True
while run:
    
    dt = clock.get_time() / 1000.0  # delta time in seconds
    
    # Calculate gamma from beta
    if beta < 1.0:
        gamma = 1 / math.sqrt(1 - beta**2)
    else:
        gamma = 1.0
    speed = 1.0  # Left clock normal speed
    speed2 = 1.0 / gamma  # Right clock dilated
    
    accumulator += dt * speed
    accumulator2 += dt * speed2
    
    clock.tick(60)

    # Update accumulators
    if accumulator >= 1:
        counter += 1
        accumulator -= 1
    if accumulator2 >= 1:
        counter2 += 1
        accumulator2 -= 1

    # Calculate slider knob position
    knob_x = slider_x_min + (beta - min_beta) / (max_beta - min_beta) * (slider_x_max - slider_x_min)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if slider_y - 15 < event.pos[1] < slider_y + 15:
                if knob_x - 12 < event.pos[0] < knob_x + 12:
                    dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                knob_x = max(slider_x_min, min(slider_x_max, event.pos[0]))
                beta = min_beta + (knob_x - slider_x_min) / (slider_x_max - slider_x_min) * (max_beta - min_beta)
            
    # Background
    window.fill(BLACK)
    
    # Draw stars
    for star in stars:
        pygame.draw.circle(window, WHITE, star, 1)
    
    # Top title
    title = title_font.render("Relativité Restreinte - Dilatation du Temps", True, WHITE)
    title_rect = title.get_rect(center=(600, 30))
    window.blit(title, title_rect)
    
    # Left clock section
    left_label = label_font.render("Référentiel au repos", True, RED)
    left_label_rect = left_label.get_rect(center=(300, 200))
    window.blit(left_label, left_label_rect)
    
    draw_analog_clock(left_clock_center, RED, counter)
    
    left_time = format_time(counter)
    left_time_text = big_font.render(left_time, True, RED)
    left_time_rect = left_time_text.get_rect(center=(300, 510))
    window.blit(left_time_text, left_time_rect)
    
    # Right clock section
    right_label = label_font.render("Référentiel en mouvement", True, GREEN)
    right_label_rect = right_label.get_rect(center=(900, 200))
    window.blit(right_label, right_label_rect)
    
    draw_analog_clock(right_clock_center, GREEN, counter2)
    
    right_time = format_time(counter2)
    right_time_text = big_font.render(right_time, True, GREEN)
    right_time_rect = right_time_text.get_rect(center=(900, 510))
    window.blit(right_time_text, right_time_rect)
    
    # Middle divider
    pygame.draw.line(window, LIGHT_GRAY, (600, 200), (600, 600), 1)
    
    # Slider section
    velocity = beta * celerite
    gamma_text = f"β = {beta:.3f}  |  v = {velocity:.0f} m/s  |  γ = {gamma:.3f}"
    velocity_label = label_font.render(gamma_text, True, BLUE)
    velocity_rect = velocity_label.get_rect(center=(600, 650))
    window.blit(velocity_label, velocity_rect)
    
    # Draw slider
    pygame.draw.line(window, LIGHT_GRAY, (slider_x_min, slider_y), (slider_x_max, slider_y), 3)
    pygame.draw.circle(window, BLUE, (int(knob_x), slider_y), 12)
    pygame.draw.circle(window, WHITE, (int(knob_x), slider_y), 8)
    
    # Slider labels
    min_label = info_font.render("0 m/s", True, LIGHT_GRAY)
    max_label = info_font.render("0.99c", True, LIGHT_GRAY)
    window.blit(min_label, (slider_x_min - 30, slider_y + 20))
    window.blit(max_label, (slider_x_max - 40, slider_y + 20))
    
    # Info text at bottom
    info_text = "Fait par Kenzo, Nolan, Julian et Matisse - 2026"
    info = info_font.render(info_text, True, WHITE)
    info_rect = info.get_rect(center=(600, 870))
    window.blit(info, info_rect)

    pygame.display.flip()

pygame.quit()