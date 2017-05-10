class Mob:
    def __init__(self, data, SPELLS):
        self.name = data['NAME']
        self.spells = [SPELLS.get(spell_id) for spell_id in data['SPELLS']]
        self.maxhp = data['BASEHP']
        self.hp = self.maxhp
        self.maxmp = data['MOVEMENTPOINTS']
        self.mp = self.maxmp
        self.maxap = data['ACTIONPOINTS']
        self.ap = self.maxap
        self.idle_anim = data['IDLE']
        self.attack_anim = data['ATTACK']
        self.movement_anim = data['MOVEMENT']
        self.level = 0
        self.mapcoords = (0, 0)

    def move(self, free, leader):
        """
        Déplace les mobs
        :param free: -> cases libres sur la carte
        """
        action = choice(['UP', 'LEFT', 'DOWN', 'RIGHT'])
        coords = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        odds = 0
        if action == 'UP':
            coords = tuple_add(self.mapcoords, coords[0])
            odds = 1 / (2**(abs(leader.mapcoords[0] - coords[0]) + abs(leader.mapcoords[1] - coords[1])))
        elif action == 'LEFT':
            coords = tuple_add(self.mapcoords, coords[1])
            odds = 1 / (2**(abs(leader.mapcoords[0] - coords[0]) + abs(leader.mapcoords[1] - coords[1])))
        elif action == 'DOWN':
            coords = tuple_add(self.mapcoords, coords[2])
            odds = 1 / (2**(abs(leader.mapcoords[0] - coords[0]) + abs(leader.mapcoords[1] - coords[1])))
        elif action == 'RIGHT':
            coords = tuple_add(self.mapcoords, coords[3])
            odds = 1 / (2**(abs(leader.mapcoords[0] - coords[0]) + abs(leader.mapcoords[1] - coords[0])))
        if coords in free and odds > random():
            print(self.name, self.mapcoords, odds)
            self.mapcoords = coords

class IdleHandler:
    def __init__(self, MOBGROUPS, MAPS, MOBS, SPELLS):
        self.MOBGROUPS = MOBGROUPS
        self.MAPS = MAPS.maps
        self.MOBS = MOBS
        self.SPELLS = SPELLS
        self.mobgroup_count = {k : 0 for k in list(self.MAPS.values())}

    def __update__(self):
        self.mobgroups = self.MOBGROUPS.mobgroups
        for mobgroup in self.mobgroups:
            if mobgroup.timer == 0:
                mobgroup.move()
            else:
                mobgroup.timer -= 1
        for _map, value in self.mobgroup_count.items():
            if value < 3:
                self.MOBGROUPS.generate(_map, self.MOBS, self.SPELLS)
                self.mobgroup_count[_map] += 1

    def battle_launched(self, _map, mobgroup):
        # Commencer bataille
        # Enlever le mobgroup de la carte
        self.mobgroup_count[_map] -= 1

class BattleHandler:
    class Battle:
        def __init__(self, playergroup, mobgroup, _map):
            self.mobgroup = mobgroup.mobgroup
            self.playergroup = playergroup
            self._map = _map
            self.queue = self.playergroup + self.mobgroup
            shuffle(self.queue)
            self.current = self.queue[0]

        def find_target(self):
            movements = []
            pmovements = {}
            for player in self.playergroup:
                movement = calculate_movement(self.current.mapcoords, player.mapcoords, self._map.obstacles)[:-1]
                pmovements[player] = movement
                movements += [movement]
            stats = {}
            i = 0
            for player in self.playergroup:
                stats[player] = 1
                stats[player] *= 2 if movements[i] == max(movements) else 1
                stats[player] *= 2 if self.current.level > player.level else 1
                stats[player] *= 4 if 0 <= player.hp/player.maxhp < 0.25 else\
                                3 if 0.25 <= player.hp/player.maxhp < 0.5 else\
                                2 if 0.5 <= player.hp/player.maxhp < 0.75 else 1
                i += 1
            player = list(stats.keys())[list(stats.values()).index(max(stats.values()))]
            path = pmovements[player]
            return player, path

        def attack_phase(self, path):
            self.current.move(self._map.free, self.mobgroup.leader)


    def __init__(self):
        self.battles = []

    def __update__(self):
        for battle in self.battles:
            if battle.current in battle.mobgroup:
                target, path = battle.find_target()
                #battle.attack_phase(path)
				

def remove_duplicates(iterable, key=None):
    """
    Renvoie un generateur sur un iterable qui enleve tous les elements en double dans une liste, conservant l'ordre.
    :param iterable:
    :param key:
    :return:
    """
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

def tuple_add(tuple1, tuple2):
    return tuple([x+y for x, y in zip(tuple1, tuple2)])

class GridCell(object):
    def __init__(self, x, y, not_obstacle):
        """
        Represente une case de la carte de jeu

        :param x: -> Coordonnee x de la case
        :param y: -> Coordonnee y de la case
        :param not_obstacle: -> Si la case est traversable par un joueur (pas un mur / riviere / tour de sauron
        """
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
    def __init__(self, start, end, obstacles):
        """
        Permet de determiner un chemin court entre deux points (start et end) avec l'algorithme A*.
        :param start: -> Coordonnees (x, y) de la case de depart
        :param end: -> Coordonnees (x, y) de la case d'arrivee
        """

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

def linearize(alist, obstacles):
    """
    Remplit l'espace entre deux cases non consecutives
    :param alist: -> Liste de coordonnees du chemin
    :param obstacles: -> Liest de coordonnees des obstacles
    :return: -> Une liste linearisee
    """
    y_dir = 1 if alist[0][1] < alist[-1][1] else -1
    x_dir = 1 if alist[0][0] < alist[-1][0] else -1
    list2 = []
    for i in range(1, len(alist) + 1):
        try:
            list2.append(alist[i-1])
            if alist[i - 1][0] != alist[i][0] and alist[i - 1][1] != alist[i][1]:
                if (alist[i - 1][0], alist[i - 1][1] + y_dir) not in obstacles:
                    list2.append((alist[i - 1][0], alist[i - 1][1] + y_dir))
                elif (alist[i - 1][0] + x_dir, alist[i - 1][1]) not in obstacles:
                    list2.append((alist[i - 1][0] + x_dir, alist[i - 1][1]))
        except IndexError:
            continue

    return list(remove_duplicates(list2))

def calculate_movement(start, end, obstacles):
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
            if len(alt) > 3:
                line = linearize(alt, obstacles)
                path = path[0:path.index(alt[0])] + line + path[path.index(alt[-1]) + 1:]
        except ValueError:
            pass
    return linearize(path, obstacles)
