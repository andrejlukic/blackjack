'''
Created on 8 Jul 2019

    Game of 21
    
    Classes for storing the state of the 21  game. Game supports single player (player against the house) or multiplayer (group of players against the house).    
    The rules for the game:        
    
    All players in the game place their bets after receiving their first card. Once everyone has placed their bets,
    the participants get a second card.
    
    One by one, the players of the game get the opportunity to play until they are finished. Each play, the
    players have the option to ‘stand’ (hold your total and end your turn, you cannot play any further), ‘hit’
    (ask for a card to bring your points as close as possible to 21), or perform special actions (here only ‘split’).
    If a player has more than 21 points in her hand, she is ‘bust’, and her bets are lost.
    
    If all players are ready (stand or bust) the bank must play (only if there are players who are not bust). The
    rules for the bank are simple: The bank must hit when it has a total of 16 points or less and must stand
    with a total of 17 points or more. When the bank and player have the same number of points, the bank
    wins. If the bank has more than 21 points, the bank is bust and all players that are standing, win.
    
    When a player gets two identical cards, she can choose to ‘split’. This means that the cards are placed next
    to each other on the table and the player can play twice, one game per card.
    
    The number of points for the cards is as follows:
    > King 3 points, queen 2 points, jack 1 point.
    > Ace is 1 or 11 points of your choice.
    > Cards 2 to 10 have their normal point value.
    > The ‘suit’ of the card is not important.
    > The Joker does not play
    
@author Andrej Lukic
'''

import os                   # for dumping and reloading state of the game
import jsonpickle, json     # for dumping and reloading state of the game
import uuid                 # for dumping and reloading state of the game
from pathlib import Path    # for dumping and reloading state of the game
import random               # shuffling card decks

