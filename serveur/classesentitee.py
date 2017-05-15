# coding=utf-8
"""Ce fichier continent toute les classe liees aux entitees, au maps ou au mobs. Il cree aussi les constantes MAPS, MOBS
et SPELLS a partir des fichiers json"""
from json import load
from enum import Enum, auto
from random import choice, randint, shuffle, random
from codecs import open as c_open
from pathfinding import *
from copy import deepcopy
from typing import Dict, List, Tuple
from math import sqrt

taille_map_x = 32
taille_map_y = 18


class Mouvements(Enum):
    """Cette enumeration represente les differents mouvements qui peuvent être fait"""
    HAUT = auto()
    BAS = auto()
    GAUCHE = auto()
    DROITE = auto()
    ERREUR = auto()


class Phase(Enum):
    """ Represente les différentes phases de combat """
    targeting = auto()
    movement = auto()
    attack = auto()
    end = auto()


class Entitee:
    """Cette classe représente toute les entitée qui peuvent se déplacer szr la carte. Elle est héritée par joueur et
    par mob"""

    def __init__(self, position: Tuple[int, int], max_vie: int, max_mp: int, max_ap: int):
        self.map_coords = position
        self.combat_coords = None
        self.max_attributs = Caracteristiques(max_vie, max_mp, max_ap)
        self.var_attributs = deepcopy(self.max_attributs)
        self.combat = None


class Map:
    """Cette classe represente une carte du jeu"""

    def __init__(self, data: Dict):
        self.actif = False
        self.semiobs = []
        self.fullobs = []
        self.free = []
        self.mobs = [mob_id for mob_id in data["MOBS"]]
        self.levelmax = data['LEVELMAX']
        self.levelmin = data['LEVELMIN']
        self.group_number = data['GROUP_NUMBER']
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

    def update(self):
        """Fonction appellée a chaque tick qui sert a faire bouger les entitées, a rafraichir les combats et a faire
        apparaitre de nouveaux ennemis"""
        for mobgroup in self.mobsgroups:
            if mobgroup.timer == 0:
                mobgroup.move(self)
            else:
                mobgroup.timer -= 1
        if len(self.mobsgroups) < self.group_number and len(self.mobs) != 0:
            self.mobsgroups.append(Mobgroup(self))
        if len(self.joueurs) == 0:
            self.actif = False
            for mobgroup in self.mobsgroups:
                mobgroup.move(self)

    def move(self, entitee: Entitee, direction: Mouvements, combat: List = [], leader=None) -> bool:
        """Cette fonction permet de déplacer une entitée sur la carte"""
        coord = entitee.map_coords
        coords = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        if direction == Mouvements.HAUT and coord[1] != 0:
            cible = tuple_add(coord, coords[0])
        elif direction == Mouvements.BAS and coord[1] != (taille_map_y - 1):
            cible = tuple_add(coord, coords[2])
        elif direction == Mouvements.GAUCHE and coord[0] != 0:
            cible = tuple_add(coord, coords[1])
        elif direction == Mouvements.DROITE and coord[0] != (taille_map_x - 1):
            cible = tuple_add(coord, coords[3])
        else:
            cible = coord

        if cible not in self.obstacles:
            if isinstance(entitee, Joueur):
                entitee.map_coords = cible
                for i in self.mobsgroups:
                    if i.group_coords == cible:
                        self.mobsgroups.remove(i)
                        del self.joueurs[entitee.id]
                        entitee.en_combat = True
                        Battle([entitee], i, self, combat)
                        return True
            elif isinstance(entitee, Mob):
                odds = 1 / (
                    2 ** (sqrt((leader.map_coords[0] - cible[0]) ** 2 + (leader.map_coords[1] - cible[1]) ** 2) - 1))
                if odds > random():
                    entitee.map_coords = cible
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

    def move(self, map: Map):
        """Cette fonction fait bouger tout les mobs d'un groupe"""
        self.timer = randint(42 * 5, 42 * 10)
        for mob in self.mobgroup[1:]:  # Leader does not move
            action = choice([Mouvements.HAUT, Mouvements.GAUCHE, Mouvements.BAS, Mouvements.DROITE])
            map.move(mob, action, leader=self.mobgroup[0])


