import sys
import math
import random
import numpy as np

import pygame

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
window = pygame.display.set_mode((1400, 1000))
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

celerite = 299792458  # m/s

# Counter variables
counter = 0.0
counter2 = 0.0
accumulator = 0.0
accumulator2 = 0.0
beta = 0.0  # v/c

# Slider 1 - vitesse (beta)
slider_y = 800
slider_x_min = 150
slider_x_max = 1050
dragging = False
min_beta = 0.0
max_beta = 0.99

# Slider 2 - vitesse de simulation
# curseur à GAUCHE = rapide (x100), MILIEU = x1, DROITE = x0.1
slider_y2 = 900
slider_x_min2 = 150
slider_x_max2 = 1050
dragging2 = False
sim_speed_t = 0.5  # 0=gauche(rapide) … 1=droite(lent)

def get_sim_speed(t):
    """t=0 (gauche) → ×100 | t=0.5 (milieu) → ×1 | t=1 (droite) → ×0.1"""
    return 10 ** (2 - t * 3)

def format_time(c):
    total_sec = int(c)
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def draw_analog_clock(center, color, total_seconds):
    pygame.draw.circle(window, color, center, clock_radius, 3)
    pygame.draw.circle(window, DARK_GRAY, center, clock_radius - 5)
    
    for hour in range(1, 13):
        angle = math.radians((hour - 3) * 30)
        x = center[0] + (clock_radius - 30) * math.cos(angle)
        y = center[1] + (clock_radius - 30) * math.sin(angle)
        hour_text = info_font.render(str(hour), True, WHITE)
        window.blit(hour_text, hour_text.get_rect(center=(x, y)))
    
    for i in range(60):
        angle = math.radians(i * 6)
        start_r = clock_radius - 20 if i % 5 == 0 else clock_radius - 12
        line_width = 3 if i % 5 == 0 else 1
        start_x = center[0] + start_r * math.cos(angle)
        start_y = center[1] + start_r * math.sin(angle)
        end_x = center[0] + clock_radius * math.cos(angle)
        end_y = center[1] + clock_radius * math.sin(angle)
        pygame.draw.line(window, WHITE, (start_x, start_y), (end_x, end_y), line_width)
    
    total_sec = int(total_seconds)
    seconds = total_sec % 60
    minutes = (total_sec // 60) % 60
    hours = (total_sec // 3600) % 12
    
    hour_angle = math.radians((hours + minutes / 60.0 - 3) * 30)
    hour_x = center[0] + clock_radius * 0.5 * math.cos(hour_angle)
    hour_y = center[1] + clock_radius * 0.5 * math.sin(hour_angle)
    pygame.draw.line(window, color, center, (hour_x, hour_y), 8)
    
    minute_angle = math.radians((minutes + seconds / 60.0 - 15) * 6)
    minute_x = center[0] + clock_radius * 0.7 * math.cos(minute_angle)
    minute_y = center[1] + clock_radius * 0.7 * math.sin(minute_angle)
    pygame.draw.line(window, color, center, (minute_x, minute_y), 5)
    
    second_angle = math.radians((seconds - 15) * 6)
    second_x = center[0] + clock_radius * 0.8 * math.cos(second_angle)
    second_y = center[1] + clock_radius * 0.8 * math.sin(second_angle)
    pygame.draw.line(window, BLUE, center, (second_x, second_y), 2)
    
    pygame.draw.circle(window, WHITE, center, 6)

stars = [(random.randint(0, 1400), random.randint(0, 1000)) for _ in range(200)]

run = True
while run:
    dt = clock.get_time() / 1000.0

    # Gamma depuis beta (slider 1 — inchangé)
    if beta < 1.0:
        gamma = 1 / math.sqrt(1 - beta**2)
    else:
        gamma = 1.0

    # Vitesse de simulation depuis slider 2
    sim_speed = get_sim_speed(sim_speed_t)

    # Horloge gauche : tourne à sim_speed
    # Horloge droite : tourne à sim_speed / gamma (dilatation du temps)
    accumulator  += dt * sim_speed
    accumulator2 += dt * sim_speed / gamma

    clock.tick(60)

    if accumulator >= 1:
        counter += 1
        accumulator -= 1
    if accumulator2 >= 1:
        counter2 += 1
        accumulator2 -= 1

    # Positions des curseurs
    knob_x  = slider_x_min  + (beta - min_beta) / (max_beta - min_beta) * (slider_x_max  - slider_x_min)
    knob_x2 = slider_x_min2 + sim_speed_t * (slider_x_max2 - slider_x_min2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if slider_y - 15 < event.pos[1] < slider_y + 15:
                if knob_x - 12 < event.pos[0] < knob_x + 12:
                    dragging = True
            elif slider_y2 - 15 < event.pos[1] < slider_y2 + 15:
                if knob_x2 - 12 < event.pos[0] < knob_x2 + 12:
                    dragging2 = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            dragging2 = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                knob_x = max(slider_x_min, min(slider_x_max, event.pos[0]))
                beta = min_beta + (knob_x - slider_x_min) / (slider_x_max - slider_x_min) * (max_beta - min_beta)
            elif dragging2:
                knob_x2 = max(slider_x_min2, min(slider_x_max2, event.pos[0]))
                sim_speed_t = (knob_x2 - slider_x_min2) / (slider_x_max2 - slider_x_min2)

    # --- Dessin ---
    window.fill(BLACK)
    for star in stars:
        pygame.draw.circle(window, WHITE, star, 1)

    # Horloge gauche
    window.blit(label_font.render("Référentiel au repos", True, RED),
                label_font.render("Référentiel au repos", True, RED).get_rect(center=(300, 200)))
    draw_analog_clock(left_clock_center, RED, counter)
    window.blit(big_font.render(format_time(counter), True, RED),
                big_font.render(format_time(counter), True, RED).get_rect(center=(300, 510)))

    # Horloge droite
    window.blit(label_font.render("Référentiel en mouvement", True, GREEN),
                label_font.render("Référentiel en mouvement", True, GREEN).get_rect(center=(900, 200)))
    draw_analog_clock(right_clock_center, GREEN, counter2)
    window.blit(big_font.render(format_time(counter2), True, GREEN),
                big_font.render(format_time(counter2), True, GREEN).get_rect(center=(900, 510)))

    # Séparateur
    pygame.draw.line(window, LIGHT_GRAY, (600, 200), (600, 600), 1)

    # Infos slider 1
    velocity = beta * celerite
    gamma_text = f"β = {beta:.3f}  |  v = {velocity:.0f} m/s  |  γ = {gamma:.3f}"
    gamma_surf = label_font.render(gamma_text, True, BLUE)
    window.blit(gamma_surf, gamma_surf.get_rect(center=(600, 650)))

    # Infos slider 2
    if sim_speed >= 10:
        sim_str = f"×{sim_speed:.0f}"
    elif sim_speed >= 1:
        sim_str = f"×{sim_speed:.1f}"
    else:
        sim_str = f"×{sim_speed:.2f}"
    sim_surf = label_font.render(f"Vitesse de simulation : {sim_str}", True, PURPLE)
    window.blit(sim_surf, sim_surf.get_rect(center=(600, 700)))

    # Slider 1 (beta) — inchangé
    pygame.draw.line(window, LIGHT_GRAY, (slider_x_min, slider_y), (slider_x_max, slider_y), 3)
    pygame.draw.circle(window, BLUE, (int(knob_x), slider_y), 12)
    pygame.draw.circle(window, WHITE, (int(knob_x), slider_y), 8)
    window.blit(info_font.render("Vitesse (β)", True, BLUE), (slider_x_min, slider_y - 28))
    window.blit(info_font.render("0", True, LIGHT_GRAY), (slider_x_min - 10, slider_y + 18))
    window.blit(info_font.render("0.99c", True, LIGHT_GRAY), (slider_x_max - 35, slider_y + 18))

    # Slider 2 (sim speed) — gauche=rapide, droite=lent
    pygame.draw.line(window, LIGHT_GRAY, (slider_x_min2, slider_y2), (slider_x_max2, slider_y2), 3)
    pygame.draw.circle(window, PURPLE, (int(knob_x2), slider_y2), 12)
    pygame.draw.circle(window, WHITE, (int(knob_x2), slider_y2), 8)
    window.blit(info_font.render("Vitesse de simulation", True, PURPLE), (slider_x_min2, slider_y2 - 28))
    window.blit(info_font.render("×100", True, LIGHT_GRAY), (slider_x_min2 - 15, slider_y2 + 18))
    window.blit(info_font.render("×1", True, LIGHT_GRAY), ((slider_x_min2 + slider_x_max2) // 2 - 8, slider_y2 + 18))
    window.blit(info_font.render("×0.1", True, LIGHT_GRAY), (slider_x_max2 - 20, slider_y2 + 18))

    # Crédits
    info_text = info_font.render("Fait par Kenzo, Nolan, Julian et Matisse - 2026", True, WHITE)
    window.blit(info_text, info_text.get_rect(center=(600, 970)))

    pygame.display.flip()

pygame.quit()