class Game21:    
    """Game (round) of 21
    
    Functions for storing the state of the game round, determining whether the round is over and who won.
    Possible modes: player against the house or group of players against the house.

    Methods
    -------
    
    addplayer(player)
        called before game starts to add player to the game. Player names must be unique within a game.
    isgameover()
        game cannot continue if either house >= 21 or all the players have >= 21
    playermove()
        function makes player's move and determines if player can continue or not
    nextplayer()
        get next player in turn   
    housemove()
        house move is predetermined: must stand if the total is 17 or more and take a card if the total is 16 or under
    settlebets()
        after the game is over see who won and who lost and pay out money
    tie(player),
    housewins(player),
    playerwins(player)
        these three methods payout money to individual players who won, lost or tied
    startgame()
        give 2 cards to the house (second face down) and give 2 cards face up to each of the players and set the turn to the first player. 
    endgame()
        prepare for next round by resetting hands and bets for each of the players. Reshuffle cards.
    """
    
    SESSIONS_DIR = 'sessions'   # used to store game state on disk
    NATURAL = 21                # target of the game is 21
    MOVE_HIT = 'hit'
    MOVE_STAND = 'stand'
    
    def __init__(self, house, num_decks = 1, gameid = None):
        self.multiplayer = False
        self.num_decks = num_decks
        self.house = house
        self.house.prepareforgame()       
        self.decks = Decks(num_decks)
        self.players = []
        self.observers = []
        self.bets = 0
        self.playerturn = None
        self.gameid = gameid        
    
    def addadeck(self):
        """Adds a new deck if not enough cards for the number of players in the game. Maximum is 3 players per deck"""
        
        self.num_decks += 1
        print('+1 deck and reshuffling')
        self.decks = Decks(self.num_decks)
    
    def addplayer(self, player, as_observer = False):
        """Adds a new player to the game.
        If a game is multiplayer and a round is underway then a player is added as observer until the new round starts.
        
        Player must have a unique name
        """
        if(player.money <= 0):
            raise                
        if(player in self.players):
            raise
                
        player.prepareforgame() # reset player state in case he had played a round before     
        
        if(not as_observer):        
            self.players.append(player)
            if( len(self.players) > self.num_decks * 3):    # maximum is 3 players per deck. Add a new deck if additional player joins.
                self.addadeck()
        else:
            self.observers.append(player)
    
    def isgameover(self):
        """Checks if either house >= 21 or all the players have >= 21"""
        
        if(self.house.has21() or self.house.isbust()):
            return True
        
        allplayersbust = True
        allplayers21 = True
        for p in self.players:
            if(not p.has21()):                
                allplayers21 = False
            if(not p.isbust()):
                allplayersbust = False
                
        return allplayersbust or allplayers21
    
    def allplayersbust(self):        
        for p in self.players:            
            if(not p.isbust()):
                return False
        return True
    
    def playermove(self, player, move):
        """Player can either take a new card (hit) or wait (stand).
        
        Arguments:
        move -- Game21.MOVE_HIT | Game21.MOVE_STAND
        
        Functions returns True if player can do another move or False if player is bust or has hit 21.
        """
        
        if(move == Game21.MOVE_HIT):
            player.getcard(self.decks.popcard())            
            return player.isbust() or player.has21()
        else:
            return True    
    
    def nextplayer(self):
        """ Called after one of the players has done the move to get the next player in order. The last player is always house. """
                
        if(isinstance(self.playerturn, PlayerGame21House)):  # this should never happen
            raise Exception('Flow error - house already played')
        
        next_player = self.players.index(self.playerturn) + 1
        if(next_player < len(self.players)):
            self.playerturn = self.players[next_player] 
        else:
            self.playerturn = self.house    #after the last player has played it's house turn        
        return self.playerturn
    
    def housemove(self):
        """ House must stand if the total is 17 or more and take a card if the total is 16 or under """
        
        while(self.house.cardsvalue() < 17):
                self.house.getcard(self.decks.popcard())                 
        self.playerturn = None  #house is the last player
            
    def settlebets(self):
        """Called after the game has finished to determine winners and losers and pay out money. 
        
        If house has 21, then player lose or tie if they also have 21.
        If house is bust player can win if they are not but lose if they are also bust.
        If house < 21, then players win if they are closer to 21, lose if they are over or tie
        """
        
        dbgmsg = [] #for UI and debugging purposes
        for p in self.players:
            if(self.house.has21()):
                if(p.has21()):      #player also has 21 it's a tie                    
                    dbgmsg.append(self.tie(p))  # player and house have a Game21.NATURAL
                else:
                    dbgmsg.append(self.housewins(p)) # player has lost
            elif(self.house.isbust()): #house > 21                
                if(not p.isbust()):
                    dbgmsg.append(self.playerwins(p)) #house is bust and player is not
                else:
                    dbgmsg.append(self.housewins(p)) #both house and player are bust so the house wins 
            else: # house < 21
                if(p.has21()): #TODO: unnecessary               
                    dbgmsg.append(self.playerwins(p)) #player wins
                elif(p.isbust()):                    
                    dbgmsg.append(self.housewins(p))
                else: # nobody has 21, check who is closest
                    distancehouse = self.house.cardsdiff()             
                    distanceplayer = p.cardsdiff()
                    if(distancehouse < distanceplayer):
                        dbgmsg.append(self.housewins(p)) #house is closer to 21 than player
                    elif(distancehouse == distanceplayer):
                        dbgmsg.append(self.tie(p)) #player and house have the same points
                    else:
                        dbgmsg.append(self.playerwins(p)) #player is closer to 21 than house
        return dbgmsg
    
    def tie(self, player):
        """ Return the bet amount to player """
        
        player.tie()
        return "{} tied".format(player.name)

    def housewins(self, player):
        """ House takes player's bet """
                
        lost = player.loose()                    
        self.house.win(lost)
        return "{} lost".format(player.name)
        
    def playerwins(self, player):
        """ Player gets bet amount """
        
        amount = player.win()   #TODO: factor is more than 1.0 if 21                    
        self.house.loose(amount)
        return "{} won".format(player.name)
          
    def startgame(self):
        """ Give cards to each of the players and set the turn to the first player. """
        
        if(self.betting_turn() == 0): # bets have not yet been placed
            # first card is dealt face up
            for p in self.players:            
                p.getcard(self.decks.popcard())
                            
            # first card is dealt to the house face up
            self.house.getcard(self.decks.popcard())
            return None
        else:
            # second card is dealt face up
            for p in self.players:            
                p.getcard(self.decks.popcard())
            
            # second card is dealt to the house face down
            self.house.getcard(self.decks.popcard(facedown = True))
            
            self.playerturn = self.players[0]                    
            return not self.isgameover() # check if it makes sense to continue playing
    
    def betting_turn(self):
        """ Whose turn is it to place bets """
          
        bet_turn = 0
        for player in self.players:
            if(player.bet_amount <= 0):
                return bet_turn
            else:
                bet_turn += 1
        return bet_turn
            
    def endgame(self, reshuffle = False):
        """ Prepare for next round by resetting hands and bets for each of the players. Reshuffle cards."""
        
        self.house.prepareforgame()
        for p in self.players:
            p.prepareforgame()
            
        if(reshuffle or len(self.decks.decks) <= 0.25 * self.num_decks * Decks.newdecksize()): # reshuffle when 25% of cards reached
            self.decks = Decks(self.num_decks)
        self.playerturn = None
    
    def gamehasstarted(self):
        """ Game has started if any cards have been dealt """
        
        if(len(self.decks.decks) < self.num_decks * Decks.newdecksize()):
            return True
        else:
            return False

    def gamehasended(self):
        """ Game has ended when it is nobody's turn any more """
        
        return self.playerturn is None and self.betting_turn() >= len(self.players)
    
    def gameisactive(self):
        """ Game is active if it has started and not yet ended """
        
        return self.gamehasstarted() and not self.gamehasended()
            
    def ismultiplayergame(self):
        return self.multiplayer
    
    def getplayerbyname(self, pname):
        for p in self.players:
            if(p.name.lower() == pname.lower()):
                return p
        raise   # TODO
    
    def removeplayer(self, player_name, as_observer = False):
        """ Removes player from the game. 
        Player can also only be an observer, in that case he is removed from observers.
        """          
        if(not as_observer):
            self.players = [p for p in self.players if(p.name != player_name) ]
        else:
            self.observers = [p for p in self.observers if(p.name != player_name) ]
           
    def dumpstate(self):
        if(not os.path.isdir(Game21.SESSIONS_DIR)):
            os.mkdir(Game21.SESSIONS_DIR)
        if(not self.gameid):
            self.gameid = str(uuid.uuid4())
        filepath = Path('{}/{}'.format(Game21.SESSIONS_DIR, self.gameid))
        with open(filepath, 'w') as filehandle:                        
            json.dump(jsonpickle.encode(self), filehandle)
        return self.gameid
    
    @classmethod
    def getstate(cls, gameid):
        filepath = Path('{}/{}'.format(Game21.SESSIONS_DIR, gameid))
        with open(filepath, 'r') as filehandle:
            return jsonpickle.decode(json.load(filehandle))
    
    @classmethod
    def getactivemultiplayergames(cls):
        """ Helper method for UI - returns all active multiplayer game ids by looking at existing game files """
        
        #sess_files = glob.glob("{}".format(Game21.SESSIONS_DIR)).sort(key=os.path.getmtime, reverse=True) # get game files and sort descending by date
        sess_files = os.listdir("{}".format(Game21.SESSIONS_DIR))
        #print('{1}: {0}'.format(sess_files,"{}".format(Game21.SESSIONS_DIR)))        
        first_players = []
        game_ids = []
        for file in sess_files:
            #gid = file.split('\\')[1] #TODO check if backslash exists
            gid = file
            #print(gid)            
            game = Game21.getstate(gid)            
            if(game.multiplayer):
                first_players.append(game.players[0].name)
                game_ids.append(gid)
        gdict = {'games' : game_ids, 'names' : first_players }        
        return gdict
        
    def __repr__(self):            
        return "\n{} Decks = {} (cards full = {}), Cards left = {}\n{} {}".format(self.gameid, self.num_decks, self.num_decks * Decks.newdecksize(), len(self.decks.decks), self.house, self.players)

