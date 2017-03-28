# coding=utf-8
from joueur import *
from pygame.locals import *


@controler_types(dict, object, object, object)
def affichercarte(ent, fenetre, fond, character):
    fenetre.blit(fond, (0, 0))
    for i in ent:
        fenetre.blit(character, (i[0] * 50, i[1] * 50))
    pygame.display.flip()


def affichercombat(ids):
    print(" --------------------")
    temp = demande("combat:entitee:" + str(ids))
    print(temp)
    print(" --------------------")


@controler_types(Joueur, object)
def boucle(joueur, fenetre):
    fond = pygame.image.load("Assets/Image/Monde/Sol1.png").convert()
    fond = pygame.transform.scale(fond, (640, 480))
    character = pygame.image.load("Assets/Image/Classes/Archer/archer4.png")
    character.set_colorkey((255, 255, 255))
    character = character.convert_alpha()
    character = pygame.transform.scale(character, (50, 50))


    while True:
        entitee = joueur.lireentitee()
        affichercarte(entitee, fenetre, fond, character)
        for event in pygame.event.get():
            if event.type == QUIT:
                joueur.quitter()
                yield False
            if event.type == KEYDOWN:
                if event.key == K_w:
                    joueur.move(Direction.HAUT)
                elif event.key == K_d:
                    joueur.move(Direction.DROITE)
                elif event.key == K_s:
                    joueur.move(Direction.BAS)
                elif event.key == K_a:
                    joueur.move(Direction.GAUCHE)
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
