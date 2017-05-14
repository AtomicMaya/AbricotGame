# coding=utf-8
"""Ce fichier contient le code principal du client"""
import pygame
from pygame.locals import *
import socket
from json import loads, load
from typing import Dict, Tuple
from pathfinding import calculate_movement
import time


def convert_image(chemin: str, couleurfond=(255, 255, 255)):
    """Cette image permet de transformer le chemin vers un fichier en image"""
    image = pygame.image.load(chemin)
    image.set_colorkey(couleurfond)
    return image.convert_alpha()


class Map:
    """Cette classe représente une carte du jeu"""

    def __init__(self, data: Dict):
        self.mobs = data["MOBS"]
        self.obstacles = []
        self.free = []
        for y in range(len(data["MAP"])):
            for x in range(len(data["MAP"][y])):
                if data["MAP"][y][x] > 0:
                    self.obstacles.append((x, y))
                else:
                    self.free.append((x, y))


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
        pygame.display.set_icon(pygame.image.load("assets/images/icone.png").convert_alpha())
        self.fond = None
        self.textures_mobs = {}
        self.textures_classes = {"001": convert_image("assets/images/classes/archer/archer4.png")}

    def charger_textures(self, joueur):
        """Cette méthode est appellée lors d'un changement de map pour charger les textures de la nouvelle map"""
        self.fond = pygame.image.load(
            "assets/images/maps/" + str(joueur.carte_id[0]) + "." + str(joueur.carte_id[1]) + ".png").convert()
        self.fond = pygame.transform.scale(self.fond, (1024, 576))
        self.textures_mobs = {}
        for mob in MAPS.get(joueur.carte_id).mobs:
            self.textures_mobs[mob] = pygame.transform.scale(
                pygame.image.load("assets/images/mobs/" + mob + ".png").convert_alpha(), (32, 32))

    def afficher_carte(self, joueur):
        """Cette fonction sert afficher la carte"""
        self.fenetre.fill((0, 0, 0))
        self.fenetre.blit(self.fond, (128, 0))
        free = MAPS.get(joueur.carte_id).free
        for i in free:
            pygame.draw.rect(self.fenetre, (0, 0, 0), (i[0] * 32 + 128, i[1] * 32, 33, 33), 1)

        if not joueur.en_combat:
            temp = False
            box = None
            x = 0
            y = 0
            for i in joueur.carte_mobs:
                self.fenetre.blit(self.textures_mobs[i[0]], decalage(i[1]))

                if i[1] == decalage_inverse(pygame.mouse.get_pos()) and not temp:
                    temp = True
                    f = pygame.font.Font(None, 30)
                    for j in joueur.groupmobs:
                        if i in j[0]:
                            max_len = 0
                            display = []
                            for k in j[0]:
                                txt = f.render(k[0].replace("_", " "), 0, (255, 255, 255))
                                if txt.get_rect()[2] > max_len:
                                    max_len = txt.get_rect()[2]
                                display.append(txt)

                            txt = f.render('Niveau ' + str(j[1]), 0, (255, 255, 255))
                            x, y = pygame.mouse.get_pos()
                            if x + max_len > 1152:
                                x = 1152 - max_len - 20
                            if y + (len(display) + 1) * 30 > 576:
                                y = 576 - (1 + len(display)) * 30

                            box = pygame.Surface((max_len + 20, (1 + len(display)) * 30 + 20))
                            box.fill((50, 50, 50))
                            box.set_alpha(200)

                            wid = txt.get_rect()[2]
                            box.blit(txt, ((max_len - wid) // 2, 10))

                            for n in range(len(display)):
                                box.blit(display[n], (10, 30 * (n + 1) + 10))

            for i in joueur.carte_joueurs:
                self.fenetre.blit(self.textures_classes[i[0]], decalage(i[1]))
            if box:
                self.fenetre.blit(box, (x, y))
        else:
            joueur.actualisecombat()
            for i in joueur.carte_mobs:
                self.fenetre.blit(self.textures_mobs[i[0]], decalage(i[1]))
            for i in joueur.carte_joueurs:
                self.fenetre.blit(self.textures_classes[i[0]], decalage(i[1]))
        pygame.display.flip()


def compare_tuple(depart: Tuple[int, int], arrivee: Tuple[int, int]):
    """Cette fonction permet de voir dans quelle direction il faut aller pour passer d'un tuple a l'autre"""
    if depart[0] - arrivee[0] == 1:
        return "left"
    elif depart[0] - arrivee[0] == -1:
        return "right"
    elif depart[1] - arrivee[1] == 1:
        return "up"
    elif depart[1] - arrivee[1] == -1:
        return "down"
    else:
        raise ValueError("Les deux tuples ne sont pas adjacents")


class Playercontroller:
    """Cette classe contient toute les informations liée au joueur"""

    def __init__(self, fenetre: RendererController):
        temp = demande("carte:connect")
        temp = temp.split(":")
        self.id = int(temp[0])
        self.position = (int(temp[1]), int(temp[2]))
        self.carte_id = (0, 0)
        self.carte_mobs = []
        self.carte_joueurs = []
        self.groupmobs = []
        self.changement_carte(fenetre)
        self.chemin = []
        self.dernier_mouvment = 0
        self.en_combat = False

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
                mob = (j[0], (j[1][0], j[1][1]))
                self.carte_mobs.append(mob)
                temp.append(mob)
            self.groupmobs.append((temp, i["level"]))
        self.carte_joueurs = []
        for i in resultat["joueurs"]:
            self.carte_joueurs.append((i["classe"], i["position"], i["name"]))
        fenetre.charger_textures(self)

    def clic(self):
        """Cette fonction est appellée quand le joueur fait un clic de souris"""
        if not self.en_combat:
            case = decalage_inverse(pygame.mouse.get_pos())
            if 0 < case[0] < 32 and 0 < case[1] < 18:
                self.move_to(case)

    def move_to(self, case: Tuple[int, int]):
        """Cette fonction calcule le chemin qu'il faut faire pour aller jusqu'a la case pointé par la souris"""
        temp = calculate_movement(self.position, case, MAPS.get(self.carte_id).obstacles)
        if len(temp) > 0:
            self.chemin = temp
            for i in range(len(self.chemin) - 1, 0, -1):
                self.chemin[i] = compare_tuple(self.chemin[i - 1], self.chemin[i])
            del self.chemin[0]

    def actualise(self):
        """En attandant d'avoir un vrai systeme"""
        resultat = loads(demande("carte:carte:" + str(self.id)))
        self.carte_id = eval(resultat["map"])
        self.carte_mobs = []
        self.groupmobs = []
        for i in resultat["mobs"]:
            temp = []
            for j in i["mobs"]:
                mob = (j[0], (j[1][0], j[1][1]))
                self.carte_mobs.append(mob)
                temp.append(mob)
            self.groupmobs.append((temp, i["level"]))
        self.carte_joueurs = []
        for i in resultat["joueurs"]:
            self.carte_joueurs.append((i["classe"], i["position"], i["name"]))

    def actualisecombat(self):
        """En attandant d'avoir un vrai systeme"""
        resultat = loads(demande("combat:carte:" + str(self.id)))
        self.carte_mobs = []
        for j in resultat["mobs"]:
            mob = (j[0], (j[1][0], j[1][1]))
            self.carte_mobs.append(mob)
        self.carte_joueurs = []
        for i in resultat["joueurs"]:
            self.carte_joueurs.append((i["classe"], i["position"], i["name"]))


def decalage(coord: Tuple[int, int]) -> Tuple[int, int]:
    """Cette fonction sert a transformer une coordonnée sur la carte en une position en pixels"""
    return coord[0] * 32 + 128, coord[1] * 32


def decalage_inverse(coord: Tuple[int, int]) -> Tuple[int, int]:
    """Cette fonction fait l'inverse de décalage et permet de transformer une position en pixel en coordonnée sur la
    carte"""
    return (coord[0] - 128) // 32, coord[1] // 32


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
            r = connexion_avec_serveur.recv(8192).decode()
            connexion_avec_serveur.close()
        except OSError:
            pass
    return r


def boucle(fenetre: RendererController, joueur: Playercontroller) -> bool:
    """Cette fonction est la boucle principale du client"""
    for event in pygame.event.get():
        if event.type == QUIT:
            if joueur.en_combat:
                return False
            else:
                commande("carte:quitter:" + str(joueur.id))
                return False
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            joueur.clic()

    fenetre.afficher_carte(joueur)

    if not joueur.en_combat:
        if len(joueur.chemin) > 0 and time.time() > 7 + joueur.dernier_mouvment:
            joueur.dernier_mouvment + time.time()
            mouvement = joueur.chemin[0]
            if demande("carte:move:" + str(joueur.id) + ":" + mouvement) == "True":
                joueur.en_combat = True
            else:
                if mouvement == "up":
                    joueur.position = (joueur.position[0], joueur.position[1] - 1)
                elif mouvement == "down":
                    joueur.position = (joueur.position[0], joueur.position[1] + 1)
                elif mouvement == "left":
                    joueur.position = (joueur.position[0] - 1, joueur.position[1])
                elif mouvement == "right":
                    joueur.position = (joueur.position[0] + 1, joueur.position[1])
                else:
                    raise ValueError("Le mouvement demandé n'exite pas")
                del joueur.chemin[0]
    return True


def main():
    """Cette fonction est la fonction principale du client"""
    pygame.init()
    actif = True
    fenetre = RendererController()
    joueur = Playercontroller(fenetre)
    while actif:
        joueur.actualise()
        actif = boucle(fenetre, joueur)
        pygame.time.Clock().tick(42)


main()
pygame.quit()
