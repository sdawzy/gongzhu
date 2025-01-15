from typing import List, TYPE_CHECKING
from ..card import Card, CardCollection
from ..player import Player
if TYPE_CHECKING:
    from env import Env

class Policy:

    def __init__(self, env: 'Env'):
        self.env = env

    def decide_action(self, 
        legal_moves: CardCollection,
        player: Player = None, 
        game_info: dict = None) -> Card:
        raise NotImplementedError("'decide_action' not yet implemented.")
        pass

    def __str___(self):
        return self.__class__.__name__