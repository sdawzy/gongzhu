# Vanilla DMC agent
from typing import List, TYPE_CHECKING
from card import Card, CardCollection
from card import PIG, SHEEP, DOUBLER, PIGPEN, BLOOD
from declaration import Declaration
from random import random
import numpy as np
from policy import Policy
from policy.models import GongzhuDMC
# from env import Gongzhu

import torch

def reshape_history(history, first_player_indices):
    # Reshape history from list of 52 x 1 vectors to 52 * 4 vectors
    history_reshaped = []
    for i, h in enumerate(history):
        index = (first_player_indices[i // 4] + i) % 4
        card_index = np.argmax(h)
        new_h = torch.zeros(4 * 52)
        new_h[4 * index + card_index] = 1
        history_reshaped.append(new_h)

    return history_reshaped

class DMC(Policy):

    def __init__(self, epsilon: float = 0.05, device: str = "cpu"):
        super().__init__(epsilon=epsilon)
        # self.epsilon = epsilon
        self.model = GongzhuDMC()
        self.device = torch.device(device)

    def load_state_dict(self, dir):
        self.model.load_state_dict(dir)

    def state_dict(self):
        return self.model.state_dict()
        
    def decide_action(self, 
        legal_moves: CardCollection,
        game_info: dict = None,
        epsilon_greedy: bool = True,
        return_value: bool = False) -> Card:

        # self.observation_space = Dict(
        #     {"agent_info": Box(0, 1, shape=(52, 6)), 
        #     "players_info": Box(0, 1, shape=(3, 52, 6)),
        #     "history": Sequence(Box(0, 1, shape=(52,))),
        #     "first_player_indices": Sequence(Discrete(4)),
        #     "is_declaration_phase": Space()},
        # )
        history = game_info['history']
        first_player_indices = game_info['first_player_indices']
        agent_info = game_info['agent_info']
        players_info = game_info['players_info']
        
        history = reshape_history(history, first_player_indices)
        # Output should be a 52 x 1 vector
        out = self.model(history=history, 
                        agent_info=agent_info,
                        player1_info=players_info[0],
                        player2_info=players_info[1],
                        player3_info=players_info[2])


        # print(out.shape)
        # print(out)
        if return_value:
            return torch.amax(torch.from_numpy(legal_moves) * out)
        
        # Sometimes play a random card
        if epsilon_greedy and random() <= self.epsilon:
            return legal_moves.get_one_random_card()

        # # Filter out legal moves
        # out = legal_moves * out 

        # out = torch.from_numpy(legal_moves) * out.detach().numpy()
        # Softmax output
        out = torch.softmax(out, dim=0)
        # Filter out legal moves
        out = torch.from_numpy(legal_moves) * out
        # Choose the best move
        action = torch.argmax(out)

        cardToPlay = Card(value=action)

        return cardToPlay

    def action_value_estimate(self, 
        legal_moves: CardCollection,
        action: Card,
        game_info: dict = None):

        assert action in legal_moves, "action must be in legal moves."
        history = game_info['history']
        first_player_indices = game_info['first_player_indices']
        agent_info = game_info['agent_info']
        players_info = game_info['players_info']
        
        history = reshape_history(history, first_player_indices)
        # Output should be a 52 x 1 vector
        out = self.model(history=history, 
                        agent_info=agent_info,
                        player1_info=players_info[0],
                        player2_info=players_info[1],
                        player3_info=players_info[2])
                
        return out[action.value]

    def parameters(self):
        return self.model.parameters()
        
    def decide_declarations(self, 
        hand: CardCollection,
        game_info: dict = None):
        # TODO: implement declaration
        return Declaration()

    def __str___(self):
        return f'VanillaDMC_Epsilon={self.epsilon}'