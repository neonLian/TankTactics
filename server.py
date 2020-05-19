from flask import Flask, render_template
from flask_socketio import SocketIO
import logging

from tile import *
from map import *
from game import *
from tank import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gG...eZ'
app.config['TEMPLATES_AUTO_RELOAD'] = True

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

socketio = SocketIO(app)

map_tiles = []
with open('maps/tunnelrows.map') as mapfile:
    for line in mapfile:
        map_tiles.append([int(x) for x in line.strip()])

game_map = Map(len(map_tiles), len(map_tiles[0]))
# game_map.setTile(3, 3, tileType["solid"])
# game_map.setTile(3, 4, tileType["solid"])
game_map.tiles = map_tiles


game = Game(game_map)
# courtyard.map
# team1_spawns = [
#     [6,1], [7,1], [8,1],
#     [6,2], [7,2], [8,2]
# ]
# team2_spawns = [
#     [5,13], [6,13], [7,13],
#     [5,14], [6,14], [7,14]
# ]

# tunnelrows.map
team1_spawns = [[y, 1] for y in range(2, 8)]
team2_spawns = [[17, x] for x in range(10,16)]

for i in range(6):
    t = game.newTank("Tank " + str(i+1), 0)
    t.x = team1_spawns[i][0]
    t.y = team1_spawns[i][1]
for i in range(6):
    t = game.newTank("Tank " + str(i+4), 1)
    t.x = team2_spawns[i][0]
    t.y = team2_spawns[i][1]

game.zoneObjectives += [
    [(1, 11, 3),(9, 0, 3)],
    [(16, 7, 3),(9, 17, 3)]
]

@app.route('/')
def sessions():
    return render_template('game.html')

@socketio.on('syncData')
def sync():
    socketio.emit('syncData', currentSyncData())

@socketio.on('move')
def move(msg):
    canMove = False
    if game.map.tiles[msg["x"]][msg["y"]] == tileType["empty"]:
        t = game.tanks[msg["tank"]]
        path = game.shortestPath(t.x, t.y, msg["x"], msg["y"])
        canMove = len(path) > 0 and len(path) <= t.energy
    if canMove:
        print(t.energy)
        t.moveTo(msg["x"], msg["y"]);
        t.energy -= len(path);
        socketio.emit('syncData', currentSyncData(), broadcast=True)

@socketio.on('checkMove')
def checkMove(msg):
    print("Received check move check")
    canMove = False
    if game.map.tiles[msg["x"]][msg["y"]] == tileType["empty"]:
        t = game.tanks[msg["tank"]]
        path = game.shortestPath(t.x, t.y, msg["x"], msg["y"])
        canMove = len(path) > 0 and len(path) <= t.energy
    print("Sending move check results")
    socketio.emit('checkMove', {"path": path, "canMove": canMove})

@socketio.on('shoot')
def shoot(msg):
    print("Received shoot message")
    t = game.tanks[int(msg['shooter'])]
    print(t.energy)
    if t.energy < 2:
        return
    # Rounding is to fix floating point division errors
    x2 = round(msg['toX'], 3)
    y2 = round(msg['toY'], 3)
    check1 = round((x2 % 1), 3) >= round((1 - TANK_WIDTH)/2, 3)
    check2 = round((x2 % 1), 3) <= round(TANK_WIDTH+(1 - TANK_WIDTH)/2, 3)
    check3 = round((y2 % 1), 3) >= round((1 - TANK_WIDTH)/2, 3)
    check4 = round((y2 % 1), 3) <= round(TANK_WIDTH+(1 - TANK_WIDTH)/2, 3)
    isTargetingTank = check1 and check2 and check3 and check4
    if isTargetingTank:
        # print("Targeted tank")
        targetTank = None
        for o in game.tanks:
            if (o.x == int(x2) and o.y == int(y2)):
                targetTank = o
                break
        if targetTank is not None:
            if t.team != targetTank.team:
                # print("Found target tank")
                canShoot = game.canShoot(t.x+0.5, t.y+0.5, msg['toX'], msg['toY'])
                if canShoot:
                    print("Registering shot...")
                    t.useEnergy(2)
                    print(t.energy)
                    targetTank.takeDamage(2)
                    socketio.emit('syncData', currentSyncData(), broadcast=True)
                else:
                    print("Not a clear shot!")
            else:
                print("Same team!")
        else:
            print("Not targeting tank tile")
    else:
        print("Not targeting tank (" + str(x2) + ", " + str(y2) + ")")

@socketio.on('nextTurn')
def nextTurn(msg):

    game.nextTurn()
    print("Next turn")
    socketio.emit('syncData', currentSyncData(), broadcast=True)

@socketio.on('checkShot')
def checkShot(msg):
    x2 = msg['toX']
    y2 = msg['toY']
    isTargetingTank = (x2 % 1) >= 1 - TANK_WIDTH and (x2 % 1) <= TANK_WIDTH and \
                      (y2 % 1) >= 1 - TANK_WIDTH and (y2 % 1) <= TANK_WIDTH
    if isTargetingTank:
        canShoot = game.canShoot(msg['fromX'], msg['fromY'], msg['toX'], msg['toY'])
    else:
        canShoot = False
    socketio.emit('checkShot', {"canShoot": canShoot, "targetingTank": isTargetingTank})

@socketio.on('checkTankShot')
def checkTankShot(msg):
    x2 = msg['toX']
    y2 = msg['toY']
    t = None
    for tank in game.tanks:
        if tank.x == floor(x2) and tank.y == floor(y2):
            t = tank
            break
    canShoot = False
    targetLoc = (x2, y2)
    if t != None:
        targets = [
            (t.x + 0.5, t.y + 0.5),  # center
            (t.x + (1-TANK_WIDTH)/2, t.y + (1-TANK_WIDTH)/2),  # top left
            (t.x + TANK_WIDTH+(1-TANK_WIDTH)/2, t.y + (1-TANK_WIDTH)/2),  # top right
            (t.x + (1-TANK_WIDTH)/2, t.y + TANK_WIDTH+(1-TANK_WIDTH)/2),  # bottom left
            (t.x + TANK_WIDTH+(1-TANK_WIDTH)/2, t.y + TANK_WIDTH+(1-TANK_WIDTH)/2),  # bottom right
        ]
        for target in targets:
            if game.canShoot(msg['fromX'], msg['fromY'], target[0], target[1]):
                targetLoc = target
                canShoot = True
                break
    socketio.emit('checkTankShot', {"canShoot": canShoot, "targetLoc": targetLoc})

def currentSyncData():
    return {"map": game_map.tiles, "tanks": game.getTanksJson(),
            "teams": {"names": game.teamNames, "colors": game.teamColors, "scores": game.teamScores},
            "zoneObjectives": game.zoneObjectives,
            "turnNumber": game.turnNumber, "turnPlayer": game.turnPlayer}

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=False)
