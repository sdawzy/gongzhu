# Vectorized version of classes related to cards
# By Yue Zhang, Feb 13, 2025
import random
import numpy as np
from typing import List

SUITE_SIZE = 52
SUITS = ["club", "diamond", "heart", "spade"]
RANKS = ["02", "03", "04", "05", "06", "07", "08", "09",
            "10", "11", "12", "13", "14"]


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
        return int(one_hot_to_value(self))

    def __bool__(self):
        """Returns False if the card is 'empty' (all zeros)."""
        return np.any(np.asarray(self))  # False if all elements are 0

    def __str__(self):
        return f"{self.suit}_{self.rank}"

    def __eq__(self, other):
        if other is None:
            return not np.any(np.asarray(self))
        assert isinstance(other, Card ), "other must be Card"
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
            return None
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
PIG = Card("12", "spade")
SHEEP = Card("11", "diamond")
DOUBLER = Card("10", "club")
BLOOD = Card("14", "heart")

PIGPEN = CardCollection(
    cards=[Card("13", "spade"), Card("14", "spade")]
)
SHEEPPEN = CardCollection(
    cards=[Card("12", "diamond"), Card("13", "diamond"), Card("14", "diamond")]
)
DOUBLERCATCHER = CardCollection(
    cards=[Card("11", "club"), Card("12", "club"), Card("13", "club"), Card("14", "club")]
)

SAFESPADE = CardCollection(
    [
        Card("02", "spade"),
        Card("03", "spade"),
        Card("04", "spade"),
        Card("05", "spade"),
        Card("06", "spade"),
        Card("07", "spade"),
        Card("08", "spade"),
        Card("09", "spade"),
        Card("10", "spade"),
        Card("11", "spade"),
    ]
)

SAFECLUB = CardCollection(
    [
        Card("02", "club"),
        Card("03", "club"),
        Card("04", "club"),
        Card("05", "club"),
        Card("06", "club"),
        Card("07", "club"),
        Card("08", "club"),
        Card("09", "club"),
    ]
)

SAFEDIAMOND = CardCollection(
    [
        Card("02", "diamond"),
        Card("03", "diamond"),
        Card("04", "diamond"),
        Card("05", "diamond"),
        Card("06", "diamond"),
        Card("07", "diamond"),
        Card("08", "diamond"),
        Card("09", "diamond"),
        Card("10", "diamond"),
    ]
)

SPADESUITE = CardCollection([Card(rank, "spade") for rank in RANKS])
DIAMONDSUITE = CardCollection([Card(rank, "diamond") for rank in RANKS])
HEARTSUITE = CardCollection([Card(rank, "heart") for rank in RANKS])
CLUBSUITE = CardCollection([Card(rank, "club") for rank in RANKS])
