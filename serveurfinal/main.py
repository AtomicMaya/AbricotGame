# coding=utf-8
"""Fichier principal du serveur"""
import socket
from codecs import open as c_open
from json import load
from itertools import filterfalse
from random import choice, randint, shuffle
import copy
import select
from heapq import heapify, heappush, heappop
import pygame
import enum

taille_map_x = 32
taille_map_y = 18


class Mouvements(enum.Enum):
    """Cette enumeration represente les differents mouvements qui peuvent être fait"""
    HAUT = enum.auto(),
    BAS = enum.auto(),
    GAUCHE = enum.auto(),
    DROITE = enum.auto(),
    ERREUR = enum.auto()


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
                messages.append((temp, client))
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


def linearize(alist, obstacles):
    """nicolass ?"""
    y_dir = 1 if alist[0][0] - alist[-1][0] > 0 else -1
    x_dir = 1 if alist[0][1] - alist[-1][1] > 0 else -1
    for i in range(1, len(alist) * 2 - 2):
        try:
            if alist[i - 1][0] != alist[i][0] and alist[i - 1][1] != alist[i][1]:
                alist.insert(i, (alist[i - 1][0], alist[i - 1][1] + y_dir)) \
                    if alist[i - 1][1] + y_dir not in obstacles \
                    else alist.insert(i, (alist[i - 1][0] + x_dir, alist[i - 1][1]))
        except IndexError:
            pass

    return list(unique_everseen(alist))


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


def calculate_movement(start, end, obstacles):
    """nicolass ?"""
    # Find 3 consec angles, test bres, if bres, then reedit, else try bresenham 1/3 of the path leading to center angle
    path = list(unique_everseen(AStar(start, end, obstacles).process()))
    corners = []
    for i in range(len(path)):
        if i < len(path) - 2 and (path[i][0] != path[i + 2][0] and path[i][1] != path[i + 2][1]):
            corners.append(path[i + 1])
    ind = []
    for i in corners:
        ind.append(path.index(i))
    ind = [0] + ind + [len(path) - 1]
    alt_paths = []
    for i in range(1, len(ind) - 1):
        br = bresenham(path[ind[i - 1]], path[ind[i + 1]])
        if set(br).isdisjoint(obstacles):
            if set(br).isdisjoint(obstacles):
                alt_paths.append(br)
        else:
            index = (ind[i - 1] + int((ind[i] - ind[i - 1]) * 0.33), ind[i + 1] - int((ind[i + 1] - ind[i]) * 0.33))
            br = bresenham(path[index[0]], path[index[1]])
            if set(br).isdisjoint(obstacles):
                if set(br).isdisjoint(obstacles):
                    alt_paths.append(br)
            else:
                index = (ind[i - 1] + int((ind[i] - ind[i - 1]) * 0.66), ind[i + 1] - int((ind[i + 1] - ind[i]) * 0.66))
                br = bresenham(path[index[0]], path[index[1]])
                if set(br).isdisjoint(obstacles):
                    if set(br).isdisjoint(obstacles):
                        alt_paths.append(br)
    alt_paths = sorted(alt_paths, key=len)[::-1]
    for alt in alt_paths:
        try:
            if len(alt) > 3:
                # noinspection PyTypeChecker
                line = linearize(alt, obstacles)
                # noinspection PyUnresolvedReferences
                path = path[0:path.index(alt[0])] + line + path[path.index(alt[-1]) + 1:]
        except ValueError:
            pass
    return linearize(path, obstacles)


def mouvement(idjoueur, direction, joueurs, MAPS, combat):
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


def commandecarte(message, client, ids, joueurs, combats, MAPS):
    """Cette fonction effectue toute le commandes liés a la carte (mouvement,objets a affichager,...)"""
    if message[0] == "move" and len(message) == 3:
        client.send(mouvement(message[1], message[2], joueurs, MAPS, combats))
    elif message[0] == "connect" and len(message) == 1:
        client.send((str(ids)).encode())
        joueurs[ids] = Joueur(ids)
        map = MAPS.get(joueurs[ids].map)
        map.actif = True
        ids += 1
        map.joueurs[ids] = joueurs[ids]
    elif message[0] == "quitter" and len(message) == 2:
        if message[1] in joueurs:
            joueur = message[1]
            if not joueur.en_combat:
                del MAPS.get(joueur.map).joueurs[joueur.id]

    return ids, joueurs


