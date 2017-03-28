# coding=utf-8
from controlleur import *


class AbstractClassError(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return ""


class Forme:
    def __init__(self):
        raise AbstractClassError()

    @controler_types(object,int,int)
    def position(self, x, y):
        self.x = x
        self.y = y

    def isin(self, x, y):
        raise AbstractClassError()


class Portee(Forme):
    def __init__(self, distancemax, distancemin=0):
        self.distancemax = distancemax
        self.distancemin = distancemin

    @controler_types(object, int, int)
    def isin(self, x, y):
        if self.distancemin <= abs(x - self.x) + abs(y - self.y) <= self.distancemax:
            return True
        return False


class Ligne(Forme):
    @controler_types(object, int)
    def __init__(self, longueur):
        self.longueur = longueur

    @controler_types(object, int, int)
    def isin(self, x, y):
        if (((x == self.x) and (abs(self.y - y) < self.longueur)) or (
                    (y == self.y) and (abs(self.x - x) < self.longueur))):
            return True
        return False


class Sort:
    def __init__(self, nom, degats, cout, forme, recharge=0):
        self.nom = nom
        self.degats = degats
        self.cout = cout
        self.recharge = recharge
        self.forme = forme


class Classe:
    @controler_types(object, str)
    def __init__(self, nom):
        self.listsort = {}
        self.nom = nom

    @controler_types(object, Sort, int)
    def addsort(self, sort, ids):
        if ids not in self.listsort:
            self.listsort[ids] = sort
        else:
            raise SyntaxError("Deux sorts ont le meme id : " + self.listsort[ids].nom + " et " + sort.nom)
        return self


listclasse = [Classe("Elementaliste")]
listclasse[0].addsort(Sort("Grele", 10, 10, Portee(5)), 0).addsort(Sort("Geyser", 100, 50, Ligne(6), recharge=1), 1)
