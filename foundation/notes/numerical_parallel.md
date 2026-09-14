# 笔记：数值与并行

- DeepSpeed #8224 是种子期最干净的软件正确性样本：单卡 bitwise 相同、多卡静默丢子图、LR=0 时看不出来。
- 归约序非确定性：推理侧当噪声底；训练侧在 RL 的 π_old 和 A/B 里是正确性问题。
- 本实验室故意不用 Apex/TE：RMSNorm 模型装 Apex 会 fail-fast；TP+EP 又强制 sequence-parallel。这些是配置死锁，进 rejected / 本地笔记，不进主编目。
