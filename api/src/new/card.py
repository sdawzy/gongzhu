# Vectorized version of classes related to cards
# By Yue Zhang, Feb 9, 2025
import random
import numpy as np
from typing import List

SUITE_SIZE = 52
SUITS = ["club", "diamond", "heart", "spade"]
RANKS = ["02", "03", "04", "05", "06", "07", "08", "09",
            "10", "11", "12", "13", "14"]


def one_hot_vector(length, location) -> np.array:
    # Create a vector of zeros with a length of length
    vector = np.zeros(length, dtype=float)
    # Set the location to 1
    vector[location] = 1.0
    return vector

def one_hot_to_value(vector):
    return np.nonzero(vector)[0][0]

# Card is parametrized as a one-hot vector
class Card:

    def __init__(self, rank=None, suit=None, value=None):
        # If the value is specified
        if value is not None:
            assert value >= 0 or value < SUITE_SIZE, \
                "Value of a card must be between 0 and 52."  
            self.vec = one_hot_vector(length=SUITE_SIZE, location=value)
            return
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        suit_index = SUITS.index(suit)
        rank_index = RANKS.index(rank)
        value = suit_index * len(RANKS) + rank_index
        self.vec = one_hot_vector(length=SUITE_SIZE, location=value)
    
    @property
    def rank(self) -> str:
        return RANKS[self.value % len(RANKS)]
    
    @property
    def suit(self) -> str:
        return SUITS[self.value // len(RANKS)]

    @property
    def value(self) -> int:
        return int(one_hot_to_value(self.vec))

    def __str__(self):
        return f"{self.suit}_{self.rank}"

    def __eq__(self, other):
        assert isinstance(other, Card ), "other must be Card"
        return self.value == other.value

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
    
    def get_vec(self) -> np.array:
        return self.vec

    def get_rank(self) -> str:
        return self.rank

    # Convert to Dictionary
    def to_dict(self):
        return {
            'id': self.value, 
            'rank': self.rank,
            'suit': self.suit, 
            'known': True
        }

# Abstract class for collections of cards
# It is a vector of {0,1}^52
class CardCollection:
    def __init__(self, cards = None, vec = None):
        # if cards is not None:
        #     self.cards : List[Card] = cards
        # else:
        #     self.cards : List[Card] = []  # Initialize the card list
        if vec is not None:
            self.vec = vec
            return
        self.vec = np.zeros(SUITE_SIZE, dtype=float)
        if cards is not None:
            for card in cards:
                self.add_card(card)
    
    @property
    def size(self) -> int:
        return int(self.vec.sum())
    
    @property
    def cards(self) -> List[Card]:
        return [Card(value=i) for i in np.nonzero(self.vec)[0]]

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

    def get_vec(self) -> np.array:
        return self.vec

    def get_cards(self):
        return self.cards

    # Add a card to the collection
    def add_card(self, card : Card):
        if card is not None:
            self.vec += card.vec

    # Add a list of cards to the collection
    def add_cards(self, card_list : List[Card]) :
        if card_list is not None:
            for card in card_list:
                self.add_card(card)

    # Add a CardCollection to the collection
    def add_cards_from_collection(self, card_collection : "CardCollection"):
        self.vec += card_collection.get_vec()

    def contains(self, card : Card) -> bool:
        # return card in self.cards
        return np.amax(self.vec + card.vec) > 1

    # # Remove the last card from the collection
    # def remove_last_card(self) -> Card:
    #     if self.is_empty:
    #         raise ValueError("No cards left in the collection!")
    #     card = 
    #     return self.cards.pop()

    # Remove and return a specific card from the collection
    def remove_specific_card(self, card : Card) -> Card:
        new_vec = self.vec - card.vec
        assert np.amin(new_vec) >= 0, "Does not have the card to remove!"
        self.vec = new_vec


    def __len__(self):
        return self.size

    def __add__(self, other) -> "CardCollection":
        if not isinstance(other, CardCollection) and not isinstance(other, Card):
            raise TypeError("Can only add CardCollection to CardCollection")
        new_vec = self.vec + other.get_vec()
        return CardCollection(vec=new_vec)
    
    def __iadd__(self, other) -> "CardCollection":
        if not isinstance(other, CardCollection) and not isinstance(other, Card):
            raise TypeError("Can only subtract CardCollection from CardCollection")
        self.vec += other.get_vec()
        return self
        
    def __sub__(self, other) -> "CardCollection":
        if not isinstance(other, CardCollection) and not isinstance(other, Card):
            raise TypeError("Can only subtract CardCollection from CardCollection")
        new_vec = self.vec - other.get_vec()
        return CardCollection(vec=new_vec)
    
    def __isub__(self, other) -> "CardCollection":
        if not isinstance(other, CardCollection) and not isinstance(other, Card):
            raise TypeError("Can only subtract CardCollection from CardCollection")
        self.vec -= other.get_vec()
        return self

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

        mask = np.zeros(SUITE_SIZE, dtype=float)
        mask[suit_index * len(RANKS) : (suit_index+1) * len(RANKS)]  = 1.0
        new_vec = self.vec * mask

        return CardCollection(vec=new_vec)
        # # Create a new collection to store the filtered cards
        # filtered_collection = CardCollection()
        # # Iterate through all cards and filter by suit
        # for card in self.cards:
        #     if card.get_suit().lower() == suit.lower():
        #         filtered_collection.add_card(card)
        # return filtered_collection  # Return the collection of matching cards

    # Get a collection of cards that is not a specific suit
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
        print(f"Dealt {card}. Current size is {self.size}")
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