class Battle:
    """Cette classe represente une instance de combat"""

    def __init__(self, players, mobgroup, map, combat):
        self.mobgroup = mobgroup.mobgroup
        for mob in self.mobgroup:
             mob.combat = self
        self.players = players
        self.map = map
        self.queue = self.players + self.mobgroup
        shuffle(self.queue)
        self.current = self.queue[0]
        self.phase = Phase.targeting
        self.target = None
        self.path = []
        combat.append(self)
        for i in self.mobgroup:
            valide = False
            cible = (-1, -1)
            while not valide:
                cible = choice(map.free)
                valide = True
                for j in self.mobgroup:
                    if cible == j.combat_coords:
                        valide = False
            i.combat_coords = cible

        for i in self.players:
            valide = False
            cible = (-1, -1)
            while not valide:
                cible = choice(map.free)
                valide = True
                for j in self.mobgroup:
                    if cible == j.combat_coords:
                        valide = False
                for j in self.players:
                    if cible == j.combat_coords:
                        valide = False
            i.combat_coords = cible
        for i in self.players:
            i.combat = self

    def update(self):
        """ Fonction appelle a chaque tick, effectuant un calcul """
        if self.current in self.mobgroup:
            if self.phase == Phase.end:
                self.end_turn()
                self.target = None
                self.path = []
                self.phase = Phase.targeting
            elif self.phase == Phase.attack:
                self.attack()
                self.phase = Phase.end
            elif self.phase == Phase.movement:
                self.movement(int(sum(self.get_ranges()) / 2))
                self.phase = Phase.attack
            elif self.phase == Phase.targeting:
                self.target, self.path = self.find_target()
                self.phase = Phase.movement

    def end_turn(self):
        """Indique le prochain joueur"""
        self.current = self.queue[(self.queue.index(self.current) + 1) % len(self.queue)]
        self.current.var_attributs.ap = self.current.max_attributs.ap
        self.current.var_attributs.mp = self.current.max_attributs.mp

    def move(self, entitee: Entitee, direction: Mouvements):
        """Cette fonction permet de déplacer une entitée sur la carte"""
        if entitee.var_attributs.mp > 0:
            entitee.var_attributs.mp -= 1
            coord = entitee.combat_coords
            coords = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            if direction == Mouvements.HAUT and coord[1] != 0:
                cible = tuple_add(coord, coords[0])
            elif direction == Mouvements.BAS and coord[1] != (taille_map_y - 1):
                cible = tuple_add(coord, coords[2])
            elif direction == Mouvements.GAUCHE and coord[0] != 0:
                cible = tuple_add(coord, coords[1])
            elif direction == Mouvements.DROITE and coord[0] != (taille_map_x - 1):
                cible = tuple_add(coord, coords[3])
            else:
                cible = coord

            if cible not in self.map.obstacles:
                valide = True
                for i in self.mobgroup:
                    if i.combat_coords == cible:
                        valide = False
                for i in self.players:
                    if i.combat_coords == cible:
                        valide = False
                if valide:
                    entitee.combat_coords = cible
                    return True
        return False

    # noinspection PyTypeChecker
    def find_target(self):
        """Permet a un mob de choisir sa cible en fonction de parametres comme la vie, la distance et le niveau du
        joueur"""
        movements = {}
        for player in self.players:
            movements[player] = calculate_movement(self.current.map_coords, player.map_coords, self.map.obstacles)

        stats = {}
        for player in self.players:
            stats[player] = 1
            stats[player] *= 2 if len(movements[player]) == min([len(mov) for mov in movements.values()]) else 1
            stats[player] *= 2 if self.current.level > player.level else 1
            stats[player] *= 4 if 0 <= player.var_attributs.hp / player.max_attributs.hp < 0.25 else 3 \
                if 0.25 <= player.var_attributs.hp / player.max_attributs.hp < 0.5 \
                else 2 if 0.5 <= player.var_attributs.hp / player.max_attributs.hp < 0.75 else 1
        player = list(stats.keys())[list(stats.values()).index(max(stats.values()))]
        path = movements[player]
        print("Mob", self.current.name, 'targets Player')
        print("PATH:", path)
        return player, path

    def get_ranges(self):
        """ :return: Portée minimale et maximale des attques du mob """
        maxs, mins = [], []
        for spell in self.current.spells:
            maxs += [spell.max_range]
            mins += [spell.min_range]
        return min(mins), max(maxs)

    def movement(self, dist):
        """ Effectue le déplacement sur la map """

        for i in range(0, min([len(self.path), dist])):
            self.move(self.current, compare_tuple(self.path[i], self.path[i + 1]))


    # def spell_range(self, spell):
    #     """ En fonction du type de sort, renvoie les cases touchees """
    #     if spell.shape == 'SPLASH':
    #         return self.splash(self.current.map_coords, spell.minRange, spell.maxRange)
    #     if isinstance(spell, LineSpell):
    #         return self.line(self.current, spell.minRange, spell.maxRange)
    # 
    # def splash(self, center: Tuple[int, int], minRange: int, maxRange: int) -> List[Tuple[int, int]]:
    #     """ Si le sort a une zone d'attaque circulaire autour de l'entite """
    #     aoe = [(0, maxRange), (maxRange, 0), (0, -maxRange), (-maxRange, 0)]
    #     aoe = [tuple_add(a, center) for a in aoe]
    #     over = bresenham(aoe[3], aoe[2])[:-1] + bresenham(aoe[2], aoe[1])
    #     under = bresenham(aoe[3], aoe[0])[:-1] + bresenham(aoe[0], aoe[1])
    #     out = over + under
    #     for ind in range(len(over) - 2):
    #         x, y = over[ind + 1]
    #         dist = under[ind + 1][1] - y
    #         for i in range(dist):
    #             out.append((x, y + i))
    #     out = list(remove_duplicates(out))
    #     for c in out:
    #         if c[0] < 0 or c[0] > 31 or c[1] < 0 or c[1] > 17:
    #             out.remove(c)
    #     edge = over + under
    #     for e in edge:
    #         br = bresenham(center, e)
    #         if not set(br).isdisjoint(self.map.fullobs):
    #             intersects_at = list(set(br).intersection(self.map.fullobs))
    #             closest = distances(center, intersects_at)
    #             try:
    #                 remove = br[br.index(closest):]
    #                 for r in remove:
    #                     out.remove(r)
    #             except ValueError:
    #                 pass
    #     if minRange != 0:
    #         for c in self.splash(center, 0, minRange):
    #             out.remove(c)
    #     return out
    # 
    # def line(self, center: Tuple[int, int], minRange: int, maxRange: int) -> List[Tuple[int, int]]:
    #     """ Si le sort a une zone d'attaque lineaire depuis l'entite """
    #     aoe = [(0, maxRange), (maxRange, 0), (0, -maxRange), (-maxRange, 0)]
    #     aoe = [tuple_add(a, center) for a in aoe]
    #     out = []
    #     for a in aoe:
    #         out += bresenham(center, a)
    #     for c in out:
    #         if c[0] < 0 or c[0] > 31 or c[1] < 0 or c[1] > 17:
    #             out.remove(c)
    #     if minRange != 0:
    #         for c in line(center, 0, minRange):
    #             try:
    #                 out.remove(c)
    #             except ValueError:
    #                 pass
    #     for o in aoe:
    #         br = bresenham(center, o)
    #         if not set(br).isdisjoint(self.map.fullobs):
    #             intersects_at = list(set(br).intersection(self.map.fullobs))
    #             closest = distances(center, intersects_at)
    #             try:
    #                 remove = br[br.index(closest):]
    #                 for r in remove:
    #                     out.remove(r)
    #             except ValueError:
    #                 pass
    #     return out

    def attack(self):
        """ Choisit soit d'attquer soit d'aider ses allies et effectue cette action """
        attack_spells = []
        assist_spells = {}
        allies = {ally.map_coords: ally for ally in self.mobgroup}
        for spell in self.current.spells:
            if spell.verif_conditions(self.current, self.target.combat_coords) and\
                            spell.spellType != 'SUPPORT':
                attack_spells.append(spell)
            if spell.spellType == 'SUPPORT' and not set(allies.keys()).isdisjoint(range):
                intersects_at = set(allies.keys()).intersection(range)
                assist_spells[spell] = [[allies[c] for c in intersects_at], range]
        most = 0
        assist_spell = 0
        for spell, r in assist_spells.items():
            if len(r[0]) > most:
                most = len(r[0])
                assist_spell = spell

        odds = most / len(self.mobgroup)
        if assist_spell in assist_spells.keys():
            assist_spells = assist_spells[assist_spell]
            odds *= sum([mob.var_attributs.hp / mob.max_attributs.hp for mob in assist_spells[0]]) / len(assist_spells[0])
            if odds > random():
                self.apply_effect(assist_spell.effects, choice(assist_spells[0]))
        elif len(attack_spells) > 0:
            available_mana = self.current.var_attributs.ap
            while True:
                spell = choice(attack_spells)
                available_mana -= spell.cost
                if available_mana >= 0:
                    self.apply_effect(spell.effects, self.target)
                else:
                    break

    def apply_effect(self, effects: Dict[str, int], target):
        """ Applique un effet (perte de vie par exemple) a la cible """
        for key, value in effects.items():
            if key == 'HP':
                target.var_attributs.hp += value
            if key == 'AP':
                target.var_attributs.ap += value
            if key == 'MP':
                target.var_attributs.mp += value


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
    """Classe represanatant un mob"""

    def __init__(self, typemob: TypeMob, level: int, position: Tuple[int, int]):
        super().__init__(position, typemob.caracteristiques.hp + typemob.xcaracteristiques.hp * level,
                         typemob.caracteristiques.mp + typemob.xcaracteristiques.mp * level,
                         typemob.caracteristiques.ap + typemob.xcaracteristiques.ap * level)
        self.name = typemob.name
        self.spells = typemob.spells
        self.idle_anim = typemob.idle_anim
        self.attack_anim = typemob.attack_anim
        self.mouvement_anim = typemob.mouvement_anim
        self.level = level


