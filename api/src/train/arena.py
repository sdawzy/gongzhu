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

def simulate(players : List[Player]):
    '''
    Simulate a game played by 4 players and update their elo ratings
    '''
    pass