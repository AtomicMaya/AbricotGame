# coding=utf-8

from entitee import *


class Direction(enum.Enum):
    HAUT = 0
    BAS = 1
    DROITE = 2
    GAUCHE = 3
    CARTE = 4
    ERREUR = 5


class Mouvementresult(enum.Enum):
    ERREUR = 0
    COMBAT = 1
    RIEN = 2


class Carte:
    """Classe représentant une carte et toute les entitee qu'elle contient"""

    @controler_types(object, str)
    def __init__(self, fichier):
        self.entites = {}
        self.joueurs = 0
        self.fichier = fichier
        self.listcombat = []
        with open(fichier) as carte:
            temp = carte.readline()
            while temp[0] == "#":
                temp = carte.readline()
            temp = temp.split(":")
            self.position = (int(temp[0]), int(temp[1]))
            temp = carte.readline()
            while temp[0] == "#":
                temp = carte.readline()
            tempforme = []
            for i in range(10):
                temp = carte.readline()
                while temp[0] == "#":
                    temp = carte.readline()
                temp = temp.replace(" ", "")
                tempforme.append([int(x) for x in temp.split(":")])
        self.forme = []
        for i in range(len(tempforme) - 1, -1, -1):
            self.forme.append(tempforme[i])

    @controler_types(object, Joueur)
    def connexion(self, joueuractif):
        """Permet de rajouter un joueur sur une carte"""
        if joueuractif.position in self.entites.keys():
            self.entites[joueuractif.position].append(joueuractif)
        else:
            self.entites[joueuractif.position] = [joueuractif]
        self.joueurs += 1

    @controler_types(object, Groupeennemi)
    def spawn(self, entiteeactive):
        """Permet de rajouter une entitee sur une carte"""
        if entiteeactive.position in self.entites.keys():
            self.entites[entiteeactive.position].append(entiteeactive)
        else:
            self.entites[entiteeactive.position] = [entiteeactive]

    @controler_types(object, Groupeennemi)
    def despawn(self, entiteeactive):
        self.entites[entiteeactive.position].remove(entiteeactive)

    @controler_types(object, Joueur)
    def deconnexion(self, joueuractif):
        """Permet de retirer un joueur d'une carte"""
        if joueuractif in self.entites.keys():
            self.entites[joueuractif.position].remove(joueuractif)
        self.joueurs -= 1
        if self.joueurs == 0 and len(self.listcombat) == 0:
            return True
        else:
            return False

    def actualiser(self):
        for i in self.listcombat:
            i.actualiser()

    @controler_types(object, Joueur, Direction)
    def move(self, joueur, directionmouvement):
        """Permet de deplacer un joueur sur une carte"""
        if directionmouvement == Direction.DROITE:
            cible = (joueur.position[0] + 1, joueur.position[1])
        elif directionmouvement == Direction.GAUCHE:
            cible = (joueur.position[0] - 1, joueur.position[1])
        elif directionmouvement == Direction.BAS:
            cible = (joueur.position[0], joueur.position[1] - 1)
        elif directionmouvement == Direction.HAUT:
            cible = (joueur.position[0], joueur.position[1] + 1)
        else:
            cible = joueur.position

        if self.forme[cible[1]][cible[0]] == 0:
            self.entites[joueur.position].remove(joueur)
            joueur.position = cible
            if joueur.position in self.entites.keys():
                ennemis = [x for x in self.entites[joueur.position] if type(x) == Groupeennemi]

                if len(ennemis) > 0:
                    if not ennemis[0].combat:
                        self.listcombat.append(Combat(self, ennemis[0]))
                    ennemis[0].combat.connect(joueur)
                    self.deconnexion(joueur)
                    joueur.etat = Etatjoueur.combat
                    return Mouvementresult.COMBAT
                else:
                    self.entites[joueur.position].append(joueur)
            else:
                self.entites[joueur.position] = [joueur]
            return Mouvementresult.RIEN
        else:
            return Mouvementresult.ERREUR


class Combat:
    @controler_types(object, Carte, Groupeennemi)
    def __init__(self, carte, ennemis):
        self.ennemis = ennemis
        ennemis.combat = self
        self.spawn = []
        self.ennemisspawn = []
        self.joueurs = {}
        self.carte = carte
        self.actif = False
        with open(carte.fichier) as fichier:
            for i in range(12):
                temp = fichier.readline()
                while temp[0] == "#":
                    temp = fichier.readline()
            tempforme = []
            for i in range(10):
                temp = fichier.readline()
                while temp[0] == "#":
                    temp = fichier.readline()
                temp = temp.replace(" ", "")
                for j in range(10):
                    tempcases = [int(x) for x in temp.split(":")]
                    for k in tempcases:
                        if k == 2:
                            self.spawn.append((i, j))
                        elif k == 3:
                            self.ennemisspawn.append((i, j))
                tempforme.append(temp)
        self.forme = []
        for i in range(len(tempforme) - 1, -1, -1):
            self.forme.append(tempforme[i])
        for i in range(len(ennemis.ennemis)):
            ennemis.ennemis[i].position = self.ennemisspawn[i]

    def start(self):
        j = True
        for i in self.joueurs.values():
            j = i and j
        if j:
            self.actif = True
            self.carte.despawn(self.ennemis)

    @controler_types(object, Joueur)
    def connect(self, joueur):
        self.joueurs[joueur] = False
        joueur.combat = self
        if len(self.joueurs) > 3:
            for i in self.joueurs:
                self.joueurs[i] = True
            self.start()
            return True
        return False

    def actualiser(self):
        pass
        """print("Go", self)"""

    def afficher(self):
        resultat = ""
        if self.actif:
            for i in self.joueurs:
                resultat += ("J:" + str(i.id) + ":" + str(i.position[0]) + ":" + str(i.position[1]) + ":")
            for i in self.ennemis.ennemis:
                resultat += ("E:" + str(i.nom) + ":" + str(i.position[0]) + ":" + str(i.position[1]) + ":")
        else:
            for i in self.joueurs:
                resultat += (str(i.id) + ":" + str(self.joueurs[i]) + "\n")
            for i in self.ennemis.ennemis:
                resultat += (i.nom + ":" + str(i.niveau) + "\n")
        return resultat[0:len(resultat) - 1]
