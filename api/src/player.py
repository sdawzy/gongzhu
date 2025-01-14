from .card import Card, CardCollection, Hand

from typing import List, TYPE_CHECKING
# from flask import jsonify
if TYPE_CHECKING:
    from env import Env

class Player:
    def __init__(self, 
        id: str, name : str, avatar_url: str):
        """
        Constructor to initialize a player.
        
        :param name: The name of the player.
        """
        self.id = id
        self.name = name
        self.avatar_url = avatar_url

        self._hand = Hand()
        self._collectedCards = CardCollection()  # Anonymous subclass not required in Python

        self._playedCards = CardCollection()  # Anonymous subclass not required in Python
        self._currentPlayedCard : Card = None  # Anonymous subclass not required in Python

        self._score = 0  # Anonymous subclass not required in Python
        self._closeDeclaredCards = CardCollection() # Anonymous subclass not required in Python
        self._openDeclaredCards = CardCollection() # Anonymous subclass not required in Python

        # """Get the player's name."""
        # return self.name

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

    def play_last_card(self):
        """
        Play the last card from the player's hand.
        
        :return: The last card in the hand.
        :raises ValueError: If the player has no cards to play.
        """
        if self._hand.size() == 0:
            raise ValueError(f"{self.name} has no cards to play!")
        card_played = self._hand.remove_last_card()
        self.set_current_played_card(card_played)
        return card_played

    def play_specific_card(self, card : Card):
        """
        Play a specific card from the player's hand.
        
        :param card: The card to play.
        :return: The played card.
        :raises ValueError: If the card is not in the player's hand or if the hand is empty.
        """
        if self._hand.size() == 0 or not self._hand.contains(card):
            raise ValueError(f"{self.name} has no cards to play!")

        self.set_current_played_card(card) 
        self.add_card_to_played_cards(card)
        return self._hand.remove_specific_card(card)

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

    def get_score(self, env : 'Env'):
        """
        Calculate the player's score using the environment rules.
        
        :param env: The game environment.
        :return: The player's score.
        """
        self._score = env.calc_score(self._collectedCards)
        return self._score

    def get_legal_moves(self, env : 'Env', played_cards : CardCollection) -> CardCollection:
        """
        Get the legal moves for the player based on the environment and played cards.
        
        :param env: The game environment.
        :param played_cards: The list of cards already played.
        :return: A CardCollection of legal moves.
        """
        return env.legal_moves(self._hand, played_cards)

    def set_current_played_card(self, card : Card):
        self._currentPlayedCard = card

    def remove_current_played_card(self):
        self._currentPlayedCard = None

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
