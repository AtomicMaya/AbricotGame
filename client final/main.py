# coding=utf-8
"""Ce fichier contient le code principal du client"""
import pygame
from pygame.locals import *
import socket
from json import loads, load
from typing import Dict, Tuple


def combat():
    pass


def move(b):
    pass


class Map:
    """Cette classe représente une carte du jeu"""

    def __init__(self, data: Dict):
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

    def get(self, map_id: Tuple[int, int]) -> Map:
        """Cette fonction permet de recupere une carte en fonction de son id"""
        return self.maps[map_id]


MAPS = Maps()


class RendererController:
    """Cette classe contient toute les méthodes liée a l'affichage et au stokage des textures"""

    def __init__(self):
        self.fenetre = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Abricot game")
        pygame.font.init()
        pygame.display.set_icon(
            pygame.transform.scale(pygame.image.load("assets/images/icone.png").convert_alpha(), (30, 30)))
        self.fond = None
        self.textures_mobs = {}
        self.textures_classes = {"001": pygame.image.load("assets/images/classes/archer/archer1.png")}
        self.textures_classes["001"].set_colorkey((255, 255, 255))
        self.textures_classes["001"] = self.textures_classes["001"].convert_alpha()

    def charger_textures(self, joueur):
        """Cette méthode est appellée lors d'un changement de map pour charger les textures de la nouvelle map"""
        self.fond = pygame.image.load(
            "assets/images/maps/" + str(joueur.carte_id[0]) + "." + str(joueur.carte_id[1]) + ".png").convert()
        self.fond = pygame.transform.scale(self.fond, (1024, 576))
        self.textures_mobs = {}
        for mob in MAPS.get(joueur.carte_id).mobs:
            self.textures_mobs[mob] = pygame.image.load("assets/images/mobs/" + mob + ".png").convert_alpha()

    def afficher_carte(self, joueur):
        """Cette fonction sert afficher la carte"""

        self.fenetre.fill((0, 0, 0))
        self.fenetre.blit(self.fond, (128, 0))
        for i in range(0, 32):
            for j in range(18):
                if j % 2 == 0 and i % 2 == 0 or j % 2 == 1 and i % 2 == 1:
                    pygame.draw.rect(self.fenetre, (0, 0, 0), (i * 32 + 128, j * 32, 33, 33), 1)

        for i in joueur.carte_mobs:
            self.fenetre.blit(self.textures_mobs[i[0]], decalage(i[1]))
            if i[1][0] == (pygame.mouse.get_pos()[0] - 128) // 32 and i[1][1] == (pygame.mouse.get_pos()[1] // 32):
                f = pygame.font.Font(None, 20)
                for j in joueur.groupmobs:
                    if i in j[0]:
                        n = 0
                        for k in j[0]:
                            # str(j[1])
                            txt = f.render(k[0], 0, (255, 255, 255))
                            x, y = pygame.mouse.get_pos()
                            self.fenetre.blit(txt, (x, y + 20 * n))
                            n += 1

        for i in joueur.carte_joueurs:
            self.fenetre.blit(self.textures_classes[i[0]], decalage(i[1]))

        pygame.display.flip()


class Playercontroller:
    """Cette classe contient toute les informations liée au joueur"""

    def __init__(self, fenetre: RendererController):
        self.id = demande("carte:connect")
        self.carte_id = (0, 0)
        self.carte_mobs = []
        self.carte_joueurs = []
        self.groupmobs = []
        self.changement_carte(fenetre)

    def changement_carte(self, fenetre: RendererController):
        """Cette fonction est appellée quand le joueur change de carte et sert a charger les nouvelles textures et la
        forme de la carte"""
        resultat = loads(demande("carte:carte:" + str(self.id)))
        self.carte_id = eval(resultat["map"])
        self.carte_mobs = []
        self.groupmobs = []
        for i in resultat["mobs"]:
            temp = []
            for j in i["mobs"]:
                tempp = (j[0], (j[1][0], j[1][1]))
                self.carte_mobs.append(tempp)
                temp.append(tempp)
            self.groupmobs.append((temp, i["level"]))
        self.carte_joueurs = []
        for i in resultat["joueurs"]:
            self.carte_joueurs.append((i["classe"], i["position"], i["name"]))
        fenetre.charger_textures(self)

    def clic(self):
        """Cette fonction est appellée quand le joueur fait un clic de souris"""
        move(pygame.mouse.get_pos())
        for mob in self.carte_mobs:
            if mob[1][0] == (pygame.mouse.get_pos()[0] - 128) / 32 and mob[1][1] == (pygame.mouse.get_pos()[1]) / 32:
                combat()


def decalage(coord: Tuple[int, int]) -> Tuple[int, int]:
    """Cette fonction sert a transformer une coordonnée sur la carte en une position en pixels"""
    new_x = coord[0] * 32 + 128
    new_y = coord[1] * 32
    return new_x, new_y


def commande(txt: str):
    """lorenzo doit le faire"""
    connexion_avec_serveur = socket.socket()
    connexion_avec_serveur.connect(("localhost", 12800))
    txt = txt.encode()
    connexion_avec_serveur.send(txt)


def demande(txt: str) -> str:
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


def boucle(fenetre: RendererController, joueur: Playercontroller) -> bool:
    """Cette fonction est la boucle principale du client"""
    for event in pygame.event.get():
        if event.type == QUIT:
            commande("carte:quitter:" + str(joueur.id))
            return False
        if event.type == MOUSEBUTTONDOWN:
            joueur.clic()
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
        pygame.time.Clock().tick(21)


main()
pygame.quit()
