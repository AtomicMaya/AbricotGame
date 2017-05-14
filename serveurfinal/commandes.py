# coding=utf-8
"""Ce fichier ce charge de traiter les commandes envoyées par les joueurs connectés"""
from classesentitee import *
from json import dumps


def mouvement(idjoueur: str, direction: str, joueurs: Dict, combat: List) -> bool:
    """Cette fonction permet a un joueur de se déplacer"""
    if int(idjoueur) in joueurs.keys():
        joueur = joueurs[int(idjoueur)]
        if not joueur.combat:
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
    return False


def connexion(client, ids: int, joueurs: Dict) -> Tuple[int, Dict]:
    """Cette fonction est appellée quand un joueur se connecte"""
    joueur = Joueur(ids)
    joueurs[ids] = joueur
    map = MAPS.get(joueur.map)
    map.actif = True
    map.joueurs[ids] = joueur
    client.send((str(ids) + ":" + str(joueur.mapcoords[0]) + ":" + str(joueur.mapcoords[1])).encode())
    ids += 1
    return ids, joueurs


def carte(id_joueur: str, joueurs: Dict) -> str:
    """Cette fonction est appellée quand le joueur arrive sur une carte et lui transmet des informations"""
    if int(id_joueur) in joueurs.keys():
        joueur = joueurs[int(id_joueur)]
        mobgroups = []
        for mobsgroups in MAPS.get(joueur.map).mobsgroups:
            temp = {"level": mobsgroups.level, "mobs": []}
            for mob in mobsgroups.mobgroup:
                temp["mobs"].append((mob.name, mob.mapcoords))
            mobgroups.append(temp)
        temp = []
        for players in MAPS.get(joueur.map).joueurs.values():
            temp.append({"name": players.name, "classe": players.classe, "position": players.mapcoords})
        return dumps({"map": joueur.map, "mobs": mobgroups, "joueurs": temp})


def commandecarte(message: List, client, ids: int, joueurs: Dict, combats: List) -> Tuple[int, Dict]:
    """Cette fonction effectue toute le commandes liés a la carte (mouvement,objets a affichager,...)"""
    if message[0] == "move" and len(message) == 3:
        client.send(str(mouvement(message[1], message[2], joueurs, combats)).encode())
    elif message[0] == "carte" and len(message) == 2:
        client.send(carte(message[1], joueurs).encode())
    elif message[0] == "connect" and len(message) == 1:
        ids, joueurs = connexion(client, ids, joueurs)
    elif message[0] == "quitter" and len(message) == 2:
        if int(message[1]) in joueurs:
            joueur = joueurs[int(message[1])]
            if not joueur.en_combat:
                del MAPS.get(joueur.map).joueurs[int(joueur.id)]

    return ids, joueurs


def entitee_combat(id: int, joueurs: Dict) -> str:
    """Cette fonction transmet au joueur toute les informations sur un combat"""
    joueur = joueurs[int(id)]
    mobs = []
    for mob in joueur.combat.mobgroup:
        mobs.append((mob.name, mob.position_combat))
    temp = []
    for players in joueur.combat.players:
        temp.append({"name": players.name, "classe": players.classe, "position": players.position_combat})
    return dumps({"mobs": mobs, "joueurs": temp})


def commandecombat(message: List, client, joueurs: Dict):
    """Cette fonction efffectue toute les commandes liée au combat (attaque,déplacement,...)"""
    if message[0] == "carte" and len(message) == 2:
        client.send(entitee_combat(int(message[1]), joueurs).encode())
