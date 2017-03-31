# coding=utf-8
import time
from joueur import *
from pygame.locals import *


@controler_types(dict, object)
def affichercarte(ent, fenetre):
    fond = pygame.image.load("Assets/Image/Monde/Sol1.png").convert()
    fond = pygame.transform.scale(fond, (640, 480))
    character = createimage("Assets/Image/Classes/Archer/archer4.png")
    character = pygame.transform.scale(character, (50, 50))
    fenetre.blit(fond, (0, 0))
    enm = createimage("Assets/Image/Classes/Démoniste/démo3.png", (129, 139, 139))
    enm = pygame.transform.scale(enm, (50, 50))
    for i in ent:
        if ent[i] == "J":
            fenetre.blit(character, (i[0] * 50, i[1] * 50))
        else:
            fenetre.blit(enm, (i[0] * 50, i[1] * 50))
    for i in range(10):
        for j in range(10):
            pygame.draw.rect(fenetre, (0, 0, 0), (i * 50, j * 50, 51, 51), 1)
    pygame.display.flip()


"""
case_x = mouse_x // ((fond_x)*0.8)/20
case_y = mouse_y // ((fond_y)*0.8)/15
"""


def affichercombat(fenetre):
    fenetre.blit(createimage("Assets/Image/UI/start.png"), (50, 50))
    pygame.display.flip()


@controler_types(Joueur, object)
def boucle(joueur, fenetre):
    chemin = []
    time_actuel = time.time()
    while True:
        entitee = joueur.lireentitee()
        affichercarte(entitee, fenetre)
        if (time.time() > time_actuel + 0.5) and len(chemin) != 0:
            joueur.move(chemin[0])
            del chemin[0]
            time_actuel = time.time()
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
                chemin = joueur.moveto(event.pos[0] // 50, event.pos[1] // 50)
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


def preparationcombat(joueur, fenetre):
    for event in pygame.event.get():
        if event.type == QUIT:
            joueur.quitter()
            return False
        if event.type==KEYDOWN:
            if 50<event.pos[0]<150 and 50<event.pos[1]<100:
                joueur.start()
    affichercombat(fenetre)
    return True


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
            actif = preparationcombat(joueur, fenetre)
        pygame.time.Clock().tick(30)


main()
