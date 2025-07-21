import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from DNPP import config

# 定义了Actor和Critic模型的网络结构。

def hidden_init(layer):
    # """为Pytorch层提供一个合理的权重初始化方案。"""
    # fan_in = layer.weight.data.size()[0]
    # lim = 1. / np.sqrt(fan_in)
    # return (-lim, lim)
    # """为PyTorch层提供一个合理的权重初始化方案。
    # 参数:
    # layer (nn.Linear): PyTorch的线性层。
    # 返回:
    # tuple: 包含均匀分布的下限和上限。
    # """
    fan_in = layer.weight.data.size()[0]
    lim = 1.0 / np.sqrt(fan_in)
    return (-lim, lim)

class Actor(nn.Module):
    # """Actor (策略) 模型，用于将状态映射到动作。"""
    # def __init__(self, state_size, action_size, seed, hidden_size=config.HIDDEN_SIZE_ACTOR):
    #     """初始化参数并构建模型。
    #     Params
    #     ======
    #         state_size (int): 状态的维度
    #         action_size (int): 动作的维度
    #         seed (int): 随机种子
    #         hidden_size (int): 隐藏层中节点的数量
    #     """
    #     super(Actor, self).__init__()
    #     self.seed = torch.manual_seed(seed)
    #     # self.fc1 = nn.Linear(state_size, hidden_size)
    #     # self.fc2 = nn.Linear(hidden_size, hidden_size)
    #     # self.fc3 = nn.Linear(hidden_size, action_size)
    #     # self.bn1 = nn.BatchNorm1d(hidden_size) # 添加批量归一化层
    #     # self.reset_parameters()

    #     # 考虑到状态是 (batch, seq_len, features)，我们需要先将其展平或使用适合序列的模型
    #     # 假设我们先展平: seq_len * features
    #     self.flatten_size = state_size # 这里的 state_size 应该是 seq_len * num_features
    #     self.fc1 = nn.Linear(self.flatten_size, hidden_size)
    #     self.bn1 = nn.BatchNorm1d(hidden_size) # 在非线性激活之前应用BN
    #     self.fc2 = nn.Linear(hidden_size, hidden_size)
    #     # self.bn2 = nn.BatchNorm1d(hidden_size) # 可选: 在第二个FC层后也加BN
    #     self.fc3 = nn.Linear(hidden_size, action_size)
    #     self.reset_parameters()


    # def reset_parameters(self):
    #     # """初始化网络层的权重。"""
    #     # self.fc1.weight.data.uniform_(*hidden_init(self.fc1))
    #     # self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
    #     # self.fc3.weight.data.uniform_(-3e-3, 3e-3)
    #     self.fc1.weight.data.uniform_(*hidden_init(self.fc1))
    #     self.fc1.bias.data.fill_(0.1)
    #     self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
    #     self.fc2.bias.data.fill_(0.1)
    #     self.fc3.weight.data.uniform_(-3e-3, 3e-3) # DDPG论文建议对最终层使用较小的权重范围
    #     self.fc3.bias.data.uniform_(-3e-3, 3e-3)


    # def forward(self, state):
    #     # """构建一个actor（策略）网络，它将状态映射到动作。"""
    #     # x = F.relu(self.bn1(self.fc1(state))) # 应用BN和ReLU
    #     # x = F.relu(self.fc2(x))
    #     # return torch.sigmoid(self.fc3(x)) # 使用 Sigmoid 将输出压缩到 (0, 1)

    #     # 展平输入状态 (batch_size, seq_len, num_features) -> (batch_size, seq_len * num_features)
    #     if state.dim() > 2: # 确保只在需要时展平
    #         state = state.view(state.size(0), -1)
        
    #     x = self.fc1(state)
    #     x = self.bn1(x) # BN层通常在全连接层之后，激活函数之前
    #     x = F.relu(x)
        
    #     x = self.fc2(x)
    #     # x = self.bn2(x) # 如果添加了第二层BN
    #     x = F.relu(x)
        
    #     return torch.sigmoid(self.fc3(x)) # 使用 Sigmoid 将输出压缩到 (0, 1)

    """Actor (策略) 模型，用于将状态映射到动作。"""
    def __init__(self, state_size, action_size, seed, hidden_size=config.HIDDEN_SIZE_ACTOR):
        """初始化参数并构建模型。
        参数:
            state_size (int): 状态的维度 (seq_len * num_features)。
            action_size (int): 动作的维度。
            seed (int): 随机种子。
            hidden_size (int): 隐藏层中节点的数量。
        """
        super(Actor, self).__init__()
        self.seed = torch.manual_seed(seed)
        
        # 假设 state_size 已经是展平后的大小 (seq_len * num_features)
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.bn1 = nn.BatchNorm1d(hidden_size) # 在非线性激活之前应用BN
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        # self.bn2 = nn.BatchNorm1d(hidden_size) # 可选: 在第二个FC层后也加BN
        self.fc3 = nn.Linear(hidden_size, action_size)
        self.reset_parameters()

    def reset_parameters(self):
        """初始化网络层的权重。"""
        self.fc1.weight.data.uniform_(*hidden_init(self.fc1))
        self.fc1.bias.data.fill_(0.1) # 偏置使用小的正值初始化可能有助于ReLU单元
        self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
        self.fc2.bias.data.fill_(0.1)
        self.fc3.weight.data.uniform_(-3e-3, 3e-3) # DDPG论文建议对最终层使用较小的权重范围
        self.fc3.bias.data.uniform_(-3e-3, 3e-3)


    def forward(self, state):
        """构建一个actor（策略）网络，它将状态映射到动作。
        参数:
            state (torch.Tensor): 输入状态，形状为 (batch_size, seq_len * num_features) 或 (batch_size, num_features) 如果seq_len=1。
                                在Agent的act方法中，如果seq_len > 1且输入是(seq_len, num_features)，它会被调整。
                                在Agent的learn方法中，从replay buffer中取出的state已经是 (batch_size, seq_len, num_features)，
                                需要在这里展平。
        返回:
            torch.Tensor: 动作输出，经过 sigmoid 激活，值域 (0, 1)。
        """
        # 如果输入状态是 (batch_size, seq_len, num_features)，则展平
        if state.dim() == 3: # (batch_size, seq_len, num_features)
            state = state.view(state.size(0), -1) # 展平为 (batch_size, seq_len * num_features)
        
        x = self.fc1(state)
        # BN层期望的输入是 (N, C) 或 (N, C, L)，其中 C 是特征数。
        # 对于FC层后的BN，输入应该是 (batch_size, num_features)，这里的num_features是hidden_size
        if x.dim() == 1: # 如果批量大小为1，BN层会出问题，需要 unsqueeze
             x = x.unsqueeze(0)
             x_bn = self.bn1(x)
             x_bn = x_bn.squeeze(0)
        elif x.size(0) > 1 : # 只有在批量大小 > 1 时才应用BN
            x_bn = self.bn1(x)
        else: # batch_size = 0 或 1 但未处理的情况（理论上不应发生）
            x_bn = x


        x = F.relu(x_bn)
        
        x = self.fc2(x)
        x = F.relu(x) # 通常在第二个FC层后不加BN，除非网络很深
        
        return torch.sigmoid(self.fc3(x)) # 使用 Sigmoid 将输出压缩到 (0, 1)


