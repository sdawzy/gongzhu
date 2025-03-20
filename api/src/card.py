# Vectorized version of classes related to cards
# By Yue Zhang, Feb 13, 2025
import random
import numpy as np
from typing import List

SUITE_SIZE = 52
SUITS = ["club", "diamond", "heart", "spade"]
# RANKS = ["02", "03", "04", "05", "06", "07", "08", "09",
#             "10", "11", "12", "13", "14"]

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9",
            "10", "Jack", "Queen", "King", "Ace"]

def one_hot_vector(length, location) -> np.array:
    # Create a vector of zeros with a length of length
    vector = np.zeros(length, dtype=int)
    # Set the location to 1
    vector[location] = 1
    return vector

def one_hot_to_value(vector):
    return np.nonzero(vector)[0][0]

# Card is parametrized as a one-hot vector
class Card(np.ndarray):
    def __new__(cls, rank=None, suit=None, value=None):
        if value is not None:
            if not (0 <= value < SUITE_SIZE):
                raise ValueError("Value of a card must be between 0 and 51.")
            obj : np.ndarray = one_hot_vector(length=SUITE_SIZE, location=value)
            return obj.view(cls)

        # Empty card
        if rank is None and suit is None:
            obj : np.ndarray = np.zeros(SUITE_SIZE, dtype=int)
            return obj.view(cls)

        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")

        suit_index = SUITS.index(suit)
        rank_index = RANKS.index(rank)
        value = suit_index * len(RANKS) + rank_index

        obj : np.ndarray = one_hot_vector(length=SUITE_SIZE, location=value)
        return obj.view(cls)
    
    @property
    def rank(self) -> str:
        return RANKS[self.value % len(RANKS)]
    
    @property
    def suit(self) -> str:
        return SUITS[self.value // len(RANKS)]

    @property
    def value(self) -> int:
        if np.asarray(self).sum() < 1:
            return -1
        return int(one_hot_to_value(self))

    def __bool__(self):
        """Returns False if the card is 'empty' (all zeros)."""
        return np.any(np.asarray(self))  # False if all elements are 0

    def __str__(self):
        return f"{self.suit}_{self.rank}"
    
    def __repr__(self):
        return f"{self.suit}_{self.rank}"

    def __eq__(self, other):
        if other is None:
            return not np.any(np.asarray(self))
        assert isinstance(other, Card), "other must be Card. Got: %s. Other is %s" % (other.__class__.__name__,  other)
        # assert hasattr(other, "value"), "other must be Card.
        return self.value == other.value
    
    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return self.value

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other
    
    def get_suit(self) -> str:
        return self.suit

    def get_rank(self) -> str:
        return self.rank

    # Convert to Dictionary
    def to_dict(self):
        if self == None:
            return {
            'id': -1,
            'rank': "NA",
            'suit': "NA",
            'known': False
        }
        return {
            'id': self.value, 
            'rank': self.rank,
            'suit': self.suit, 
            'known': True
        }

# Abstract class for collections of cards
# It is a vector of {0,1}^52
class CardCollection(np.ndarray):
    def __new__(cls, cards = None):
        obj = np.zeros(52, dtype=int).view(cls)

        if cards is not None:
            if isinstance(cards, (list, tuple)):
                for card in cards:
                    obj.add_card(card)  # Use add_card to populate the collection
            elif isinstance(cards, Card):
                obj.add_card(cards)
            else:
                raise TypeError("Expected a list of Cards or a single Card.")

        return obj
    
    @property
    def size(self) -> int:
        return int(self.sum())
    
    @property
    def cards(self) -> List[Card]:
        self_vec = np.asarray(self)
        return [Card(value=i) for i in range(52) if self_vec[i] > 0]

    def __repr__(self) -> str:
        return str([card for card in self.cards])

    def __iter__(self):
        self.index = 0  # Initialize the index when iteration starts
        return self

    def __next__(self):
        if self.index < self.size:
            result = self.cards[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.cards[index]

    def __contains__(self, other):
        if np.asarray(other).sum() < 1:
            return True
        index = np.argmax(other)  # Gets the position where card == 1
        return np.asarray(self)[index] > 0  # Check if the count is greater than 0

    def add_card(self, card):
        """Adds a single Card to the collection."""
        if not isinstance(card, Card):
            raise TypeError("Expected a Card object.")
        self += card  # Since Card is a one-hot vector, this adds its count.

    def add_cards(self, cards):
        """Adds multiple Cards to the collection."""
        for card in cards:
            self.add_card(card)

    # Add a CardCollection to the collection
    def add_cards_from_collection(self, card_collection : "CardCollection"):
        self += card_collection

    def contains(self, card : Card) -> bool:
        # return card in self.cards
        index = np.argmax(card)  # Gets the position where card == 1
        return np.asarray(self)[index] > 0  # Check if the count is greater than 0

    # Remove and return a specific card from the collection
    def remove_card(self, card : Card) -> Card:
        """Removes a single card from the collection."""
        if not isinstance(card, Card):
            raise TypeError("Expected a Card object.")
        if np.any(np.asarray(self - card) < 0):
            raise ValueError("Cannot remove a card that is not in the collection.")
        self -= card
        return card

    def has_card(self, card : Card):
        """Checks if the collection contains a given card."""
        if not isinstance(card, Card):
            raise TypeError("Expected a Card object.")
        index = np.argmax(card)  # Gets the position where card == 1
        return np.asarray(self)[index] > 0  # Check if the count is greater than 0


    def get_cards(self):
        """Returns a list of Card objects present in the collection."""
        return [Card(value=i) for i in range(52) if self[i] > 0]

    def is_empty(self):
        """Checks if the collection is empty."""
        return np.all(self == 0)


    def __len__(self):
        return self.size

    def __add__(self, other) -> "CardCollection":
        """Union of two card collections."""
        if not isinstance(other, (CardCollection, Card)):
            raise TypeError("Can only add another CardCollection.")
        new_collection = self.copy()
        new_collection += other
        return new_collection

    def __sub__(self, other) -> "CardCollection":
        """Removes cards from one collection that exist in another."""
        if not isinstance(other, (CardCollection, Card)):
            raise TypeError("Can only subtract another CardCollection.")
        if not other in self:
            raise ValueError("Cannot remove more cards than present.")
        new_collection = self.copy()
        new_collection -= other
        return new_collection

    def intersect(self, other) -> "CardCollection":
        if not isinstance(other, (CardCollection, Card)):
            raise TypeError("Can only intersect another CardCollection or Card.")
        new_collection = np.asarray(self.copy())
        new_collection *= np.asarray(other)
        return new_collection.view(CardCollection)

    def __eq__(self, other):
        if other is None:
            return not np.any(np.asarray(self))
        assert isinstance(other, Card ), "other must be Card"
        return np.array_equal(self, other)

    def is_empty(self):
        return self.size == 0

    # Sort the cards
    def sort(self):
        return

    # Display the cards
    def show(self, name):
        print(name)
        for card in self.cards:
            print(f"  {card}")

    # Get a collection of cards with a specific suit
    def get_cards_by_suit(self, suit) -> "CardCollection":
        if isinstance(suit, str):
            suit_index = SUITS.index(suit)
        else:
            suit_index = suit
        assert suit_index >= 0 and suit_index < 4, "Invalid suit!"

        mask = np.zeros(SUITE_SIZE, dtype=int)
        mask[suit_index * len(RANKS) : (suit_index+1) * len(RANKS)]  = 1
        new_vec = self * mask

        return new_vec

    def get_cards_by_not_suit(self, suit) -> "CardCollection":
        return self - self.get_cards_by_suit(suit)

    def get_one_random_card(self) -> Card:
        if not self.cards:
            raise ValueError("No cards left in the collection!")
        random_index = random.randint(0, len(self.cards) - 1)
        return self.cards[random_index]

    def to_dict(self):
        return {'cards': [card.to_dict() for card in self.cards]}
    
    def to_list(self):
        return [card.to_dict() for card in self.cards]


class Deck(CardCollection):
    # Constructor to initialize a standard 52-card deck
    def shuffle(self):
        return

    def __init__(self):
        super().__init__()  # Call parent constructor

        for suit in SUITS:
            for rank in RANKS:
                self.add_card(Card(rank, suit))

    # Deal a card (specific to Deck)
    def deal_card(self) -> Card:
        card = self.get_one_random_card()
        self -= card
        # print(f"Dealt {card}. Current size is {self.size}")
        return card


class Hand(CardCollection):
    # Constructor initializes an empty hand
    def __init__(self):
        super().__init__()

    # Specific method to display hand
    def show_hand(self, player_name):
        self.show(player_name)

# Some Constant Cards and Hands
PIG = Card("Queen", "spade")
SHEEP = Card("Jack", "diamond")
DOUBLER = Card("10", "club")
BLOOD = Card("Ace", "heart")

SPECIAL_CARDS = [PIG, SHEEP, DOUBLER, BLOOD]

EMPTY_CARD = Card()

PIGPEN = CardCollection(
    cards=[Card("King", "spade"), Card("Ace", "spade")]
)
SHEEPPEN = CardCollection(
    cards=[Card("Queen", "diamond"), Card("King", "diamond"), Card("Ace", "diamond")]
)
DOUBLERCATCHER = CardCollection(
    cards=[Card("Jack", "club"), Card("Queen", "club"), Card("King", "club"), Card("Ace", "club")]
)

SAFESPADE = CardCollection(
    [
        Card("2", "spade"),
        Card("3", "spade"),
        Card("4", "spade"),
        Card("5", "spade"),
        Card("6", "spade"),
        Card("7", "spade"),
        Card("8", "spade"),
        Card("9", "spade"),
        Card("10", "spade"),
        Card("Jack", "spade"),
    ]
)

SAFECLUB = CardCollection(
    [
        Card("2", "club"),
        Card("3", "club"),
        Card("4", "club"),
        Card("5", "club"),
        Card("6", "club"),
        Card("7", "club"),
        Card("8", "club"),
        Card("9", "club"),
    ]
)

SAFEDIAMOND = CardCollection(
    [
        Card("2", "diamond"),
        Card("3", "diamond"),
        Card("4", "diamond"),
        Card("5", "diamond"),
        Card("6", "diamond"),
        Card("7", "diamond"),
        Card("8", "diamond"),
        Card("9", "diamond"),
        Card("10", "diamond"),
    ]
)

SPADESUITE = CardCollection([Card(rank, "spade") for rank in RANKS])
DIAMONDSUITE = CardCollection([Card(rank, "diamond") for rank in RANKS])
HEARTSUITE = CardCollection([Card(rank, "heart") for rank in RANKS])
CLUBSUITE = CardCollection([Card(rank, "club") for rank in RANKS])
