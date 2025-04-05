# Arena for testing performance of difference agents
from card import Card, CardCollection
from card import PIG, SHEEP, DOUBLER, PIGPEN, BLOOD
from env import Gongzhu
from player import Player
from policy import Policy, RandomPolicy, GreedyPolicy, DMC, MFE
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

def update_ratings(players : List[Player], margin : float, indices, ratings, lock, k : float = 16):
    with lock:
        for i, index in enumerate(indices):
            players[i].set_rating(ratings[index])
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
        for i, index in enumerate(indices):
            ratings[index] = players[i].get_rating()

def simulate(env : Gongzhu, players : List[Player], indices, ratings, lock):
    '''
    Simulate a game played by 4 players and update their elo ratings
    '''
    assert len(players) == 4, "You must have exactly 4 players"
    _players =[player.duplicate() for player in players]
    state, info = env.reset(ai_players=_players)
    terminated = False
    final_reward = None
    while not terminated:
        action = _players[0].policy.decide_action(legal_moves = env.agent_legal_moves(), 
                                                game_info=state)
        state, reward, terminated, _, _ = env.step(action)
        if terminated:
            final_reward = reward
    # Update elo ratings
    update_ratings(players, margin=final_reward, indices=indices, ratings=ratings, lock=lock)
    # print(f"After update ratings, the players are {players}")
    return final_reward

def calculate_player_statistics(players : List[Player]):
    player_ratings = [player.get_rating() for player in players]
    mean_rating = np.mean(player_ratings)
    std_dev = np.std(player_ratings)
    return player_ratings, mean_rating, std_dev

def play(players : List[Player], num_simulations : int, iteration, ratings, same_agent, lock):
    global iteration_lock
    local_simulations = 0
    env = Gongzhu()
    while iteration.value < num_simulations:
        # Randomly choose 4 players 
        if same_agent:
            players_to_simulate_indices = np.random.choice(range(len(players)), size=2, replace=False)
            players_to_simulate = [players[i] for i in players_to_simulate_indices] * 2
        else:
            players_to_simulate_indices = np.random.choice(range(len(players)), size=4, replace=False)
            players_to_simulate = [players[i] for i in players_to_simulate_indices]
        # print(f"Simulation {cnt+1}:")
        # print(f"Players: {players_to_simulate}")
        # Simulate the game
        final_reward = simulate(env=env, players=players_to_simulate, 
                                indices=players_to_simulate_indices, ratings=ratings,
                                lock=lock)
        # print(f"Final Reward: {final_reward}")
        # print(f"Players: {players_to_simulate}")
        with lock:
            if iteration.value % 1000 == 0:
                print(f"Iteration {iteration.value}")
            iteration.value += 1
            local_simulations += 1  
    
    # print(f"Local simulations: {local_simulations}")

