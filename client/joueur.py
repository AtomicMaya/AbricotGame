# coding=utf-8

import enum
from client.controlleur import *
from client.tempserv import *
from client.classes import *


class Direction(enum.Enum):
    HAUT = 0
    BAS = 1
    DROITE = 2
    GAUCHE = 3


class Etat(enum.Enum):
    COMBAT = 0
    PREPARATIONCOMBAT = 1
    NORMAL = 2


class Chemin:
    @controler_types(object, int, int, list)
    def __init__(self, x, y, mouvements):
        self.actuel = (x, y)
        self.mouvement = mouvements


@controler_types(list, int, int, int, int)
def findchemin(grille, xactuel, yactuel, xcible, ycible):
    """Methode servant a trouver le plus court chemin entre deux points"""
    casesvisitee = [(xactuel, yactuel)]

    chemins = [Chemin(xactuel, yactuel, [])]

    resultat = chemins[0]

    if resultat.actuel == (xcible, ycible):
        resultat.mouvement = [-1]
    else:
        for i in chemins:
            tempx = i.actuel[0] + 1
            tempy = i.actuel[1]
            if -1 < tempx < 10 and -1 < tempy < 10:
                if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                    nouvmouvement = list(i.mouvement)
                    nouvmouvement.append(Direction.HAUT)
                    resultat = Chemin(tempx, tempy, nouvmouvement)
                    chemins.append(resultat)
                    casesvisitee.append((tempx, tempy))
                    if resultat.actuel == (xcible, ycible):
                        break
            tempx = i.actuel[0] - 1
            tempy = i.actuel[1]
            if -1 < tempx < 10 and -1 < tempy < 10:
                if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                    nouvmouvement = list(i.mouvement)
                    nouvmouvement.append(Direction.BAS)
                    resultat = Chemin(tempx, tempy, nouvmouvement)
                    chemins.append(resultat)
                    casesvisitee.append((tempx, tempy))
                    if resultat.actuel == (xcible, ycible):
                        break
            tempx = i.actuel[0]
            tempy = i.actuel[1] + 1
            if -1 < tempx < 10 and -1 < tempy < 10:
                if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                    nouvmouvement = list(i.mouvement)
                    nouvmouvement.append(Direction.DROITE)
                    resultat = Chemin(tempx, tempy, nouvmouvement)
                    chemins.append(resultat)
                    casesvisitee.append((tempx, tempy))
                    if resultat.actuel == (xcible, ycible):
                        break
            tempx = i.actuel[0]
            tempy = i.actuel[1] - 1
            if -1 < tempx < 10 and -1 < tempy < 10:
                if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                    nouvmouvement = list(i.mouvement)
                    nouvmouvement.append(Direction.GAUCHE)
                    resultat = Chemin(tempx, tempy, nouvmouvement)
                    chemins.append(resultat)
                    casesvisitee.append((tempx, tempy))
                    if resultat.actuel == (xcible, ycible):
                        break

    return resultat.mouvement


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


class Joueur:
    def __init__(self):
        self.carte = _carte()
        self.position = _position()
        self.id = _id()
        self.forme = _forme(self.carte)
        self.classe = _classes()
        self.etat = Etat.NORMAL

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

        if -1 < ciblex < 10 and -1 < cibley < 10:
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
                self.position = (9, cibley)

            elif direction == Direction.HAUT:
                self.carte = (self.carte[0], self.carte[1] + 1)
                self.position = (ciblex, 0)

            elif direction == Direction.BAS:
                self.carte = (self.carte[0], self.carte[1] - 1)
                self.position = (ciblex, 9)
            self.forme = _forme(self.carte)

    def quitter(self):
        commande("carte:quitter:" + str(self.id))

    @controler_types(object, int, int)
    def moveto(self, x, y):
        if self.forme[y][x] == 0:
            temp = findchemin(self.forme, self.position[0], self.position[1], x, y)
            self.move(temp[0])
        else:
            temp = []
        return temp

    def start(self):
        commande("combat:start:" + str(self.id))
        self.etat == Etat.COMBAT
