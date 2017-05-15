# coding=utf-8
"""Ce fichier contient tout les éléments liés au calcul de chemin"""
from itertools import filterfalse
from heapq import heapify, heappush, heappop
from typing import Tuple, List
from math import sqrt


def tuple_add(tuple1: Tuple, tuple2: Tuple) -> Tuple:
    """Cette fonction permet d'additionner deux tuples"""
    return tuple([x + y for x, y in zip(tuple1, tuple2)])


def remove_duplicates(iterable, key=None):
    """
    Renvoie un generateur sur un iterable qui enleve tous les elements en double dans une liste, conservant l'ordre."""
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def linearize(path: List, obstacles: List[Tuple]) ->List:
    """
    Remplit l'espace entre deux cases non consecutives
    :param path: -> Liste de coordonnees du chemin
    :param obstacles: -> Liste de coordonnees des obstacles
    :return: -> Une liste linearisee
    """
    y_dir = 1 if path[0][1] < path[-1][1] else -1
    x_dir = 1 if path[0][0] < path[-1][0] else -1
    list2 = []
    for i in range(1, len(path) + 1):
        try:
            list2.append(path[i - 1])
            if path[i - 1][0] != path[i][0] and path[i - 1][1] != path[i][1]:
                if (path[i - 1][0], path[i - 1][1] + y_dir) not in obstacles:
                    list2.append((path[i - 1][0], path[i - 1][1] + y_dir))
                elif (path[i - 1][0] + x_dir, path[i - 1][1]) not in obstacles:
                    list2.append((path[i - 1][0] + x_dir, path[i - 1][1]))
        except IndexError:
            continue

    return list(remove_duplicates(list2))


def bresenham(player: Tuple, end: Tuple)->List:
    """ Algorithme de Bresenham
    Prend en entree deux tuples de coordonnees et indique les cases traversees par une ligne passant de l'une à l'autre
    :param player:
    :param end:
    """
    x1, y1 = player
    x2, y2 = end
    # Derivees
    dx = x2 - x1
    dy = y2 - y1

    # Verification de l'inclinaison de pente
    slope = abs(dy) > abs(dx)

    # Si trop inclinee. rotation de la pente
    if slope:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Inverse les coordonnees en x et y si necessaire
    switched = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        switched = True

    # Recalcul des derivees
    dx = x2 - x1
    dy = y2 - y1

    # Calcul de l'erreur
    error = int(dx / 2.0)
    y_step = 1 if y1 < y2 else -1

    # Itere par dessus les cases generant les points traverses entre le joueur et la fin de sa visibilite
    y = y1
    crossed_points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if slope else (x, y)
        crossed_points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx

    # Inversion de la liste si les points originaux ont etes inverses
    if switched:
        crossed_points.reverse()
    return list(remove_duplicates(crossed_points))


def calculate_movement(start: Tuple, end: Tuple, obstacles: List[Tuple]):
    """
    Calcule le chemin entre une case de depart et une case d'arrivee, par une linearisation de l'Algorithme A*
    :param start: -> Coordonnees de la case de depart
    :param end: -> Coordonnees de la case d'arrivee
    :param obstacles: -> Obstacles sur la carte
    :return:
    """
    path = list(remove_duplicates(AStar(start, end, obstacles).process()))
    try:
        corners = []
        for i in range(len(path)):
            if i < len(path) - 2 and (path[i][0] != path[i + 2][0] and path[i][1] != path[i + 2][1]):
                corners.append(path[i + 1])
        corners = [start] + corners + [end]
        ind = []
        for i in corners:
            ind.append(path.index(i))
        alt_paths = []
        for i in range(1, len(ind) - 1):
            br = linearize(bresenham(path[ind[i - 1]], path[ind[i + 1]]), obstacles)
            if set(br).isdisjoint(obstacles):
                alt_paths.append(br)
            else:
                index = (ind[i - 1] + int((ind[i] - ind[i - 1]) * 0.5), ind[i + 1] - int((ind[i + 1] - ind[i]) * 0.5))
                br = bresenham(path[index[0]], path[index[1]])
                if set(br).isdisjoint(obstacles):
                    alt_paths.append(br)
        alt_paths = sorted(alt_paths, key=len)[::-1]
        for alt in alt_paths:
            try:
                if len(alt) > 5:
                    line = linearize(alt, obstacles)
                    path = path[0:path.index(alt[0])] + line + path[path.index(alt[-1]) + 1:]
            except ValueError:
                pass

        return linearize(path, obstacles)
    except ValueError:
        return path


