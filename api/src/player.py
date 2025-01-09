from card import Card, CardCollection, Hand
from env import Env
from typing import List

class Player:
    def __init__(self, name):
        """
        Constructor to initialize a player.
        
        :param name: The name of the player.
        """
        self.name = name
        self.hand = Hand()
        self.collected_cards = CardCollection()  # Anonymous subclass not required in Python

    def get_name(self):
        """Get the player's name."""
        return self.name

    def get_hand(self):
        """Get the player's hand."""
        return self.hand

    def sort_hand(self):
        """Sort the player's hand."""
        self.hand.sort()

    def show_hand(self):
        """Display the player's hand."""
        self.hand.show_hand(self.name + "\'s hand:")
    
    def show_collected_cards(self):
        self.collected_cards.sort()
        self.collected_cards.show(f"{self.name}'s collected cards")

    def add_card_to_hand(self, card : Card):
        """
        Add a card to the player's hand.
        
        :param card: The card to add.
        """
        self.hand.add_card(card)

    def play_card(self):
        """
        Play the last card from the player's hand.
        
        :return: The last card in the hand.
        :raises ValueError: If the player has no cards to play.
        """
        if self.hand.size() == 0:
            raise ValueError(f"{self.name} has no cards to play!")
        return self.hand.remove_card()

    def play_specific_card(self, card : Card):
        """
        Play a specific card from the player's hand.
        
        :param card: The card to play.
        :return: The played card.
        :raises ValueError: If the card is not in the player's hand or if the hand is empty.
        """
        if self.hand.size() == 0 or not self.hand.contains(card):
            raise ValueError(f"{self.name} has no cards to play!")
        return self.hand.remove_specific_card(card)

    def add_collected_card(self, card : Card):
        """
        Add a card to the player's collected cards.
        
        :param card: The card to add.
        """
        self.collected_cards.add_card(card)

    def add_collected_cards(self, cards : List[Card]):
        """
        Add multiple cards to the player's collected cards.
        
        :param cards: A list of cards to add.
        """
        for card in cards:
            self.collected_cards.add_card(card)

    def get_collected_cards_size(self):
        """Get the size of the player's collected cards."""
        return self.collected_cards.size()

    def show_collected_cards(self):
        """Display the player's collected cards."""
        self.collected_cards.sort()
        self.collected_cards.show(f"{self.name}'s Collected Cards")

    def get_score(self, env : Env):
        """
        Calculate the player's score using the environment rules.
        
        :param env: The game environment.
        :return: The player's score.
        """
        return env.calc_score(self.collected_cards)

    def get_legal_moves(self, env : Env, played_cards : CardCollection) -> CardCollection:
        """
        Get the legal moves for the player based on the environment and played cards.
        
        :param env: The game environment.
        :param played_cards: The list of cards already played.
        :return: A CardCollection of legal moves.
        """
        return env.legal_moves(self.hand, played_cards)
