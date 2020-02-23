from tank import *
from map import *
from util import *
from math import floor, ceil

class Game:
    def __init__(self, map):
        self.tanks = []
        self.map = map
        self.teamColors = {"Cobalt": ["#080163", "#0a0096"], "Vermillion": ["#cf2b1d", "#E34234"]}

    def newTank(self, name: str, team: int):
        tank = Tank(name, team)
        tank.setColors(list(self.teamColors.values())[team][0], list(self.teamColors.values())[team][1])
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
        return True

    def shortestPath(self, x1, y1, x2, y2):
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
