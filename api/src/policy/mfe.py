# Manual feature extraction policy
# In order to shrink the state space
# And accelerate training
from typing import List, TYPE_CHECKING
from card import Card, CardCollection
from card import PIG, SHEEP, DOUBLER, PIGPEN, BLOOD, HEARTSUITE, SHEEPPEN, DOUBLERCATCHER
from declaration import Declaration
from random import random
import numpy as np
from policy import Policy
from policy.models import GongzhuMFE
from policy.dmc import reshape_history, reshape_history_single
import torch.nn.utils.rnn as rnn_utils
import torch

def state_transformation(states):
    new_states = {
        'history' : [state['history'] for state in states],
        'first_player_indices' : [state['first_player_indices'] for state in states],
        'agent_info' : [state['agent_info'] for state in states],
        'players_info' : [[state['players_info'][i] for state in states] for i in range(3)],
        'scores' : [state['scores'] for state in states]
    }
    return new_states

class ManualFeatureExtractor(Policy):

    def __init__(self, label : str = "MFE",
                epsilon: float = 0.05,
                n_features: int = 600,
                device: str = "cpu",
                temperature: float = 1):
        super().__init__(label=label, epsilon=epsilon)
        # Number of extracted features
        self.device = device
        self.n_features = n_features
        self.model = GongzhuMFE(feature_size=self.n_features)

    def extract_features(self, game_info : dict):
        # Extract relevant features from game_info
        # Return a tensor of shape (n_features)
        # First, extract the four 
        features = np.zeros(self.n_features)
        history = game_info['history']
        first_player_indices = game_info['first_player_indices']
        agent_info = game_info['agent_info']
        players_info = game_info['players_info']
        scores = game_info['scores']
        # General features
        # Cards have been played in this game
        features[:52] = np.sum(history)
        # Agent's hand
        features[52:104] = agent_info[0]
        # Agent's collected cards
        features[104:156] = agent_info[1]
        # Agent's played cards
        features[156:208] = agent_info[2]
        # Cards collected/played by other players
        features[208:260] = players_info[0][0]
        features[260:312] = players_info[0][1]
        features[312:364] = players_info[1][0]
        features[364:416] = players_info[1][1]
        features[416:468] = players_info[2][0]
        features[468:520] = players_info[2][1]
        B = 520
        # See if the four special cards have been played
        features[B + 0] = self.hasPlayedTheCard(PIG, history)
        features[B + 1] = self.hasPlayedTheCard(SHEEP, history)
        features[B + 2] = self.hasPlayedTheCard(DOUBLER, history)
        features[B + 3] = self.hasPlayedTheCard(BLOOD, history)
        # Number of cards played in each suit
        features[B + 4] = np.sum(features[:13])
        features[B + 5] = np.sum(features[13:26])
        features[B + 6] = np.sum(features[26:39])
        features[B + 7] = np.sum(features[39:52])
        B = B + 8
        # Number of cards played in each suit for all players
        for i in range(4):
            features[B + i * 4] = np.sum(features[156 + 52 * i : 169 + 52 * i])
            features[B + 1 + i * 4] = np.sum(features[169 + 52 * i : 182 + 52 * i])
            features[B + 2 + i * 4] = np.sum(features[182 + 52 * i : 195 + 52 * i])
            features[B + 3 + i * 4] = np.sum(features[195 + 52 * i : 208 + 52 * i])
        B = B + 16
        # Determine if any player run out of a suit
        # And if they have started a suit
        first_player_index = first_player_indices[0]
        current_suit = None
        for index, h in enumerate(history):
            card : Card = h.view(Card)
            first_player_index = first_player_indices[index // 4]
            this_player_index = (first_player_index + index) % 4
            if index % 4 == 0:
                current_suit = card.suit
                features[B + 16 + this_player_index * 4 + (card.value // 4)] = 1
            elif card.suit != current_suit:
                features[B + this_player_index * 4 + (card.value // 4)] = 1
        for j in range(4):
            if features[524 + j] >= 13:
                for i in range(4):  
                    features[B + i * 4 + j] = 1
        B = B + 32
        # Determine if each player still has chance to collect every heart
        for i in range(4):
            features[B + i] = 1 if features[526] == features[528 + 4*i + 2] else 0
        B = B + 4
        # Current score of each player
        features[B : B + 4] = scores
        # Team scores
        features[B+4] = features[B] + features[B+2]
        features[B+5] = features[B+1] + features[B+3]
        B = B + 6
        # Some misc information
        # Whether the agent has pigpens
        agent_hand : CardCollection = agent_info[0].view(CardCollection)
        if agent_hand.intersect(PIGPEN) is not None:
            features[B + 0] = 1
        if agent_hand.intersect(SHEEPPEN) is not None:
            features[B + 1] = 1        
        if agent_hand.intersect(DOUBLERCATCHER) is not None:
            features[B + 2] = 1      
        return torch.from_numpy(features)

    def action_value_estimate(self, 
        legal_moves: CardCollection,
        action: Card,
        game_info: dict):

        assert action in legal_moves, "action must be in legal moves."

        out = self.forward(game_info)
                
        return out[action.value]
    def decide_action(self, 
        legal_moves: CardCollection,
        game_info: dict = None,
        epsilon_greedy: bool = True,
        return_value: bool = False,
        batch : bool = False,
        return_probs : bool = False) -> Card:

        out = self.forward(game_info, batch=batch)
        # print(out)
        # In return value mode, we can directly return a vector
        if return_probs:
            
            pass

        if return_value:
            return torch.amax(torch.from_numpy(np.array(legal_moves)) * out)
            
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
        # print(out)
        # Choose the best move
        action = torch.argmax(out)

        cardToPlay = Card(value=action)

        return cardToPlay

    def parameters(self):
        return self.model.parameters()
        
    def decide_declarations(self, 
        hand: CardCollection,
        game_info: dict = None):
        # TODO: implement declaration
        return Declaration()

    def __str___(self):
        return f'MFE_Epsilon={self.epsilon}'
    
    def load_state_dict(self, dir):
        self.model.load_state_dict(dir)

    def state_dict(self):
        return self.model.state_dict()
    
    def forward(self, game_info, batch : bool = False):
        # print(game_info.__class__.__name__)
        states = state_transformation(game_info) if batch else game_info
        history = states['history']
        first_player_indices = states['first_player_indices']
        
        history = reshape_history(history, first_player_indices) if batch else \
                  reshape_history_single(history, first_player_indices)  
        
        features = self.extract_features(game_info) if not batch else \
            torch.stack([self.extract_features(info) for info in game_info])

        # Output should be a 52 x 1 vector
        out = self.model(history=history, features=features)
        return out
    
    def eval(self) -> None:
        self.model.eval()
    
    def train(self) -> None:
        self.model.train()