def arena(policies : List[Policy], num_players : int,
          num_simulations : int, num_processes : int,
          same_agent : bool = False):
    # Create players
    players_by_policies = [[Player(policy=policy) for _ in range(num_players_per_policy)] 
        for policy in policies]
    players = [player for players_by_policy in players_by_policies for player in players_by_policy ]

    # Initialize multithreading pool
    ctx = mp.get_context('spawn')
    # global ratings
    ratings = ctx.Array('f', [player.get_rating() for player in players])
    lock = mp.Lock()
    iteration = ctx.Value('i', 0)
    actor_processes : List[mp.Process] = []
    for i in range(num_processes):
        actor = ctx.Process(
            target=play,
            args=(players, num_simulations, iteration, ratings, same_agent, lock)
        )
        actor_processes.append(actor)

    # Start timer
    start_time = time.time()

    # Start all processes
    for actor in actor_processes:
        actor.start()
    # Wait for all processes to finish
    for actor in actor_processes:
        actor.join()
        
    for i, player in enumerate(players):
        player.set_rating(ratings[i])
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    print(f"Simulated {num_simulations} games with {num_processes} processes. Elapsed time: {elapsed_time} seconds")

    # Plot the results
    from matplotlib import pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 6), gridspec_kw={'width_ratios': [3, 1]})

    # Whole picture of the simulation
    # player_ratings, player_mean, player_std = calculate_player_statistics(players)
    # print(f"Mean = {player_mean}, std = {player_std}")

    for i, policy in enumerate(policies):
        player_ratings, player_mean, player_std = calculate_player_statistics(players_by_policies[i])
        print(f"{policy.get_label()}\nMean = {player_mean}, std = {player_std}")
        # Scatter plot
        axes[0].scatter([i+1] * num_players_per_policy, 
            player_ratings, label=f"{policy.get_label()}", alpha=0.6)
        # Histogram Plot
        axes[1].hist(player_ratings, 
            bins=20, alpha=0.6, orientation='horizontal', label=f"{policy.get_label()}")
    
    axes[0].set_xticks(range(1, len(policies)+1))
    axes[0].set_xticklabels([policy.get_label() for policy in policies])
    axes[0].set_ylabel("Player Ratings")
    axes[0].set_title("Scatter Plot")
    axes[1].set_title("Histograms")
    axes[1].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='GongzhuAI arena')
    parser.add_argument('--num_players', default=50, type=int,
                    help='Number of players per agent to simulate')
    parser.add_argument('--num_simulations', default=100000, type=int,
                        help='Number of simulations')    
    parser.add_argument('--num_processes', default=4, type=int,
                        help='Number of processes to simulate') 
    parser.add_argument('--same_agent', action='store_true', default=True,
                    help='Force teammates to have the same agent')
    args = parser.parse_args()

    # Hyperparameters
    num_players_per_policy = args.num_players
    num_simulations = args.num_simulations
    num_processes = args.num_processes
    same_agent = args.same_agent
    print(f"num_players_per_policy={num_players_per_policy}")
    print(f"num_simulations={num_simulations}")
    print(f"num_processes={num_processes}")
    print(f"same_agent={same_agent}")

    checkpoint_state = torch.load(
        "gongzhuai_checkpoints/models/dmc/weights_1e6_2.ckpt"
    )
    random_policy = RandomPolicy(label="Random")
    greedy_policy = GreedyPolicy(label="Greedy")
    # dmc_0 = DMC(label="DMC_0")
    dmc_1e6 = DMC(label="DMC_1e6")
    dmc_1e6.load_state_dict(checkpoint_state)

    # checkpoint_state = torch.load(
    #     "gongzhuai_checkpoints/models/mfe/weights_15e5.ckpt"
    # )
    num_mfe = 4
    mfes_15e5 = []
    for i in range(num_mfe):
        mfes_15e5.append(MFE(label=f"MFE_15e5_{i+1}"))
        checkpoint_state = torch.load(
            f"gongzhuai_checkpoints/models/mfe/weights_15e5_{i+1}.ckpt"
        )
        mfes_15e5[-1].load_state_dict(checkpoint_state)

    # Run the arena simulations
    arena(
        # policies=[random_policy, greedy_policy, dmc_1e6, mfe_15e5],
        policies=[random_policy, greedy_policy, dmc_1e6,
            *mfes_15e5],
        num_players=num_players_per_policy,
        num_processes=num_processes,
        num_simulations=num_simulations,
        same_agent=same_agent)
    # # Create players
    # random_players = [Player(policy=RandomPolicy()) for _ in range(num_players_per_policy)]
    # greedy_players = [Player(policy=GreedyPolicy(epsilon=0)) for _ in range(num_players_per_policy)]
    # checkpoint_state = torch.load(
    #     "gongzhuai_checkpoints/gongzhuai/weights_10027.ckpt"
    # )
    # dmc_1e6 = DMC()
    # dmc_1e6.load_state_dict(checkpoint_state)
    # dmc_players = [Player(policy=dmc_model) for _ in range(num_players_per_policy)]
    # players = random_players + greedy_players + dmc_players
    # # print(ratings)
    
    # env = Gongzhu()

    # # Initialize multithreading pool
    # ctx = mp.get_context('spawn')
    # # global ratings
    # ratings = ctx.Array('f', [player.get_rating() for player in players])
    # players_lock = ctx.Lock()
    # lock = mp.Lock()
    # iteration = ctx.Value('i', 0)
    # actor_processes : List[mp.Process] = []
    # for i in range(num_processes):
    #     actor = ctx.Process(
    #         target=play,
    #         args=(players, num_simulations, iteration, ratings, lock)
    #     )
    #     actor_processes.append(actor)

    # # Start timer
    # start_time = time.time()

    # # Start all processes
    # for actor in actor_processes:
    #     actor.start()
    # # Wait for all processes to finish
    # for actor in actor_processes:
    #     actor.join()
        
    # for i, player in enumerate(players):
    #     player.set_rating(ratings[i])
    # # Calculate elapsed time
    # elapsed_time = time.time() - start_time
    # print(f"Simulated {num_simulations} games with {num_processes} processes. Elapsed time: {elapsed_time} seconds")
    # random_player_ratings, random_player_mean, random_player_std = calculate_player_statistics(random_players)
    # print(f"Random Player ratings = {random_player_ratings}, \nMean = {random_player_mean}, std = {random_player_std}")
    # greedy_player_ratings, greedy_player_mean, greedy_player_std = calculate_player_statistics(greedy_players)
    # print(f"Greedy Player ratings = {greedy_player_ratings}, \nMean = {greedy_player_mean}, std = {greedy_player_std}")
    # dmc_player_ratings, dmc_player_mean, dmc_player_std = calculate_player_statistics(dmc_players)
    # print(f"DMC Player ratings = {dmc_player_ratings}, \nMean = {dmc_player_mean}, std = {dmc_player_std}")

    # # Plot the results
    # from matplotlib import pyplot as plt
    # # plt.scatter([1]*num_players_per_policy, random_player_ratings, label='Random Players')
    # # plt.scatter([2]*num_players_per_policy, greedy_player_ratings, label='Greedy Players')
    # # plt.scatter([3]*num_players_per_policy, dmc_player_ratings, label='DMC Players')
    # # plt.legend(loc='upper right')
    # # plt.show()
    # fig, axes = plt.subplots(1, 2, figsize=(10, 6), gridspec_kw={'width_ratios': [3, 1]})

    # # Scatter plot
    # axes[0].scatter([1] * num_players_per_policy, random_player_ratings, label="Random Players", color="blue", alpha=0.6)
    # axes[0].scatter([2] * num_players_per_policy, greedy_player_ratings, label="Greedy Players", color="green", alpha=0.6)
    # axes[0].scatter([3] * num_players_per_policy, dmc_player_ratings, label="DMC Players", color="red", alpha=0.6)
    # axes[0].set_xticks([1, 2, 3])
    # axes[0].set_xticklabels(["Random", "Greedy", "DMC"])
    # axes[0].set_ylabel("Player Ratings")
    # axes[0].set_title("Scatter Plot")

    # # Histogram Plot
    # axes[1].hist(random_player_ratings, bins=20, color="blue", alpha=0.6, orientation='horizontal', label="Random")
    # axes[1].hist(greedy_player_ratings, bins=20, color="green", alpha=0.6, orientation='horizontal', label="Greedy")
    # axes[1].hist(dmc_player_ratings, bins=20, color="red", alpha=0.6, orientation='horizontal', label="DMC")
    # axes[1].set_title("Histograms")
    # axes[1].legend()

    # plt.tight_layout()
    # plt.show()