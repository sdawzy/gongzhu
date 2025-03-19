from typing import List, TYPE_CHECKING
from card import Card, CardCollection
from card import PIG, SHEEP, DOUBLER, PIGPEN, BLOOD
from declaration import Declaration
from random import random
import numpy as np
from policy import Policy

# Simple greedy policy
# Only aims to minimize own loss
# Avoids getting any Blood, Pig or Doubler. 
# Does not care about the score of the teammate
class GreedyPolicy(Policy):

    def decide_action(self, 
        legal_moves: CardCollection,
        game_info: dict = None) -> Card:

        # Sometimes play a random card
        if random() <= self.epsilon:
            return legal_moves.get_one_random_card()

        # Play the only card in the trivial case
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        
        cardToPlay = None
        # cardsPlayedThisRound = game_info['cardsPlayedThisRound']
        cardsPlayedThisRound = self.getCardsPlayedThisRound(game_info['history'])
        # cardsPlayedThisRound = [Card(card['rank'], card['suit']) for card in cardsPlayedThisRound ]
        # If I starts the round
        if len(cardsPlayedThisRound) == 0:  
            # If I don't have the pig
            if PIG not in legal_moves:
                # Play a spade if I have a safe spade
                safeSpades = self.getSpadesSmallerThanPig(legal_moves)
                if len(safeSpades) > 0:
                    cardToPlay = safeSpades[-1]

            if cardToPlay is None and SHEEP in legal_moves:
                cardsWithoutSheep = self.getCardsExcludingOneCard(legal_moves, SHEEP)
                cardToPlay = cardsWithoutSheep.get_one_random_card()
            
        else:
            # If legal moves are the same suit as the first played card
            if legal_moves[0].get_suit() == cardsPlayedThisRound[0].get_suit():
                current_suit = legal_moves[0].get_suit()
                if current_suit == "spade":
                    spadesWithoutPig = self.getCardsExcludingOneCard(legal_moves, PIG)
                    if PIG in legal_moves:
                        if self.getCurrentLargest(cardsPlayedThisRound) in PIGPEN:
                            cardToPlay = PIG
                        else:
                            cardToPlay = spadesWithoutPig[-1]
                    else:
                        # If you are the last player, playing the largest spade
                        if len(cardsPlayedThisRound) == 3:
                            cardToPlay = spadesWithoutPig[-1]
                        else:
                            safeSpades = self.getSpadesSmallerThanPig(legal_moves)
                            if len(safeSpades) > 0:
                                cardToPlay = safeSpades[-1]
                
                if current_suit == "club":
                    clubsWithoutDoubler = self.getCardsExcludingOneCard(legal_moves, DOUBLER)
                    if DOUBLER in legal_moves:
                        if self.getCurrentLargest(cardsPlayedThisRound) > DOUBLER:
                            cardToPlay = DOUBLER
                        else:
                            cardToPlay = clubsWithoutDoubler[-1]
                    else:
                        # If you are the last player, playing the largest spade
                        if len(cardsPlayedThisRound) == 3:
                            cardToPlay = clubsWithoutDoubler[-1]
                        else:
                            safeClubs = self.getClubsSmallerThanDoubler(legal_moves)
                            if len(safeClubs) > 0:
                                cardToPlay = safeClubs[-1]
                
                if current_suit == "diamond":
                    if SHEEP in legal_moves:
                        if len(cardsPlayedThisRound) == 3 and self.getCurrentLargest(cardsPlayedThisRound) < SHEEP:
                            cardToPlay = SHEEP
                        else:
                            diamondsWithoutSheep = self.getCardsExcludingOneCard(legal_moves, SHEEP)
                            cardToPlay = diamondsWithoutSheep.get_one_random_card()
                    else:
                        if self.getCurrentLargest(cardsPlayedThisRound) < SHEEP:
                            cardToPlay = legal_moves[-1]
                        else:
                            smallDiamonds = self.getDiamondsSmallerThanSheep(legal_moves)
                            if len(smallDiamonds) > 0:
                                cardToPlay = smallDiamonds[-1]

                if current_suit == "heart":
                    smallerHearts = self.getCardsSmallerThan(
                        legal_moves,
                        self.getCurrentLargest(cardsPlayedThisRound)
                    )
                    if len(smallerHearts) > 0:
                        cardToPlay = smallerHearts[-1]

            else:
                # First, get rid of the pig
                if PIG in legal_moves:
                    cardToPlay = PIG
                # Get rid of doubler
                elif DOUBLER in legal_moves:
                    cardToPlay = DOUBLER
                # Get rid of large heart
                else:
                    heartCards = legal_moves.get_cards_by_suit("heart")
                    if len(heartCards) > 0:
                        cardToPlay = heartCards[-1]
                
                # Get rid of pig gen
                if cardToPlay is None and PIGPEN[0] in legal_moves:
                    cardToPlay = PIGPEN[0]
                if cardToPlay is None and PIGPEN[1] in legal_moves:
                    cardToPlay = PIGPEN[1]
                
                # Get rid of doubler catchers
                clubCards = legal_moves.get_cards_by_suit("club")
                if cardToPlay is None and len(clubCards) > 0:
                    cardToPlay = clubCards[-1]
        
        # If current hand does not satisfy any of the case above,
        # Play a random card
        if cardToPlay is None:
            cardToPlay = legal_moves.get_one_random_card()

        return cardToPlay

    def decide_declarations(self, 
        hand: CardCollection,
        game_info: dict = None):
        # TODO: implement declaration
        return Declaration()

    def __str___(self):
        return f'GreedyPolicy_Epsilon={self.epsilon}'