class Critic(nn.Module):
    # """Critic (价值) 模型，用于将 (状态, 动作) 对映射到Q值。"""
    # def __init__(self, state_size, action_size, seed, hidden_size=config.HIDDEN_SIZE_CRITIC):
    #     """初始化参数并构建模型。
    #     Params
    #     ======
    #         state_size (int): 状态的维度
    #         action_size (int): 动作的维度
    #         seed (int): 随机种子
    #         hidden_size (int): 隐藏层中节点的数量
    #     """
    #     super(Critic, self).__init__()
    #     self.seed = torch.manual_seed(seed)
    #     # self.fcs1 = nn.Linear(state_size, hidden_size) # 第一个处理状态的层
    #     # self.fc2 = nn.Linear(hidden_size + action_size, hidden_size) # 动作在第一个隐层后引入
    #     # self.fc3 = nn.Linear(hidden_size, 1) # 输出Q值
    #     # self.bn1 = nn.BatchNorm1d(hidden_size) # 添加批量归一化层
    #     # self.reset_parameters()

    #     # 假设 state_size 是展平后的大小: seq_len * num_features
    #     self.flatten_size = state_size
    #     self.fcs1 = nn.Linear(self.flatten_size, hidden_size)
    #     self.bn1 = nn.BatchNorm1d(hidden_size) # BN层在状态路径上
        
    #     self.fc_action = nn.Linear(action_size, hidden_size) # 可选：单独处理动作的路径，然后合并

    #     # 合并后的路径
    #     # self.fc2 = nn.Linear(hidden_size + action_size, hidden_size) # 原 DDPG 论文方法
    #     self.fc2 = nn.Linear(hidden_size + hidden_size, hidden_size) # 如果动作也被映射到hidden_size
        
    #     self.fc3 = nn.Linear(hidden_size, 1)
    #     self.reset_parameters()

    # def reset_parameters(self):
    #     # """初始化网络层的权重。"""
    #     # self.fcs1.weight.data.uniform_(*hidden_init(self.fcs1))
    #     # self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
    #     # self.fc3.weight.data.uniform_(-3e-3, 3e-3)
    #     self.fcs1.weight.data.uniform_(*hidden_init(self.fcs1))
    #     self.fcs1.bias.data.fill_(0.1)
    #     self.fc_action.weight.data.uniform_(*hidden_init(self.fc_action)) # 如果使用 fc_action
    #     self.fc_action.bias.data.fill_(0.1)                               # 如果使用 fc_action
    #     self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
    #     self.fc2.bias.data.fill_(0.1)
    #     self.fc3.weight.data.uniform_(-3e-3, 3e-3)
    #     self.fc3.bias.data.uniform_(-3e-3, 3e-3)


    # def forward(self, state, action):
    #     # """构建一个critic（价值）网络，它将（状态，动作）对映射到Q值。"""
    #     # # 展平状态
    #     # if state.dim() > 2:
    #     #     state = state.view(state.size(0), -1)
        
    #     # xs = F.relu(self.bn1(self.fcs1(state))) # 状态路径应用BN和ReLU
    #     # x = torch.cat((xs, action), dim=1) # 在第一个隐层后合并状态和动作
    #     # x = F.relu(self.fc2(x))
    #     # return self.fc3(x) # 输出Q值

    #      # 展平输入状态 (batch_size, seq_len, num_features) -> (batch_size, seq_len * num_features)
    #     if state.dim() > 2:
    #         state = state.view(state.size(0), -1)

    #     s_path = self.fcs1(state)
    #     s_path = self.bn1(s_path) # BN层
    #     s_path = F.relu(s_path)

    #     # 动作路径（如果单独处理）
    #     a_path = F.relu(self.fc_action(action)) # 动作路径也用ReLU

    #     # x = torch.cat((s_path, action), dim=1) # 原DDPG论文方式，动作直接拼接到第一个隐层输出
    #     x = torch.cat((s_path, a_path), dim=1) # 如果动作也经过一个FC层

    #     x = F.relu(self.fc2(x))
    #     return self.fc3(x)

    """Critic (价值) 模型，用于将 (状态, 动作) 对映射到Q值。"""
    def __init__(self, state_size, action_size, seed, hidden_size=config.HIDDEN_SIZE_CRITIC):
        """初始化参数并构建模型。
        参数:
            state_size (int): 状态的维度 (seq_len * num_features)。
            action_size (int): 动作的维度。
            seed (int): 随机种子。
            hidden_size (int): 隐藏层中节点的数量。
        """
        super(Critic, self).__init__()
        self.seed = torch.manual_seed(seed)
        
        # 假设 state_size 已经是展平后的大小 (seq_len * num_features)
        self.fcs1 = nn.Linear(state_size, hidden_size) # 处理状态的第一个全连接层
        self.bn1 = nn.BatchNorm1d(hidden_size) # 对状态路径的第一个FC层输出进行BN
        
        # DDPG论文建议将动作输入到网络的第二隐藏层
        # 因此，第一层只处理状态，然后将状态的表示与动作连接起来
        self.fc2 = nn.Linear(hidden_size + action_size, hidden_size) # 动作在第一个隐层处理后的状态表示之后引入
        self.fc3 = nn.Linear(hidden_size, 1) # 输出Q值
        self.reset_parameters()

    def reset_parameters(self):
        """初始化网络层的权重。"""
        self.fcs1.weight.data.uniform_(*hidden_init(self.fcs1))
        self.fcs1.bias.data.fill_(0.1)
        self.fc2.weight.data.uniform_(*hidden_init(self.fc2))
        self.fc2.bias.data.fill_(0.1)
        self.fc3.weight.data.uniform_(-3e-3, 3e-3)
        self.fc3.bias.data.uniform_(-3e-3, 3e-3)


    def forward(self, state, action):
        """构建一个critic（价值）网络，它将（状态，动作）对映射到Q值。
        参数:
            state (torch.Tensor): 输入状态，形状为 (batch_size, seq_len * num_features) 或 (batch_size, num_features)。
                                 需要在此处展平。
            action (torch.Tensor): 输入动作，形状为 (batch_size, action_dim)。
        返回:
            torch.Tensor: Q值输出。
        """
        # 如果输入状态是 (batch_size, seq_len, num_features)，则展平
        if state.dim() == 3: # (batch_size, seq_len, num_features)
            state = state.view(state.size(0), -1) # 展平为 (batch_size, seq_len * num_features)

        xs = self.fcs1(state)
        # 对fcs1的输出应用BN
        if xs.dim() == 1: # 批量大小为1的情况
            xs = xs.unsqueeze(0)
            xs_bn = self.bn1(xs)
            xs_bn = xs_bn.squeeze(0)
        elif xs.size(0) > 1: # 批量大小 > 1
            xs_bn = self.bn1(xs)
        else: # 批量大小 = 0 或 1 但未处理（不应发生）
            xs_bn = xs

        xs = F.relu(xs_bn)
        
        # 将动作连接到经过第一层处理和激活后的状态表示上
        x = torch.cat((xs, action), dim=1)
        x = F.relu(self.fc2(x))
        return self.fc3(x) 