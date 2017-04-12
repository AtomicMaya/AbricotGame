# coding=utf-8
import time
from joueur import *
from pygame.locals import *


@controler_types(dict, object, tuple)
def affichercarte(ent, affichage, taille):
    fenetre = affichage[1]
    fond = pygame.image.load("Assets/Image/Monde/Sol1.png").convert()
    fond = pygame.transform.scale(fond, (1000, 725))
    character = createimage("Assets/Image/Classes/Archer/archer4.png")
    character = pygame.transform.scale(character, (50, 50))
    fenetre.blit(fond, (100, 0))
    enm = createimage("Assets/Image/Classes/Demoniste/demo3.png")
    # enm = pygame.transform.scale(enm, (50, 50))
    for i in ent:
        if ent[i] == "J":
            fenetre.blit(character, (i[0] * 50 + 100, i[1] * 50))
        else:
            fenetre.blit(enm, (i[0] * 50 + 10 + 100, i[1] * 50))
    for i in range(20):
        for j in range(15):
            pygame.draw.rect(fenetre, (0, 0, 0), (i * 50 + 100, j * 50, 51, 51), 1)
    affichage[0].blit(pygame.transform.scale(fenetre, taille), (0, 0))
    pygame.display.flip()


def affichercombat(fenetre):
    fenetre.blit(createimage("Assets/Image/UI/start.png"), (50, 50))
    pygame.display.flip()


@controler_types(Joueur, object, tuple)
def boucle(joueur, fenetre, taille_fenetre):
    chemin = []
    time_actuel = time.time()
    while True:
        entitee = joueur.lireentitee()
        affichercarte(entitee, fenetre, taille_fenetre)
        if (time.time() > time_actuel + 0) and len(chemin) != 0:
            joueur.move(chemin[0])
            del chemin[0]
            time_actuel = time.time()
        for event in pygame.event.get():
            if event.type == QUIT:
                joueur.quitter()
                yield False
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    joueur.move(Direction.HAUT)
                elif event.key == K_RIGHT:
                    joueur.move(Direction.DROITE)
                elif event.key == K_DOWN:
                    joueur.move(Direction.BAS)
                elif event.key == K_LEFT:
                    joueur.move(Direction.GAUCHE)
            elif event.type == MOUSEBUTTONDOWN:
                event.pos = (event.pos[0] - 100)*taille_fenetre[0]/1280, event.pos[1]*taille_fenetre[1]/800
                if event.pos[0] // 50 < 20 and event.pos[1] // 50 < 15:
                    chemin = joueur.moveto(int(event.pos[0] // 50), int(event.pos[1] // 50))
            elif event.type == VIDEORESIZE:
                taille_fenetre = (event.w, event.h)
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
        if event.type == MOUSEBUTTONDOWN:
            if 50 < event.pos[0] < 150 and 50 < event.pos[1] < 100:
                joueur.start()
    affichercombat(fenetre)
    return True


def main():
    pygame.init()
    joueur = Joueur()
    actif = True
    fenetre = pygame.display.set_mode((1200, 800), RESIZABLE)
    image = pygame.Surface((1280, 720))
    pygame.display.set_icon(
        pygame.transform.scale(pygame.image.load("Assets/Image/UI/icone.png").convert_alpha(), (30, 30)))
    pygame.display.set_caption("Abricot game")
    principale = boucle(joueur, (fenetre, image), fenetre.get_size())
    while actif:
        if joueur.etat == Etat.NORMAL:
            actif = next(principale)
        elif joueur.etat == Etat.COMBAT:
            combat(joueur)
        elif joueur.etat == Etat.PREPARATIONCOMBAT:
            actif = preparationcombat(joueur, fenetre)
        pygame.time.Clock().tick(60)


main()
pygame.quit()
