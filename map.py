tileType = {
    "empty": 1,
    "solid": 2,
    "half": 3,
    "hole": 4
}

class Map:
    def __init__(self, w: int, h: int):
        self.tiles = [];
        for row in range(h):
            self.tiles.append([])
            for col in range(w):
                self.tiles[row].append(tileType["empty"])

        self.name = "";

    def getTile(self, x: int, y: int):
        return self.tiles[x][y]

    def setTile(self, x: int, y: int, type: int):
        self.tiles[x][y] = type
