import math

def tri(f, x, a=.5):
    p = 1/f
    return ((2*a)/math.pi) * math.asin(math.sin(((2*math.pi)/p)*x))

import pygame

pygame.init()

w = pygame.display.set_mode([400, 400])
c = pygame.time.Clock()

freq = 440

running = True
while running:
    c.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    w.fill((0, 0, 0))
    
    for x in range(400):
        y = (tri(freq, x)*200)+200
        pygame.draw.circle(w, (255, 0, 0), (x, y), 2)
    
    pygame.display.flip()
pygame.quit()
