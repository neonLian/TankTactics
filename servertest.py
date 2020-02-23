from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ggez'
socketio = SocketIO(app)
speed = 25;
rectX = 100;
rectY = 100;

@app.route('/')
def sessions():
    return render_template('servertest.html')

@socketio.on('move')
def move(json):
    global socketio, rectX, rectY
    if json['direction'] == "up":
        rectY -= speed;
    if json['direction'] == "down":
        rectY += speed;
    socketio.emit('moveResponse', {"rectX": rectX, "rectY": rectY})

@socketio.on('syncData')
def sync():
    socketio.emit('syncData', {"rectX": rectX, "rectY": rectY})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