def commandecombat(message):
    """Cette fonction efffectue toute les commandes liée au combat (attaque,déplacement,...)"""
    pass


class GridCell:
    """
    Represente une case de la carte de jeu

    :param x: -> Coordonnee x de la case
    :param y: -> Coordonnee y de la case
    :param not_obstacle: -> Si la case est traversable par un joueur (pas un mur, rivière, autre obstacle)
    """

    def __init__(self, x, y, not_obstacle):
        self.not_obstacle = not_obstacle
        self.x = x
        self.y = y
        self.parent = None

        self.f = 0
        self.g = 0
        self.h = 0

    """ Les fonctions suivantes permettent à heapq de pouvoir comparer les differentes cases """

    def __eq__(self, other_cell):
        """ Permet case == autre_case """
        return not (self.x, self.y) < (other_cell.x, other_cell.y) and not (other_cell.x, other_cell.y) < (
            self.x, self.y)

    def __ne__(self, other_cell):
        """ Permet case != autre_case """
        return (self.x, self.y) < (other_cell.x, other_cell.y) or (other_cell.x, other_cell.y) < (self.x, self.y)

    def __gt__(self, other_cell):
        """ Permet case > autre_case """
        return (other_cell.x, other_cell.y) < (self.x, self.y)

    def __ge__(self, other_cell):
        """ Permet case >= autre_case """
        return not (self.x, self.y) < (other_cell.x, other_cell.y)

    def __lt__(self, other_cell):
        """ Permet case < autre_case """
        return (other_cell.x, other_cell.y) > (self.x, self.y)

    def __le__(self, other_cell):
        """ Permet case <= autre_case """
        return not (other_cell.x, other_cell.y) < (self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))


