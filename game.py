from tank import *
from map import *
from util import *
from math import floor, ceil

from queue import PriorityQueue


POINTS_TO_WIN = 8

class Game:
    def __init__(self, map):
        self.tanks = []
        self.map = map
        self.defaultTeamNames = ["Cobalt", "Vermillion"]
        self.teamNames = list(self.defaultTeamNames)
        self.teamColors = [["#080163", "#0a0096"], ["#cf2b1d", "#E34234"]]
        self.teamScores = [0, 0]

        self.pathfinding = {
            "dist": {},
            "prev": {},
            "source": None
        }

        self.turnNumber = 1
        self.turnPlayer = 0

        # Contains one list per team, each team has tuples (x, y, w) where x and y are
        # top left corner coordinates and w is the width of the zone
        self.zoneObjectives = []

        self.winner = -1

    def nextTurn(self):
        # Calculate objective points
        for objTeam in range(len(self.zoneObjectives)):
            if objTeam == self.turnPlayer: continue
            for obj in self.zoneObjectives[objTeam]:
                numTanks = [0, 0]
                for t in self.tanks:
                    if t.x >= obj[0] and t.x < obj[0] + obj[2] and \
                       t.y >= obj[1] and t.y < obj[1] + obj[2]:
                       numTanks[t.team] += 1
                if numTanks[self.turnPlayer] > 0 and numTanks[self.turnPlayer] > numTanks[objTeam]:
                    self.teamScores[self.turnPlayer] += 1

        # Change turn
        self.turnNumber += 1
        if (self.turnPlayer == 0):
            self.turnPlayer = 1
        else:
            self.turnPlayer = 0

        # Reset tank energy
        for t in self.tanks:
            if t.team == self.turnPlayer:
                t.energy = TANK_MAX_ENERGY
            else:
                t.energy = 0

    def checkWinner(self):
        # Objective win
        for team in range(len(self.teamScores)):
            if self.teamScores[team] >= POINTS_TO_WIN:
                self.winner = team
                print("Objective win for " + str(team))
                return team

        # Elimination win
        tanksAlive = [0, 0]
        for t in self.tanks:
            if t.hp > 0:
                tanksAlive[t.team] += 1
        print(tanksAlive)
        if tanksAlive[0] >= 0 and tanksAlive[1] <= 0:
            self.winner = 0
            print("Elimination win for 0")
            return 0
        elif tanksAlive[0] <= 0 and tanksAlive[1] >= 0:
            self.winner = 1
            print("Elimination win for 1")
            return 1


        self.winner = -1
        return -1




    def newTank(self, name: str, team: int):
        tank = Tank(name, team)
        tank.setColors(self.teamColors[team][0], self.teamColors[team][1])
        self.tanks.append(tank)
        return tank

    def getTanksJson(self):
        out = []
        for t in self.tanks:
            out.append(vars(t))
        return out

    def canShoot(self, x1, y1, x2, y2):
        if x1 < 0 or x1 >= len(self.map.tiles) or x2 < 0 or x2 >= len(self.map.tiles) or y1 < 0 or y1 >= len(self.map.tiles[0]) or y2 < 0 or y2 >= len(self.map.tiles[0]):
            return False
        for row in range(floor(min(x1, x2)), ceil(max(x1, x2))):
            for col in range(floor(min(y1, y2)), ceil(max(y1, y2))):
                if (self.map.tiles[row][col] == tileType["solid"]):
                    tileIntersect = intersectSquare((x1, y1), (x2, y2), row, col, 1)
                    if tileIntersect:
                        return False
        for t in self.tanks:
            if t.x == floor(x1) and t.y == floor(y1): continue
            if t.x == floor(x2) and t.y == floor(y2): continue

            if intersectSquare((x1, y1), (x2, y2), t.x + (1-TANK_WIDTH)/2, t.y + (1-TANK_WIDTH)/2, TANK_WIDTH):
                return False
        return True

    def calculatePaths(self, x1, y1):
        self.pathfinding["dist"] = {}
        self.pathfinding["prev"] = {}
        self.pathfinding["source"] = (x1, y1)

        pq = PriorityQueue()
        pq.put( (0, (x1,y1)) )
        self.pathfinding["dist"][(x1, y1)] = 0
        while not pq.empty():
            cur = pq.get()[1]
            x = cur[0]
            y = cur[1]

            others = [
                            (x, y-1),
                (x-1, y),             (x+1, y),
                            (x, y+1),
                (x-1, y-1),           (x+1, y-1),
                (x-1, y+1),           (x+1, y+1)
            ]
            connected = []
            for o in others:
                if o[0] >= 0 and o[0] < len(self.map.tiles) and o[1] >= 0 and o[1] < len(self.map.tiles[0]):
                        if self.map.tiles[o[0]][o[1]] == tileType["empty"]:
                            hasTank = False
                            for t in self.tanks:
                                if o[0] == t.x and o[1] == t.y:
                                    hasTank = True
                                    break
                            if not hasTank:
                                connected.append(o)
            for o in connected:
                if  o not in self.pathfinding["dist"] or \
                    self.pathfinding["dist"][o] > self.pathfinding["dist"][cur] + 1:

                    d = self.pathfinding["dist"][cur] + 1;
                    self.pathfinding["dist"][o] = d;
                    self.pathfinding["prev"][o] = cur;
                    if d <= TANK_MAX_ENERGY:
                        pq.put( (d, o) )
        print("Finished calculating paths for root " + str((x1, y1)))
        # print("prev: " + str(self.pathfinding["prev"]))
        # print("dist: " + str(self.pathfinding["dist"]))


    def shortestPath(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return []
        source = self.pathfinding["source"]
        if source is None or (source[0] != x1 or source[1] != y1):
            self.calculatePaths(x1, y1)
        path = []
        current = (x2, y2)
        while True:
            if ((current[0] == x1) and (current[1] == y1)) or current in self.pathfinding["prev"]:

                # print(str(current) + " " + str(path))
                # print(self.pathfinding["prev"][current])
                if (current[0] == x1) and (current[1] == y1):
                    # print(str(current) + " is source node (" + x1 + ", " + y1 + ")")
                    return path
                path.insert(0, current)
                current = self.pathfinding["prev"][current]
            else:
                return []


    def shortestPathOld(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return []
        visited = [[None]*len(self.map.tiles[0]) for x in [None]*len(self.map.tiles)]
        queue = []
        queue.append([x1, y1])
        path = []
        while len(queue) > 0:
            current = queue.pop(0)
            x = current[0]
            y = current[1]
            if x == x2 and y == y2:
                path = []
                while True:
                    if x == x1 and y == y1:
                        break
                    path.insert(0, [x, y])
                    prev = visited[x][y]
                    x = prev[0]
                    y = prev[1]
                queue = []
            else:
                others = [
                    [x-1, y-1], [x, y-1], [x+1, y-1],
                    [x-1, y],             [x+1, y],
                    [x-1, y+1], [x, y+1], [x+1, y+1]
                ]
                for o in others:
                    if o[0] >= 0 and o[0] < len(self.map.tiles) and o[1] >= 0 and o[1] < len(self.map.tiles[0]):
                        if (o[0] != x1 or o[1] != y1) and visited[o[0]][o[1]] is None:
                            if self.map.tiles[o[0]][o[1]] == 1:
                                queue.append(o)
                                visited[o[0]][o[1]] = [x, y]
        return path
