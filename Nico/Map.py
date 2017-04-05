from pprint import pprint
from random import sample, randint

class Mob:
    def __init__(self, name, level):
        self.name = name
        self.level = level


class Map:
    class MobGroup:
        def __init__(self, map):
            main = Mob(sample(map.map_mobs, 1)[0], map.map_level)
            other = sample(map.map_mobs*3, randint(1, 7))
            self.mobs = [main] + [Mob(other[i], map.map_level - randint(1, 5)) for i in range(len(other))]
            self.tick_counter = 0
            self.level = sum([mob.level for mob in self.mobs])

        def spawn(self, coords):
            pass
            # Spawn at coords on map

        def update(self):
            if self.tick_counter <= 0:
                self.tick_counter = randint(60, 300)
                for mob in self.mobs[1:]:
                    movement = randint(1, 8)
                    if movement == 1:
                        pass
                        # UP
                        print("MOB:", mob.name, "goes UP")
                    elif movement == 2:
                        pass
                        # LEFT
                        print("MOB:", mob.name, "goes LEFT")
                    elif movement == 3:
                        pass
                        # DOWN
                        print("MOB:", mob.name, "goes DOWN")
                    elif movement == 4:
                        pass
                        # RIGHT
                        print("MOB:", mob.name, "goes RIGHT")
                    else:
                        pass
                        # print("MOB:", mob.name, "does nothing")
            else:
                self.tick_counter -= 5 # Number of ticks from server tick
                print(self.tick_counter)

    def __init__(self, map_id):
        self.map_id = map_id
        self.map_data = [l.replace('\n', '') for l in open("MAP" + map_id + ".txt").readlines()]
        self.map = self.map_data[:22]
        self.map_level = int(self.map_data[23])
        self.map_mobs = self.map_data[25:29]
        self.free = []
        self.obstacles = []

        for line in range(1, len(self.map) - 1):
            for row in range(1, len(self.map[line]) - 1):
                if self.map[line][row] == '_':
                    self.free.append((row, line))
                elif self.map[line][row] == 'x':
                    self.obstacles.append((row, line))

        """
        print('\nObstacles : ')
        pprint(self.obstacles)
        """

map = Map('0001')
mg = Map.MobGroup(map)
print([mob.name + " " + str(mob.level) for mob in mg.mobs])
for i in range(600):
    mg.update()