import random
import numpy as np
import torch
from collections import deque, namedtuple
from DNPP import config

class ReplayBuffer:
    """固定大小的缓冲区，用于存储经验元组，供 DDPG Agent 学习。"""

    def __init__(self, buffer_size, batch_size, seed):
        """初始化一个 ReplayBuffer 对象。
        参数:
            buffer_size (int): 缓冲区的最大大小。
            batch_size (int): 每个训练批次的大小。
            seed (int): 随机数生成种子。
        """
        self.memory = deque(maxlen=buffer_size)
        self.batch_size = batch_size
        # 使用 namedtuple 定义经验结构，更易读
        self.experience = namedtuple("Experience", field_names=["state", "action", "reward", "next_state", "done"])
        self.seed = random.seed(seed)
        np.random.seed(seed) # 确保Numpy的随机操作也是可复现的
        torch.manual_seed(seed) # 确保PyTorch的随机操作也是可复现的

    def add(self, state, action, reward, next_state, done):
        """向内存中添加新的经验。"""
        e = self.experience(state, action, reward, next_state, done)
        self.memory.append(e)

    def sample(self):
        """从内存中随机抽取一批经验。"""
        experiences = random.sample(self.memory, k=self.batch_size)

        # 将经验元组列表转换为适合 PyTorch 张量处理的格式
        # states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(config.DEVICE)
        # actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).float().to(config.DEVICE)
        # rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(config.DEVICE)
        # next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(config.DEVICE)
        # dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(config.DEVICE)

        # 修正：确保状态和下一个状态是三维的 (batch_size, seq_len, num_features)
        # 并且 action, reward, done 是二维的 (batch_size, 1)
        states_list = []
        actions_list = []
        rewards_list = []
        next_states_list = []
        dones_list = []

        for e in experiences:
            if e is not None:
                states_list.append(e.state)
                actions_list.append(e.action)
                rewards_list.append(e.reward)
                next_states_list.append(e.next_state)
                dones_list.append(e.done)
        
        # states: (batch_size, sequence_length, num_features)
        states = torch.from_numpy(np.array(states_list)).float().to(config.DEVICE) 
        # next_states: (batch_size, sequence_length, num_features)
        next_states = torch.from_numpy(np.array(next_states_list)).float().to(config.DEVICE)

        # actions: (batch_size, action_dim)
        actions = torch.from_numpy(np.array(actions_list)).float().to(config.DEVICE)
        # rewards: (batch_size, 1)
        rewards = torch.from_numpy(np.array(rewards_list).reshape(-1,1)).float().to(config.DEVICE)
        # dones: (batch_size, 1)
        dones = torch.from_numpy(np.array(dones_list).astype(np.uint8).reshape(-1,1)).float().to(config.DEVICE)

        return (states, actions, rewards, next_states, dones)

    def __len__(self):
        """返回当前内存中经验的数量。"""
        return len(self.memory) 