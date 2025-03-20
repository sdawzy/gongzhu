# Arena for testing performance of difference agents
from card import Card, CardCollection
from card import PIG, SHEEP, DOUBLER, PIGPEN, BLOOD
from env import Gongzhu
from player import Player
from policy import Policy, RandomPolicy, GreedyPolicy, DMC
from typing import List, Tuple, Dict

import threading
import numpy as np
import timeit
import time
import torch
from torch import multiprocessing as mp
from torch import nn
import pprint

from multiprocessing import SimpleQueue
from .file_writer import FileWriter
from .utils import sampler, Flag, create_buffers, create_optimizer, get_batch, log
import os
from policy import DMC

def sigmoid_base_ten(x):
    return 1 / (1 + np.power(10, -x))

def update_ratings(players : List[Player], margin : float, k : float = 16):
    # Scale the k factor with respect to the scale of the margin
    adjusted_k = k * np.log(1 + np.abs(margin))
    agent_team_rating = (players[0].get_rating() + players[2].get_rating()) / 2
    opponent_team_rating = (players[1].get_rating() + players[3].get_rating()) / 2
    # Calculate the expected score
    e_a = sigmoid_base_ten((agent_team_rating-opponent_team_rating) / 400)
    e_b = sigmoid_base_ten((opponent_team_rating-agent_team_rating) / 400)
    # Determine the actual score
    s_a = 1 if margin > 0 else 0 if margin < 0 else 0.5
    s_b = 1 - s_a
    # Calculate the change of ratings
    change_agent_team_rating = adjusted_k * (s_a - e_a)
    change_opponent_team_rating = adjusted_k * (s_b - e_b)
    # Update the ratings
    players[0].update_rating(change_agent_team_rating / 2)
    players[2].update_rating(change_agent_team_rating / 2)
    players[1].update_rating(change_opponent_team_rating / 2)
    players[3].update_rating(change_opponent_team_rating / 2)

def simulate(env : Gongzhu, players : List[Player]):
    '''
    Simulate a game played by 4 players and update their elo ratings
    '''
    assert len(players) == 4, "You must have exactly 4 players"
    state, info = env.reset(ai_players=players)
    terminated = False
    final_reward = None
    while not terminated:
        action = players[0].policy.decide_action(legal_moves = env.agent_legal_moves(), 
                                                game_info=state)
        state, reward, terminated, _, _ = env.step(action)
        if terminated:
            final_reward = reward
    # Update elo ratings
    update_ratings(players, margin=final_reward)
    # print(f"After update ratings, the players are {players}")
    return final_reward

def calculate_player_statistics(players : List[Player]):
    player_ratings = [player.get_rating() for player in players]
    mean_rating = np.mean(player_ratings)
    std_dev = np.std(player_ratings)
    return player_ratings, mean_rating, std_dev

if __name__ == "__main__":
    num_players_per_policy = 20
    num_simulations = 65531
    # Create players
    random_players = [Player(policy=RandomPolicy()) for _ in range(num_players_per_policy)]
    greedy_players = [Player(policy=GreedyPolicy(epsilon=0)) for _ in range(num_players_per_policy)]
    checkpoint_state = torch.load(
        "gongzhuai_checkpoints/gongzhuai/weights_10027.ckpt"
    )
    dmc_model = DMC()
    dmc_model.load_state_dict(checkpoint_state)
    dmc_players = [Player(policy=dmc_model) for _ in range(num_players_per_policy)]
    players = random_players + greedy_players + dmc_players

    iteration = 0
    env = Gongzhu()
    while iteration < num_simulations:
        if iteration % 1000 == 0:
            print(f"Iteration {iteration}")
        # Randomly choose 4 players 
        players_to_simulate = np.random.choice(players, size=4, replace=False)
        # print(f"Simulation {cnt+1}:")
        # print(f"Players: {players_to_simulate}")
        # Simulate the game
        final_reward = simulate(env=env, players=players_to_simulate)
        # print(f"Final Reward: {final_reward}")
        # print(f"Players: {players_to_simulate}")
        iteration += 1

    random_player_ratings, random_player_mean, random_player_std = calculate_player_statistics(random_players)
    print(f"Random Player ratings = {random_player_ratings}, mean = {random_player_mean}, std = {random_player_std}")
    greedy_player_ratings, greedy_player_mean, greedy_player_std = calculate_player_statistics(greedy_players)
    print(f"Greedy Player ratings = {greedy_player_ratings}, mean = {greedy_player_mean}, std = {greedy_player_std}")
    dmc_player_ratings, dmc_player_mean, dmc_player_std = calculate_player_statistics(dmc_players)
    print(f"DMC Player ratings = {dmc_player_ratings}, mean = {dmc_player_mean}, std = {dmc_player_std}")

    # print(f"Random Players: {random_players}")
    # print(f"Greedy Players: {greedy_players}")