import sys
import math
import random
from turtle import width
import pygame

pygame.init()

window = pygame.display.set_mode((1100, 900))
pygame.display.set_caption('pygame_window')

run = False
while run:
    pygame.time.delay(60)
    print("test")

    for event in pygame.event.get():
        if event.type == pygame.QUIT: #pour quitter le jeu
            run = False

pygame.quit()