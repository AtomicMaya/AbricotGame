# coding=utf-8
"""Ce fichier ce charge de traiter les commandes envoyées par les joueurs connectés"""
from classesentitee import *


def mouvement(idjoueur, direction, joueurs, combat):
    """Cette fonction permet a un joueur de se déplacer"""
    if idjoueur in joueurs:
        joueur = joueurs[idjoueur]
        if not joueur.en_combat:
            if direction == "right":
                directionmouv = Mouvements.DROITE
            elif direction == "left":
                directionmouv = Mouvements.GAUCHE
            elif direction == "up":
                directionmouv = Mouvements.HAUT
            elif direction == "down":
                directionmouv = Mouvements.BAS
            else:
                return False
            return MAPS.get(joueur.map).move(joueur, directionmouv, combat)


def connexion(client, ids, joueurs):
    """Cette fonction est appellée quand un joueur se connecte"""
    client.send((str(ids)).encode())
    joueurs[ids] = Joueur(ids)
    map = MAPS.get(joueurs[ids].map)
    map.actif = True
    map.joueurs[ids] = joueurs[ids]
    ids += 1
    return ids, joueurs


def commandecarte(message, client, ids, joueurs, combats):
    """Cette fonction effectue toute le commandes liés a la carte (mouvement,objets a affichager,...)"""
    if message[0] == "move" and len(message) == 3:
        client.send(mouvement(message[1], message[2], joueurs, combats))
    elif message[0] == "connect" and len(message) == 1:
        ids, joueurs = connexion(client, ids, joueurs)
    elif message[0] == "quitter" and len(message) == 2:
        if message[1] in joueurs:
            joueur = message[1]
            if not joueur.en_combat:
                del MAPS.get(joueur.map).joueurs[joueur.id]

    return ids, joueurs


def commandecombat(message):
    """Cette fonction efffectue toute les commandes liée au combat (attaque,déplacement,...)"""
    pass
