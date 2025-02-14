# Vectorized version of the player class
# By Yue Zhang, Feb 11, 2025
import numpy as np
from card import Card, CardCollection, Hand
from policy import Policy, RandomPolicy
from typing import List, TYPE_CHECKING
from gymnasium import Env
# from flask import jsonify
if TYPE_CHECKING:
    from env_new import Gongzhu
    

class Player:
    def __init__(self,
        policy : Policy = RandomPolicy,
        id: str = None, 
        name : str = None, 
        avatar_url: str = None,
        rating : float = None):

        self.policy = policy

        self.id = id
        self.name = name 
        self.avatar_url = avatar_url

        # 52 x 1 vector representing the hand
        self._hand = Hand()
        # 52 x 1 vector representing the cards collected
        self._collectedCards = CardCollection()  

        # 52 x 1 vector representing the cards played
        self._playedCards = CardCollection()  
        # 52 x 1 one-hot / empty vector representing the current playing card
        self._currentPlayedCard : Card = Card()
        # 52 x 1 vector representing the close-declared cards 
        self._closeDeclaredCards = CardCollection() 
        # 52 x 1 vector representing the close-declared cards 
        self._openDeclaredCards = CardCollection()

        self._score = 0 

        self.rating = 1500
        if self.rating is not None:
            self.rating = rating

    def score(self, env : Env):
        """Get the player's score."""
        return env.calc_score(self._collectedCards)

    # reset player data
    def reset(self):
        self._hand = Hand()
        self._collectedCards = CardCollection()  
        self._playedCards = CardCollection()  
        self._currentPlayedCard : Card = Card()

        self._score = 0  
        self._closeDeclaredCards = CardCollection() 
        self._openDeclaredCards = CardCollection() 
    
    # Get methods
    def get_id(self):
        """Get the player's ID."""
        return self.id
    
    def get_avatar_url(self):
        """Get the player's avatar URL."""
        return self.avatar_url
    
    def get_name(self):
        """Get the player's name."""
        return self.name

    def get_hand(self):
        """Get the player's hand."""
        return self._hand

    def get_collected_cards(self):
        """Get the player's collected cards."""
        return self._collectedCards
    
    def get_played_cards(self):
        """Get the player's played cards."""
        return self._playedCards
    
    def get_current_played_card(self):
        """Get the current played card."""
        return self._currentPlayedCard

    def get_close_declared_cards(self):
        """Get the player's close declared cards."""
        return self._closeDeclaredCards
    
    def get_open_declared_cards(self):
        """Get the player's open declared cards."""
        return self._openDeclaredCards

    def show_hand(self):
        """Display the player's hand."""
        self._hand.show_hand(self.name + "\'s hand:")
    
    def sort_hand(self):
        self._hand.sort()

    def sort_collected_cards(self):
        self._collectedCards.sort()

    def show_collected_cards(self):
        self._collectedCards.sort()
        self._collectedCards.show(f"{self.name}'s collected cards")

    def add_card_to_hand(self, card : Card):
        """
        Add a card to the player's hand.
        
        :param card: The card to add.
        """
        self._hand.add_card(card)

    def add_cards_to_hand(self, cards : List[Card]):
        for card in cards:
            self._hand.add_card(card)
    
    def add_card_to_played_cards(self, card):
        self._playedCards.add_card(card)

    def play_specific_card(self, card : Card):
        """
        Play a specific card from the player's hand.
        
        :param card: The card to play.
        :return: The played card.
        :raises ValueError: If the card is not in the player's hand or if the hand is empty.
        """
        if self._hand.size == 0 or not self._hand.contains(card):
            raise ValueError(f"{self.name} has no cards to play!")

        self.set_current_played_card(card) 
        self.add_card_to_played_cards(card)
        return self._hand.remove_card(card)

    def add_collected_card(self, card : Card):
        """
        Add a card to the player's collected cards.
        
        :param card: The card to add.
        """
        self._collectedCards.add_card(card)

    def add_collected_cards(self, cards : List[Card]):
        """
        Add multiple cards to the player's collected cards.
        
        :param cards: A list of cards to add.
        """
        for card in cards:
            self._collectedCards.add_card(card)

    def get_collected_cards_size(self):
        """Get the size of the player's collected cards."""
        return self._collectedCards.size()

    def show_collected_cards(self):
        """Display the player's collected cards."""
        self._collectedCards.sort()
        self._collectedCards.show(f"{self.name}'s Collected Cards")

    def get_score(self, env : 'Gongzhu'):
        """
        Calculate the player's score using the environment rules.
        
        :param env: The game environment.
        :return: The player's score.
        """
        self._score = env.calc_score(self._collectedCards)
        return self._score

    def get_legal_moves(self, env : 'Gongzhu', played_cards : CardCollection) -> CardCollection:
        """
        Get the legal moves for the player based on the environment and played cards.
        
        :param env: The game environment.
        :param played_cards: The list of cards already played.
        :return: A CardCollection of legal moves.
        """
        return Gongzhu.legal_moves(self._hand, played_cards)

    def set_current_played_card(self, card : Card):
        self._currentPlayedCard = card

    def remove_current_played_card(self):
        self._currentPlayedCard = Card()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'hand': self._hand.to_list(),
            'collectedCards': self._collectedCards.to_list(),
            'playedCards': self._playedCards.to_list(),
            'currentPlayedCard':  None if self._currentPlayedCard is None else self.get_current_played_card().to_dict(),
            'closeDeclaredCards': self._closeDeclaredCards.to_list(),
            'openDeclaredCards': self._openDeclaredCards.to_list(),
            'score': self._score
        }
    
    # Vectorized (matrix) representation of a player
    # Currently, it is a 52 x 6 matrix
    @property
    def vec_full(self) -> np.array:
        return np.array( 
            [np.asarray(self._hand),
            np.asarray(self._collectedCards),
            np.asarray(self._playedCards),
            np.asarray(self._currentPlayedCard),
            np.asarray(self._closeDeclaredCards),
            np.asarray(self._openDeclaredCards)]
        )

    @property
    def vec_partial(self) -> np.array:
        return np.array( 
            [self._collectedCards,
            self._playedCards,
            self._currentPlayedCard,
            self._openDeclaredCards]
        )