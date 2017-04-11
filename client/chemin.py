# coding=utf-8
from controlleur import controler_types
import enum


class Direction(enum.Enum):
    HAUT = 0
    BAS = 1
    DROITE = 2
    GAUCHE = 3


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
    if chemins[0].actuel == (xcible, ycible):
        return []
    resultat = chemins[0]

    for i in chemins:
        tempx = i.actuel[0] + 1
        tempy = i.actuel[1]
        if -1 < tempx < 20 and -1 < tempy < 15:
            if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                nouvmouvement = list(i.mouvement)
                nouvmouvement.append(Direction.DROITE)
                resultat = Chemin(tempx, tempy, nouvmouvement)
                chemins.append(resultat)
                casesvisitee.append((tempx, tempy))
                if resultat.actuel == (xcible, ycible):
                    break
        tempx = i.actuel[0] - 1
        tempy = i.actuel[1]
        if -1 < tempx < 20 and -1 < tempy < 15:
            if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                nouvmouvement = list(i.mouvement)
                nouvmouvement.append(Direction.GAUCHE)
                resultat = Chemin(tempx, tempy, nouvmouvement)
                chemins.append(resultat)
                casesvisitee.append((tempx, tempy))
                if resultat.actuel == (xcible, ycible):
                    break
        tempx = i.actuel[0]
        tempy = i.actuel[1] + 1
        if -1 < tempx < 20 and -1 < tempy < 15:
            if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                nouvmouvement = list(i.mouvement)
                nouvmouvement.append(Direction.HAUT)
                resultat = Chemin(tempx, tempy, nouvmouvement)
                chemins.append(resultat)
                casesvisitee.append((tempx, tempy))
                if resultat.actuel == (xcible, ycible):
                    break
        tempx = i.actuel[0]
        tempy = i.actuel[1] - 1
        if -1 < tempx < 20 and -1 < tempy < 15:
            if (tempx, tempy) not in casesvisitee and grille[tempy][tempx] == 0:
                nouvmouvement = list(i.mouvement)
                nouvmouvement.append(Direction.BAS)
                resultat = Chemin(tempx, tempy, nouvmouvement)
                chemins.append(resultat)
                casesvisitee.append((tempx, tempy))
                if resultat.actuel == (xcible, ycible):
                    break

    return resultat.mouvement
