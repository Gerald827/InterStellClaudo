
import sys
import math
import random
from turtle import width
import numpy as np

import pygame
import random

# Couleurs 

WHITE = (255, 255, 255)
RED = (212, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

pygame.init()
window = pygame.display.set_mode((900, 900))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 100)

celerite = 299792458  # m/s aka vitesse de la lumière

counter = 0
counter2 = 0
text = font.render(str(counter), True, (RED))
text2 = font.render(str(counter2), True, (GREEN))

time_delay = 1000
timer_delay_2 = 500
timer_event = pygame.USEREVENT + 1
timer_event2 = pygame.USEREVENT + 2
pygame.time.set_timer(timer_event, time_delay)
pygame.time.set_timer(timer_event2, timer_delay_2)

stars = [(random.randint(0, 900), random.randint(0, 900)) for _ in range(150)]

run = True
while run:
    
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == timer_event:
            counter += 1
            text = font.render(str(counter), True, (RED))
        elif event.type == timer_event2:
            counter2 += 1
            text2 = font.render(str(counter2), True, (GREEN))
            
    window.fill((0, 0, 0))
    #étoils des années 39 - 45
    for star in stars:
        pygame.draw.circle(window, (255, 255, 255), star, 2)

    # afficher le compteur
    text_rect = text.get_rect(center=(text.get_width() // 2, window.get_height() // 2))
    window.blit(text, text_rect)
    #jusqu'a la

    text_rect2 = text2.get_rect(center=(window.get_width() - text2.get_width() // 2, window.get_height() // 2))
    window.blit(text2, text_rect2)
    pygame.display.flip()#flip flop

pygame.quit()#Quitter