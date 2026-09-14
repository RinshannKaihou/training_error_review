# 与 `inference_error_review` 的交叉

原则：**训练期机制在这边写全；serving 期机制在那边写全；交叉只留指针。**

| 训练 ID | 推理 ID | 关系 |
|---|---|---|
| HW.05 `training_sdc_checkpoint_inherit` | 1.6 同名 | 同一机制的两端：训练写入，推理加载 |
| CKPT.03 `from_pretrained_silent_random_init` | 12.2 同名 | 加载器漏洞；训练当起点，推理当线上模型 |
| DATA.04 分词器错位 | §10 分词器/模板 | 训练用错表会把错绑定烤进权重 |
| SFT.01 模板不一致 | §10 chat template | 训练根因，推理症状 |
| KER.03 内核同步语义 | 1.9 | 同一编译器/运行时缺陷，训练 GEMM 也会吃 |
| NUM.03 归约序 | 4.x fp_reduction_order | 推理当噪声底；训练当 A/B 与 RL π_old 的正确性问题 |
| ACT.01 MoE 重算分叉 | 模型图类 dispatch/recompute | 训练主路径 |

不要做的事：

- 不要把 vLLM KV 串扰、CUDA graph 指针冻结写进本目录。
- 不要把 `RL-RO` TIM 写进推理目录当「又一条 serving bug」——除非同一内核在纯 serving 下也损坏用户输出。