class AStar(object):
    """
    Permet de determiner un chemin court entre deux points (start et end) avec l'algorithme A*.
    :param start: -> Coordonnees (x, y) de la case de depart
    :param end: -> Coordonnees (x, y) de la case d'arrivee
    """

    def __init__(self, start, end, obstacles):
        self.open_list = []
        heapify(self.open_list)
        self.closed_list = set()
        self.all_cells = []

        self.grid_height = 18
        self.grid_width = 32
        self.start_x, self.start_y = start
        self.end_x, self.end_y = end
        self.obstacles = obstacles
        self._init_grid()

    def _init_grid(self):
        """
        Initie la representation de la grille, avec prise en compte des obstacles
        """

        """ Parcours la carte en longueur puis en largeur """
        for x in range(1, self.grid_width + 1):
            for y in range(1, self.grid_height + 1):
                not_obstacle = True if (x, y) not in self.obstacles else False
                self.all_cells.append(GridCell(x, y, not_obstacle))

        self.start = self.get_cell(self.start_x, self.start_y)
        self.end = self.get_cell(self.end_x, self.end_y)

    def calculate_h(self, cell):
        """
        :param cell:
        :return: -> Distance Manhattan entre la case visitee actuellement et la case d'arrivee
        """
        return 10 * (abs(cell.x - self.end_x) + abs(cell.y - self.end_y))

    def get_cell(self, x, y):
        """
        :param x: -> Coordonnee x de la case à extraire
        :param y: -> Coordonnee y de la case à extraire
        :return: -> La case à ces coordonnees
        """
        return self.all_cells[(x - 1) * self.grid_height + (y - 1)]

    def get_neighbor_cells(self, cell):
        """
        :param cell: -> Cellule etudiee
        :return: -> Liste de toutes les cases voisines à cette case
        """
        cells = []
        if cell.x < self.grid_width - 1:
            cells.append(self.get_cell(cell.x + 1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y - 1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x - 1, cell.y))
        if cell.y < self.grid_height - 1:
            cells.append(self.get_cell(cell.x, cell.y + 1))
        return cells

    def display_path(self):
        """
        :return path: -> Le chemin entre la première case et la dernière case
        """
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))
        return [(self.start.x, self.start.y)] + path[::-1]

    def update_cell(self, neighbor, cell):
        """
        Met a jour les valeurs de la case voisine
        :param neighbor: -> Un voisin de cette case
        :param cell: -> La case en question
        """
        neighbor.g = cell.g + 10
        neighbor.h = self.calculate_h(neighbor)
        neighbor.parent = cell
        neighbor.f = neighbor.g + neighbor.h

    def process(self):
        """
        Trouve un des plus courts chemins entre la case de depart et celle d'arrivee
        """
        heappush(self.open_list, (self.start.f, self.start))
        while len(self.open_list):
            f, cell = heappop(self.open_list)
            self.closed_list.add(cell)
            if cell is self.end:
                break
            neighbor_cells = self.get_neighbor_cells(cell)
            for n_cell in neighbor_cells:
                if n_cell.not_obstacle and n_cell not in self.closed_list:
                    if (n_cell.f, n_cell) in self.open_list:
                        if n_cell.g > cell.g + 10:
                            self.update_cell(n_cell, cell)
                    else:
                        self.update_cell(n_cell, cell)
                        heappush(self.open_list, (n_cell.f, n_cell))
        return self.display_path()


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
        print("fonction non finie,applayeffect")

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
        valide = False
        while not valide:
            self.group_coords = choice(map.free)
            for i in map.mobsgroupe:
                if i.group_coords != self.group_coords:
                    valide = True

        self.mobgroup = [MOBS.get(choice(map.mobs), randint(map.levelmin, map.levelmax), self.group_coords) for _ in
                         range(randint(2, 8))]
        self.level = 0
        for mob in self.mobgroup:
            self.level += mob.level
        self.timer = 0

    def move(self, map):
        """Cette fonction fait bouger tout les mobs d'un groupe"""
        self.timer = randint(42 * 10, 42 * 30)
        for mob in self.mobgroup[1:]:  # Leader does not move
            action = choice([Mouvements.HAUT, Mouvements.GAUCHE, Mouvements.BAS, Mouvements.DROITE, 'NONE', 'NONE'])
            if action != 'NONE':
                map.move(mob, action)


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
        self.joueurs = {}
        for y in range(len(data["MAP"])):
            for x in range(len(data["MAP"][y])):
                if data["MAP"][y][x] == 1:
                    self.fullobs.append((x, y))
                elif data["MAP"][y][x] == 2:
                    self.semiobs.append((x, y))
                else:
                    self.free.append((x, y))
        self.obstacles = self.semiobs + self.fullobs

    def update(self, MOBS):
        """Fonction appellée a chaque tick qui sert a faire bouger les entitées, a rafraichir les combats et a faire
        apparaitre de nouveaux ennemis"""
        for mobgroup in self.mobsgroups:
            if mobgroup.timer == 0:
                mobgroup.move(self)
            else:
                mobgroup.timer -= 1
        if len(self.mobsgroups) < 3 and len(self.mobs) != 0:
            self.mobsgroups.append(Mobgroup(self, MOBS))
        if len(self.joueurs) == 0:
            self.actif = False
            for mobgroup in self.mobsgroups:
                mobgroup.move(self)

    def move(self, entitee, direction, combat):
        """Cette fonction permet de déplacer une entitée sur la carte"""
        coord = entitee.mapcoords
        if direction == Mouvements.HAUT and coord[1] != 0:
            cible = (coord[0], coord[1] - 1)
        elif direction == Mouvements.BAS and coord[1] != taille_map_y:
            cible = (coord[0], coord[1] + 1)
        elif direction == Mouvements.GAUCHE and coord[0] != 0:
            cible = (coord[0] - 1, coord[1])
        elif direction == Mouvements.DROITE and coord[0] != taille_map_x:
            cible = (coord[0] + 1, coord[1])
        else:
            cible = (coord[0], coord[1])

        if cible not in self.obstacles:
            entitee.mapcoords = cible
            if entitee not in self.mobs:
                for i in self.mobsgroups:
                    if i.group_coords == cible:
                        self.mobsgroups.remove(i)
                        del self.joueurs[entitee.id]
                        entitee.en_combat = True
                        Battle(entitee, i, self, combat)
                        return True
            return False


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


