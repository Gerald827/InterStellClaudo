import pygame
import random

pygame.init()
window = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 100)

counter = 0
text = font.render(str(counter), True, (0, 255, 0))

time_delay = 1000
timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(timer_event, time_delay)

stars = [(random.randint(0, 800), random.randint(0, 800)) for _ in range(150)]

run = True
while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == timer_event:
            counter += 1
            text = font.render(str(counter), True, (212,0 , 0))

    # fond noir
    window.fill((0, 0, 0))

    for star in stars:
        pygame.draw.circle(window, (255, 255, 255), star, 2)

    # afficher le compteur
    text_rect = text.get_rect(center=window.get_rect().center)
    window.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()