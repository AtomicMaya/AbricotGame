# coding=utf-8


class Forme:
    def position(self, x, y):
        self.x = x
        self.y = y

    def isin(self, x, y):
        return False


class Portee(Forme):
    def __init__(self, distance):
        self.distance = distance

    def isin(self, x, y):
        if abs(x - self.x) + abs(y - self.y) <= self.distance:
            return True
        return False


class Ligne(Forme):
    def __init__(self, longueur):
        self.longueur = longueur

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
    def __init__(self, nom):
        self.listsort = {}
        self.nom = nom

    def addsort(self, sort, ids):
        if ids not in self.listsort:
            self.listsort[ids] = sort
        else:
            raise SyntaxError("Deux sorts ont le meme id : " + self.listsort[ids].nom + " et " + sort.nom)
        return self


listclasse = [Classe("Elementaliste")]
listclasse[0].addsort(Sort("Grele", 10, 10, Portee(5)), 0).addsort(Sort("Geyser", 100, 50, Ligne(6), recharge=1), 1)
