# Modified from DouZero https://github.com/kwai/DouZero
from card import Card, CardCollection
from card import PIG, SHEEP, DOUBLER, PIGPEN, BLOOD
from env import Gongzhu
from player import Player
from policy import Policy, RandomPolicy, GreedyPolicy, DMC
from typing import List, Dict, TypedDict, Literal
import numpy as np
import logging
import torch
from torch import nn
import queue
from queue import Queue
from multiprocessing import SimpleQueue


# Set up the logger
shandle = logging.StreamHandler()
shandle.setFormatter(
    logging.Formatter(
        '[%(levelname)s:%(process)d %(module)s:%(lineno)d %(asctime)s] '
        '%(message)s'))
log = logging.getLogger('gongzhuai')
log.propagate = False
log.addHandler(shandle)
log.setLevel(logging.INFO)

# Buffers are used to transfer data between actor processes
# and learner processes. They are shared tensors in GPU
Buffers = Dict[str, List[torch.Tensor]]
# Typed Version of argument flags
class Flag(TypedDict):
    xpid : int
    save_interval : int
    objective: Literal['adp', 'wp', 'logadp']
    # Training Settings
    actor_device_cpu : bool
    training_device : str
    gpu_devices : int
    num_actor_devices : int
    num_actors : int
    training_device : str
    load_model : bool
    disable_checkpoint : bool
    savedir : str

    total_frames : int
    exp_epsilon : float
    batch_size : int
    num_buffers : int
    num_threads : int
    unroll_length : int
    max_grad_norm : float

    # Optimizer hyperparameters
    learning_rate : float
    momentum : float
    epsilon : float
    alpha : float

def get_batch(free_queue : SimpleQueue,
              full_queue : SimpleQueue,
              buffers : Buffers,
              flags : Flag,
              lock):
    """
    This function will sample a batch from the buffers based
    on the indices received from the full queue. It will also
    free the indices by sending it to full_queue.
    """
    with lock:
        indices = [full_queue.get() for _ in range(flags.batch_size)]
    batch = {
        key: torch.stack([buffers[key][m] for m in indices], dim=1)
        for key in buffers
    }
    for m in indices:
        free_queue.put(m)
    return batch

def create_optimizer(flags : Flag, 
                    learner_model : nn.Module):
    """
    Create an optimizer for the learner_model
    """
    optimizer = torch.optim.RMSprop(
            learner_model.parameters(),
            lr=flags.learning_rate,
            momentum=flags.momentum,
            eps=flags.epsilon,
            alpha=flags.alpha)

    return optimizer


def create_buffers(flags : Flag, device_iterator):
    """
    We create buffers for different positions as well as
    for different devices (i.e., GPU). That is, each device
    will have three buffers for the three positions.
    """
    T = flags.unroll_length
    buffers = {}
    for device in device_iterator:
        buffers[device] = {}
        x_dim = 319 if position == 'landlord' else 430
        specs = dict(
            done=dict(size=(T,), dtype=torch.bool),
            episode_return=dict(size=(T,), dtype=torch.float32),
            target=dict(size=(T,), dtype=torch.float32),
            obs_x_no_action=dict(size=(T, x_dim), dtype=torch.int8),
            obs_action=dict(size=(T, 54), dtype=torch.int8),
            obs_z=dict(size=(T, 5, 162), dtype=torch.int8),
        )
        _buffers: Buffers = {key: [] for key in specs}
        for _ in range(flags.num_buffers):
            for key in _buffers:
                if not device == "cpu":
                    _buffer = torch.empty(**specs[key]).to(torch.device('cuda:'+str(device))).share_memory_()
                else:
                    _buffer = torch.empty(**specs[key]).to(torch.device('cpu')).share_memory_()
                _buffers[key].append(_buffer)
        buffers[device] = _buffers
    return buffers

def sampler(n : int, models : List[Policy], agent_policy: Policy):
    env = Gongzhu()
    n_models = len(models)
    buffers = {
        "state" : [],
        "action" : [],
        "reward" : [],
        "final_reward" : [],
        "terminated" : [],
        "legal_moves" : [],
        "info" : []
    }
    for i in range(n):
        # print(f"i = {i}")
        records = []
        policies = [agent_policy, *np.random.choice(models, size=3, replace=False)]
        ai_players = [Player(policy=policy) for policy in policies]
        state, info = env.reset(ai_players=ai_players)
        final_reward = 0
        terminated = False
        round = 0
        while not terminated:
            legal_moves = env.agent_legal_moves()
            action = agent_policy.decide_action(game_info=state, legal_moves=legal_moves)
            next_state, reward, terminated, info, _ = env.step(action)
            state = next_state
            round += 1
            records.append({
                "state": state,
                "action": action,
                "reward": reward,
                "terminated": terminated,
                "info": info,
                "legal_moves": legal_moves
            })
            if terminated:
                final_reward = reward

        for record in records:
            buffers["state"].append(record["state"])
            buffers["action"].append(record["action"])
            buffers["reward"].append(record["reward"])
            buffers["final_reward"].append(final_reward)
            buffers["terminated"].append(record["terminated"])
            buffers["info"].append(record["info"])
            buffers["legal_moves"].append(record["legal_moves"])
        # buffers.append(record)
    return buffers


# Test some samples
if __name__ == '__main__':
    agent_policy = DMC()
    models = [RandomPolicy(), RandomPolicy(), 
                RandomPolicy(), RandomPolicy(), DMC(),
                RandomPolicy(), GreedyPolicy()]
    n = 89
    # Keep track of the time taken
    import time
    start_time = time.time()
    # Run the simulation
    # games = sample(n = n, models = models, agent_policy=agent_policy)
    # print(f"Number of games: {len(games)}")
    # print(games)
    buffers = sampler(n = n, models = models, agent_policy=agent_policy)
    end_time = time.time()
    print(f"Time taken to get {n} samples: {end_time - start_time} seconds")
    # print(buffers)
    # print(f"Number of games: {len(games)}")
    # print(games)