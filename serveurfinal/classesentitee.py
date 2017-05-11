# coding=utf-8
"""Ce fichier continent toute les classe liées aux entitées, au maps ou au mobs. Il crée aussi les constantes MAPS,MOBS
et SPELLS a partir des fichiers json"""
from json import load
from enum import Enum, auto
from random import choice, randint, shuffle
from codecs import open as c_open
from pathfinding import *
from copy import deepcopy
from typing import Dict

taille_map_x = 32
taille_map_y = 18


class Mouvements(Enum):
    """Cette enumeration represente les differents mouvements qui peuvent être fait"""
    HAUT = auto(),
    BAS = auto(),
    GAUCHE = auto(),
    DROITE = auto(),
    ERREUR = auto()


class Entitee:
    """Cette classe représente toute les entitée qui peuvent se déplacer szr la carte. Elle est héritée par joueur et
    par mob"""

    def __init__(self, position: Tuple[int, int]):
        self.mapcoords = position


class Map:
    """Cette classe représente une carte du jeu"""

    def __init__(self, data: Dict):
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

    def update(self, combats: List):
        """Fonction appellée a chaque tick qui sert a faire bouger les entitées, a rafraichir les combats et a faire
        apparaitre de nouveaux ennemis"""
        for mobgroup in self.mobsgroups:
            if mobgroup.timer == 0:
                mobgroup.move(self, combats)
            else:
                mobgroup.timer -= 1
        if len(self.mobsgroups) < 3 and len(self.mobs) != 0:
            self.mobsgroups.append(Mobgroup(self))
        if len(self.joueurs) == 0:
            self.actif = False
            for mobgroup in self.mobsgroups:
                mobgroup.move(self, combats)

    def move(self, entitee: Entitee, direction: Mouvements, combat: List) -> bool:
        """Cette fonction permet de déplacer une entitée sur la carte"""
        coord = entitee.mapcoords
        if direction == Mouvements.HAUT and coord[1] != 0:
            cible = (coord[0], coord[1] - 1)
        elif direction == Mouvements.BAS and coord[1] != (taille_map_y - 1):
            cible = (coord[0], coord[1] + 1)
        elif direction == Mouvements.GAUCHE and coord[0] != 0:
            cible = (coord[0] - 1, coord[1])
        elif direction == Mouvements.DROITE and coord[0] != (taille_map_x - 1):
            cible = (coord[0] + 1, coord[1])
        else:
            cible = (coord[0], coord[1])

        if cible not in self.obstacles:
            entitee.mapcoords = cible
            if isinstance(entitee, Joueur):
                for i in self.mobsgroups:
                    if i.group_coords == cible:
                        self.mobsgroups.remove(i)
                        del self.joueurs[entitee.id]
                        entitee.en_combat = True
                        Battle([entitee], i, self, combat)
                        return True
            return False


class Mobgroup:
    """Cette classe représente un groupe de mobs """

    def __init__(self, map: Map):
        valide = False
        while not valide:
            self.group_coords = choice(map.free)
            valide = True
            for i in map.mobsgroups:
                if i.group_coords == self.group_coords:
                    valide = False

        self.mobgroup = [MOBS.get(choice(map.mobs), randint(map.levelmin, map.levelmax), self.group_coords) for _ in
                         range(randint(2, 8))]
        self.level = 0
        for mob in self.mobgroup:
            self.level += mob.level
        self.timer = 1

    def move(self, map: Map, combat: List):
        """Cette fonction fait bouger tout les mobs d'un groupe"""
        self.timer = randint(42 * 1, 42 * 10)
        for mob in self.mobgroup[1:]:  # Leader does not move
            action = choice([Mouvements.HAUT, Mouvements.GAUCHE, Mouvements.BAS, Mouvements.DROITE, 'NONE', 'NONE'])
            if action != 'NONE':
                map.move(mob, action, combat)


