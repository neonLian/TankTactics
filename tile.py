import enum

class TileType(enum.Enum):
    Empty = 1
    Solid = 2
    Half = 3
    Hole = 4
    
class Tile:
    def __init__(self, x: int, y: int, type: TileType):
        self.x = x
        self.y = y

        self.type = type

        self.top = None
        self.left = None
