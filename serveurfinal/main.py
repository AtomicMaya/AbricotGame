# coding=utf-8
"""Fichier principal du serveur"""
import socket
from codecs import open as c_open
from json import load
from itertools import filterfalse
from random import choice, randint
import copy
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
        try:
            clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
            clients_connectes = clients_connectes[-5:]
        except select.error:
            pass
        else:
            for client in clients_a_lire:
                temp = client.recv(1024)
                temp = temp.decode()
                messages.append(temp)
        yield messages


def unique_everseen(iterable, key=None):
    """Nicolass ?"""
    elem_vus = set()
    seen_add = elem_vus.add
    if key is None:
        for element in filterfalse(elem_vus.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in elem_vus:
                seen_add(k)
                yield element


def bresenham(player, end):
    """ Algorithme de Bresenham
    Indique les cases traversees par une ligne passant de l'une à l'autre
    :param player: -> Coordonnees du joueur
    :param end: -> Coordonnees de la destination
    """
    x1, y1 = player
    x2, y2 = end
    # Differences
    dx = x2 - x1
    dy = y2 - y1

    # Teste l'inclinaison de pente
    pente = abs(dy) > abs(dx)

    # Effectue une rotation de la pente si trop inclinee
    if pente:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Inverse les coordonnees en x et y si necessaire
    switched = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        switched = True

    # Recalcul des differences
    dx = x2 - x1
    dy = y2 - y1

    # Calcul de l'erreur
    error = int(dx / 2.0)
    y_step = 1 if y1 < y2 else -1

    # Itere par dessus les cases generant les points traverses entre le joueur et la fin de sa visibilite
    y = y1
    crossed_points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if pente else (x, y)
        crossed_points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx

    # Inversion de la liste si les points originaux ont etes inverses
    if switched:
        crossed_points.reverse()
    return list(unique_everseen(crossed_points))


class Spell:
    """Cette classe permet de définir un sort et d'appliquer ses effets"""

    def __init__(self, name, damage, cost, shape, spell_type, max_range, min_range, reload, aoe, aoe_range, aoe_shape,
                 effects, onself):
        self.name = name
        self.damage = int(damage)
        self.cost = int(cost)
        self.shape = shape
        self.spellType = spell_type
        self.maxRange = int(max_range)
        self.minRange = min_range
        self.reload = int(reload)
        self.aoe = bool(aoe)
        self.aoeRange = aoe_range
        self.aoeShape = aoe_shape
        self.effects = effects
        self.on_self = True if onself == 1 else False

    def apply_effect(self, target):
        pass

    def impact(self, coords):
        x, y = coords
        points = [(x, y + self.maxRange), (x + self.maxRange, y), (x, y - self.maxRange), (x - self.maxRange, y)]
        outline = []
        outline += [bresenham(points[3], points[0]) + bresenham(points[0], points[1])]
        outline += [bresenham(points[3], points[2]) + bresenham(points[2], points[1])]
        out = []
        for i in range(len(outline[0])):
            out += bresenham(outline[0][i], outline[1][i])
        out = list(set(out))
        if not self.on_self:
            out.remove(coords)
        return out


class Spells:
    """Cette classe contient la liste de tout les sorts du jeu"""

    def __init__(self):
        json_file = c_open("spells.json", encoding='utf-8')
        file_spells = load(json_file)
        json_file.close()
        self.spells = {}
        for ids in file_spells:
            if ids != '_template':
                self.spells[ids] = Spell(file_spells[ids]['NAME'], file_spells[ids]['DAMAGE'],
                                         file_spells[ids]['COST'], file_spells[ids]['SHAPE'],
                                         file_spells[ids]['TYPE'], file_spells[ids]['ATTACKMAXRANGE'],
                                         file_spells[ids]['ATTACKMINRANGE'], file_spells[ids]['RELOAD'],
                                         file_spells[ids]['AOE'], file_spells[ids]['AOERANGE'],
                                         file_spells[ids]['AOESHAPE'],
                                         file_spells[ids]['EFFECTS'], file_spells[ids]['SELFCAST'])

    def get(self, spell_id: str):
        """Cette fonction permet de réuperer un sort grace a son id"""
        return self.spells[spell_id]


class Mobgroup:
    """Cette classe représente un groupe de mobs """

    def __init__(self, map, MOBS):
        group_coords = choice(map.free)
        self.mobgroup = [MOBS.get(choice(map.mobs), randint(map.levelmin, map.levelmax), group_coords) for _ in
                         range(randint(2, 8))]
        self.level = 0
        for mob in self.mobgroup:
            self.level += mob.level
        self.timer = 0

    def move(self):
        """Cette fonction fait bouger tout les mobs d'un groupe"""
        self.timer = randint(42 * 10, 42 * 30)
        for mob in self.mobgroup[1:]:  # Leader does not move
            action = choice(['UP', 'LEFT', 'DOWN', 'RIGHT', 'NONE', 'NONE'])
            mob.move(action)


class Map:
    """Cette classe représente une carte du jeu"""

    def __init__(self, data):
        self.actif = False
        self.semiobs = []
        self.fullobs = []
        self.free = []
        self.mobs = [mob_id for mob_id in data["MOBS"]]
        self.levelmax = data['LEVELMAX']
        self.levelmin = data['LEVELMIN']
        self.mobsgroups = []
        for y in range(len(data["MAP"])):
            for x in range(len(data["MAP"][y])):
                if data["MAP"][y][x] == 1:
                    self.fullobs.append((x, y))
                elif data["MAP"][y][x] == 2:
                    self.semiobs.append((x, y))
                else:
                    self.free.append((x, y))
        self.obstacles = self.semiobs + self.fullobs

    def actualiser(self, MOBS):
        """Fonction appellée a chaque tick qui sert a faire bouger les entitées, a rafraichir les combats et a faire
        apparaitre de nouveaux ennemis"""
        for mobgroup in self.mobsgroups:
            if mobgroup.timer == 0:
                mobgroup.move()
            else:
                mobgroup.timer -= 1
        if len(self.mobsgroups) < 3 and len(self.mobs) != 0:
            self.mobsgroups.append(Mobgroup(self, MOBS))


class Maps:
    """Cette classe contient la liste de toute les cartes du jeu"""

    def __init__(self):
        json_file = open("maps.json")
        file_maps = load(json_file)
        json_file.close()
        self.maps = {}
        for ids in file_maps:
            if ids != '_template':
                self.maps[ids] = Map(file_maps[ids])

    def get(self, map_id: str):
        """Cette fonction permet de recupere une carte en fonction de son id"""
        return self.maps[map_id]


class caracteristiques:
    """Cette classe représente les caactéristiques de combat d'un mob ou d'un joueur"""

    def __init__(self, hp, mp, ap):
        self.hp = hp
        self.mp = mp
        self.ap = ap

    def __add__(self, autre):
        return caracteristiques(self.hp + autre.hp, self.mp + autre.mp, self.ap + autre.ap)

    def __mul__(self, autre):
        return caracteristiques(self.hp * autre, self.mp * autre, self.ap * autre)

    def __rmul__(self, autre):
        return self * autre


class Type_Mob:
    """Cette classe représente une catégorie de mob"""

    def __init__(self, data, SPELLS):
        self.name = data['NAME']
        self.spells = [SPELLS.get(spell_id) for spell_id in data['SPELLS']]
        self.idle_anim = data['IDLE']
        self.attack_anim = data['ATTACK']
        self.mouvement_anim = data['MOVEMENT']
        self.caracteristiques = caracteristiques(data['BASEHP'], data['MOVEMENTPOINTS'], data['ACTIONPOINTS'])
        self.xcaracteristiques = caracteristiques(data['XHP'], 0, 0)


class Mob:
    """Classe représanatant un mob"""

    def __init__(self, typemob, level, position):
        self.name = typemob.name
        self.spells = typemob.spells
        self.maxcaracteristiques = typemob.caracteristiques + typemob.xcaracteristiques * level
        self.actuelcaracteristiques = copy.deepcopy(self.maxcaracteristiques)
        self.idle_anim = typemob.idle_anim
        self.attack_anim = typemob.attack_anim
        self.mouvement_anim = typemob.mouvement_anim
        self.level = level
        self.mapcoords = position


class Mobs:
    """Classe contenant la liste de tout les mobs"""

    def __init__(self, SPELLS):
        json_file = c_open("mobs.json", encoding='utf-8')
        file_mobs = load(json_file)
        json_file.close()
        self.mobs = {}
        for ids in file_mobs:
            if ids != '_template':
                self.mobs[ids] = Type_Mob(file_mobs[ids], SPELLS)

    def get(self, mob_id: str, level, position):
        """Permet de récuperer un mob grace a son id"""
        return Mob(self.mobs[mob_id], level, position)


def start_server():
    """Fonction servant a initialiser toutes les variables"""
    SPELLS = Spells()
    MAPS = Maps()
    MOBS = Mobs(SPELLS)
    return lire_message(), SPELLS, MAPS, MOBS


def boucle(commandes, MAPS, MOBS):
    """Boucle principale du serveur"""
    messages = next(commandes)
    for text in messages:
        text = text.split(":")
        # if text[0] == "carte":
        #     temp = temp[1:len(temp)]
        #     if temp[0] == "carte" and len(temp) == 3:
        #         client.send((str(cartes[(int(temp[1]), int(temp[2]))].forme)).encode())
        #
        #     elif temp[0] == "entitee" and len(temp) == 3:
        #         client.send((_entitee(cartes[(int(temp[1]), int(temp[2]))].entites)).encode())
        #
        #     elif temp[0] == "move" and len(temp) == 3:
        #         joueur = joueurs[int(temp[1])]
        #         if joueur.etat == Etatjoueur.normal:
        #             if temp[2] == "right":
        #                 directionmouv = Direction.DROITE
        #
        #                 if joueur.position[0] == 19:
        #                     directionmouv = Direction.CARTE
        #                     if cartes[joueur.carte].deconnexion(joueur):
        #                         del cartes[joueur.carte]
        #                     joueur.carte = (joueur.carte[0] + 1, joueur.carte[1])
        #                     joueur.position = (0, joueur.position[1])
        #                     if joueur.carte not in cartes.keys():
        #                         cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
        #                     cartes[joueur.carte].connexion(joueur)
        #                     client.send(b"True")
        #
        #             elif temp[2] == "left":
        #                 directionmouv = Direction.GAUCHE
        #
        #                 if joueur.position[0] == 0:
        #                     directionmouv = Direction.CARTE
        #                     if cartes[joueur.carte].deconnexion(joueur):
        #                         del cartes[joueur.carte]
        #                     joueur.carte = (joueur.carte[0] - 1, joueur.carte[1])
        #                     joueur.position = (19, joueur.position[1])
        #                     if joueur.carte not in cartes.keys():
        #                         cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
        #                     cartes[joueur.carte].connexion(joueur)
        #                     client.send(b"True")
        #
        #             elif temp[2] == "down":
        #                 directionmouv = Direction.BAS
        #
        #                 if joueur.position[1] == 0:
        #                     directionmouv = Direction.CARTE
        #                     if cartes[joueur.carte].deconnexion(joueur):
        #                         del cartes[joueur.carte]
        #                     joueur.carte = (joueur.carte[0], joueur.carte[1] - 1)
        #                     joueur.position = (joueur.position[0], 14)
        #                     if joueur.carte not in cartes.keys():
        #                         cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
        #                     cartes[joueur.carte].connexion(joueur)
        #                     client.send(b"True")
        #
        #             elif temp[2] == "up":
        #                 directionmouv = Direction.HAUT
        #
        #                 if joueur.position[1] == 14:
        #                     directionmouv = Direction.CARTE
        #                     if cartes[joueur.carte].deconnexion(joueur):
        #                         del cartes[joueur.carte]
        #                     joueur.carte = (joueur.carte[0], joueur.carte[1] + 1)
        #                     joueur.position = (joueur.position[0], 0)
        #                     if joueur.carte not in cartes.keys():
        #                         cartes[joueur.carte] = Carte("cartes/" + listecarte[joueur.carte])
        #                     cartes[joueur.carte].connexion(joueur)
        #                     client.send(b"True")
        #
        #             else:
        #                 directionmouv = Direction.ERREUR
        #             if directionmouv != Direction.CARTE:
        #                 tempmove = cartes[joueur.carte].move(joueur, directionmouv)
        #                 if tempmove == Mouvementresult.ERREUR:
        #                     client.send(b"False")
        #                 elif tempmove == Mouvementresult.COMBAT:
        #                     client.send(b"Combat")
        #                 else:
        #                     client.send(b"True")
        #         else:
        #             client.send(b"False")
        #
        #     elif temp[0] == "connect" and len(temp) == 1:
        #         if len(idslibre) == 0:
        #             tempid = ids
        #             ids += 1
        #         else:
        #             tempid = idslibre[0]
        #             del idslibre[0]
        #         client.send((str(tempid)).encode())
        #         temp = Joueur(tempid)
        #         joueurs[tempid] = temp
        #
        #         if temp.carte not in cartes.keys():
        #             cartes[temp.carte] = Carte("cartes/" + listecarte[temp.carte])
        #         cartes[temp.carte].connexion(temp)
        #
        #     elif temp[0] == "quitter" and len(temp) == 2:
        #         tempid = int(temp[1])
        #         idslibre.append(tempid)
        #         while (ids - 1) in idslibre:
        #             ids -= 1
        #             idslibre.remove(ids)
        #         if cartes[joueurs[tempid].carte].deconnexion(joueurs[tempid]):
        #             del cartes[joueurs[tempid].carte]
        #         del joueurs[tempid]
        #
        # elif text[0] == "combat":
        #     if temp[1] == "start":
        #         if not joueurs[int(temp[2])].combat.actif:
        #             joueurs[int(temp[2])].combat.joueurs[joueurs[int(temp[2])]] = True
        #             joueurs[int(temp[2])].combat.start()
        #     elif temp[1] == "entitee":
        #         client.send((joueurs[int(temp[2])].combat.afficher()).encode())
        #     elif temp[1] == "sort":
        #         print("sortlance")

    for i in MAPS.maps.values():
        if i.actif:
            i.actualiser(MOBS)


def main():
    """Fonction principale du programme"""
    commandes, SPELLS, MAPS, MOBS = start_server()
    while True:
        boucle(commandes, MAPS, MOBS)


main()
