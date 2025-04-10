# Vanilla DMC agent
from typing import List, TYPE_CHECKING
from card import Card, CardCollection
from card import PIG, SHEEP, DOUBLER, PIGPEN, BLOOD
from declaration import Declaration
from random import random
import numpy as np
from policy import Policy
from policy.models import GongzhuDMC
import torch.nn.utils.rnn as rnn_utils

# from env import Gongzhu

import torch

# def reshape_history(history, first_player_indices):
#     # Reshape history from list of 52 x 1 vectors to 208 x 1 vectors
#     history_reshaped = []
#     for i, h in enumerate(history):
#         index = (first_player_indices[i // 4] + i) % 4
#         card_index = np.argmax(h)
#         new_h = torch.zeros(4 * 52)
#         new_h[52 * index + card_index] = 1
#         history_reshaped.append(new_h)

#     return history_reshaped

def reshape_history_single(history, first_player_indices):
    # Convert to tensor
    if len(history) == 0:
        return torch.zeros(52, 4 * 52)
    _history = torch.zeros(52, 52)
    history = torch.from_numpy(np.array(history))
    _history[:len(history)] = history
    
    # # Create a tensor and fill the first values
    # first_player_indices = torch.tensor(first_player_indices) 
    # indices = torch.zeros(13, dtype=int)
    # indices[:len(first_player_indices)] = torch.tensor(first_player_indices, dtype=torch.int64)
    # Directly convert first_player_indices to a tensor of the correct dtype
    first_player_indices = torch.tensor(first_player_indices, dtype=torch.int64)

    # Pre-allocate indices tensor and fill it directly in one step
    indices = torch.zeros(13, dtype=torch.int64)
    indices[:first_player_indices.size(0)] = first_player_indices

    # Use broadcasting to expand indices and add `torch.arange(4)`
    indices = (indices.unsqueeze(1) + torch.arange(4)).flatten() % 4


    # Find card indices
    _card_indices = torch.zeros(52, dtype=int)
    card_indices = torch.argmax(_history, dim=1)
    _card_indices[:len(card_indices)] = card_indices

    # Create one-hot encoding
    history_reshaped = torch.zeros(52, 4 * 52)
    row_indices = torch.arange(52)
    history_reshaped[row_indices, (52 * indices) + _card_indices] = 1

    return history_reshaped

def reshape_history(history, first_player_indices):
    """
    Converts a batch of history matrices into a batch of reshaped one-hot encoded representations.

    Args:
        history: A tensor of shape (batch_size, n, 52), where `n` is the number of steps in each batch.
        first_player_indices: A tensor or list of shape (batch_size, 13), representing the first player indices.

    Returns:
        A tensor of shape (batch_size, n, 4 * 52) with the reshaped history.
    """

    batch_size = len(history)

    # Convert history to tensors and pad sequences
    history_tensors = [torch.tensor(h, dtype=torch.float32) for h in history]  # Convert list to tensors
    padded_history = rnn_utils.pad_sequence(history_tensors, batch_first=True)  # (batch_size, max_seq_len, 52)

    # Convert first_player_indices to tensor
    # indices = torch.zeros(batch_size, 13, dtype=int)
    # indices[:len(first_player_indices)] = torch.tensor(first_player_indices, dtype=torch.int64)
    index_tensors = [torch.tensor(indices, dtype=int) for indices in first_player_indices]
    indices = rnn_utils.pad_sequence(index_tensors, batch_first=True)
    # Get max sequence length
    max_seq_len = padded_history.shape[1]

    # Compute player indices (batch-wise)
    indices = (indices.unsqueeze(-1) + torch.arange(4)) % 4  # Shape: (batch_size, 13, 4)
    indices = indices.reshape(batch_size, -1)  # Flatten (batch_size, 52)

    # Find card indices
    card_indices = torch.argmax(padded_history, dim=-1)  # Shape: (batch_size, seq_len)

    # Create one-hot encoding
    history_reshaped = torch.zeros(batch_size, max_seq_len, 4 * 52)  # Output shape (batch_size, seq_len, 208)

    # Compute positions for one-hot assignment
    row_indices = torch.arange(max_seq_len).expand(batch_size, -1)  # Shape: (batch_size, seq_len)
    batch_indices = torch.arange(batch_size).unsqueeze(1).expand(-1, max_seq_len)  # Shape: (batch_size, seq_len)

    # Compute final one-hot indices
    final_indices = (52 * indices) + card_indices  # Shape: (batch_size, seq_len)

    # Assign values in one-hot tensor
    history_reshaped[batch_indices, row_indices, final_indices] = 1

    return history_reshaped

class DMC(Policy):

    def __init__(self, label : str = None, epsilon: float = 0.05, device: str = "cpu"):
        super().__init__(label=label, epsilon=epsilon)
        # self.epsilon = epsilon
        self.model = GongzhuDMC()
        self.device = torch.device(device)

    def load_state_dict(self, dir):
        self.model.load_state_dict(dir)

    def state_dict(self):
        return self.model.state_dict()
    
    def forward(self, game_info, batch : bool = False):
        # print(game_info.__class__.__name__)
        history = game_info['history']
        first_player_indices = game_info['first_player_indices']
        agent_info = game_info['agent_info']
        players_info = game_info['players_info']
        
        history = reshape_history(history, first_player_indices) if batch else \
                  reshape_history_single(history, first_player_indices)  
        # Output should be a 52 x 1 vector
        out = self.model(history=history, 
                        agent_info=torch.tensor(agent_info),
                        player1_info=torch.tensor(players_info[0]),
                        player2_info=torch.tensor(players_info[1]),
                        player3_info=torch.tensor(players_info[2]))
        return out

    def decide_action(self, 
        legal_moves: CardCollection,
        game_info: dict = None,
        epsilon_greedy: bool = True,
        return_value: bool = False,
        batch : bool = False) -> Card:

        out = self.forward(game_info, batch=batch)

        # In return value mode, we can directly return a vector
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
        # Choose the best move
        action = torch.argmax(out)

        cardToPlay = Card(value=action)

        return cardToPlay

    def action_value_estimate(self, 
        legal_moves: CardCollection,
        action: Card,
        game_info: dict):

        assert action in legal_moves, "action must be in legal moves."

        out = self.forward(game_info)
                
        return out[action.value]

    def eval(self) -> None:
        self.model.eval()
    
    def train(self) -> None:
        self.model.train()

    def parameters(self):
        return self.model.parameters()
        
    def decide_declarations(self, 
        hand: CardCollection,
        game_info: dict = None):
        # TODO: implement declaration
        return Declaration()

    def __str___(self):
        return f'VanillaDMC_Epsilon={self.epsilon}'