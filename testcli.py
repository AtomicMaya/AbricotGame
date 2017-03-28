# coding=utf-8
import client.tempserv
from client.joueur import *
import pygame
from pygame.locals import *


@controler_types(dict, dict, object, object,object)
def affichercarte(ent, enm, fenetre, fond,character):
    fenetre.blit(fond, (0, 0))
    for i in ent:
        fenetre.blit(character, (i[0]*50,i[1]*50))
    fenetre.blit(character,0,0)
    pygame.display.flip()
    """print(" --------------------")
    for y in range(len(joueur.forme) - 1, -1, -1):
        print("|", end="")
        for x in range(len(joueur.forme[y])):
            if x == joueur.position[0] and y == joueur.position[1]:
                print("2", end=" ")
            elif (x, y) in ent:
                print(ent[(x, y)], end=" ")
            else:
                print(joueur.forme[y][x], end=" ")
        print("|", end="")

        tempint = len(joueur.forme) - y - 1
        if tempint in enm:
            print("    " + str(tempint) + " > " + enm[len(joueur.forme) - y - 1])
        else:
            print()
    print(" --------------------")"""


def affichercombat(ids):
    print(" --------------------")
    temp = client.tempserv.demande("combat:entitee:" + str(ids))
    print(temp)
    print(" --------------------")


class Etat_lecture_ennemis(enum.Enum):
    NEUTRE = 0
    JOUEUR = 1
    ENNEMI = 2
    STOP = 3


@controler_types(Joueur)
def lireentitee(joueur):
    temp = client.tempserv.demande("carte:entitee:" + str(joueur.carte[0]) + ":" + str(joueur.carte[1]))
    temp = temp.split(":")
    etat = Etat_lecture_ennemis.NEUTRE
    indice = 0
    tempentitee = {}
    tempennemi = {}
    tempintentitee = 4
    while indice < len(temp):
        i = temp[indice]
        if etat == Etat_lecture_ennemis.NEUTRE:
            if i == "J":
                etat = Etat_lecture_ennemis.JOUEUR
            elif i == "G":
                etat = Etat_lecture_ennemis.ENNEMI
            else:
                break
            indice += 1
        elif etat == Etat_lecture_ennemis.JOUEUR:
            if not (i == joueur.id):
                tempentitee[(int(temp[indice + 1]), int(temp[indice + 2]))] = 3
            indice += 3
            etat = Etat_lecture_ennemis.NEUTRE
        elif etat == Etat_lecture_ennemis.ENNEMI:
            tempentitee[(int(temp[indice]), int(temp[indice + 1]))] = tempintentitee
            tempindice = indice + 3
            tempstr = ""
            for j in range(int(temp[indice + 2])):
                tempstr += (temp[tempindice] + " niveau : " + temp[tempindice + 1] + " | ")
                tempindice += 2
            tempennemi[tempintentitee] = tempstr
            indice = tempindice
            tempintentitee += 1
            etat = Etat_lecture_ennemis.NEUTRE
    return tempentitee, tempennemi


@controler_types(Joueur)
def boucle(joueur):
    fenetre = pygame.display.set_mode((640, 480))
    fond = pygame.image.load("Assets/Image/Monde/sol1.png").convert()  # Chargement et collage du fond
    fond = pygame.transform.scale(fond, (640, 480))

    character = pygame.image.load("Assets/Image/Classes/Archer/archer4.png")
    character.set_colorkey((255, 255, 255))
    character = character.convert_alpha()
    character = pygame.transform.scale(character, (50, 50))
    tempchemin = []
    while True:
        entitee, ennemis = lireentitee(joueur)
        affichercarte(entitee, ennemis, fenetre, fond,character)
        for event in pygame.event.get():
            if event.type == QUIT:
                joueur.quitter()
                yield False
        temp = "rien"
        temp = temp.split(":")
        if temp[0] == "w":
            joueur.move(Direction.HAUT)
            tempchemin = []
        elif temp[0] == "d":
            joueur.move(Direction.DROITE)
            tempchemin = []
        elif temp[0] == "s":
            joueur.move(Direction.BAS)
            tempchemin = []
        elif temp[0] == "a":
            joueur.move(Direction.GAUCHE)
            tempchemin = []
        elif temp[0] == "move":
            tempchemin = joueur.moveto(int(temp[1]), int(temp[2]))
            del tempchemin[0]
        elif len(tempchemin) != 0:
            joueur.move(tempchemin[0])
            del tempchemin[0]
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
    principale = boucle(joueur)
    while actif:
        if joueur.etat == Etat.NORMAL:
            actif = next(principale)
        elif joueur.etat == Etat.COMBAT:
            combat(joueur)
        elif joueur.etat == Etat.PREPARATIONCOMBAT:
            preparationcombat(joueur)
        pygame.time.Clock().tick(30)


def image_character(character):
    perso = pygame.image.load(character)
    perso.set_colorkey((255, 255, 255))
    return perso.convert_alpha()


main()