class Maps:
    """Cette classe contient la liste de toute les cartes du jeu"""

    def __init__(self):
        json_file = c_open("maps.json", encoding='utf-8')
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
    """Cette classe abstraite est héritée par tout les sorts"""

    def __init__(self, name: str, cost: int, spell_type: str, reload: int, effects: Dict):
        self.name = name
        self.cost = cost
        self.spellType = spell_type
        self.reload = int(reload)
        self.effects = effects

    def verif_conditions(self, joueur, cible):
        """Cette fonction détermine si le sort est valide"""
        return False


class LineSpell(Spell):
    """Cette classe représente un sort lancé en ligne droite"""

    def __init__(self, name: str, cost: int, spell_type: str, reload: int, effects: Dict, forme: Dict):
        super().__init__(name, cost, spell_type, reload, effects)
        self.max_range = forme["MAXRANGE"]
        self.min_range = forme["MINRANGE"]

    def verif_conditions(self, entitee, cible):
        """Cette fonction détermine si le sort est valide"""
        if entitee.var_attributs.ap > self.cost:
            if entitee.combat_coords[0] == cible[0]:
                if not (self.max_range >= abs(entitee.combat_coords[1] - cible[1]) >= self.min_range):
                    return False
            elif entitee.combat_coords[1] == cible[1]:
                if not (self.max_range >= abs(entitee.combat_coords[0] - cible[0]) >= self.min_range):
                    return False
            else:
                return False
            cases_traversee = bresenham(entitee.combat_coords, cible)
            for i in cases_traversee:
                if i in entitee.combat.map.fullobs:
                    return False
            entitee.var_attributs.ap -= self.cost
            return True
        return False


