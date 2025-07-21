import torch

# """
# 配置文件，包含超参数和路径设置。
# """

# # 数据参数
# # FILE_PATH = 'CL.NYM（1988.3.11-2025.5.15）.xlsx'  # Excel 文件路径
# FILE_PATH = 'CL.NYM(1988.3.11-2025.5.15).xlsx' # Excel 文件路径 (修正括号)
# PRICE_COLUMN = '收盘价(元)'  # Excel 文件中相关的价格列名
# DATE_COLUMN = '日期' # Excel 文件中相关的日期列名
# SEQUENCE_LENGTH = 10  # 用于构建状态的序列长度 (例如，过去10天的数据)
# TRAIN_RATIO = 0.8  # 训练集所占比例
# VAL_RATIO = 0.1 # 验证集所占比例 (剩余部分为测试集)

# # 技术指标参数
# SMA_WINDOWS = [5, 10]  # 简单移动平均线的窗口期
# EMA_WINDOWS = [5, 10]  # 指数移动平均线的窗口期
# RSI_WINDOW = 14  # 相对强弱指数的窗口期
# MACD_FAST = 12  # MACD快线周期
# MACD_SLOW = 26  # MACD慢线周期
# MACD_SIGNAL = 9  # MACD信号线周期

# # 模型参数
# INPUT_SIZE_FACTOR = 1  # 状态特征数量的因子 (例如，价格 + 各技术指标)
#                         # 这个值会在 data_utils.py 中根据选择的特征动态计算确定
# HIDDEN_SIZE_ACTOR = 128  # Actor 网络的隐藏层大小
# HIDDEN_SIZE_CRITIC = 128  # Critic 网络的隐藏层大小
# ACTION_DIM = 1  # 动作维度 (预测下一个价格，归一化到0-1)

# # 训练参数
# TOTAL_EPISODES = 2000  # 总训练回合数
# BATCH_SIZE = 64  # 批量大小
# BUFFER_SIZE = int(1e5)  # 经验回放缓冲区的最大容量
# GAMMA = 0.99  # 折扣因子
# TAU = 0.005  # 目标网络软更新的系数
# ACTOR_LR = 2e-4  # Actor 网络的学习率
# CRITIC_LR = 1e-3  # Critic 网络的学习率
# CLIP_GRAD_NORM_ACTOR = 1.0 # Actor梯度裁剪阈值
# CLIP_GRAD_NORM_CRITIC = 1.0 # Critic梯度裁剪阈值

# # 噪声参数
# # OUNoise 参数
# OU_MU = 0.0  # OUNoise 的均值
# OU_THETA = 0.15  # OUNoise 的 theta 参数 (速率)
# OU_SIGMA = 0.2  # OUNoise 的 sigma 参数 (波动率)

# # DynamicNoise 参数 (GBM 部分)
# GBM_SIGMA = 0.1  # GBM 噪声的波动率 (用于动态噪声的价格冲击部分)

# # Beta_t (动态Actor学习率调整) 参数
# K_BETA = 0.5  # 用于调整 Beta_t 的敏感度因子 (较大的 K_BETA 意味着对损失比率变化更敏感)
# MIN_ACTOR_LR_FACTOR = 0.1 # Actor学习率相对于初始学习率的最小调整比例
# MAX_ACTOR_LR_FACTOR = 10.0 # Actor学习率相对于初始学习率的最大调整比例

# # 奖励函数参数
# # REWARD_DIRECTION_WEIGHT = 1.0 # 方向正确时的奖励权重 (已在 train_evaluate.py 中硬编码)
# # REWARD_MSE_PENALTY_WEIGHT = 0.1 # 幅度错误的惩罚权重 (基于实际价格差异) (已在 train_evaluate.py 中硬编码)
# REWARD_MSE_WEIGHT_NORMALIZED = 0.5 # 基于归一化价格差异的MSE惩罚权重，用于新的奖励函数

# # 设备配置 (优先使用MPS，其次CUDA，最后CPU)
# if torch.backends.mps.is_available() and torch.backends.mps.is_built():
#     DEVICE = torch.device("mps")
#     print("MPS is available and built. Using MPS.")
# elif torch.cuda.is_available():
#     DEVICE = torch.device("cuda")
#     print("CUDA is available. Using CUDA.")
# else:
#     DEVICE = torch.device("cpu")
#     print("MPS and CUDA are not available. Using CPU.")


# # 输出路径
# MODEL_SAVE_PATH = './saved_models/' # 模型保存路径
# PLOT_SAVE_PATH = './plots/' # 图表保存路径

# # 多步预测参数
# MULTI_STEP_PREDICTIONS = 30 # 要进行的多步预测的天数 