# Classes related to cards
import random
from typing import List

SUITS = ["club", "diamond", "heart", "spade"]
RANKS = ["02", "03", "04", "05", "06", "07", "08", "09",
            "10", "11", "12", "13", "14"]

class Card:

    def __init__(self, rank, suit, known=True):
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank
        self.suit = suit
        self.id = self.suit + "_" + self.rank
        # only applicable to close declared card
        # By default is true
        # False means the card is closed declared and not yet played
        self.known = known

    def __str__(self):
        return f"{self.suit}_{self.rank}"

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
    
    def get_suit(self) -> str:
        return self.suit
    
    def get_rank(self):
        return self.rank

    # Convert to Dictionary
    def to_dict(self):
        return {
            'id': self.id, 
            'rank': self.rank,
            'suit': self.suit, 
            'known': self.known
        }


# Abstract class for collections of cards
class CardCollection:
    def __init__(self, cards = None):
        if cards is not None:
            self.cards : List[Card] = cards
        else:
            self.cards : List[Card] = []  # Initialize the card list

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

    def __getitem__(self, index):
        return self.cards[index]

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
    def remove_last_card(self):
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

    def __len__(self):
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

    def to_dict(self):
        return {'cards': [card.to_dict() for card in self.cards]}
    
    def to_list(self):
        return [card.to_dict() for card in self.cards]


class Deck(CardCollection):
    # Constructor to initialize a standard 52-card deck
    def __init__(self):
        super().__init__()  # Call parent constructor

        for suit in SUITS:
            for rank in RANKS:
                self.add_card(Card(rank, suit))

    # Deal a card (specific to Deck)
    def deal_card(self):
        return self.remove_last_card()


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