class TypeMob:
    """Cette classe représente une catégorie de mob"""

    def __init__(self, data: Dict):
        self.name = data['NAME']
        self.spells = [SPELLS.get(spell_id) for spell_id in data['SPELLS']]
        self.idle_anim = data['IDLE']
        self.attack_anim = data['ATTACK']
        self.mouvement_anim = data['MOVEMENT']
        self.caracteristiques = Caracteristiques(data['BASEHP'], data['MOVEMENTPOINTS'], data['ACTIONPOINTS'])
        self.xcaracteristiques = Caracteristiques(data['XHP'], 0, 0)


class Mob(Entitee):
    """Classe représanatant un mob"""

    def __init__(self, typemob: TypeMob, level: int, position: Tuple[int, int]):
        super().__init__(position)
        self.name = typemob.name
        self.spells = typemob.spells
        self.maxcaracteristiques = typemob.caracteristiques + typemob.xcaracteristiques * level
        self.actuelcaracteristiques = deepcopy(self.maxcaracteristiques)
        self.idle_anim = typemob.idle_anim
        self.attack_anim = typemob.attack_anim
        self.mouvement_anim = typemob.mouvement_anim
        self.level = level


class Battle:
    """Cette classe représente une instance de combat"""

    def __init__(self, players: List, mobgroup: Mobgroup, map: Map, combat: List):
        self.mobgroup = mobgroup.mobgroup
        self.players = []
        for i in players:
            self.players.append(i)
        self.map = map
        self.queue = self.players + self.mobgroup
        shuffle(self.queue)
        self.current = self.queue[0]
        combat.append(self)

    # noinspection PyTypeChecker
    def find_target(self, mob: Mob) -> List:
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

    def get(self, map_id: str) -> Map:
        """Cette fonction permet de recupere une carte en fonction de son id"""
        return self.maps[map_id]


class Mobs:
    """Classe contenant la liste de tout les mobs"""

    def __init__(self):
        json_file = c_open("mobs.json", encoding='utf-8')
        file_mobs = load(json_file)
        json_file.close()
        self.mobs = {}
        for ids in file_mobs:
            if ids != '_template':
                self.mobs[ids] = TypeMob(file_mobs[ids])

    def get(self, mob_id: str, level: int, position: Tuple[int, int]) -> Mob:
        """Permet de récuperer un mob grace a son id"""
        return Mob(self.mobs[mob_id], level, position)


class Spell:
    """Cette classe permet de définir un sort et d'appliquer ses effets"""

    def __init__(self, name: str, damage: int, cost: int, shape: str, spell_type: str, max_range: int, min_range: int,
                 reload: int, aoe, aoe_range, aoe_shape, effects):
        self.name = name
        self.damage = damage
        self.cost = cost
        self.shape = shape
        self.spellType = spell_type
        self.maxRange = int(max_range)
        self.minRange = min_range
        self.reload = int(reload)
        self.aoe = bool(aoe)
        self.aoeRange = aoe_range
        self.aoeShape = aoe_shape
        self.effects = effects

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
                                         file_spells[ids]['EFFECTS'])

    def get(self, spell_id: str) -> Spell:
        """Cette fonction permet de réuperer un sort grace a son id"""
        return self.spells[spell_id]


class Caracteristiques:
    """Cette classe représente les caactéristiques de combat d'un mob ou d'un joueur"""

    def __init__(self, hp: int, mp: int, ap: int):
        self.hp = hp
        self.mp = mp
        self.ap = ap

    def __add__(self, autre):
        return Caracteristiques(self.hp + autre.hp, self.mp + autre.mp, self.ap + autre.ap)

    def __mul__(self, autre):
        return Caracteristiques(self.hp * autre, self.mp * autre, self.ap * autre)

    def __rmul__(self, autre):
        return self * autre


class Joueur(Entitee):
    """Cette classe représente un joueur connecté au jeu"""

    def __init__(self, id: int):
        super().__init__((31, 4))
        self.name = ""
        self.spells = []
        self.maxcaracteristiques = Caracteristiques(0, 0, 0)
        self.actuelcaracterisiques = deepcopy(self.maxcaracteristiques)
        self.level = 0
        self.map = "(0,0)"
        self.en_combat = False
        self.id = id
        self.classe = "001"


SPELLS = Spells()
MAPS = Maps()
MOBS = Mobs()
