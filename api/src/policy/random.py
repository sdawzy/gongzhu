from typing import List, TYPE_CHECKING
from ..card import Card, CardCollection
from .policy import Policy

# Random policy
# Play a random card from legal moves
class RandomPolicy(Policy):
    def decide_action(self, legal_moves: CardCollection, 
        game_info: dict = None) -> Card:
        return legal_moves.get_one_random_card()
    
    def __str__(self):
        return "RandomPolicy"