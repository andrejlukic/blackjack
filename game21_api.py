'''
Created on 8 Jul 2019

    Game of 21 API    

@author Andrej Lukic
'''

import os
import json
from flask import Flask, render_template, request
from pathlib import Path    # for dumping and reloading state of the game
from game21 import Game21, PlayerGame21, PlayerGame21House
import time # timer between restarting the game
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)

DEFAULT_DECKS_NUM = 3   # default number of decks to start a game with

@app.route("/", methods=['GET'])
def frontpage():    
    return render_template('cards.html')
    
def messageReceived(methods=['GET', 'POST']):
    debugout('received.')

@socketio.on('connected')
def on_connected(json, methods=['GET', 'POST']):
    debugout('Client connected:{0} {1}'.format(str(json), request.sid))    
    socketio.emit('my response', json, callback=messageReceived, room="jabolko")

@socketio.on('list_multiplayer_games')
def list_games(data, methods=['GET', 'POST']):
    debugout('{0}: list multiplayer games'.format(data['player_name'], data['bet_amount']))    
    json_response = json.dumps( Game21.getactivemultiplayergames() )
    socketio.emit('display_multiplayer_games', json_response, callback=messageReceived, room = request.sid)
       
@socketio.on('addfirstplayer')
def addfirstplayer(data, methods=['GET', 'POST']):
    """Start single or multiplayer game by adding the first player to the room.
    
    If the game is singleplayer just start it and the roomid = sessionid of the player
    If the game is multiplayer enter waiting state until the next user joins, gameid = sessionid of the first player
    
    PARAMETERS:
        game_type -- singleplayer | multiplayer        
        player_name -- name of the first player
    """
    
    debugout('{1} first player, game type = {0}'.format(data['game_type'], data['player_name']))
    
    firstplayer = PlayerGame21(data['player_name'], 1000)
    game = Game21(PlayerGame21House(), gameid = request.sid, num_decks=DEFAULT_DECKS_NUM)
    game.addplayer(firstplayer)
    
    if(data['game_type'] == 'singleplayer'):  #todo replace constant              
        startbettinground(game) # directly start the betting round
    else:   # multiplayer game, wait for the other user
        game.multiplayer = True        
        join_room(game.gameid)
        debugout("{}: creates room {}".format(firstplayer.name, game.gameid))
        game.dumpstate() # save the game state
        socketio.emit('wait_others', json.dumps(getpayload(game, None, None, True)), callback=messageReceived, room=game.gameid)

@socketio.on('join_game')
def joingame(data, methods=['GET', 'POST']):
    """player joins the game (only for multiplayer game)
    
    Player can join an active game - in this case he must wait until the current round is over and then he starts with the new round.
    Otherwise player is joining a new game and the game will start when the game creator starts it.
    
    PARAMETERS:
    gameid -- id of the multiplayer game    
    player_name -- name of the joined player
    """
       
    gameid = data['gameid']
    player_name = data['player_name']    
    debugout('{0} {1} wants to join'.format(gameid, player_name))
        
    secondplayer = PlayerGame21(player_name, 1000)        
    game = Game21.getstate(gameid)
    debugout('{0} Game => isactive={1} hasended={2} hasstarted={3}'.format(gameid, game.gameisactive(), game.gamehasended(), game.gamehasstarted()))
    if(not game.gameisactive()): # player is joining a new game
        game.addplayer(secondplayer)
    else:    # player is joining an already active game, must wait until round ends
        game.addplayer(secondplayer, as_observer = True)    
    join_room(gameid)
    game.dumpstate() # save the game state
    socketio.emit('player_joined', json.dumps(getpayload(game, None, None, True)), callback=messageReceived, room=game.gameid)
    # startbettinground(game)

@socketio.on('start_multiplayer_game')
def startmultiplayergame(data, methods=['GET', 'POST']):
    """After all the players had joined player starts the game    
    
    PARAMETERS:
    gameid -- id of the multiplayer game    
    player_name -- name of the joined player
    """
       
    gameid = data['gameid']
    player_name = data['player_name']    
    debugout('{0} {1} starts the multiplayer game'.format(gameid, player_name))
    game = Game21.getstate(gameid)
    startbettinground(game)

def startbettinground(game):
    """ All players place bets """
    game.startgame() # deal the first card  
    game.dumpstate()    
    debugout('{0} start betting round with player {1}'.format(game.gameid, game.betting_turn()))
    socketio.emit('start_betting', json.dumps(getpayload(game, None, None, True)), callback=messageReceived, room=game.gameid)
     
@socketio.on('place_bet')
def placebet(data):
    """ Players place bets """
     
    gameid = data['gameid'] 
    name = data['player_name']        
    amount = int(data['bet_amount'])
    
    debugout('{0} - {1} bets {2}'.format(gameid, name, amount))    
    
    game = Game21.getstate(gameid)
    player = game.players[game.betting_turn()]
    if(player.name != name):
        raise   # should not happen
    player.bet(amount)
    game.dumpstate()
    
    if(game.betting_turn() >= len(game.players)): # last player has placed her bet        
        gamestart(game)
    else: # not all players have placed their bets          
        payload = getpayload(game, None, None, True)
        socketio.emit('start_betting', json.dumps(payload), callback=messageReceived, room=game.gameid)
     