class Card:
    """Card base class
    
    The card is represented by a tuple of (rank, suit)     
    """
    
    def __init__(self, r, s):  
        """Arguments:
        
        r -- rank
        s -- suit
        """         
        
        self._card = (r,s)
        self.facedown = False    
    
    def __repr__(self):            
        return "{}".format(self._card)
    
    def tonum(self):
        """Returns numeric representation this card in a deck (used for web interface)"""
        
        rank = self.RANK.index(self._card[0])
        suit = self.SUIT.index(self._card[1])        
        print('{0} => {1} ({2}, {3})'.format(self._card, (rank * suit), rank, suit))
        return (rank + suit * 13) + 1


class Game21Card(Card):
    """Card for Game of 21
    
    Values of Blackjack hand:
    2 - 10 = face value
    J = 1
    Q = 2
    K = 3
    Ace = 11
    """
    
    RANK = [i for i in range(2, 11)] + ['JACK', 'QUEEN', 'KING', 'ACE']
    SUIT = ['SPADE', 'HEART ', 'CLUB', 'DIAMOND']
    
    def getval(self):
        """ Returns card value consistent with rules of game of 21. """
        
        if(self._card[0] not in ['JACK', 'QUEEN', 'KING', 'ACE']):
            return int(self._card[0])
        elif(self._card[0] == 'JACK'):
            return 1
        elif(self._card[0] == 'QUEEN'):
            return 2
        elif(self._card[0] == 'KING'):
            return 3
        elif(self._card[0] == 'ACE'):
            return 11        
    
    def __repr__(self):
        #rname = '♠'
        #if(self._card[1] == 'HEART'):
        #    rname='♡'
        #elif(self._card[1] == 'DIAMOND'):
        #    rname='♢'
        #elif(self._card[1] == 'CLUB'):
        #    rname='♣'        
            
        return "{0}-{1}".format(self._card[1], self._card[0])


