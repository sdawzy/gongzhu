from typing import TYPE_CHECKING
import torch
from torch import nn
if TYPE_CHECKING:
    from env import Gongzhu

# First, the model class
class HistoryGRU(nn.Module):
    def __init__(self, input_size = 52 * 4, hidden_size=131, output_size=17):
        super().__init__()
        self.output_size = output_size
        self.gru = nn.GRU(input_size=input_size, hidden_size=hidden_size, batch_first=True)
        self.dense1 = nn.Linear(hidden_size, 255)
        self.dense2 = nn.Linear(255, 255)
        self.dense3 = nn.Linear(255, 255)
        self.dense4 = nn.Linear(255, 255)
        self.dense5 = nn.Linear(255, 255)
        self.dense6 = nn.Linear(255, output_size)

    def forward(self, history : torch.Tensor):
        if len(history) == 0:
            return torch.zeros(self.output_size)
        # history = torch.stack(history)
        gru_out, h_n = self.gru(history.transpose(0, -2))
        gru_out = gru_out[-1,:]
        x = gru_out
        x = self.dense1(x)
        x = torch.relu(x)
        x = self.dense2(x)
        x = torch.relu(x)
        x = self.dense3(x)
        x = torch.relu(x)
        x = self.dense4(x)
        x = torch.relu(x)
        x = self.dense5(x)
        x = torch.relu(x)
        x = self.dense6(x)
        # print(f"proccessed histroy through GRU.")
        return x
        if return_value:
            return dict(values=x)
        else:
            if flags is not None and flags.exp_epsilon > 0 and np.random.rand() < flags.exp_epsilon:
                action = torch.randint(x.shape[0], (1,))[0]
            else:
                action = torch.argmax(x,dim=0)[0]
            return dict(action=action)

class InfoExtractor(nn.Module):
    def __init__(self, input_size=52, hidden_size=131, output_size=17):
        super().__init__()
        self.input_size = input_size
        self.dense1 = nn.Linear(input_size, hidden_size)
        self.dense2 = nn.Linear(hidden_size, hidden_size)
        self.dense3 = nn.Linear(hidden_size, hidden_size)
        self.dense4 = nn.Linear(hidden_size, hidden_size)
        self.dense5 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x : torch.Tensor):
        x = x.flatten(start_dim=-2, end_dim=-1).float()  # Flatten the input tensor
        x = self.dense1(x)
        x = torch.relu(x)
        x = self.dense2(x)
        x = torch.relu(x)
        x = self.dense3(x)
        x = torch.relu(x)
        x = self.dense4(x)
        x = torch.relu(x)
        x = self.dense5(x)
        return x

class GongzhuDMC(nn.Module):

    def __init__(self, hidden_size=131, output_size=97):
        super().__init__()
        # GRU for processing the history
        # self.history_gru = nn.GRU(input_size=52 * 4, hidden_size=hidden_size, batch_first=True)
        self.history_gru : HistoryGRU = HistoryGRU(input_size=52 * 4, hidden_size=hidden_size, output_size=output_size)
        # Four different agent info extractors
        self.agent_info_extractor = InfoExtractor(input_size=6 * 52, 
                                                hidden_size=hidden_size, 
                                                output_size=output_size)
        self.player1_info_extractor = InfoExtractor(input_size=6 * 52, 
                                                hidden_size=hidden_size, 
                                                output_size=output_size)
        self.player2_info_extractor = InfoExtractor(input_size=6 * 52, 
                                                hidden_size=hidden_size, 
                                                output_size=output_size)
        self.player3_info_extractor = InfoExtractor(input_size=6 * 52, 
                                                hidden_size=hidden_size, 
                                                output_size=output_size)    
        self.dense1 = nn.Linear(5 * output_size, hidden_size * 3)
        self.dense2 = nn.Linear(hidden_size * 3, 52)                                           
        
    def forward(self, history: torch.Tensor,
                      agent_info : torch.Tensor,
                      player1_info : torch.Tensor,
                      player2_info : torch.Tensor,
                      player3_info : torch.Tensor):
        history_out = self.history_gru(history)
        agent_info_out = self.agent_info_extractor(agent_info)
        player1_info_out = self.player1_info_extractor(player1_info)
        player2_info_out = self.player2_info_extractor(player2_info)
        player3_info_out = self.player3_info_extractor(player3_info)
        # print(history.shape)
        # print(history_out.shape)
        # print(agent_info_out.shape)
        # print(player1_info_out.shape)

        x = torch.cat([history_out, agent_info_out, 
                       player1_info_out, player2_info_out, player3_info_out], dim=-1)
        x = self.dense1(x)  
        x = torch.relu(x)
        x = self.dense2(x)
        return x
