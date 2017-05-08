import asyncio
from json import load
from codecs import open as c_open
from random import choice, randint, shuffle
from itertools import filterfalse
from heapq import heapify, heappush, heappop

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

def unique_everseen(iterable, key=None):
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

class GridCell:
    def __init__(self, x, y, not_obstacle):
        """
        Represente une case de la carte de jeu

        :param x: -> Coordonnee x de la case
        :param y: -> Coordonnee y de la case
        :param not_obstacle: -> Si la case est traversable par un joueur (pas un mur, rivière, autre obstacle)
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

def linearize(alist, obstacles):
    y_dir = 1 if alist[0][0]-alist[-1][0] > 0 else -1
    x_dir = 1 if alist[0][1]-alist[-1][1] > 0 else -1
    for i in range(1, len(alist) * 2 - 2):
        try:
            if alist[i-1][0] != alist[i][0] and alist[i-1][1] != alist[i][1]:
                alist.insert(i, (alist[i-1][0], alist[i-1][1] + y_dir)) \
                    if alist[i-1][1] + y_dir not in obstacles \
                    else alist.insert(i, (alist[i-1][0] + x_dir, alist[i-1][1]))
        except IndexError:
            pass

    return list(unique_everseen(alist))

def calculate_movement(start, end, obstacles):
    # Find 3 consec angles, test bres, if bres, then reedit, else try bresenham 1/3 of the path leading to center angle
    path = list(unique_everseen(AStar(start, end, obstacles).process()))
    corners = []
    for i in range(len(path)):
        if i < len(path) - 2 and (path[i][0] != path[i+2][0] and path[i][1] != path[i+2][1]):
            corners.append(path[i+1])
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
            index = (ind[i-1] + int((ind[i] - ind[i-1])*0.33), ind[i+1] - int((ind[i+1] - ind[i])*0.33))
            br = bresenham(path[index[0]], path[index[1]])
            if set(br).isdisjoint(obstacles):
                if set(br).isdisjoint(obstacles):
                    alt_paths.append(br)
            else:
                index = (ind[i-1] + int((ind[i] - ind[i-1])*0.66), ind[i+1] - int((ind[i+1] - ind[i])*0.66))
                br = bresenham(path[index[0]], path[index[1]])
                if set(br).isdisjoint(obstacles):
                    if set(br).isdisjoint(obstacles):
                        alt_paths.append(br)
    alt_paths = sorted(alt_paths, key=len)[::-1]
    for alt in alt_paths:
        try:
            if len(alt) > 3:
                line = linearize(alt, obstacles)
                path = path[0:path.index(alt[0])] + line + path[path.index(alt[-1])+1:]
        except ValueError:
            pass
    return linearize(path, obstacles)

class Spell:
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
    def __init__(self):
        json_file = c_open("spells.json", 'r', 'utf-8')
        file_spells = load(json_file)
        json_file.close()
        self.spells = {}
        for id in file_spells:
            if id != '_template':
                self.spells[id] = Spell(file_spells[id]['NAME'], file_spells[id]['DAMAGE'], file_spells[id]['COST'], file_spells[id]['SHAPE'], file_spells[id]['TYPE'], file_spells[id]['ATTACKMAXRANGE'],
                        file_spells[id]['ATTACKMINRANGE'], file_spells[id]['RELOAD'], file_spells[id]['AOE'], file_spells[id]['AOERANGE'], file_spells[id]['AOESHAPE'],
                         file_spells[id]['EFFECTS'], file_spells[id]['SELFCAST'])

    def get(self, spell_id : str):
        return self.spells[spell_id]

class Map:
    def __init__(self, data):
        self.semiobs = []
        self.fullobs = []
        self.free = []
        self.mobs = [mob_id for mob_id in data["MOBS"]]
        self.level = data['LEVEL']
        for y in range(len(data["MAP"])):
            for x in range(len(data["MAP"][y])):
                if data["MAP"][y][x] == 1:
                    self.fullobs.append((x, y))
                elif data["MAP"][y][x] == 2:
                    self.semiobs.append((x, y))
                else:
                    self.free.append((x, y))
        self.obstacles = self.semiobs + self.fullobs

class Maps:
    def __init__(self):
        self.size = (32, 18)
        json_file = open("maps.json")
        file_maps = load(json_file)
        json_file.close()
        self.maps = {}
        for id in file_maps:
            if id != '_template':
                self.maps[id] = Map(file_maps[id])

    def get(self, map_id : str):
        return self.maps[map_id]

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

    def move(self, free):
        """
        Déplace les mobs
        :param free: -> cases libres sur la carte
        """
        action = choice(['UP', 'LEFT', 'DOWN', 'RIGHT', 'NONE', 'NONE'])
        coords = (0, 0)
        if action == 'UP':
            coords = (self.mapcoords[0], self.mapcoords[1] - 1)
        elif action == 'LEFT':
            coords = (self.mapcoords[0] - 1, self.mapcoords[1])
        elif action == 'DOWN':
            coords = (self.mapcoords[0], self.mapcoords[1] + 1)
        elif action == 'RIGHT':
            coords = (self.mapcoords[0] + 1, self.mapcoords[1])
        if coords in free and action != 'NONE':
            self.mapcoords = coords
            print(coords)

class Mobs:
    def __init__(self):
        json_file = c_open("mobs.json", 'r', 'utf-8')
        self.file_mobs = load(json_file)
        json_file.close()

    def get(self, mob_id : str, SPELLS):
        return Mob(self.file_mobs[mob_id], SPELLS)

class Mobgroup:
    def __init__(self, _map, MOBS, SPELLS):
        self.assigned_map = _map
        self.mobgroup = [MOBS.get(choice(self.assigned_map.mobs), SPELLS) for i in range(randint(2, 8))]
        self.level = 0
        group_coords = choice(_map.free)
        for mob in self.mobgroup:
            mob.level = randint(self.assigned_map.level, self.assigned_map.level + 5)
            mob.mapcoords = group_coords
            self.level += mob.level
        self.timer = 0

    def move(self):
        self.timer = randint(42*10, 42*30)
        print('New Timer', self.timer/42, 'Mobcount', len(self.mobgroup))
        for mob in self.mobgroup[1:]: # Leader does not move
            mob.move(self.assigned_map.free)

class Mobgroups:
    def __init__(self, MAPS):
        self.mobgroups = []
        self.MAPS = MAPS

    def generate(self, _map, MOBS, SPELLS):
        self.mobgroups.append(Mobgroup(_map, MOBS, SPELLS))

class Player:
    def __init__(self, SPELLS, spells, hp, mp, ap, level, coords):
        self.spells = [SPELLS.get(spell_id) for spell_id in spells]
        self.maxhp = hp
        self.hp = self.maxhp
        self.maxmp = mp
        self.mp = self.maxmp
        self.maxap = ap
        self.ap = self.maxap
        self.level = level
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

        def find_target(self, mob):
            movements = []
            for player in self.playergroup:
                movement = calculate_movement(mob.mapcoords, player.mapcoords, self._map.obstacles)
                movements += [movement]

            stats = {}
            i = 0
            for player in self.playergroup:
                stats[player] = 1
                stats[player] *= 2 if movements[i] == max(movements) else 1
                stats[player] *= 2 if mob.level > player.level else 1
                stats[player] *= 4 if 0 <= player.hp/player.maxhp < 0.25 else\
                                3 if 0.25 <= player.hp/player.maxhp < 0.5 else\
                                2 if 0.5 <= player.hp/player.maxhp < 0.75 else 1
                i += 1
            print(stats)
            #get player 
            path = []
            return path

    def __init__(self):
        self.battles = []

    def __update__(self):
        for battle in self.battles:
            if battle.current in battle.mobgroup:
                target = battle.find_target(battle.current)
                print(battle.current, target)

def start_server():
    SPELLS = Spells()
    MOBS = Mobs()
    MAPS = Maps()
    MOBGROUPS = Mobgroups(MAPS)
    idle_handler = IdleHandler(MOBGROUPS, MAPS, MOBS, SPELLS)
    battle_handler = BattleHandler()
    return idle_handler, battle_handler

SPELLS = Spells()
MAPS = Maps()
MOBS = Mobs()
_map = MAPS.get('(0,0)')
bh = BattleHandler()
ba = bh.Battle([Player(SPELLS, ['001', '002'], 200, 100, 3, 6, (10, 10)),
                Player(SPELLS, ['001', '002'], 180, 100, 3, 5, (31, 14))],
               Mobgroup(_map, MOBS, SPELLS), _map)
bh.battles.append(ba)

async def ticker(delay, to):
    for i in range(42*to):
        yield i
        await asyncio.sleep(delay)

async def run(number: int):
    async for i in ticker(0.02381, number):
        bh.__update__()

idle_handler, battle_handler = start_server()
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run(1000))
finally:
    loop.close()


"""
def update(idle_handler, battle_handler):
    idle_handler.__update__()
    battle_handler.__update__()


async def ticker(delay, to):
    for i in range(42*to):
        yield i
        await asyncio.sleep(delay)

async def run(number: int, idle_handler, battle_handler):
    async for i in ticker(0.02381, number):
        update(idle_handler, battle_handler)

idle_handler, battle_handler = start_server()
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run(3000, idle_handler, battle_handler))
finally:
    loop.close()
"""
