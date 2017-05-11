# coding=utf-8
"""Ce fichier contient tout les éléments liés au calcul de chemin"""
from heapq import heapify, heappush, heappop
from typing import Tuple, List


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
        self.start_x, self.start_y = start
        self.end_x, self.end_y = end
        self.obstacles = obstacles
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
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))
        return [(self.start.x, self.start.y)] + path[::-1]

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


# noinspection PyUnresolvedReferences
def calculate_movement(start: Tuple, end: Tuple, obstacles: List[Tuple]):
    """
    Calcule le chemin entre une case de depart et une case d'arrivee, par une linearisation de l'Algorithme A*
    :param start: -> Coordonnees de la case de depart
    :param end: -> Coordonnees de la case d'arrivee
    :param obstacles: -> Obstacles sur la carte
    :return:
    """
    path = list(remove_duplicates(AStar(start, end, obstacles).process()))
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
            if len(alt) > 5:  # MODIFIED
                line = linearize(alt, obstacles)
                path = path[0:path.index(alt[0])] + line + path[path.index(alt[-1]) + 1:]
        except ValueError:
            pass
    return linearize(path, obstacles)
