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

def compute_ppo_loss(log_probs_old, log_probs_new, advantages, epsilon=0.2):
    """Computes the PPO surrogate loss with clipping."""
    ratio = torch.exp(log_probs_new - log_probs_old)  # Importance sampling ratio
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - epsilon, 1 + epsilon) * advantages
    return -torch.min(surr1, surr2).mean()  # Negative for gradient ascent

def compute_value_loss(values, targets):
    """Computes the value function loss using MSE."""
    return nn.MSELoss()(values.squeeze(), targets)

def compute_entropy_loss(probs):
    """Encourages exploration by maximizing entropy."""
    return -torch.mean(torch.sum(probs * torch.log(probs + 1e-10), dim=-1))

def learn_ppo(learner_model : MFE,
          samples: dict,
          optimizer: torch.optim.Optimizer,
          flags,
          scale: float = 0.001,
          entropy_coef: float = 0.01,
          epsilon: float = 1e-10):
    """Performs a PPO update step."""
    
    # Convert rewards to tensors and scale
    targets = torch.Tensor(samples["final_reward"]) * scale
    legal_moves = samples["legal_moves"]
    states = samples['state']
    
    # Forward pass through the model
    outputs, values_old, log_probs_old = learner_model.decide_action(
        legal_moves=legal_moves, batch=True, game_info=states, 
        return_value=True, return_log_probs=True
    )
    
    # Compute advantages
    advantages = (targets - values_old).detach()  # Simple advantage computation
    
    # Compute new log probabilities after update
    log_probs_new = outputs.log_prob(samples["actions"])
    
    # Compute PPO loss components
    policy_loss = compute_ppo_loss(log_probs_old, log_probs_new, advantages, epsilon=flags.clip_epsilon)
    value_loss = compute_value_loss(values_old, targets)
    entropy_loss = compute_entropy_loss(torch.softmax(outputs, dim=-1))  # Encourages exploration

    # Total loss
    loss = policy_loss + 0.5 * value_loss - entropy_coef * entropy_loss
    
    # Gradient update
    optimizer.zero_grad()
    loss.backward()
    nn.utils.clip_grad_norm_(learner_model.parameters(), flags.max_grad_norm)
    optimizer.step()

    return loss.item(), None

def compute_loss(logits, targets) -> torch.Tensor:
    loss = ((logits.squeeze(0) - targets)**2).mean()
    return loss

def learn_mse(learner_model,
          samples : List,
          optimizer : torch.optim.Optimizer,
          flags : Flag,
          scale : float = 0.001):
    targets = torch.Tensor(samples["final_reward"]) * scale

    legal_moves = samples["legal_moves"]
    states = samples['state']

    outputs = learner_model.decide_action(legal_moves=legal_moves, batch=True,
                         game_info=states, return_value=True)
    nn.utils.clip_grad_norm_(learner_model.parameters(), flags.max_grad_norm)

    loss = compute_loss(outputs, targets)
    optimizer.zero_grad()
    loss.backward()
    nn.utils.clip_grad_norm_(learner_model.parameters(), flags.max_grad_norm)
    optimizer.step()
    return loss.item(), None

def learn_old():
# def learn(actor_models : List[DMC],
#           model : DMC,
#           batch,
#           optimizer,
#           flags : Flag,
#           lock):
#     """Performs a learning (optimization) step."""
#     if flags.training_device != "cpu":
#         device = torch.device('cuda:'+str(flags.training_device))
#     else:
#         device = torch.device('cpu')
#     obs_x_no_action = batch['obs_x_no_action'].to(device)
#     obs_action = batch['obs_action'].to(device)
#     obs_x = torch.cat((obs_x_no_action, obs_action), dim=2).float()
#     obs_x = torch.flatten(obs_x, 0, 1)
#     obs_z = torch.flatten(batch['obs_z'].to(device), 0, 1).float()
#     target = torch.flatten(batch['target'].to(device), 0, 1)
#     episode_returns = batch['episode_return'][batch['done']]
#     mean_episode_return_buf[position].append(torch.mean(episode_returns).to(device))
        
#     with lock:
#         learner_outputs = model(obs_z, obs_x, return_value=True)
#         loss = compute_loss(learner_outputs['values'], target)
#         stats = {
#             'mean_episode_return_'+position: torch.mean(torch.stack([_r for _r in mean_episode_return_buf[position]])).item(),
#             'loss_'+position: loss.item(),
#         }
        
