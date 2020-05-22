TANK_MAX_ENERGY = 4
TANK_WIDTH = 0.6

class Tank:
    def __init__(self, name, team):
        self.name = name
        self.hp = 5
        self.enabled = True
        self.energy = TANK_MAX_ENERGY
        self.team = team
        self.strokeColor = "#CCCCCC"
        self.fillColor = "#FFFFFF"

        self.selected = False

        self.x = 0
        self.y = 0
        self.width = TANK_WIDTH;

    def setColors(self, stroke, fill):
        self.strokeColor = stroke
        self.fillColor = fill

    def moveTo(self, x, y):
        self.x = x;
        self.y = y;

    def takeDamage(self, damage):
        self.hp -= damage;
        if self.hp <= 0:
            self.hp = 0
            self.enabled = False
            self.x = -3
            self.y = -3

    def useEnergy(self, energy):
        self.energy -= energy
        if self.energy < 0:
            self.energy = 0