class SplashSpell(Spell):
    # Agit comme LineSpell -> FloError
    """Cette classe représente un sort lancé en ligne droite"""

    def __init__(self, name: str, cost: int, spell_type: str, reload: int, effects: Dict, forme: Dict):
        super().__init__(name, cost, spell_type, reload, effects)
        self.max_range = forme["MAXRANGE"]
        self.min_range = forme["MINRANGE"]

    def verif_conditions(self, entitee, cible):
        """Cette fonction détermine si le sort est valide"""
        if entitee.var_attributs.ap > self.cost:
            if entitee.combat_coords[0] == cible[0]:
                if not (self.max_range >= abs(entitee.combat_coords[1] - cible[1]) >= self.min_range):
                    return False
            elif entitee.combat_coords[1] == cible[1]:
                if not (self.max_range >= abs(entitee.combat_coords[0] - cible[0]) >= self.min_range):
                    return False
            else:
                return False
            cases_traversee = bresenham(entitee.combat_coords, cible)
            for i in cases_traversee:
                if i in entitee.combat.map.fullobs:
                    return False
            entitee.var_attributs.ap -= self.cost
            return True
        return False


class Spells:
    """Cette classe contient la liste de tout les sorts du jeu"""

    def __init__(self):
        json_file = c_open("spells.json", encoding='utf-8')
        file_spells = load(json_file)
        json_file.close()
        self.spells = {}
        for ids in file_spells:
            if ids != '_template':
                if file_spells[ids]['SHAPE']["SHAPE"] == "LINE":
                    self.spells[ids] = LineSpell(file_spells[ids]['NAME'], file_spells[ids]['COST'],
                                                 file_spells[ids]['TYPE'], file_spells[ids]['RELOAD'],
                                                 file_spells[ids]['EFFECTS'], file_spells[ids]['SHAPE'])

    def get(self, spell_id: str):
        """
        Cette fonction permet de recuperer un sort grace a son id
        :param spell_id: -> Identifiant de sort
        :return: -> Le sort
        """
        return self.spells[spell_id]


