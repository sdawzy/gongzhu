# Policy Interface
# By Yue Zhang
from typing import List, TYPE_CHECKING
from abc import ABC, abstractmethod
import numpy as np
from ..declaration import Declaration
from ..card import Card, CardCollection
from ..card import PIG, SHEEP, DOUBLER, BLOOD, PIGPEN, SHEEPPEN, DOUBLERCATCHER
from ..card import SAFESPADE, SAFECLUB, SAFEDIAMOND


if TYPE_CHECKING:
    from gymnasium import Env
    

class Policy(ABC):
    def __init__(self, env: 'Env', epsilon: float = 0.05):
        self.env = env
        self.epsilon = epsilon

    @abstractmethod
    def decide_action(self, 
        legal_moves: CardCollection,
        game_info: dict = None) -> Card:
        raise NotImplementedError("'decide_action' not yet implemented.")

    @abstractmethod
    def decide_declarations(self, 
        hand: CardCollection,
        game_info: dict = None) -> Declaration:
        raise NotImplementedError("'decide_declarations' not yet implemented.")
    
    def __str___(self):
        return self.__class__.__name__
    
    # Some helper functions

    def getCardsPlayedBySuit(self, suit: str, game_info: dict) -> CardCollection:
        pass

    def getCardsNotPlayedBySuit(self, suit: str, game_info: dict) -> CardCollection:
        pass
    
    def getDiamondsSmallerThanSheep(self, hand: CardCollection) -> CardCollection:
        ret = CardCollection()
        for card in SAFEDIAMOND:
            if card in hand:
                ret.add_card(card)
        return ret

    def getClubsSmallerThanDoubler(self, hand: CardCollection) -> CardCollection:
        ret = CardCollection()
        for card in SAFECLUB:
            if card in hand:
                ret.add_card(card)
        return ret

    def getSpadesSmallerThanPig(self, hand: CardCollection) -> CardCollection:
        ret = CardCollection()
        for card in SAFESPADE:
            if card in hand:
                ret.add_card(card)
        return ret

    def getCardsSmallerThan(self, hand: CardCollection, card: Card) -> CardCollection:
        ret = CardCollection()
        for card_ in hand:
            if card_ > card:
                break
            else:
                ret.add_card(card_)
        return ret
    
    def getCardsLargerThan(self, hand: CardCollection, card: Card) -> CardCollection:
        ret = CardCollection()
        for card_ in hand:
            if card_ > card:
                ret.add_card(card_)
        return ret

    def getCardsExcludingOneCard(self, hand: CardCollection, card: Card) -> CardCollection:
        ret = CardCollection()
        for card_ in hand:
            if card_!= card:
                ret.add_card(card_)
        return ret

    def getCurrentLargest(self, playedCards: List[Card]) -> Card:
        return self.env.find_largest_card(playedCards)