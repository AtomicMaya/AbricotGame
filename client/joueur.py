# coding=utf-8
from tempserv import *
from classes import *
from chemin import *
import pygame


class Etat(enum.Enum):
    COMBAT = 0
    PREPARATIONCOMBAT = 1
    NORMAL = 2


class EtatLectureEnnemis(enum.Enum):
    NEUTRE = 0
    JOUEUR = 1
    ENNEMI = 2
    STOP = 3


@controler_types(str)
def tolist(string):
    string = string[1:len(string) - 2]
    string = string.replace(" ", "")
    string = string.replace("[", "")
    string = string.replace("],", "]")
    string = string.split("]")
    resultat = []
    for element in string:
        element = element.split(",")
        temp = []
        for i in element:
            temp.append(int(i))
        resultat.append(temp)
    return resultat


def _carte():
    return 0, 0


def _position():
    return 5, 5


def _id():
    return int(demande("carte:connect"))


def _classes():
    return listclasse[0]


@controler_types(tuple)
def _forme(carte):
    return tolist(demande("carte:carte:" + str(carte[0]) + ":" + str(carte[1])))


def createimage(chemin, couleurfond=(255, 255, 255)):
    chemin = pygame.image.load(chemin)
    chemin.set_colorkey(couleurfond)
    return chemin.convert_alpha()


class Joueur:
    def __init__(self):
        self.carte = _carte()
        self.position = _position()
        self.id = _id()
        self.forme = _forme(self.carte)
        self.classe = _classes()
        self.etat = Etat.NORMAL

    @controler_types(object, int, int, int)
    def sort(self, ids, x, y):
        if True:
            demande("combat:sort:" + str(self.id) + ":" + str(ids) + ":" + str(x) + ":" + str(y))

    @controler_types(object, Direction)
    def move(self, direction):

        if direction == Direction.DROITE:
            ciblex = self.position[0] + 1
            cibley = self.position[1]
            direct = ":right"

        elif direction == Direction.GAUCHE:
            cibley = self.position[1]
            ciblex = self.position[0] - 1
            direct = ":left"

        elif direction == Direction.HAUT:
            ciblex = self.position[0]
            cibley = self.position[1] + 1
            direct = ":up"

        elif direction == Direction.BAS:
            ciblex = self.position[0]
            cibley = self.position[1] - 1
            direct = ":down"
        else:
            ciblex = self.position[0]
            cibley = self.position[1]
            direct = ":nul"

        if -1 < ciblex < 20 and -1 < cibley < 15:
            if self.forme[cibley][ciblex] == 0:
                tempmove = demande("carte:move:" + str(self.id) + direct)
                if tempmove == "True":
                    self.position = (ciblex, cibley)
                elif tempmove == "Combat":
                    self.position = (ciblex, cibley)
                    self.etat = Etat.PREPARATIONCOMBAT
        else:
            demande("carte:move:" + str(self.id) + direct)
            if direction == Direction.DROITE:
                self.carte = (self.carte[0] + 1, self.carte[1])
                self.position = (0, cibley)

            elif direction == Direction.GAUCHE:
                self.carte = (self.carte[0] - 1, self.carte[1])
                self.position = (19, cibley)

            elif direction == Direction.HAUT:
                self.carte = (self.carte[0], self.carte[1] + 1)
                self.position = (ciblex, 0)

            elif direction == Direction.BAS:
                self.carte = (self.carte[0], self.carte[1] - 1)
                self.position = (ciblex, 14)
            self.forme = _forme(self.carte)

    def quitter(self):
        commande("carte:quitter:" + str(self.id))

    @controler_types(object, int, int)
    def moveto(self, x, y):
        if self.forme[y][x] == 0:
            temp = findchemin(self.forme, self.position[0], self.position[1], x, y)
        else:
            temp = []
        return temp

    def start(self):
        self.etat == Etat.COMBAT
        commande("combat:start:" + str(self.id))

    def lireentitee(self):
        temp = demande("carte:entitee:" + str(self.carte[0]) + ":" + str(self.carte[1]))
        temp = temp.split(":")
        etat = EtatLectureEnnemis.NEUTRE
        indice = 0
        tempentitee = {}
        tempennemi = {}
        tempintentitee = 4
        while indice < len(temp):
            i = temp[indice]
            if etat == EtatLectureEnnemis.NEUTRE:
                if i == "J":
                    etat = EtatLectureEnnemis.JOUEUR
                elif i == "G":
                    etat = EtatLectureEnnemis.ENNEMI
                else:
                    break
                indice += 1
            elif etat == EtatLectureEnnemis.JOUEUR:
                tempentitee[(int(temp[indice + 1]), int(temp[indice + 2]))] = "J"
                indice += 3
                etat = EtatLectureEnnemis.NEUTRE
            elif etat == EtatLectureEnnemis.ENNEMI:
                tempentitee[(int(temp[indice]), int(temp[indice + 1]))] = "E"
                tempindice = indice + 3
                tempstr = ""
                for j in range(int(temp[indice + 2])):
                    tempstr += (temp[tempindice] + " niveau : " + temp[tempindice + 1] + " | ")
                    tempindice += 2
                tempennemi[tempintentitee] = tempstr
                indice = tempindice
                tempintentitee += 1
                etat = EtatLectureEnnemis.NEUTRE
        return tempentitee
