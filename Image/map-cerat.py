import pygame
from pygame.locals import *
import json

dim = (18, 32)
l = []
for i in range(dim[0]):
    temp = [0]*dim[1]
    l.append(temp)

window = pygame.display.set_mode((1280, 720))
dx = dy = 40
fond = pygame.image.load(input("local map file : ")).convert()
fond = pygame.transform.scale(fond, (1280, 720))

continueP = True

while continueP:
    pygame.time.Clock().tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            continueP = False
        elif event.type == MOUSEBUTTONDOWN:
            x, y = event.pos[0]//40, event.pos[1]//40
            if event.button == 1:
                l[y][x] += 1
            elif event.button == 3:
                l[y][x] -= 1

    window.blit(fond, (0, 0))
    for i in range(dim[0]):
        for j in range(dim[1]):
            pygame.draw.rect(window, (0, 0, 0), (j*dy, i*dy, 40, 40), 1)
            if l[i][j] == 1:
                pygame.draw.circle(window, (255, 0, 0), (j*dy+dy//2, i*dx+dx//2), dx//2, 2)
            if l[i][j] == 2:
                pygame.draw.circle(window, (0, 0, 255), (j*dy+dy//2, i*dx+dx//2), dx//2, 2)
    pygame.display.flip()

s = json.dumps(l)
with open(input("File name :"), "w") as file:
    file.write(s)

pygame.quit()
                
    
