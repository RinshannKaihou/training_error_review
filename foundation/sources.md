# 矿源账本

基础调研（2026-08-17）挖过什么、为什么留下。

## 论文（入选）

| 文献 | 为什么留 |
|---|---|
| Ma et al. arXiv:2502.12340 ACL 2025 | 第一篇用生产不健康节点对照训 LLM |
| Llama 3 Herd arXiv:2407.21783 | 54 天 6 次 GPU SDC 的生产计数 |
| Dixit et al. arXiv:2102.11245；Cores that don't count | fleet 基率 |
| Tung et al. arXiv:2605.04213 | 有限值 SDC 占优 |
| LLM-PRISM arXiv:2604.10390 | 永久 GPU 故障 × 训练 |
| SCOUT arXiv:2608.11034 | DP 共识离群 |
| Altenberd et al. arXiv:2604.00726 | 训练 SDC 综述/挑战 |
| Takase et al. arXiv:2312.16903 Spike No More | loss spike 的谱范数机制 |
| Zheng et al. 低精度 GD 鞅发散 | FP8 / 本地 martingale |
| Zhong et al. arXiv:2605.14220 TIM / VeXact | 训推错配能单独打崩 RL |
| Qi et al. arXiv:2510.26788 FP16 | 精度选择压 TIM |
| Liu et al. arXiv:2503.20783 DrGRPO | std / 长度偏置 |
| DAPO | token-level loss、dynamic sampling |
| R3 arXiv:2510.11370 | MoE 路由回放 |
| ByteDance arXiv:2509.16293 | implicit failure 分类 |

## GitHub（入选）

| 条目 | 为什么留 |
|---|---|
| DeepSpeed #8224 | 教科书级「多卡静默错梯度」，对照实验干净 |
| OpenRLHF #1295 / #1293 / #1309 / #1270 | TIM 校正与 GRPO 统计的实现级缺陷 |
| Megatron-LM #6509 / #5997 / #6521 | TE extra state、batch-invariant |
| DeepSpeed #5794 / #6891；Megatron #1754 | 专家 reshard（推理编目已引，训练侧补全） |
| DeepSpeed #8230 | ZeRO universal ckpt 几何 |

## GitHub（扫了但未编目）

未认证 Search 噪声极大：Megatron `NaN OR silent` 576 命中里大量是功能 PR。原始 JSON 在 `foundation/raw/*.json`。422：`volcengine/verl` 与 `NVIDIA/NeMo` 查询串被 API 拒，种子期未纳入。

不把「最近 10 条按时间排序的 PR 标题」当故障。

## 本地

`../opensource_training_megatron`：FA backward 双注入点、`stability_monitor`、`martingale_monitor`、MMIDIDX、Apex/RMSNorm、torchrun 吞环境变量。

## 推理编目回链

`1.6 training_sdc_checkpoint_inherit`、`12.2 from_pretrained_silent_random_init`、`1.9 kernel_sync_semantic`、分词器/模板、有限值 SDC META。

## 故意没挖深的

ColossalAI / llama-factory / slime / NeMo 全历史。留在 `tools/scan/repos.yaml` 给 Phase 3。
