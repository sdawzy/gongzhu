# Classes related to cards
import random

SUITS = ["Club", "Diamond", "Heart", "Spade"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9",
            "10", "Jack", "Queen", "King", "Ace"]

class Card:

    def __init__(self, rank, suit):
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        suit_index = SUITS.index(self.suit)
        rank_index = RANKS.index(self.rank)
        # Compute a unique hash based on suit and rank indices
        return suit_index * len(RANKS) + rank_index

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        self_suit_index = SUITS.index(self.suit)
        other_suit_index = SUITS.index(other.suit)
        
        if self_suit_index != other_suit_index:
            return self_suit_index < other_suit_index
        
        self_rank_index = RANKS.index(self.rank)
        other_rank_index = RANKS.index(other.rank)
        return self_rank_index < other_rank_index

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other
    
    def get_suit(self):
        return self.suit
    
    def get_rank(self):
        return self.rank



# Abstract class for collections of cards
class CardCollection:
    def __init__(self, cards = None):
        if cards is not None:
            self.cards = cards
        else:
            self.cards = []  # Initialize the card list

    def __iter__(self):
        self.index = 0  # Initialize the index when iteration starts
        return self

    def __next__(self):
        if self.index < len(self.cards):
            result = self.cards[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

    def get_cards(self):
        return self.cards

    # Add a card to the collection
    def add_card(self, card):
        if card is not None:
            self.cards.append(card)

    # Add a list of cards to the collection
    def add_cards(self, card_list):
        if card_list:
            for card in card_list:
                if card is not None:
                    self.cards.append(card)

    # Add a CardCollection to the collection
    def add_cards_from_collection(self, card_collection):
        self.add_cards(card_collection.get_cards())

    def contains(self, card):
        return card in self.cards

    # Remove the last card from the collection
    def remove_card(self):
        if not self.cards:
            raise ValueError("No cards left in the collection!")
        return self.cards.pop()

    # Remove and return a specific card from the collection
    def remove_specific_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            return card  # Card successfully removed, return it
        raise ValueError("Card not found in the collection!")

    # Get the size of the collection
    def size(self):
        return len(self.cards)

    def is_empty(self):
        return len(self.cards) == 0

    # Shuffle the cards
    def shuffle(self):
        random.shuffle(self.cards)

    # Sort the cards
    def sort(self):
        self.cards.sort()  # Assumes Card class implements comparison methods

    # Display the cards
    def show(self, name):
        print(name)
        for card in self.cards:
            print(f"  {card}")

    # Get a collection of cards with a specific suit
    def get_cards_by_suit(self, suit):
        # Create a new collection to store the filtered cards
        filtered_collection = CardCollection()
        # Iterate through all cards and filter by suit
        for card in self.cards:
            if card.get_suit().lower() == suit.lower():
                filtered_collection.add_card(card)
        return filtered_collection  # Return the collection of matching cards

    # Get a collection of cards that is not a specific suit
    def get_cards_by_not_suit(self, suit):
        # Create a new collection to store the filtered cards
        filtered_collection = CardCollection()
        # Iterate through all cards and filter by suit
        for card in self.cards:
            if card.get_suit().lower() != suit.lower():
                filtered_collection.add_card(card)
        return filtered_collection  # Return the collection of matching cards

    def get_one_random_card(self):
        if not self.cards:
            raise ValueError("No cards left in the collection!")
        random_index = random.randint(0, len(self.cards) - 1)
        return self.cards[random_index]


class Deck(CardCollection):
    # Constructor to initialize a standard 52-card deck
    def __init__(self):
        super().__init__()  # Call parent constructor

        for suit in SUITS:
            for rank in RANKS:
                self.add_card(Card(rank, suit))

    # Deal a card (specific to Deck)
    def deal_card(self):
        return self.remove_card()


class Hand(CardCollection):
    # Constructor initializes an empty hand
    def __init__(self):
        super().__init__()

    # Specific method to display hand
    def show_hand(self, player_name):
        self.show(player_name)
