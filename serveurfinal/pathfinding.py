# coding=utf-8
"""Ce fichier contient tout les éléments liés au calcul de chemin"""
from itertools import filterfalse
from heapq import heapify, heappush, heappop


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
