# coding=utf-8
"""Ce fichier contient le code principal du client"""
import pygame
from pygame.locals import *
import socket
from json import loads, load


class Map:
    """Cette classe représente une carte du jeu"""

    def __init__(self, data):
        self.mobs = data["MOBS"]
        self.semiobs = []
        self.fullobs = []
        self.free = []
        for y in range(len(data["MAP"])):
            for x in range(len(data["MAP"][y])):
                if data["MAP"][y][x] == 1:
                    self.fullobs.append((x, y))
                elif data["MAP"][y][x] == 2:
                    self.semiobs.append((x, y))
                else:
                    self.free.append((x, y))
        self.obstacles = self.semiobs + self.fullobs


class Maps:
    """Cette classe contient la liste de toute les cartes du jeu"""

    def __init__(self):
        json_file = open("assets/cartes/maps.json")
        file_maps = load(json_file)
        json_file.close()
        self.maps = {}
        for ids in file_maps:
            if ids != '_template':
                self.maps[eval(ids)] = Map(file_maps[ids])

    def get(self, map_id: str):
        """Cette fonction permet de recupere une carte en fonction de son id"""
        return self.maps[map_id]


MAPS = Maps()


class Playercontroller:
    """Cette classe contient toute les informations liée au joueur"""

    def __init__(self, fenetre):
        self.id = demande("carte:connect")
        self.carte_id = 0
        self.carte_mobs = []
        self.carte_joueurs = []
        self.changement_carte(fenetre)

    def changement_carte(self, fenetre):
        """Cette fonction est appellée quand le joueur change de carte et sert a charger les nouvelles textures et la
        forme de la carte"""
        resultat = loads(demande("carte:carte:" + str(self.id)))
        self.carte_id = eval(resultat["map"])
        self.carte_mobs = []
        for i in resultat["mobs"]:
            for j in i:
                self.carte_mobs.append((j[0], (j[1][0], j[1][1])))
        self.carte_joueurs = []
        for i in resultat["joueurs"]:
            self.carte_joueurs.append((i["classe"], i["position"], i["name"]))
        fenetre.charger_textures(self)


class RendererController:
    """Cette classe contient toute les méthodes liée a l'affichage et au stokage des textures"""

    def __init__(self):
        self.fenetre = pygame.display.set_mode((640, 480))
        self.fond = None
        self.textures_mobs = {}
        self.textures_classes = {"001": pygame.image.load("assets/images/classes/archer/archer1.png").convert()}

    def charger_textures(self, joueur):
        """Cette méthode est appellée lors d'un changement de map pour charger les textures de la nouvelle map"""
        self.fond = pygame.image.load(
            "assets/images/maps/" + str(joueur.carte_id[0]) + "." + str(joueur.carte_id[1]) + ".png").convert()
        self.fond = pygame.transform.scale(self.fond, (640, 480))
        self.textures_mobs = {}
        for mob in MAPS.get(joueur.carte_id).mobs:
            self.textures_mobs[mob] = pygame.image.load("assets/images/mobs/" + mob + ".png").convert_alpha()

    def afficher_carte(self, joueur):
        """Cette fonction sert afficher la carte"""
        self.fenetre.blit(self.fond, (0, 0))
        for i in joueur.carte_mobs:
            self.fenetre.blit(self.textures_mobs[i[0]], (i[1][0], i[1][1]))
        pygame.display.flip()


def commande(txt):
    """lorenzo doit le faire"""
    connexion_avec_serveur = socket.socket()
    connexion_avec_serveur.connect(("localhost", 12800))
    txt = txt.encode()
    connexion_avec_serveur.send(txt)


def demande(txt):
    """Cette fonction sert a demander des informations au serveur"""
    r = None
    while not r:
        try:
            connexion_avec_serveur = socket.socket()
            connexion_avec_serveur.connect(("localhost", 12800))
            txt = txt.encode()
            connexion_avec_serveur.send(txt)
            r = connexion_avec_serveur.recv(1024).decode()
            connexion_avec_serveur.close()
        except OSError:
            pass
    return r


def boucle(fenetre, joueur):
    """Cette fonction est la boucle principale du client"""
    for event in pygame.event.get():
        if event.type == QUIT:
            commande("carte:quitter:" + str(joueur.id))
            return False
    fenetre.afficher_carte(joueur)
    return True


def main():
    """Cette fonction est la fonction principale du client"""
    pygame.init()
    actif = True
    fenetre = RendererController()
    joueur = Playercontroller(fenetre)
    while actif:
        actif = boucle(fenetre, joueur)


main()