class Classe:
    """Cette classe permet de definir un sort et d'appliquer ses effets"""

    def __init__(self, name: str, spells: Dict, basehp: int, xhp: int, mouvement_point: int, action_point: int,
                 id: str):
        self.name = name
        self.spells = spells
        self.caracteristiques = Caracteristiques(basehp, mouvement_point, action_point)
        self.xcaracteristiques = Caracteristiques(xhp, 0, 0)
        self.id = id

    def __str__(self):
        return self.id


class Classes:
    """Cette classe contient la liste de tout les sorts du jeu"""

    def __init__(self):
        json_file = c_open("classes.json", encoding='utf-8')
        file_classes = load(json_file)
        json_file.close()
        self.classes = {}
        for ids in file_classes:
            if ids != '_template':
                self.classes[ids] = Classe(file_classes[ids]['NAME'],
                                           file_classes[ids]['SPELLS'], file_classes[ids]['BASEHP'],
                                           file_classes[ids]['XHP'], file_classes[ids]['MOVEMENTPOINTS'],
                                           file_classes[ids]["ACTIONPOINTS"], ids)

    def get(self, classe_id: str):
        """Permet de récupérer une classe a partir de son id"""
        return self.classes[classe_id]


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
    """Cette classe represente un joueur connecte au jeu"""

    def __init__(self, id: int):
        super().__init__((31, 4), 150, 3, 150)
        self.name = ""
        self.spells = []
        self.level = 0
        self.map = "(0,0)"
        self.id = id
        self.classe = CLASSES.get("001")

def compare_tuple(depart: Tuple[int, int], arrivee: Tuple[int, int]):
    """Cette fonction permet de voir dans quelle direction il faut aller pour passer d'un tuple a l'autre"""
    if depart[0] - arrivee[0] == 1:
        return Mouvements.GAUCHE
    elif depart[0] - arrivee[0] == -1:
        return Mouvements.DROITE
    elif depart[1] - arrivee[1] == 1:
        return Mouvements.HAUT
    elif depart[1] - arrivee[1] == -1:
        return Mouvements.BAS
    else:
        raise ValueError("Les deux tuples ne sont pas adjacents")

SPELLS = Spells()
MAPS = Maps()
MOBS = Mobs()
CLASSES = Classes()
