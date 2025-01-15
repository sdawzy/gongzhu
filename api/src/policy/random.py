from typing import List, TYPE_CHECKING
from ..card import Card, CardCollection
from ..player import Player
from .policy import Policy
if TYPE_CHECKING:
    from env import Env

# Random policy
class RandomPolicy(Policy):
    def decide_action(self, legal_moves: CardCollection, 
        player: Player = None, game_info: dict = None) -> Card:
        return legal_moves.get_one_random_card()