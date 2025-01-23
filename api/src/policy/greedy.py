from typing import List, TYPE_CHECKING
from ..card import Card, CardCollection
from ..player import Player
from .policy import Policy
if TYPE_CHECKING:
    from env import Env

# Simple greedy policy

class GreedyPolicy(Policy):

    def decide_action(self, 
        legal_moves: CardCollection,
        player: Player = None, 
        game_info: dict = None) -> Card:
        pass

    def __str___(self):
        return f'GreedyPolicy_Epsilon={self.epsilon}'