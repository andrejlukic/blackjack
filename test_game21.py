'''
Created on 9 Jul 2019

@author: Andrej Lukic
'''
import unittest
from game21 import Game21, PlayerGame21, PlayerGame21House, Game21Card


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass
    
    def test_hand_value(self):
        """Card for Game of 21
    
        Values of Blackjack hand:
        2 - 10 = face value
        J = 1
        Q = 2
        K = 3
        Ace = 11
        """
        player = PlayerGame21("TestPlayer")
        king = Game21Card('KING','SPADE')
        two = Game21Card('2','HEART')
        ace = Game21Card('ACE','HEART')
        player.getcard(king)
        player.getcard(two)
        player.getcard(ace)
        self.assertEqual( player.cardsvalue(), 16) # ace values full 11 the first time
        player.getcard(ace) 
        self.assertEqual( player.cardsvalue(), 17) # since it's over 21 now one Ace should be automatically excluded
        
    def test_settle_bets(self):
        """Card for Game of 21
    
        Values of Blackjack hand:
        2 - 10 = face value
        J = 1
        Q = 2
        K = 3
        Ace = 11
        """
        
        king = Game21Card('KING','SPADE')
        ten = Game21Card('10','DIAMOND')
        two = Game21Card('2','HEART')
        ace = Game21Card('ACE','HEART')
        
        
        house = PlayerGame21House()
        house.getcard(king)
        house.getcard(ten)        
        
        player1 = PlayerGame21("TestPlayer")
        player1.getcard(two)
        player1.getcard(ace)
        
        game = Game21(house)
        game.addplayer(player1)
  
        self.assertEqual( game.settlebets(), ['TestPlayer tied']) # player has 13 == 13 of house
        
        player1.getcard(two)        
        self.assertEqual( game.settlebets(), ['TestPlayer won']) # player has 15 > 13 of house
        
        player1.getcard(ten)        
        self.assertEqual( game.settlebets(), ['TestPlayer won']) # Player has 15 now (Ace is now 1)
        
        player1.getcard(ten)        
        self.assertEqual( game.settlebets(), ['TestPlayer lost']) # Player has 25 now and is bust
        
    def test_choosing_next_player(self):       
        king = Game21Card('KING','SPADE')
        ten = Game21Card('10','DIAMOND')
        two = Game21Card('2','HEART')
        ace = Game21Card('ACE','HEART')
        
        
        house = PlayerGame21House()
        house.getcard(king)
        house.getcard(ten)        
        
        player1 = PlayerGame21("1")
        player1.getcard(two)
        player1.getcard(ace)
        
        player2 = PlayerGame21("2")
        player2.getcard(two)
        player2.getcard(ace)
        
        player3 = PlayerGame21("3")
        player3.getcard(two)
        player3.getcard(ace)
        
        game = Game21(house)
        game.addplayer(player1)
        game.addplayer(player2)
        game.addplayer(player3)
        
        game.startgame() # starts the betting turn
        
        self.assertEqual( game.betting_turn(), 0) # player 1 must bet        
        player1.bet(10)        
        self.assertEqual( game.betting_turn(), 1) # player 2 must bet
        player2.bet(10)
        self.assertEqual( game.betting_turn(), 2) # player 3 must bet
        player3.bet(10)
        self.assertEqual( game.betting_turn(), 3) # betting done
        
        game.startgame()    # now the turns start        
  
        self.assertEqual( game.playerturn.name, '1') # player 1 starts the game        
        game.nextplayer()        
        self.assertEqual( game.playerturn.name, '2') # player 2
        game.nextplayer()        
        self.assertEqual( game.playerturn.name, '3') # player 3
        game.nextplayer()        
        self.assertEqual( game.playerturn.name, 'house') # house
        
        with self.assertRaises(Exception):
             game.nextplayer()  # this should raise an exception because the house has already played
        

        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()