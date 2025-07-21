import numpy as np
import torch
import copy
from DNPP import config

class OUNoise:
    """Ornstein-Uhlenbeck 过程，用于在 DDPG 中为 actor 的动作添加时间相关的噪声，以促进探索。

    它生成一种均值回归的噪声，这意味着它会围绕一个平均值（通常为0）波动，
    并且不会无限期地偏离太远。这在物理控制任务中很有用，因为它可以模拟惯性，
    并且在连续动作空间中比简单的高斯噪声更有效。
    """
    def __init__(self, size, seed, mu=config.OU_MU, theta=config.OU_THETA, sigma=config.OU_SIGMA):
        """初始化参数。
        参数:
            size (int): 动作空间的维度。
            seed (int): 用于随机数生成的种子。
            mu (float): 过程的均值。
            theta (float): 状态被拉回到 mu 的速率。
            sigma (float): 过程的波动性或噪声量。
        """
        self.mu = mu * np.ones(size)
        self.theta = theta
        self.sigma = sigma
        self.seed = np.random.seed(seed)
        self.size = size
        self.reset()

    def reset(self):
        """将内部状态重置为均值。"""
        self.state = copy.copy(self.mu)

    def sample(self):
        """更新内部状态并将其作为噪声样本返回。"""
        x = self.state
        # dx = self.theta * (self.mu - x) + self.sigma * np.array([np.random.randn() for i in range(len(x))])
        # 使用 np.random.randn(self.size) 更高效
        dx = self.theta * (self.mu - x) + self.sigma * np.random.randn(self.size)
        self.state = x + dx
        return self.state

class DynamicNoise:
    """动态噪声，结合了 OUNoise 和一个基于当前价格的几何布朗运动 (GBM) 冲击。

    这种噪声机制旨在根据当前市场情况（通过当前价格表示）调整探索策略。
    GBM 组件引入了一个与当前价格成比例的随机冲击，模拟金融市场中常见的价格波动特性。
    """
    def __init__(self, size, seed, ou_mu=config.OU_MU, ou_theta=config.OU_THETA, ou_sigma=config.OU_SIGMA, gbm_sigma=config.GBM_SIGMA):
        """初始化动态噪声参数。
        参数:
            size (int): 动作空间的维度。
            seed (int): 随机数生成种子。
            ou_mu (float): OUNoise 的均值。
            ou_theta (float): OUNoise 的 theta 参数。
            ou_sigma (float): OUNoise 的 sigma 参数。
            gbm_sigma (float): GBM 冲击的波动率。
        """
        self.ou_noise = OUNoise(size, seed, mu=ou_mu, theta=ou_theta, sigma=ou_sigma)
        self.gbm_sigma = gbm_sigma
        self.seed = seed # 虽然 OUNoise 内部有自己的seed，这里也保留一个以备将来可能的使用
        # np.random.seed(seed) # OUNoise中已经设置了

    def sample_gbm_delta_p(self, current_normalized_price):
        """根据当前归一化价格生成一个 GBM 风格的价格变化量 (delta P)。
        这个delta P旨在模拟价格的一个小的随机冲击。
        参数:
            current_normalized_price (float): 当前的归一化价格 (通常在0到1之间)。
        返回:
            float: GBM 风格的价格变化量。
        """
        # delta_P = P * mu*dt + P * sigma * dW_t
        # 这里我们简化，只使用波动项作为随机冲击，mu*dt被认为是OU噪声的一部分或由actor学习
        # dW_t 是一个标准正态分布的随机变量
        # 为了避免过大的冲击，特别是当 current_normalized_price 接近0或1时，
        # 我们直接使用 gbm_sigma 乘以一个随机数，然后可能再乘以 current_normalized_price
        # 但考虑到 actor 的输出已经是归一化的，这里的冲击也应该是相对较小的归一化值。
        # 原始论文中 N_t_dynamic = N_t_ou + N_t_shock
        # N_t_shock = sgn(randn) * delta_p_t * randn (sgn(randn)和randn感觉有些重复)
        # 简化版：delta_p_t 正比于 P_t-1 * sigma_gbm
        # delta_p = current_normalized_price * self.gbm_sigma * np.random.randn() # 原始想法

        # 更新后的想法：让冲击本身的大小由 gbm_sigma 控制，而不是直接乘以价格，
        # 因为价格本身已经是归一化的，乘以它可能会使得接近0的价格几乎没有冲击。
        # Actor 的输出会被 sigmoid 限制在 (0,1)，然后被反归一化。
        # 这里的噪声是加在 actor 输出 *之前* 的logit上的，还是 *之后* 的action上的？
        # DDPG通常是加在action上的。Action是归一化价格。
        # 所以，这个冲击也应该是对归一化价格的一个小调整。
        shock = self.gbm_sigma * np.random.randn() # 生成一个随机冲击值
        # 确保这个冲击不会导致价格超出合理范围 (例如，加上冲击后仍在0-1附近)
        # 在 agent.py 的 act 方法中，会对 action + noise 进行裁剪
        return shock

    def sample(self, current_normalized_price):
        """生成动态噪声样本。
        参数:
            current_normalized_price (float): 当前的归一化价格，用于 GBM 组件。
        返回:
            numpy.ndarray: 结合了 OU 噪声和 GBM 冲击的噪声值。
        """
        ou_sample = self.ou_noise.sample()
        gbm_shock = self.sample_gbm_delta_p(current_normalized_price)

        # 假设动作维度为1 (因为我们预测单个价格)
        # 论文中的公式是 N_t_dynamic = N_t_ou + N_t_shock
        # N_t_shock 部分的定义有点模糊，它提到了 delta_p_t，但没有明确如何与 N_t_ou 结合
        # 这里，我们将 gbm_shock 直接加到 ou_sample 上
        # 注意：如果 ou_sample 是多维的，需要确保 gbm_shock 的维度匹配或正确广播
        # 鉴于我们的 action_dim=1，这里的 size 应该是 1，所以 ou_sample 和 gbm_shock 都是标量数组
        dynamic_noise_sample = ou_sample + gbm_shock
        return dynamic_noise_sample 