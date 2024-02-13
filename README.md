# TankTactics
A 2D turn based tactics/strategy game with tanks

## How to start server

To start the server, run `server.py` with python. By default it will open on port 5000. To play the game, go to your IP address at port 5000 in your browser:

`http://<your IP address>:5000`

## Dependencies
The server runs on Python 3 using flask and SocketIO. It is very important to get the exact version of flask-socketio below or it might not work.

A `requirements.txt` file is in the repository to install the correct versions easily. Use the below command to install flask and socketio with the necessary versions:
```
pip install -r requirements.txt
```

Python modules:
```
flask
flask-socketio==4.3
gevent-socketio
```

## How to play
Learn how to play TankTactics here: https://docs.google.com/document/d/1ly9lh8qnriQrqWU6vsNoSh7yAaOpZFHahgXtHfhiv-g/edit?usp=sharing
