# Declaration Interface
# By Yue Zhang, Feb 18, 2025
from .card import Card, SPECIAL_CARDS
from typing import List

class Declaration:
    def __init__(self, closed_declarations : List[dict] = [], 
                        open_declarations : List[Card] = []):
        # Sanity check
        for card in open_declarations:
            if card not in SPECIAL_CARDS:
                raise ValueError(f"Invalid open declaration: {card}")
        for closed_card in closed_declarations:
            if closed_card["card"] not in SPECIAL_CARDS:
                raise ValueError(f"Invalid closed declaration: {closed_card['card']}")
            if closed_card["revealed"] != True and closed_card["revealed"] != False:
                raise ValueError(f"Invalid revealed value: {closed_card['revealed']}")
        self.open_declarations = open_declarations
        self.closed_declarations = closed_declarations
    
    def to_dict(self):
        return {
            "open_declarations": [card.to_dict() for card in self.open_declarations],
            "closed_declarations": [card.to_dict() for card in self.get_revealed_closed_declarations()],
            "num_unrevealed": self.num_unrevealed
        }
    
    @property
    def num_unrevealed(self):
        cnt = 0
        for closed_card in self.closed_declarations:
            if closed_card["revealed"] == False:
                cnt += 1
        return cnt

    def reveal(self, card):
        for declaration in self.closed_declarations:
            if declaration["card"] == card:
                declaration["revealed"] = True
                return True
        return False

    def get_open_declarations(self) -> List[Card]:
        return self.open_declarations
    
    def get_all_closed_declarations(self) -> List[Card]:
        return [declaration['card'] for declaration in 
                self.closed_declarations]

    def get_revealed_closed_declarations(self) -> List[Card]:
        return [declaration['card'] for declaration in 
                self.closed_declarations if declaration["revealed"]]