#         optimizer.zero_grad()
#         loss.backward()
#         nn.utils.clip_grad_norm_(model.parameters(), flags.max_grad_norm)
#         optimizer.step()

#         for actor_model in actor_models:
#             actor_model.load_state_dict(model.state_dict())
#         return stats
    pass

def train(flags : Flag):
    """
    Right now process in single thread
    """
    if not flags.actor_device_cpu or flags.training_device != 'cpu':
        if not torch.cuda.is_available():
            raise AssertionError("CUDA not available. If you have GPUs, please specify the ID after `--gpu_devices`. Otherwise, please train with CPU with `python3 train.py --actor_device_cpu --training_device cpu`")
    
    plogger = FileWriter(
        xpid=flags.xpid,
        xp_args=flags.__dict__,
        rootdir=flags.savedir,
    )
    
    checkpointpath = os.path.expandvars(
        os.path.expanduser('%s/%s/%s' % (flags.savedir, flags.xpid, f'model_{flags.training_device}.tar')))


    if flags.actor_device_cpu:
        device_iterator = ['cpu']
    else:
        device_iterator = range(flags.num_actor_devices)
        assert flags.num_actor_devices <= len(flags.gpu_devices.split(',')), 'The number of actor devices can not exceed the number of available devices'

    # # Initialize actor models
    # models : Dict[str, DMC] = {}
    # for device in device_iterator:
    #     model = DMC(device=device)
    #     models[device] = model

    # Actor models used for sampling
    default_actor_models : List[Policy] = [RandomPolicy(), RandomPolicy(),
                 GreedyPolicy(), GreedyPolicy()]
    # actor_models : Dict[str, List[Policy]] = default_actor_models

    num_old_versions : int = 0

    dmc_old = DMC()
    mfe1_old = MFE()
    mfe2_old = MFE()
    mfe3_old = MFE()
    dmc_old.load_state_dict(torch.load(
        "gongzhuai_checkpoints/models/dmc/weights_1e6_2.ckpt"
    ))
    mfe1_old.load_state_dict(torch.load(
        "gongzhuai_checkpoints/models/mfe/weights_15e5_1.ckpt"
    ))
    mfe2_old.load_state_dict(torch.load(
        "gongzhuai_checkpoints/models/mfe/weights_15e5_2.ckpt"
    ))
    mfe3_old.load_state_dict(torch.load(
        "gongzhuai_checkpoints/models/mfe/weights_15e5_3.ckpt"
    ))
    default_actor_models.append(dmc_old)
    default_actor_models.append(mfe1_old)
    default_actor_models.append(mfe2_old)
    default_actor_models.append(mfe3_old)
    def init_buffers():
    # Initialize buffers
    # buffers = create_buffers(flags, device_iterator)
   
    # Initialize queues
    # actor_processes = []
    # ctx = mp.get_context('spawn')
    # free_queue : Dict[str, SimpleQueue] = {}
    # full_queue : Dict[str, SimpleQueue] = {}
        
    # for device in device_iterator:
    #     _free_queue = ctx.SimpleQueue()
    #     _full_queue = ctx.SimpleQueue()
    #     free_queue[device] = _free_queue
    #     full_queue[device] = _full_queue
        pass

    # Learner model for training
    # learner_model = DMC(device=flags.training_device)
    learner_model = MFE(device=flags.training_device)
    # Create optimizers
    optimizer = create_optimizer(flags, learner_model)

    # Stat Keys
    stat_keys = [
        'loss',
        'mean_epsilon_return'
    ]
    frames = 0
    stats = {k: 0 for k in stat_keys}

    def checkpoint(frames):
        if flags.disable_checkpoint:
            return
        log.info('Saving checkpoint to %s', checkpointpath)
        torch.save({
            'model_state_dict': learner_model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            # 'num_old_versions': old_versions,
            # 'old_versions': [old_version.state_dict() 
            #         for old_version in old_versions],
            "stats": stats,
            'flags': vars(flags),
            'frames': frames,
        }, checkpointpath)

        # Save the weights for evaluation purpose
        model_weights_dir = os.path.expandvars(os.path.expanduser(
            '%s/%s/%s' % (flags.savedir, flags.xpid, 'weights_'+str(frames)+'.ckpt')))
        torch.save(learner_model.state_dict(), model_weights_dir)

    # Load models if any
    if flags.load_model and os.path.exists(checkpointpath):
        checkpoint_states = torch.load(
            checkpointpath
        )
        learner_model.load_state_dict(checkpoint_states["model_state_dict"])
        optimizer.load_state_dict(checkpoint_states["optimizer_state_dict"])
        num_old_versions = checkpoint_states["num_old_versions"]
        old_version_states = checkpoint_states["old_versions"]
        # actor_models[device] = []
        old_versions = [MFE() for _ in range(num_old_versions)]
        old_versions = [old_versions[i].load_state_dict(old_version_states[i]) 
                        for i in range(num_old_versions)]

        stats = checkpoint_states["stats"]
        frames = checkpoint_states["frames"]
        log.info(f"Resuming preempted job, current stats:\n{stats}")

    def multithread():
    # Starting actor processes
    # for device in device_iterator:
    #     num_actors = flags.num_actors
    #     for i in range(flags.num_actors):
    #         actor = ctx.Process(
    #             target=act,
    #             args=(i, device, free_queue[device], full_queue[device], models[device], buffers[device], flags))
    #         actor.start()
    #         actor_processes.append(actor)

    # def batch_and_learn(i, device, local_lock, lock=threading.Lock()):
    #     """Thread target for the learning process."""
    #     nonlocal frames, stats
    #     while frames < flags.total_frames:
    #         batch = get_batch(free_queue[device], full_queue[device], buffers[device], flags, local_lock)
    #         _stats = learn(models, learner_model, batch, 
    #             optimizer, flags)

    #         with lock:
    #             for k in _stats:
    #                 stats[k] = _stats[k]
    #             to_log = dict(frames=frames)
    #             to_log.update({k: stats[k] for k in stat_keys})
    #             plogger.log(to_log)
    #             frames += T * B

    # # Intialize free queues
    # for device in device_iterator:
    #     for m in range(flags.num_buffers):
    #         free_queue[device].put(m)
    #         free_queue[device].put(m)
    #         free_queue[device].put(m)

    # # Initialize threads and locks
    # threads : List[threading.Thread] = []
    # locks = {}
    # for device in device_iterator:
    #     locks[device] = {'landlord': threading.Lock(), 'landlord_up': threading.Lock(), 'landlord_down': threading.Lock()}

    # for device in device_iterator:
    #     for i in range(flags.num_threads):
    #         thread = threading.Thread(
    #             target=batch_and_learn, name='batch-and-learn-%d' % i, args=(i,device,locks[device]))
    #         thread.start()
    #         threads.append(thread)
        pass

    fps_log = []
    timer = timeit.default_timer
    try:
        last_checkpoint_time = timer() - flags.save_interval * 60
        while frames < flags.total_frames:

            start_frames = frames
            start_time = timer()
            time.sleep(2)

            # Sampler episodes
            samples = sampler(n = flags.batch_size, models=default_actor_models,
                              agent_policy=learner_model)
            print(f"Sampler episodes took {timer() - start_time} seconds")
            # Train on the samples
            training_start_time = timer()
            loss, msr = learn_mse(learner_model=learner_model,
                samples=samples,
                optimizer=optimizer,
                flags=flags,
                )
            training_time = timer() - training_start_time
            print(f"Training took {training_time} seconds")
            frames += flags.batch_size * 13
            # Save progress
            stats['loss'] = loss
            if timer() - last_checkpoint_time > flags.save_interval * 60:  
                checkpoint(frames)
                last_checkpoint_time = timer()
            end_time = timer()
            # Calculate fps and other relevant progress info
            fps = (frames - start_frames) / (end_time - start_time)
            fps_log.append(fps)
            if len(fps_log) > 24:
                fps_log = fps_log[1:]
            fps_avg = np.mean(fps_log)

            log.info(
                f"After {frames},"
                f"@ {fps:.1f} fps (avg@ {fps_avg:.1f} fps) "
                f"Stats:\n{pprint.pformat(stats)}"
            )

    except KeyboardInterrupt:
        return 
    else:
        # for thread in threads:
        #     thread.join()
        log.info('Learning finished after %d frames.', frames)

    checkpoint(frames)
    plogger.close()

if __name__ == '__main__':
    from .arguments import parser
    flags : Flag = parser.parse_args()
    print(flags)
    train(flags=flags)