# coding=utf-8

from controlleur import controler_types
import enum


class Etatjoueur(enum.Enum):
    normal = 0
    combat = 1


class EntiteeCarte:
    """Classe a ne pas utiliser represantant une entitee (joueur ou enemi)"""

    def __init__(self):
        self.position = (5, 5)
        self.carte = (0, 0)
        self.combat = None


class EntiteeCombat(EntiteeCarte):
    def __init__(self):
        super().__init__()
        self._vie = 500

    def mort(self):
        print("mort")

    def _getvie(self):
        return self._vie

    def _setvie(self, new):
        self._vie = new
        if new <= 0:
            self.mort()

    vie = property(_getvie, _setvie)


class Joueur(EntiteeCombat):
    """Classe represantant un joueur sur une carte"""

    @controler_types(object, int)
    def __init__(self, idd):
        super().__init__()
        self.id = idd
        self.etat = Etatjoueur.normal


class Ennemi(EntiteeCombat):
    """Classe represantatn un ennemi controller par le serveur"""

    @controler_types(object, str, int)
    def __init__(self, nom, niveau):
        super().__init__()
        self.nom = nom
        self.niveau = niveau
        self.position = None


class Groupeennemi(EntiteeCarte):
    def __init__(self, x, y, *listeennemis):
        super().__init__()
        self.position = (x, y)
        self.ennemis = list(listeennemis)
