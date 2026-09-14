# 笔记：本地 `opensource_training_megatron`

已核实、与编目的对应：

| 本地事实 | 编目 |
|---|---|
| FA bwd 对 O / dO 做 bitshift 或 round2nearest | KER.01 / KER.02 |
| `per_token_entropy` 先塌再炸 | MOE.01 |
| QK 谱 climb→collapse | LOSS.04 的信号面 |
| `realized_var` 在 grad 前抬升 | NUM.01 |
| torchrun 丢掉 `STABILITY_MONITOR_ENABLED` | OBS.01 / OBS.02 |
| nanoGPT bin 当 MMIDIDX | DATA.05 |
| Qwen3 padded vocab 151936 | DATA.04 |

fail-fast、不进主编目：

- 安装 Apex → RMSNorm `AssertionError`
- TP>1 + EP>1 无 TE 时 sequence-parallel 死锁
- CE logits `.float()` OOM（TP=1、大词表）
- 共享机器上释放 GPU 后 30–60s 驱动仍占显存

注入原语只打 backward，full recompute 下前向跑两次也不重复注入。
