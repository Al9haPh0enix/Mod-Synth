import pygame

pygame.init()

w = pygame.display.set_mode([400, 400])
c = pygame.time.Clock()

window = pygame.Rect(100, 100, 200, 200)

inputNodes = 3
outputNodes = 3

running = True
while running:
    c.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    w.fill((0, 0, 0))
    
    pygame.draw.rect(w, (127, 127, 127), window)

    for i in range(inputNodes):
        i += 1
        percentageDown = (i/inputNodes)
        y = (window.y + (percentageDown*window.height))

        pygame.draw.circle(w, (255, 0, 0), (window.x, y), 3)
    
    pygame.display.flip()
pygame.quit()
