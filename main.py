'''
Created on 8 Jul 2019

Simple command line interface for the blackjack game.

@author: Andrej
'''
from blackjack import GameBlackJack, PlayerBlackJack, PlayerBlackJackHouse

if __name__ == '__main__':
    dbg = input("(n)ew game or (l)oad state: ")    
    pn = input("\nplayer name: ")
    player = PlayerBlackJack(pn, 1000)  # init player
    house = PlayerBlackJackHouse()  #init house player
    while(True):
        bet_str = input("bet amount: ")
        player.bet(int(bet_str))
        game = GameBlackJack(house)
        gid = game.dumpstate()
        #print("\tdumped to {0}".format(gid))
        if(dbg == 'l'): # load previously saved state for debugging
            gid = input("game id:")
            game = GameBlackJack.getstate(gid)                        
        game.addplayer(player)
        oktocontinue = game.startgame() 
        print(game) 
        if(oktocontinue):  # player < 21        
            # ask each player:
            for p in game.players:
                game.nextplayer()
                hitloop = True
                while(hitloop): # player <= 21
                    action = input("\n{} 'hit' or 'stand'? ".format(p.name))
                    hitloop = not game.playermove(p, action)
                    print(player)
            #dealer's turn
            game.housemove()
            print(game.house)
        else:
            print(game)
        msg = game.settlebets() # pay out money
        game.endgame(gid) # clean up
        print(msg)
        pn = input("\nPress enter to continue s to stop l to load game ...")
        if(pn == 's'):
            break
        elif(pn == 'l'):
            dbg='l'
        else:
            dbg='n'
        
    
        





    