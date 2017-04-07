import pygame
from pygame.locals import *
import os
import time
from random import *

pygame.init()
fenetre = pygame.display.set_mode((640, 480))
chemimages=[]
images=[]
intervalle=0.1
for element in os.listdir("./images"):
    if not os.path.isdir(element):
        chemimages.append(element)
images = [""] * len(chemimages)
for i in chemimages:
    temp=pygame.image.load("images/"+i)
    temp.set_colorkey((255,255,255))
    images[int(i[i.find('_')+1:i.find('.')])-1] = temp.convert_alpha()
del chemimages
indice=0
continuer = 1
pos = (10,10)

while continuer:
    pygame.time.Clock().tick(6)
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = 0
    fenetre.fill((0,0,0))
    fenetre.blit(images[indice], pos)
    pygame.display.flip()
    indice+=1
    if indice>=len(images):
        indice=0
        pos = (randint(0,600),randint(0,450))

pygame.quit()
