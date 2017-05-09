# coding=utf-8
"""Ce fichier contient le code principal du client"""
import pygame
from pygame.locals import *
import socket


class Playercontroller:
    """Cette classe contient toute les informations liée au joueur"""

    def __init__(self):
        self.id = demande("carte:connect")


class RendererController:
    """Cette classe contient toute les méthodes liée a l'affichage"""

    def __init__(self):
        self.fenetre = pygame.display.set_mode((640, 480))


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
            commande("carte:quitter")
            return False
    return True


def main():
    """Cette fonction est la fonction principale du client"""
    pygame.init()
    actif = True
    fenetre = RendererController()
    joueur = Playercontroller()
    while actif:
        actif = boucle(fenetre, joueur)


main()
