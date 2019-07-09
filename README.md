### Singleplayer / Multiplayer Game of 21 (Eenentwintgen) in Python, Flask-API, SocketIO and HTML/CSS

### Eenentwintgen / Twenty-One

Twenty-One is a card game in which a player tries to reach a total of 21 points (without exceeding this) - the value of ace is 1 or 11. The game seems to be quite old, as the spanish version (veintiuna) was first mentioned by Miguel de Cervantes between 1601-1602 [source: wikipedia](https://en.wikipedia.org/wiki/Blackjack), so it was most likely been played even before then. The rules are a little bit different to Blackjack in that players place their bets after receiving their first card. Once everyone has placed their bets, they get a second card and the game begins.

The code is free and you can download it here: [Eenentwintigen](https://github.com/andrejlukic/blackjack/tree/Eenentwintigen)

You can play around with the live demo here: [Eenentwintigen live demo](http://crunchymebumblebee.org/)

![multiplayer version](https://github.com/andrejlukic/blackjack/blob/master/docs/15_multiplayer_game_play.png "Multiplayer gameplay")

### Application

You can play as one player against the dealer or with another person against the dealer (backend should support N players but the UI supports only 2 players). Not all of the game options were implemented - for example there is no split, double-down or insurance. 

#### Singleplayer
Simply enter your name and press the button *Play*, then add the amount that you want to bet (each player starts with 1000€ by default).

#### Multiplayer (2 players)
One player has to start the game and then other players may join: 
+ First player: check the Multiplayer checkbox and click the button *Start new game* then wait ... 
+ Second player: check the Multiplayer checkbox and click the button *Join existing game*. You should see a list of all active multiplayer games with the names of the players that started them. After you select a game, the betting round will start so that each of the players can place bets. The game will start with the player who started the multiplayer game. You will know that it is your turn when two buttons pop up (Hit or Stand).

After each round the game will restart automatically with the betting round. You will see the result of the previous game on the right side in a simple text log output.

### Requirements & Installation

Python 3.6 (flask, flask_socketio, jsonpickle, json, glob, random, uuid) 

#### Dev environment

Simply download the files and run python main.py to play the command line vesion or run python game21_api.py to start the Flask server and then hit 127.0.0.1:88 from any web browser. You should see an empty bootstrap page template with a simple form to start the game. You can change the url to whatever you like, but you have to do it in two places - in game21_api.py and in templates/cards.html.

Note: if you are tired of always running dev environment, it is also possible to wrap it as a service, but it is not recommended to run it like this in production environment (I have included an example config at the end of this document)

#### Production - Nginx as reverse proxy and Flask-API via Gunicorn

For production environment you can use Nginx as reverse proxy and then a Gunicorn/uWSGI server on the backend. I will post examples of config files at the end of this readme.

Note: I am using Python 3 and I think at the moment if you install Gunicorn it will use Python 2 by default, but you can install gunicorn3 package and it will use the correct version

Note: I had also tried using uWSGI but I had problems with SSL handshake, for which there supposedly is a solution but I didn't try it out.

### The code

I was thinking about a simple way to add UI and since I had just recently discovered [SocketIO](https://socket.io/) I wanted to try that. The basic architecture is a Python backend exposed with Flask-API with SocketIO support and a simple web page with SocketIO to exchange messages between the client and the server. I was very lucky to have found HTML+CSS code for drawing the cards from [Juha Lindtstedt](https://medium.com/@pakastin/javascript-playing-cards-part-2-graphics-cd65d331ad00) for which I am very grateful.

+ *game21.py* - game logic split into the following classes:
  + Game21
  + Player, PlayerGame21, PlayerGame21House
  + Decks: stores N decks of cards and shuffling 
  + Game21Card
+ *main.py* - logic for playing game via a command line interface
+ *game21_api.py* - logic for playing game via a web interface
+ *templates/cards.html* - web game UI using JQuery and SocketIO for communication with the backend. The code for the communication is embedded inside HTML and is a total mess (TODO: refactoring)
+ *static/** - all the static CSS and *js files for displaying the cards + generic bootstrap files

Only the most important unit tests have been implemented and there is no error handling and (almost) zero input validation. Any bad input will break the game.

#### Web interface

In the beginning I wanted to completely avoid using server memory for state persistence, so my plan was to have a unique ID for each new game and store the game state somewhere on disk and later switch to a db, thus avoiding any ugly in-memory session. The client would store the game ID in some hidden input field and send it with every request. This would have worked nicely had I not decided to use SocketIO, which must have a session. In their documentation on scaling they explicitly [say](https://socket.io/docs/using-multiple-nodes/): " ... requests associated with a particular session ID must connect to the process that originated them". SocketIO assigns a session ID to every user that connects. So obviously scaling is not SocketIO's strong point, but on the other hand it supports nice things like broadcasting and multicasting messages, which fit perfectly with implementing a game room, and it gives a nice responsive feel to it. Thus, the basic logic is like this:
+ when a new client connects to the backend, SocketIO assigns it a new sessionid
+ this sessionid is then used to store the game state somewhere (disk,db)
+ any subsequent requests from this user use this sessionid to identify a game and load its state
+ in multiplayer game the sessionid of the first player is used to create a room, to which all other players join
+ each player is identified with a name, so names are unique

#### SocketIO and sending a message to a "game room

A game room is a way to send a certain message to some list of recipients (instead of everybody or one person). Sending a message to clients with SocketIO is as simple as:

```python
  ...
  socketio.emit('game_start', json.dumps(payload), callback=messageReceived)
  ...
```

however this is broadcasting and this message will be received by everone with an active session. Most of the time we want to notify a specific client or a group of clients. This is where the concept of rooms comes in handy. A room is just some identifier you can send a message to: 

```python
  from flask_socketio import SocketIO

  ...
  socketio.emit('game_start', payload, callback=messageReceived, room=game.gameid) # received by all the users in the room game.gameid
  ...
```

and any user can join a room simply by calling join_room:

```python
  from flask_socketio import SocketIO, join_room
  ...
  join_room(game.gameid) # currently connected user joins the room with id game.gameid
  ...
```

So once the user has joined the room any message sent to this room will be received by him as well. In the case of a single player game a room only has one player so (almost) the same logic applies.


### Example config files

Nginx as reverse proxy:

```apacheconf {
  
    listen [::]:80;
    listen 80;
    server_name mydomain.org www.mydomain.org;
    root /home/myusername/eenentwintgen;
    
    proxy_connect_timeout       605;
    proxy_send_timeout          605;
    proxy_read_timeout          605;
    send_timeout                605;
    keepalive_timeout           605;
    
    location = / {        
        proxy_pass http://127.0.0.1:1234;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
}
```

via Gunicorn3:
prerequisites: 
+ Gunicorn3 installed (apt-get install gunicorn3)
+ entry point called wsgi [short and nice tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)


```
    [Unit]
    Description=Gunicorn instance to serve myproject
    After=network.target

    [Service]
    User=myusername
    Group=www-data
    WorkingDirectory=/home/myusername/eenentwintgen    
    ExecStart=/usr/bin/gunicorn3 --workers 3 --bind unix:eenentwintgen.sock -m 007 wsgi:app

    [Install]
    WantedBy=multi-user.target
```

If you want to simplify things as much as possible it is also possible to directly run Flask as service but this is not reccomended for a production environment:

```
    [Unit]
    Description=Eenentwintgen Flask web server
    After=network.target
    
    [Install]
    WantedBy=multi-user.target
    
    [Service]
    User=myusername
    PermissionsStartOnly=true
    WorkingDirectory=/home/myusername/eenentwintgen
    ExecStart=/usr/bin/python3 game21_api.py
    TimeoutSec=600
    Restart=on-failure
    RuntimeDirectoryMode=755
   
```