class Decks:    
    """ A stack of N decks hand """
    
    def __init__(self, num_decks = 1):
        """    
        Create a stack of num_decks of decks of hand. 
        Cards are shuffled automatically.        
        
        Arguments:
        num_decks -- number of decks    
        """
    
        self.decks = []
        for _ in range(0, num_decks):            
            self.decks += [Game21Card(r,s) for r in Game21Card.RANK for s in Game21Card.SUIT]
        random.shuffle(self.decks)
        
    def popcard(self, facedown = False):
        card = self.decks.pop()
        card.facedown = facedown
        return card
    
    @classmethod
    def newdecksize(cls):
        return len(Game21Card.RANK) * len(Game21Card.SUIT)
    
    def __repr__(self):            
        return "{}".format([c.getval() for c in self.decks if not c.facedown])

class Player:    
    """Player in a betting card game.
    
    Player starts with some money and his name must be unique. PLayer's name cannot be house

    Methods
    -------
    win(factor = 1.0), 
    loose(), 
    tie()
        called after a game round is over. Player's money is increased or decreased based on game result.        
    bet(amount)
        called before the second card is dealt to bet some money.
    prepareforgame()
        called after the round is over to reset the hand and bet amount
    getcard(card)
        player receivs a card            
    """
    
    def __init__(self, name = "Player", money=1000):
        if(name == 'house'):
            raise   #TODO
        
        self.name = name
        self.money = money
        self.bet_amount = 0  
        self.hand = []
    
    def bet(self, amount):
        """ Player can bet some money, but not more than he has. """
        
        if(self.money < amount):            
            self.bet_amount = self.money
        else:
            self.bet_amount = amount
        self.money -= self.bet_amount
        return self.bet_amount
    
    def win(self, factor = 1.0):        
        """Arguments:
        
        factor -- in certain cases player wins bet amount multiplied by some factor
        """
        
        won = self.bet_amount * factor
        self.money += (self.bet_amount + won)
        self.bet_amount = 0
        return won
    
    def tie(self):
        tied = self.bet_amount
        self.money += self.bet_amount
        self.bet_amount = 0
        return tied
    
    def loose(self):
        lost = self.bet_amount
        self.bet_amount = 0        
        return lost
    
    def prepareforgame(self):
        self.hand = []
        self.bet_amount = 0
        
    def getcard(self, card):
        self.hand.append(card)
    
    def __eq__(self, other):        
        return self.name.lower() == other.name.lower()
    
    def toDict(self):
        #return jsonpickle.encode(self)
        return {'name': self.name, 'money': self.money, 'bet_amount': self.bet_amount, 'hand': [i.tonum() for i in self.hand], 'points': self.cardsvalue()}

    def __repr__(self):            
        return "{0}\n{1}EUR\n{2}".format(self.name, self.money, self.hand)
    
class PlayerGame21(Player):
    """Player of Game21
    
    Player's hand is evaluated by the rules of Game of 21.

    Methods
    -------
    
    isbust(), 
    has21()
        player's hand can have special values of over 21 (bust) or 21 (Natural)
    cardsvalue()
        player's hand is evaluated by the rules of game of 21
    cardsdiff()
        difference between value of player's hand and target value of 21                
    """
    
    def cardsvalue(self):
        """Returns hand value that is closest to 21 
        
        Since Aces can have a value of wither 1 or 11, they initially count as 11. 
        If the sum is over 21, Aces start counting as 1 until there is no more Aces left or the sum is under 21. 
        
        Values of Game of 21 cards:
        2 - 10 = face value
        J = 1,Q = 2,K = 3
        Ace = 1 or 11
        """
        
        cardsum = 0
        aces = 0
        for c in self.hand:
            cardval = c.getval()
            cardsum += cardval
            if(cardval == 11):                
                aces += 1
        while(aces > 0 and cardsum > Game21.NATURAL): # count Aces as 1 instead until the sum is under 21
            cardsum -= 10
            aces -= 1                                
        return cardsum
    
    def cardsdiff(self):                                    
        return Game21.NATURAL - self.cardsvalue()
    
    def has21(self):
        return self.cardsvalue() == Game21.NATURAL
    
    def isbust(self):
        return self.cardsvalue() > Game21.NATURAL

    def __repr__(self):            
        return "\n{0}\t[{1}EUR]\t{2} = {3} [bet {4}EUR]".format(self.name, self.money, self.hand, self.cardsvalue(), self.bet_amount)


class PlayerGame21House(PlayerGame21):
    """House in Game of 21 is just another player
        
    House has unlimited money and always matches other players's bets.
    House always wins with factor = 1.0
    """
    
    def __init__(self):
        super().__init__()
        self.name = "house"
        self.money = 0    # "unlimited"

    def win(self, amount):
        self.money += amount
    
    def loose(self, lost):        
        self.money -= lost
    
    def tie(self):
        pass
    
    def __repr__(self):
        return "\nhouse\t[{0}EUR]\t{1}".format(self.money, [c for c in self.hand if not c.facedown], self.cardsvalue())
