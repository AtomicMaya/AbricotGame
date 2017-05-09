# coding=utf-8
"""Fichier principal du serveur"""
import pygame
from commandes import *
import socket
import select


def lire_message():
    """Lorenzo doit le faire"""
    clients_connectes = []
    connexion = socket.socket()
    connexion.bind(('', 12800))
    connexion.listen(5)
    while True:
        messages = []
        connexions_demandees, wlist, xlist = select.select([connexion], [], [], 0.05)
        for c in connexions_demandees:
            connexion_avec_client, infos_connexion = c.accept()
            clients_connectes.append(connexion_avec_client)

        if len(clients_connectes) > 0:
            clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
            clients_connectes = clients_connectes[-5:]
            for client in clients_a_lire:
                temp = client.recv(1024)
                temp = temp.decode()
                messages.append((temp, client))
        yield messages


def boucle(commandes, combats, ids, joueurs):
    """Boucle principale du serveur"""
    messages = next(commandes)
    for demande in messages:
        text = demande[0]
        text = text.split(":")
        if len(text) > 1:
            if text[0] == "carte":
                ids, joueurs = commandecarte(text[1:len(text)], demande[1], ids, joueurs, combats)
            # if temp[0] == "carte" and len(temp) == 3:
            #         client.send((str(cartes[(int(temp[1]), int(temp[2]))].forme)).encode())
            #
            #     elif temp[0] == "entitee" and len(temp) == 3:
            #         client.send((_entitee(cartes[(int(temp[1]), int(temp[2]))].entites)).encode())
            elif text[0] == "combat":
                commandecombat(text[1:len(text)])

    for i in MAPS.maps.values():
        if i.actif:
            i.update(combats)
    for i in combats:
        i.update()

    return ids, joueurs, combats


def main():
    """Fonction principale du programme"""
    commandes = lire_message()
    ids = 0
    joueurs = {}
    combats = []
    while True:
        ids, joueurs, combats = boucle(commandes, combats, ids, joueurs)
        pygame.time.Clock().tick(42)


main()