class Entitee:
    """Cette classe représente toute les entitée qui peuvent se déplacer szr la carte. Elle est héritée par joueur et
    par mob"""

    def __init__(self, position):
        self.mapcoords = position


class Mob(Entitee):
    """Classe représanatant un mob"""

    def __init__(self, typemob, level, position):
        super().__init__(position)
        self.name = typemob.name
        self.spells = typemob.spells
        self.maxcaracteristiques = typemob.caracteristiques + typemob.xcaracteristiques * level
        self.actuelcaracteristiques = copy.deepcopy(self.maxcaracteristiques)
        self.idle_anim = typemob.idle_anim
        self.attack_anim = typemob.attack_anim
        self.mouvement_anim = typemob.mouvement_anim
        self.level = level


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


class Battle:
    """Cette classe représente une instance de combat"""

    def __init__(self, players, mobgroup, map, combat):
        self.mobgroup = mobgroup.mobgroup
        self.players = players
        self.map = map
        self.queue = self.players + self.mobgroup
        shuffle(self.queue)
        self.current = self.queue[0]
        combat.append(self)

    # noinspection PyTypeChecker
    def find_target(self, mob):
        """Permet a un mob de choisir sa cible en fonction de critères comme la vie, la distance et le niveau du
        joueur"""
        movements = []
        for player in self.players:
            movement = calculate_movement(mob.mapcoords, player.mapcoords, self.map.obstacles)
            movements += [movement]

        stats = {}
        i = 0
        for player in self.players:
            stats[player] = 1
            stats[player] *= 2 if movements[i] == max(movements) else 1
            stats[player] *= 2 if mob.level > player.level else 1
            stats[player] *= 4 if 0 <= player.hp / player.maxhp < 0.25 else 3 \
                if 0.25 <= player.hp / player.maxhp < 0.5 else 2 if 0.5 <= player.hp / player.maxhp < 0.75 else 1
            i += 1
        # get player
        print("fonction non finie,findtarget")
        path = []
        return path

    def update(self):
        """Fonction appellé a chaque tick"""
        if self.current in self.mobgroup:
            print("fonction non finie,Battle.update")


class Joueur(Entitee):
    """Cette classe représente un joueur connecté au jeu"""

    def __init__(self, id):
        super().__init__((0, 0))
        self.name = ""
        self.spells = []
        self.maxcaracteristiques = caracteristiques(0, 0, 0)
        self.actuelcaracterisiques = copy.deepcopy(self.maxcaracteristiques)
        self.level = 0
        self.map = "(0,0)"
        self.en_combat = False
        self.id = id


def start_server():
    """Fonction servant a initialiser toutes les variables"""
    SPELLS = Spells()
    MAPS = Maps()
    MOBS = Mobs(SPELLS)
    return lire_message(), MAPS, SPELLS, MOBS


def boucle(commandes, MAPS, MOBS, combats, ids, joueurs):
    """Boucle principale du serveur"""
    messages = next(commandes)
    for demande in messages:
        text = demande[0]
        text = text.split(":")
        if len(text) > 2:
            if text[0] == "carte":
                ids, joueurs = commandecarte(text[1:len(text)], demande[1], ids, joueurs, combats, MAPS)
            # if temp[0] == "carte" and len(temp) == 3:
            #         client.send((str(cartes[(int(temp[1]), int(temp[2]))].forme)).encode())
            #
            #     elif temp[0] == "entitee" and len(temp) == 3:
            #         client.send((_entitee(cartes[(int(temp[1]), int(temp[2]))].entites)).encode())
            elif text[0] == "combat":
                commandecombat(text[1:len(text)])

    for i in MAPS.maps.values():
        if i.actif:
            i.update(MOBS)
    for i in combats:
        i.update()

    return ids, joueurs, combats


def main():
    """Fonction principale du programme"""
    commandes, MAPS, SPELLS, MOBS = start_server()
    ids = 0
    joueurs = {}
    combats = []
    while True:
        ids, joueurs, combats = boucle(commandes, MAPS, MOBS, combats, ids, joueurs)
        pygame.time.Clock().tick(42)


main()
