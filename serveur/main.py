# coding=utf-8
import select
import socket
from carte import *
from entitee import *
from controlleur import controler_types


def tempspawnentitee(listecarte, cartes):
    cartes[(0, 0)] = Carte("cartes/" + listecarte[(0, 0)])
    cartes[(0, 0)].spawn(Groupeennemi(4, 4, Ennemi("Patate", 5), Ennemi("Abricot", 3), Ennemi("Carote", 6)))


def demarage():
    listecarte = {}
    with open("cartes/dico") as fichier:
        for carte in fichier:
            carte = carte.split(":")
            carte[2] = carte[2].replace("\n", "")
            listecarte[(int(carte[0]), int(carte[1]))] = carte[2]
    connexion = socket.socket()
    connexion.bind(('', 12800))
    connexion.listen(5)
    print("Ok")
    return connexion, listecarte


@controler_types(dict)
def _entitee(dico):
    resultat = ""
    for i in dico.values():
        for j in i:
            if type(j) == Joueur:
                resultat += ("J:" + str(j.id) + ":" + str(j.position[0]) + ":" + str(j.position[1]) + ":")
            else:
                resultat += ("G:" + str(j.position[0]) + ":" + str(j.position[1]) + ":" + str(len(j.ennemis)) + ":")
                for k in j.ennemis:
                    resultat += (k.nom + ":" + str(k.niveau) + ":")
    return resultat


@controler_types(int, dict, dict, object, object, list, dict)
def boucle(ids, joueurs, cartes, connexion, clients_connectes, idslibre, listecarte):
    # connexions
    connexions_demandees, wlist, xlist = select.select([connexion], [], [], 0.05)
    for c in connexions_demandees:
        connexion_avec_client, infos_connexion = c.accept()
        clients_connectes.append(connexion_avec_client)
    # messages
    try:
        clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
        clients_connectes = clients_connectes[-5:]
    except select.error:
        pass
    # liremessage
    else:
        for client in clients_a_lire:
            temp = client.recv(1024)
            temp = temp.decode()
            temp = temp.split(":")
            # carte
            if temp[0] == "carte":
                temp = temp[1:len(temp)]
                if temp[0] == "carte" and len(temp) == 3:
                    client.send((str(cartes[(int(temp[1]), int(temp[2]))].forme)).encode())

                elif temp[0] == "entitee" and len(temp) == 3:
                    client.send(    (  _entitee(cartes[(int(temp[1]), int(temp[2]))].entites)  )     .encode())

                elif temp[0] == "move" and len(temp) == 3:
                    joueur = joueurs[int(temp[1])]
                    if joueur.etat == Etatjoueur.normal:
                        if temp[2] == "right":
                            directionmouv = Direction.DROITE

                            if joueur.position[0] == 19:
                                directionmouv = Direction.CARTE
                                if cartes[joueur.carte].deconnexion(joueur):
                                    del cartes[joueur.carte]
                                joueur.carte = (joueur.carte[0] + 1, joueur.carte[1])
                                joueur.position = (0, joueur.position[1])
                                if joueur.carte not in cartes.keys():
                                    cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
                                cartes[joueur.carte].connexion(joueur)
                                client.send(b"True")

                        elif temp[2] == "left":
                            directionmouv = Direction.GAUCHE

                            if joueur.position[0] == 0:
                                directionmouv = Direction.CARTE
                                if cartes[joueur.carte].deconnexion(joueur):
                                    del cartes[joueur.carte]
                                joueur.carte = (joueur.carte[0] - 1, joueur.carte[1])
                                joueur.position = (19, joueur.position[1])
                                if joueur.carte not in cartes.keys():
                                    cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
                                cartes[joueur.carte].connexion(joueur)
                                client.send(b"True")

                        elif temp[2] == "down":
                            directionmouv = Direction.BAS

                            if joueur.position[1] == 0:
                                directionmouv = Direction.CARTE
                                if cartes[joueur.carte].deconnexion(joueur):
                                    del cartes[joueur.carte]
                                joueur.carte = (joueur.carte[0], joueur.carte[1] - 1)
                                joueur.position = (joueur.position[0], 14)
                                if joueur.carte not in cartes.keys():
                                    cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
                                cartes[joueur.carte].connexion(joueur)
                                client.send(b"True")

                        elif temp[2] == "up":
                            directionmouv = Direction.HAUT

                            if joueur.position[1] == 14:
                                directionmouv = Direction.CARTE
                                if cartes[joueur.carte].deconnexion(joueur):
                                    del cartes[joueur.carte]
                                joueur.carte = (joueur.carte[0], joueur.carte[1] + 1)
                                joueur.position = (joueur.position[0], 0)
                                if joueur.carte not in cartes.keys():
                                    cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
                                cartes[joueur.carte].connexion(joueur)
                                client.send(b"True")

                        else:
                            directionmouv = Direction.ERREUR
                        if directionmouv != Direction.CARTE:
                            tempmove = cartes[joueur.carte].move(joueur, directionmouv)
                            if tempmove == Mouvementresult.ERREUR:
                                client.send(b"False")
                            elif tempmove == Mouvementresult.COMBAT:
                                client.send(b"Combat")
                            else:
                                client.send(b"True")
                    else:
                        client.send(b"False")

                elif temp[0] == "connect" and len(temp) == 1:
                    if len(idslibre) == 0:
                        tempid = ids
                        ids += 1
                    else:
                        tempid = idslibre[0]
                        del idslibre[0]
                    client.send((str(tempid)).encode())
                    temp = Joueur(tempid)
                    joueurs[tempid] = temp

                    if temp.carte not in cartes.keys():
                        cartes[temp.carte] = Carte("cartes/" + listecarte[temp.carte])
                    cartes[temp.carte].connexion(temp)

                elif temp[0] == "quitter" and len(temp) == 2:
                    tempid = int(temp[1])
                    idslibre.append(tempid)
                    while (ids - 1) in idslibre:
                        ids -= 1
                        idslibre.remove(ids)
                    if cartes[joueurs[tempid].carte].deconnexion(joueurs[tempid]):
                        del cartes[joueurs[tempid].carte]
                    del joueurs[tempid]

            elif temp[0] == "combat":
                if temp[1] == "start":
                    if not joueurs[int(temp[2])].combat.actif:
                        joueurs[int(temp[2])].combat.joueurs[joueurs[int(temp[2])]] = True
                        joueurs[int(temp[2])].combat.start()
                elif temp[1] == "entitee":
                    client.send((joueurs[int(temp[2])].combat.afficher()).encode())
                elif temp[1] == "sort":
                    print("sortlance")
    for i in cartes.values():
        for j in [x for x in i.listcombat if x.actif]:
            j.actualiser()

    return ids, clients_connectes


def main():
    connexion, listecarte = demarage()
    ids = 0
    clients_connectes = []
    joueurs = {}
    cartes = {}
    idslibre = []
    tempspawnentitee(listecarte, cartes)
    while True:
        ids, clients_connectes = boucle(ids, joueurs, cartes, connexion, clients_connectes, idslibre, listecarte)


main()