def gamestart(game):
    """ Start game of 21 after betting round has been completed """
    
    debugout('{1} - game start, bets placed = {2}'.format(game.players[0].name, game.gameid, game.betting_turn()))
     
    oktocontinue = game.startgame()
       
    msg=''
    if(not oktocontinue):   # check if makes sense to continue playing
        msg = ','.join(game.settlebets())
    
    while(game.playerturn.has21() and game.playerturn.name != 'house'): # skip players who already have 21
        game.nextplayer()    

    payload = getpayload(game, msg, None, oktocontinue)
    #debugout('{0} send response to room {1}'.format(game.gameid, payload))
    game.dumpstate()
    socketio.emit('game_start', json.dumps(payload), callback=messageReceived, room=game.gameid)
    
@socketio.on('game_restart')
def gamerestart(data, methods=['GET', 'POST']):
    """Restart the game 
    
    PARAMETERS:
    gameid -- id of the game to restart
    """
    
    gameid = data['gameid']    
    debugout('{0} restart'.format(gameid))    
    game = Game21.getstate(gameid)
    debugout('Old state:\n{0}'.format(game))
    for o in game.observers:    #there might be observers waiting to be added to the game
        game.addplayer(o)
        game.removeplayer(o.name, as_observer = True)    
    game.endgame()  # this cleans up the state for every player
    debugout('New state:\n{0}'.format(game))    
    
    startbettinground(game)

@socketio.on('exit_game')
def playerexit(data, methods=['GET', 'POST']):
    """Player exits game 
    
    PARAMETERS:
    gameid -- id of the game
    """
    
    gameid = data['gameid']
    player_name = data['player_name']   
    debugout('{0} player {1} exits'.format(gameid, player_name))
    game = Game21.getstate(gameid)
    game.removeplayer(player_name)
    leave_room(game.gameid)
    game.endgame()  # this cleans up the state for every player    
    debugout('{0}'.format(game))
    
    socketio.emit('player_exited', json.dumps(getpayload(game, '{0}'.format(player_name), None, True)), callback=messageReceived, room=game.gameid)
    time.sleep(8)
    startbettinground(game)
    
@socketio.on('player_move')
def playermove(data, methods=['GET', 'POST']):
    """player makes a move    
    
    PARAMETERS:
    gameid -- id of the multiplayer game
    action -- hit | stand
    player_name -- name of the first player
    """
    
    gameid = data['gameid']
    action = data['action']
    name = data['player_name']
    debugout('{2} - {0} => {1}'.format(data['player_name'], action, gameid))
       
    game = Game21.getstate(gameid)
    if(game.playerturn.name != name):   # this shold not occur
        raise Exception('turn is on: {0} not on {1}'.format(game.playerturn, name))  #TODO: implement exception here
    
    playerfinished = game.playermove(game.playerturn, action)
    if(not playerfinished): # player is still on the move
        payload = getpayload(game, None, action, True)
        debugout(payload)        
        game.dumpstate()
        socketio.emit('player_move', json.dumps(payload), callback=messageReceived, room=game.gameid)
        return
    else: # player is finished. next player is selected        
        nextplayermove(game, action)

def nextplayermove(game, previous_action):  
    
    # determine next player for the move:
    game.nextplayer()
    while(game.playerturn.has21() and game.playerturn.name != 'house'):
        game.nextplayer()
    #debugout("Next player {}".format(game.playerturn))
    debugout('{1} - next player = {0}'.format(game.playerturn.name, game.gameid))    
    if(game.playerturn.name != 'house'):    # next player is on the move    
        payload = getpayload(game, None, previous_action, True)        
        debugout(payload)
        game.dumpstate()        
        socketio.emit('player_move', json.dumps(payload), callback=messageReceived, room=game.gameid)
    else:   # house is on the move and then game ends, house only moves if not all players are bust!
        if(not game.allplayersbust()):                
            game.housemove()        
        msg = game.settlebets()                  
        debugout(','.join(msg))
        payload = getpayload(game, ', '.join(msg), previous_action, False)
        game.endgame()
        game.dumpstate()
        debugout(payload)        
        json_response = json.dumps(payload)        
        socketio.emit('player_move', json_response, callback=messageReceived, room=game.gameid)

@socketio.on('disconnect')
def cleanup():
    debugout('{} disconnected'.format(request.sid))
    fs = Path('{}/{}'.format(Game21.SESSIONS_DIR, request.sid))    
    if(os.path.isfile(fs)):
        pass    #TODO cleanup session files
        #os.remove(fs)

def getpayload(game, msg, action, uistate):
    
    turn = None
    if(game.betting_turn() >= len(game.players)):
        betting_turn_name = None
    else:
        betting_turn_name = game.players[game.betting_turn()].name
        
    if(game.playerturn):
        turn = game.playerturn.name
     
    return {'players': [p.toDict() for p in game.players], 
            'observers': [p.toDict() for p in game.observers], 
            'house': game.house.toDict(),
            'betting_turn': betting_turn_name,
            'action':action, 
            'gameid':game.gameid, 
            'player_turn': turn, 
            'game_state': uistate,
            'gameactive': game.gameisactive(), 
            'msg': msg }

def debugout(msg):
    print(msg)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port=88, debug=True)
    #app.run(host='0.0.0.0',port=80,debug=True)