class GridCell(object):
    """
    Represente une case de la carte de jeu

    :param x: -> Coordonnee x de la case
    :param y: -> Coordonnee y de la case
    :param not_obstacle: -> Si la case est traversable par un joueur (pas un mur / riviere / tour de sauron
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
    def __init__(self, start: Tuple, end: Tuple, obstacles: List[Tuple]):
        self.open_list = []
        heapify(self.open_list)
        self.closed_list = set()
        self.all_cells = []

        self.grid_height = 18
        self.grid_width = 32
        self.start_x, self.start_y = tuple_add(start, (1, 1))
        self.end_x, self.end_y = tuple_add(end, (1, 1))
        self.obstacles = [tuple_add(o, (1, 1)) for o in obstacles]
        self._init_grid()

    def _init_grid(self):
        """
        Initie la representation de la grille, avec prise en compte des obstacles
        """

        """ Parcoure la carte en longueur puis en largeur """
        for x in range(1, self.grid_width + 1):
            for y in range(1, self.grid_height + 1):
                not_obstacle = True if (x, y) not in self.obstacles else False
                self.all_cells.append(GridCell(x, y, not_obstacle))

        self.start = self.get_cell(self.start_x, self.start_y)
        self.end = self.get_cell(self.end_x, self.end_y)

    def calculate_h(self, cell: GridCell):
        """
        :param cell:
        :return: -> Distance Manhattan entre la case visitee actuellement et la case d'arrivee
        """
        return 10 * (abs(cell.x - self.end_x) + abs(cell.y - self.end_y))

    def get_cell(self, x: int, y: int):
        """
        :param x: -> Coordonnee x de la case à extraire
        :param y: -> Coordonnee y de la case à extraire
        :return: -> La case à ces coordonnees
        """
        return self.all_cells[(x - 1) * self.grid_height + (y - 1)]

    def get_neighbor_cells(self, cell: GridCell):
        """
        :param cell: -> Cellule etudiee
        :return: -> Liste de toutes les cases voisines à cette case
        """
        cells = []
        if cell.x < self.grid_width:
            cells.append(self.get_cell(cell.x + 1, cell.y))
        if cell.y > 1:
            cells.append(self.get_cell(cell.x, cell.y - 1))
        if cell.x > 1:
            cells.append(self.get_cell(cell.x - 1, cell.y))
        if cell.y < self.grid_height:
            cells.append(self.get_cell(cell.x, cell.y + 1))
        return cells

    def display_path(self):
        """
        :return path: -> Le chemin entre la premiere case et la derniere case
        """
        cell = self.end
        path = [(cell.x - 1, cell.y - 1)]
        if cell.parent is not None:
            while cell.parent is not self.start:
                cell = cell.parent
                path.append((cell.x - 1, cell.y - 1))
            return [(self.start.x - 1, self.start.y - 1)] + path[::-1]
        else:
            return []

    def update_cell(self, neighbor: GridCell, cell: GridCell):
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


def distances(center: Tuple[int, int], values: List[Tuple[int, int]]) -> Tuple[int, int]:
    smallest = None
    small = 100
    for c in values:
        d = int(sqrt((c[0]-center[0])**2+(c[1]-center[1])**2))
        if d < small:
            small = d
            smallest = c
    return smallest
