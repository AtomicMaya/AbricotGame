# coding=utf-8
import time
from joueur import *
from pygame.locals import *


@controler_types(dict, object)
def affichercarte(ent, fenetre):
    fond = pygame.image.load("Assets/Image/Monde/Sol1.png").convert()
    fond = pygame.transform.scale(fond, (640, 480))
    character = pygame.image.load("Assets/Image/Classes/Archer/archer4.png")
    character.set_colorkey((255, 255, 255))
    character = character.convert_alpha()
    character = pygame.transform.scale(character, (50, 50))
    fenetre.blit(fond, (0, 0))
    for i in ent:
        fenetre.blit(character, (i[0] * 50, i[1] * 50))
    case = createimage("Assets/Image/Monde/block_grille.png")
    for i in range(10):
        for j in range(10):
            fenetre.blit(case, (i*50,j*50))
    pygame.display.flip()
"""
case_x = mouse_x // ((fond_x)*0.8)/20
case_y = mouse_y // ((fond_y)*0.8)/15
"""

def affichercombat(ids):
    print(" --------------------")
    temp = demande("combat:entitee:" + str(ids))
    print(temp)
    print(" --------------------")


@controler_types(Joueur, object)
def boucle(joueur, fenetre):
    chemin=[]
    time_actuel=time.time()
    while True:
        entitee = joueur.lireentitee()
        affichercarte(entitee, fenetre)
        if (time.time()>time_actuel+0.5) and len(chemin)!=0:
            joueur.move(chemin[0])
            del chemin[0]
            time_actuel=time.time()
        for event in pygame.event.get():
            if event.type == QUIT:
                joueur.quitter()
                yield False
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    joueur.move(Direction.HAUT)
                elif event.key == K_RIGHT:
                    joueur.move(Direction.DROITE)
                elif event.key == K_DOWN:
                    joueur.move(Direction.BAS)
                elif event.key == K_LEFT:
                    joueur.move(Direction.GAUCHE)
            if event.type == MOUSEBUTTONDOWN:
                chemin = joueur.moveto(event.pos[0]//50,event.pos[1]//50)
        """
        elif temp[0] == "move":
            tempchemin = joueur.moveto(int(temp[1]), int(temp[2]))
            del tempchemin[0]
        elif len(tempchemin) != 0:
            joueur.move(tempchemin[0])
            del tempchemin[0]
        """
        yield True


def combat(joueur):
    affichercombat(joueur.id)
    temp = input("> ")
    temp = temp.split(":")
    if temp[0] == "w" or temp[0] == "z":
        joueur.move(Direction.HAUT)
    elif temp[0] == "d":
        joueur.move(Direction.DROITE)
    elif temp[0] == "s":
        joueur.move(Direction.BAS)
    elif temp[0] == "a" or temp[0] == "q":
        joueur.move(Direction.GAUCHE)
    elif temp[0] == "sort":
        joueur.sort(int(temp[1]), int(temp[2], int(temp[3])))


def preparationcombat(joueur):
    temp = input("> ")
    temp = temp.split(":")
    if temp[0] == "start":
        joueur.start()
    affichercombat(joueur.id)


def main():
    pygame.init()
    joueur = Joueur()
    actif = True
    fenetre = pygame.display.set_mode((640, 480))
    principale = boucle(joueur, fenetre)
    while actif:
        if joueur.etat == Etat.NORMAL:
            actif = next(principale)
        elif joueur.etat == Etat.COMBAT:
            combat(joueur)
        elif joueur.etat == Etat.PREPARATIONCOMBAT:
            preparationcombat(joueur)
        pygame.time.Clock().tick(30)


main()
