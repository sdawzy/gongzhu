from typing import List, TYPE_CHECKING
from card import Card, CardCollection
from declaration import Declaration
from policy import Policy
from card import PIG, SHEEP, DOUBLER, BLOOD
import numpy as np
from random import random

# Random policy
# Play a random card from legal moves
class RandomPolicy(Policy):
    def decide_action(self, legal_moves: CardCollection, 
        game_info: dict = None) -> Card:
        return legal_moves.get_one_random_card()
    
    def decide_declarations(self, 
        hand: CardCollection,
        game_info: dict = None) -> Declaration:
        closed_declarations = []
        open_declarations = []
        for index, card in enumerate([PIG, SHEEP, DOUBLER, BLOOD]):
            if hand.contains(card):
                decision = random()
                if decision < 0.3:
                    closed_declarations.append({
                        "card": card,
                        "revealed": False,
                    })
                elif decision < 0.6:
                    open_declarations.append(card)
        return Declaration(closed_declarations=closed_declarations, 
                        open_declarations=open_declarations)
    
    def __str__(self):
        return "RandomPolicy"