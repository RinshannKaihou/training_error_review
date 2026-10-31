# LLM 训练故障模式编目（结构化视图）

> 本文件由 `python3 tools/catalog_tool.py build` 从 `catalog/entries/*.yaml` 生成，**不要手改**。
> 字段说明见 `catalog/SCHEMA.md`，受控词表见 `catalog/vocab.yaml`。

共 564 条；状态：active 564

| 原因子系统 | 条数 |
|---|---|
| 硬件 | 9 |
| 算子/内核 | 140 |
| 编译器 | 18 |
| 运行时/执行 | 13 |
| 集合通信 | 9 |
| 并行切分 | 32 |
| KV缓存 | 2 |
| 调度/服务 | 1 |
| 输出解析 | 1 |
| 解码/采样 | 2 |
| 量化 | 25 |
| 位置编码 | 7 |
| 分词/模板 | 8 |
| 模型定义 | 11 |
| 权重/检查点 | 33 |
| 数据管线 | 39 |
| 优化器 | 42 |
| 损失计算 | 24 |
| MoE路由 | 26 |
| 重计算/卸载 | 16 |
| RL训练回路 | 84 |
| 观测/评测 | 16 |
| 配置/参数 | 4 |
| 构建/发布 | 1 |
| 待定 | 1 |

## 硬件

### TRN-0001 `training_sdc_unhealthy_node_optima_shift` 训练 SDC：不健康节点把模型推向另一局部最优

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 HW.01

- **原因对象**：硬件 / 硬件 / 生产集群不健康节点的计算单元
- **原因行为**：被自动化清扫出的不健康节点仍在跑训练，其静默数据损坏扰动子模块计算与单次 optimizer step，且故障往往不在矩阵乘单元。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 Xid、无 NaN 也能训下去，权重轨迹分叉进入另一局部最优，最终 ckpt 与健康节点同配置不同权重；部分节点打出 loss spike，微调阶段可见不同幅度 spike；ABFT 对 GEMM 的覆盖大多失败。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2502.12340

### TRN-0002 `llama3_sdc_job_interrupt_fraction` Llama 3 预训练 GPU SDC 占意外中断 1.4%

`统计` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 HW.02

- **原因对象**：硬件 / 硬件 / GPU 计算硅
- **原因行为**：GPU 发生静默数据损坏（SDC）；约 78% 的意外中断归因于确认或疑似的硬件问题。
- **影响对象**：可用性/进度；梯度（报错）
- **影响详情**：16K GPU Llama 3 预训练 54 天：466 次 job 中断中 419 次意外，其中 GPU SDC 单独记 6 次（占意外中断 1.4%）；集群层表现为未计划中断，未被抓住的同类事件会以坏梯度/坏权重进入后续 step。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2407.21783

### TRN-0003 `fleet_sdc_cpu_base_rate` 大规模 CPU fleet 静默计算错误基率约 1/1000 器件

`统计` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 HW.03

- **原因对象**：硬件 / 硬件 / fleet 中的缺陷 CPU 器件
- **原因行为**：超大规模 CPU fleet 中部分器件产生静默计算错误，实测基率约 1/1000 器件，远高于宇宙线软错误；并非 LLM 特有机制。
- **影响对象**：数值结果；模型权重（静默错误）
- **影响详情**：单 step 几乎看不见，长跑中以极低频率污染一次更新；检测须在 fleet/设备尺度进行，而非 per-step 语义探针。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2102.11245

### TRN-0004 `gemini_weekly_sdc_cadence` Gemini 训练中 SDC 约每 1–2 周发生一次

`统计` · `active` · `pretrain` · `documented` · `var` · 发现 2026-08-17 · 旧号 HW.04

- **原因对象**：硬件 / 硬件 / 大规模训练集群加速器
- **原因行为**：大规模训练中硬件静默数据损坏反复发生：公开转述 Gemini 训练约每 1–2 周一次，与 Llama 3 的 54 天 6 次同量级。
- **影响对象**：训练轨迹；训练信号（不可复现）
- **影响详情**：长跑中周期性出现无法短时复现的轨迹异常或 NaN；停机诊断时窗口往往已错过故障器件。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2502.12340
- **关联**：var:TRN-0002

### TRN-0005 `training_sdc_checkpoint_inherit` 训练期 SDC 坏更新被发布检查点继承

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 HW.05

- **原因对象**：硬件 / 硬件 / 训练期加速器计算
- **原因行为**：训练期一次静默坏更新（SDC）未被发现，进入发布检查点。
- **影响对象**：模型权重；输出内容（质量退化）
- **影响详情**：之后任何 serving 前向都是干净的，但发布模型 perplexity 略差、偶发更糟答案；单模型自参照监控原理上看不见，需干净参照 ckpt 做流形对比。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2502.12340；https://arxiv.org/abs/2604.00726
- **关联**：cross:INF-0006

### TRN-0006 `llm_prism_permanent_gpu_fault` LLM-PRISM：GPU 永久性故障在训练中转为 SDC

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 HW.06

- **原因对象**：硬件 / 硬件 / GPU 永久性故障器件
- **原因行为**：GPU 存在永久性故障（非单次 SEU），故障器件在每个 step 都执行同一类错误计算；研究以 RTL 级仿真随机注入刻画哪些层/位/算子会把它变成 SDC。
- **影响对象**：数值结果；模型权重（静默错误）
- **影响详情**：比瞬态 SDC 更容易把权重推离正常轨迹，也更容易被重复模式抓到。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2604.10390

### TRN-0007 `scout_pretrain_consensus_outlier` SCOUT：用 DP 副本共识离群检测定位故障 rank

`方法` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 HW.07

- **原因对象**：硬件 / 硬件 / 数据并行副本所在故障设备
- **原因行为**：预训练中某数据并行副本所在设备发生故障，该副本的计算被污染。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：被污染的 DP 副本在共识统计上离群；若无副本间对照，故障会均进 AllReduce 后成为共识错误梯度，只能等 loss 炸掉才暴露。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2608.11034

### TRN-0008 `sdc_forward_qk_backward_grad_exponent` TrainSDC：前向 Q/K 路径与反向梯度指数的 SDC 易损性

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-09-02 · 旧号 HW.08

- **原因对象**：硬件 / 硬件 / 加速器计算（Q/K 路径、反向梯度）
- **原因行为**：瞬态 SDC 落在前向 Q/K 路径时产生持续性训练偏差而非局部噪声；反向易损性主要由梯度指数分布尾部支配，与计算位置基本无关。
- **影响对象**：训练轨迹；隐状态；梯度（静默错误）
- **影响详情**：单次瞬态 SDC 是否演化为轨迹级偏差由落点决定：Q/K 路径、大梯度指数位的故障无 Xid、无 NaN 地把训练推离原轨迹；对计算接口均匀设防的 ABFT 类方案对这两类热点覆盖差。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2608.30769

### TRN-0009 `fp_sketch_post_hoc_gemm_sdc_localization` FP-Sketch：免改 kernel 的 GEMM SDC 事后检出与定位

`方法` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-09-19 · 旧号 HW.09

- **原因对象**：硬件 / 硬件 / tensor core GEMM（半精度操作数）
- **原因行为**：半精度（fp16/bf16）操作数、FP32 累加的 tensor core GEMM 发生 SDC，输出中出现损坏条目。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：坏 GEMM 输出无报错地进入梯度，未设防时可把训练推入另一局部最优（HW.01）；FP-Sketch 在未修改的 GEMM 之后每次调用都能检出损坏，并给出损坏条目的坐标与幅度。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2609.19758

## 算子/内核

### TRN-0012 `fp_reduction_order_training_nondeterminism` 浮点归约顺序随 batch/tile 变化致训练梯度不可复现

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 NUM.03

- **原因对象**：算子/内核 / 通用 / GEMM/归约 kernel 的归约树
- **原因行为**：浮点加法非结合，归约树随 batch/tile 变化，同一输入两次 backward 得不到 bitwise 一致的梯度。
- **影响对象**：梯度；训练信号（不可复现）
- **影响详情**：同 seed 重跑曲线漂移；做 A/B、重算 oracle 或 RL 的 π_old 时成为正确性故障，trainer 重算的 logprob 与 rollout 对不齐。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6521

### TRN-0040 `hybridep_intermittent_bad_gradients` HybridEP 梯度范数间歇放大/NaN，疑 GEMM 与 NCCL 并发

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-17 · 旧号 PAR.12

- **原因对象**：算子/内核 / cuda / cublasLt GEMM 与 NCCL 异流并发
- **原因行为**：BF16 GEMM（beta=0）与 NCCL all-gather/reduce-scatter 异流并发时，本应覆写的输出元素残留预填旧值；根因尚未最终定位，已提交 NVIDIA 内部 bug。
- **影响对象**：梯度；数值结果（数值异常）
- **影响详情**：MFSDP v2+HybridEP+专家 optimizer sharding 下梯度范数间歇放大或 NaN（3254.10@step2）；clip 关时日志打印 grad norm 0，需 PRE_OPT 仪器才可见；对插桩敏感，换 alltoall dispatcher 健康。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7400；https://nvbugspro.nvidia.com/bug/6798870；https://github.com/NVIDIA/Megatron-LM/issues/7232

### TRN-0091 `swa_branch_overwrites_caller_attention_mask` Megatron 融合 softmax 的 SWA 分支覆写调用方 mask

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-09-03 · 旧号 DATA.09

- **原因对象**：算子/内核 / megatron-lm / 融合 softmax 的 SWA 分支
- **原因行为**：forward_torch_softmax 的 sliding-window 分支无条件用滑窗因果 mask 覆写调用方传入的 mask；相邻 plain-causal 分支有 mask is None 守卫，SWA 分支没有。
- **影响对象**：跨请求/跨样本数据；数值结果（静默错误）
- **影响详情**：SWA 层走 torch fallback（未开 softmax 融合）时，padding mask（mbs>1）或 packing 文档 mask 被丢弃，pad/跨文档 token 参与注意力；无异常无警告，loss 被静默污染，仅部分层出错。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7039

### TRN-0132 `fa_backward_mantissa_truncation` FA backward 对 O/dO 尾数截断致梯度系统性偏移

`故障` · `active` · `pretrain` · `verified` · `NEW` · 发现 2026-08-17 · 旧号 KER.01

- **原因对象**：算子/内核 / 待定 / FA backward 保存的 O 与 dO
- **原因行为**：在 FlashAttention backward 里对保存的 O 和/或 dO 做尾数截断（bitshift）或就近舍入（round2nearest），污染 softmax_d = rowsum(dO⊙O)，前向保持干净。
- **影响对象**：梯度；训练轨迹（质量退化）
- **影响详情**：dq/dk/dv 系统性偏移但不出 NaN；QK 谱先升后塌、realized_var 抬升、MoE per_token_entropy 先塌，之后才出现 grad norm 或 loss spike；本实验室作为低精度注意力的可控阳性注入。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：`opensource_training_megatron` `fault_injected_attention.py` / `fault_injection.py`；

### TRN-0133 `fa_backward_dual_site_O_and_dO` FA backward 的 O 与 dO 是两个不同注入点

`故障` · `active` · `pretrain` · `verified` · `var` · 发现 2026-08-17 · 旧号 KER.02

- **原因对象**：算子/内核 / 通用 / FA backward O 与 dO 注入点
- **原因行为**：同一 FA backward kernel 上 O 与 dO 两处低精度注入机制不同：O 经 softmax_d 间接污染梯度，dO 直接进入 backward GEMM；bitshift 与 round2nearest 环境变量互斥。
- **影响对象**：梯度；训练轨迹（质量退化）
- **影响详情**：同样剂量下 O 与 dO 两个注入点的谱与鞅时钟曲线不同，对照实验不声明注入点则结果不可比。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：同 KER.01；
- **关联**：var:TRN-0132

### TRN-0141 `dsa_cudnn_packed_cp_wrong_values_flaky_masked` DSA cuDNN packed+CP 错值被 flaky 掩盖

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-09-09 · 旧号 KER.10

- **原因对象**：算子/内核 / megatron-lm / DSA cuDNN 路径 THD+CP；观测/评测 / megatron-lm / DSA parity 单测 flaky 标记
- **原因行为**：DSA cuDNN real-kernel 路径在 packed-THD + CP>1 下 top-k 索引整体错位、融合输出错值，根因分层未定；对应单测自 #5099 起带 flaky 标记，掩盖了真实数值失败。
- **影响对象**：数值结果；测试判定（静默错误）
- **影响详情**：张量全部有限、训练不崩，单测中 top-k 索引 8/8 全错、输出与参考 cosine 仅 0.365，CI 因 flaky 标记永远报绿；GB200/SM100 上 packed+CP 配置触发，生产形状 loss 暂未见差异，中招形状未定位。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7105；https://github.com/NVIDIA/Megatron-LM/issues/7463

### TRN-0143 `cudnn_sdpa_backward_padded_tile_scores_zero` cuDNN SDPA 反向 padding 半区计 0 分致 dQ NaN

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-13 · 旧号 KER.12

- **原因对象**：算子/内核 / cudnn / cuDNN SDPA bwd padding 半区
- **原因行为**：cuDNN SDPA backward 在显式 mask、L%128==64 且有 lse<−88.7 的行时，把末个 key tile 的 padding 半区打 0 分而非 −inf，exp 溢出后 inf×0 得 NaN 进 dQ。
- **影响对象**：梯度（数值异常）
- **影响详情**：DPO/KTO 带 padding mask（全 True 也触发）约 60 步内 grad_norm 永久 NaN；lse 未过阈时 dQ 带有限错值而静默；前向正确，换 EFFICIENT/MATH 后端或 is_causal=True 则干净。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7181

### TRN-0147 `triton_int32_offset_wraparound_oob_rw` DeepSpeed Triton int32 偏移回绕为负致越界读写

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-09-19 · 旧号 KER.16

- **原因对象**：算子/内核 / deepspeed / swiglu/AutoEP Triton 偏移
- **原因行为**：swiglu 与 AutoEP fused kernel 用 int32 算元素偏移，元素数超 2^31 时回绕为负；掩码 offsets<n_elements 不拒绝负偏移，kernel 对张量起始前的内存 load/store。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：元素数 >2^31（bf16 即 >4 GiB 张量，MoE 大 hidden 或长序列可达）时触发；本报告 repro 表现为 CUDA illegal memory access，若负偏移落在合法映射区则静默写坏别的张量、读取侧把垃圾当梯度。现有单测规模过小未覆盖。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8590
- **关联**：var:TRN-0140

### TRN-0248 `veomni_chunked_logprob_backward_drops_decoder_grads` VeOmni 分块 log-prob 反向静默丢失 decoder 梯度

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-10 · 旧号 RL-RO.26

- **原因对象**：算子/内核 / verl / VeOmni 分块 log-prob 反向
- **原因行为**：chunked log-prob backward 从保存的 reshaped hidden states 读 requires_grad 决定梯度流，别名张量的梯度标志未跟随 ctx.needs_input_grad。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：仅 VeOmni 0.1.11 下触发，无 crash；RL 打分阶段 decoder 参数拿不到（部分）梯度，表征学习静默退化，loss 与指标正常。仅 CPU 回归闭合，CUDA 与分布式 FSDP2 路径未验证。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/8108

### TRN-0271 `index_put_v2_stride_u32_overflow` IndexPutV2 大 stride 偏移 uint32 溢出写错地址

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-15

- **原因对象**：算子/内核 / cann / IndexPutV2 偏移计算整型宽度
- **原因行为**：非连续（大 stride）目标张量上索引偏移以 uint32 计算：idx×stride ≥ 2^32 时回绕，写入落到 (idx×stride) mod 2^32 的错误地址。
- **影响对象**：数值结果（静默错误）
- **影响详情**：Ascend 950DT、CANN 9.2.0：uint8 大张量切片视图（stride(0)=228352 > size(1)=16896）view[18816]=0x5A，期望写行 18816，实际写在行 7/偏移 105472；数据布局静默破坏，无报错。
- **改进措施**：检测 写入后读回校验目标位置；触发条件为非连续大张量 + 越界乘积超 2^32，可静态排查 stride×max_idx。；修复 待定（issue 未附修复 MR，未核实）
- **来源**：https://gitcode.com/cann/ops-nn/issues/6523
- **关联**：var:TRN-0147

### TRN-0273 `fa_grad_sink_dsink_uninitialized` NPU FA 反向 sink 场景 dsink 工作区未清零致梯度爆炸

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / cann / FA 反向 dsink 工作区清零
- **原因行为**：FlashAttentionScoreGrad 的 dsink 工作区仅在 IS_ATTEN_MASK 或 IS_TND 模板清零；causal 等稀疏无 mask 模式对应槽位永不写入，post 阶段累加读未初始化内存。
- **影响对象**：梯度（数值异常）
- **影响详情**：带可学习 sink 的网络用 causal 注意力（无 attenMask 张量、BNSD/BSH）训练若干 step 后，sink 参数被垃圾梯度更新、随后全网梯度爆炸；去掉 sink 输入或换无条件清零实现（arch22）训练稳定。
- **改进措施**：检测 对 dsink 输出与 -Σ(P·dP)·P_sink 参考对账；训练期监控 sink 参数值与梯度范数突变。；修复 修复 MR !13822（open 未合入、未发布）：sink 使能即无条件清零 dsink 工作区，与 arch22 实现对齐。https://gitcode.com/cann/ops-transformer/merge_requests/13822
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6148；https://gitcode.com/cann/ops-transformer/merge_requests/13822

### TRN-0275 `aclnn_empty_input_early_return_unwritten` aclnn 空输入早退不写非空出参返回脏数据

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / cann / aclnn 空张量早退分支
- **原因行为**：aclnn 两段式接口早退条件覆盖输入空×出参非空组合：不写出参即返回 ACLNN_SUCCESS；CheckShape 未绑定出参空性随输入联动。
- **影响对象**：数值结果；梯度（不可复现）
- **影响详情**：pad 系反向/UnfoldGrad 的 gradInput、Multinomial 的 out、MedianDim 输出、DynamicQuant 的 scaleOut 残留未初始化内存（实测哨兵/NaN），接口返回成功无报错。
- **改进措施**：检测 出参预填哨兵值做 round-trip 校验；PyTorch 参考语义为空 grad_output 回全零，可对账。；修复 待定：同机理先例 ops-math #3360（aclnnCdistBackward）已闭环；本批 #3553/#3560/#6582/#6605 暂未见已合入修复（各 issue 关联 MR 状态未逐一核实）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3553；https://gitcode.com/cann/ops-math/issues/3560；https://gitcode.com/cann/ops-nn/issues/6582；https://gitcode.com/cann/ops-nn/issues/6605；https://gitcode.com/cann/ops-math/merge_requests/6366；https://gitcode.com/cann/ops-nn/issues/7246；https://gitcode.com/cann/ops-math/issues/3840；https://gitcode.com/cann/ops-math/issues/3841；https://gitcode.com/cann/ops-math/issues/3838；https://gitcode.com/cann/ops-math/issues/3846
- **关联**：cross:INF-1794

### TRN-0276 `add_rms_norm_gamma_mul_order_overflow` Ascend 950 AddRmsNorm 先乘 gamma 致 FP32 溢出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / cann / AddRmsNorm trans 模板乘法顺序
- **原因行为**：Ascend 950 regbase 的 AddRmsNorm/InplaceAddRmsNorm trans 模板按 (x1+x2)*gamma*rstd 计算，先乘 gamma 可使 FP32 中间结果提前超范围，输出 Inf。
- **影响对象**：数值结果（数值异常）
- **影响详情**：输入与 gamma 均有限、归一化结果也应有限时输出 Inf：x1=2^32、gamma=2^100 期望 2^100 实得 Inf；24 条 trans 溢出用例修复前全 FAIL、修复后全 PASS。
- **改进措施**：检测 对 AddRmsNorm 输出做有限性抽检；固定输入回归用例（x1=2^32、gamma=2^100）。；修复 修复 MR !11953 已合入（2026-10-15 批次快照确认 merged），issue #6679 已 closed：先以 FP32 计算 xSum*rstd 再乘 gamma，两次乘法间不转回低精度；两算子 arch35 ST CSV 各加固定输入回归用例。https://gitcode.com/cann/ops-nn/merge_requests/11953
- **来源**：https://gitcode.com/cann/ops-nn/issues/6679；https://gitcode.com/cann/ops-nn/merge_requests/11953

### TRN-0279 `torch_npu_oob_index_silent_wrong` torch_npu 索引/损失算子越界输入静默错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / torch_npu / gather/scatter/CE 越界校验缺失
- **原因行为**：torch_npu 对 gather/scatter/index_put/cross_entropy/nll_loss 缺 host 越界校验：越界读拿垃圾、越界写被丢弃，无异常；CPU/CUDA 会 raise。
- **影响对象**：数值结果（静默错误）
- **影响详情**：A3 真机确定性复现：cross_entropy 越界 target 返回数值不报错；gather 越界返回垃圾；scatter_ 越界写被静默丢弃。数据侧 bug 被无声吞掉。
- **改进措施**：检测 训练前对 index/target 做范围断言；与 CPU 参考实现对账。；修复 待定（F.embedding、Tensor.select 越界在 NPU 仍会 raise，说明该校验可实现；issue 建议 host 端补齐对齐 CPU/CUDA 语义，未见修复 MR）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5296
- **关联**：cross:INF-1378

### TRN-0282 `add_rms_norm_tiling_mode_bypass_silent` AddRmsNorm tiling 不拦 PRE/POST 模式静默算错越界

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / cann / AddRmsNorm tiling 分派校验
- **原因行为**：Ascend 950 regbase 仅支持普通模式，aclnn 层已拦截但 tiling 层分派时不校验 norm_key：绕过 aclnn 的路径（GE 直构/TTK 直调）传 PRE/POST 形态不被拒。
- **影响对象**：数值结果（静默错误）
- **影响详情**：regbase tiling 未剥离 PRE/POST 模式 gamma 前导 1，numRow 少算（(B,S,H) 只算 B 行），输出大半为未初始化内存；kernel 无条件写 rstd/xOut 越界写；全程不报错。aclnn 公开接口与 A2/A3 不受影响。
- **改进措施**：检测 TTK/GE 直调路径下对输出与参考对账；PR #11564 反例 UT（pre/post_mode_rejected）可作探针。；修复 已修复：PR #11564（merged）tiling 层拒绝 PRE/POST 模式返回 GRAPH_FAILED，修复后 ophost UT 30/30、opapi UT 18/18、950+910b 定向 CI 全过。https://gitcode.com/cann/ops-nn/pull/11564
- **来源**：https://gitcode.com/cann/ops-nn/issues/6482；https://gitcode.com/cann/ops-nn/pull/11564
- **关联**：cross:INF-1382

### TRN-0283 `silu_grad_exp_intermediate_overflow_flag` SiluGrad 指数中间溢出置硬件溢出标志，AMP 持续跳过更新

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：算子/内核 / cann / SiluGrad sigmoid 实现的中间指数
- **原因行为**：SiluGrad 各浮点及混合类型路径直接计算 exp(-x)，大负有限输入的中间指数超出 FP32 有限范围产生溢出并置硬件浮点状态；FP16/BF16 转 FP32 路径同样存在。
- **影响对象**：训练轨迹；训练信号（静默错误）
- **影响详情**：输入与最终梯度均有限的正常训练 step 被浮点状态检测判为 overflow，AMP 持续跳过参数更新；输出值本身可能仍正确，无 NaN 无报错。
- **改进措施**：检测 观察 AMP 每步跳过率与 loss 长期不动；固定 x=-100/-109 等梯度用例检查硬件溢出标志。；修复 修复 MR !12059（open 未合入）：sigmoid 改用非正指数稳定形式 exp(min(x,0))/(1+exp(-|x|))；CANN 9.1.0-beta.1 + Ascend910B1 显式饱和模式下三种 dtype 有限梯度用例溢出标志 true→false。https://gitcode.com/cann/ops-nn/merge_requests/12059
- **来源**：https://gitcode.com/cann/ops-nn/issues/6737；https://gitcode.com/cann/ops-nn/merge_requests/12059

### TRN-0284 `matmulv3_mode4_uninit_k_tail_nan_pollution` MatMulV3 mode4 读同 stream 前序残留 NaN 污染输出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：算子/内核 / cann / MatMulV3 A 尾部
- **原因行为**：FORCE_GRP_ACC_FOR_FP32（mode4）下 A 的 K 尾部未被输入覆盖的加载区不初始化也不屏蔽，NaN×0=NaN 把残留 NaN 扩散进整块归约；mode0 不受影响。
- **影响对象**：数值结果；训练轨迹（数值异常）
- **影响详情**：输入矩阵全部有限且逐位不变时输出 16/16 NaN；训练中同 stream 任意前序 NaN fill 可让后续正常 matmul 间歇性全 NaN，随内存历史变化，难以稳定复现。
- **改进措施**：检测 输入有限性检查无法发现（输入本就有限）；对 matmul 输出抽查非有限值；用零历史 vs NaN 历史对照定位；issue 附常量矩阵脚本在原安装包 10/10 触发。；修复 待定（issue open；最强根因判断为 TO_MUL 路径 A 的 K 尾部未初始化，参考实现仅增加 A 清零后 5/5 恢复正确，维护方未回应；正确修法应为初始化或屏蔽尾部而非只补零乘法侧）
- **来源**：https://gitcode.com/cann/ops-nn/issues/6698

### TRN-0291 `hinge_loss_grad_boundary_gate_decay` HingeLossGrad hinge 边界附近正梯度被错误缩小

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：算子/内核 / cann / epsilon 平滑门函数
- **原因行为**：kernel 把 margin>0 门函数实现为 (margin+|margin|)/(2*(|margin|+1e-7))，margin 为很小正数时系数<1，有效梯度被错误衰减；文档/注释/golden 均定义为严格阈值。
- **影响对象**：梯度（静默错误）
- **影响详情**：预测值紧邻 hinge 边界且 margin 为极小正数（如 5.96e-8）时，梯度幅值被静默压低，最严重约 0.37 倍，更新方向对但步长错；无报错无 NaN，边界样本学习偏慢、收敛质量受损；远离边界样本无差异。
- **改进措施**：检测 对紧邻边界的 margin（nextafter(1,0) 等）构造梯度对照用例。；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/12150（2026-10-17 open）：Compares(GT)+Select 硬阈值替代软门，float32 与 fp16/bf16 路径都改；910B1 三 dtype UT 全绿，未发布
- **来源**：https://gitcode.com/cann/ops-nn/issues/6730；https://gitcode.com/cann/ops-nn/merge_requests/12150

### TRN-0296 `conv3d_backprop_filter_uint_underflow_oob_write` conv3d 反向 uint 下溢回绕致 Fixpipe 越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：算子/内核 / cann / baseNIter 无符号下溢
- **原因行为**：baseNIter 在 c1hkwk+head_<hwK_ 时 uint64 下溢回绕（≈2.05e18），j 循环越界写 L0C/GM；host 侧 3D DW L1 估算另有 int64→int32 截断致分支选路错误。
- **影响对象**：数值结果；可用性/进度（报错）
- **影响详情**：Ascend 950 特定形状输入必现：3D 卷积反向 tail 块 c1hkwk+head_<hwK_ 时 Fixpipe 循环越界写 L0C/GM，后续算子读到损坏数据或设备崩溃，报错点远离根因；大 shape 下 host 侧 L1 超限判断失真致 tiling 分支选错，症状混杂。
- **改进措施**：检测 conv3d 反向后校验输出与相邻内存；触发面为特定 tail 块形状组合。；修复 修复 MR !12006 状态 closed（2026-10-16 关闭，非 merged，原因未核实；issue #6706 仍 open）：复用 117-119 行条件保护写法替换 :182/:241 两处；host 侧统一 int64_t/uint64_t。https://gitcode.com/cann/ops-nn/merge_requests/12006
- **来源**：https://gitcode.com/cann/ops-nn/issues/6706；https://gitcode.com/cann/ops-nn/merge_requests/12006

### TRN-0297 `radix_top_k_ws_sync_missing_int64_overflow` RadixTopK WS 变体 V→MTE3 失同步与 int64 索引越界

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：算子/内核 / cann / radix_top_k WS 同步与索引
- **原因行为**：V写tileTopK、MTE3读同块UB，原SToMTE3Sync覆盖不到V→MTE3，可读旧值；i64多段且tileNum_超UB上限，无符号下溢越出6144元素缓冲区；跨核前缀和可超2^31而累加器int32；UT未测int64主路径
- **影响对象**：数值结果（静默错误）
- **影响详情**：910B/910_93上，超大sortLen（>2^31，约21亿元素）的int64 topk（MoE大词表/超长序列采样）输出k配额错乱（少选/多选）、索引越界写破坏相邻内存或跨核前缀和溢出错值，均无报错；普通规模正常，仅int64大shape且K配额需末轮边界补齐时触发。
- **改进措施**：检测 对 topk 输出做配额/去重校验；触发面为 sortLen>2^31 或 K 需末轮边界补齐的大 shape。；修复 修复 MR !6396 已 merged（2026-10-16，批次快照核实）；issue #3604 已 closed。VToMTE3Sync 替换、CreateVecIndex4TopK 前置防御、ComputeCumSumPrev 统一 int64、static_assert、host UT 补 bit3 编码。https://gitcode.com/cann/ops-math/merge_requests/6396
- **来源**：https://gitcode.com/cann/ops-math/issues/3604；https://gitcode.com/cann/ops-math/merge_requests/6396

### TRN-0300 `ragged_bincount_deterministic_switch_ignored` RaggedBinCount 显式确定性开关未生效

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：算子/内核 / cann / RaggedBinCount 确定性 tiling
- **原因行为**：host tiling 未消费 GE 确定性选项：非二值加权场景显式开启 ge.deterministic=1 后仍可能走浮点 atomic 累加。
- **影响对象**：数值结果（不可复现）
- **影响详情**：Ascend 950 非二值加权 RaggedBinCount 显式开启 ge.deterministic=1 后，本地以同一冻结输入重复执行，输出位模式仍不同（3 次 MD5 不一致），无报错。
- **改进措施**：检测 冻结输入重复执行 3+ 次比较输出 MD5；GEIR 显式 --pc=1 --dl=1；修复 修复 MR !6428（open，多轮受测）：非二值输出加确定性 key 8/9，固定线程扫描/固定分块固定顺序合并/有界精确整数直方图+RNE 舍入；本地冻结输入各 10 次 MD5 一致、A100 三方 200/200、ST36；线上 CI 仍在跑（run5154 ABI 问题已修）。issue #3626 附完整回归账本。https://gitcode.com/cann/ops-math/merge_requests/6428
- **来源**：https://gitcode.com/cann/ops-math/issues/3626；https://gitcode.com/cann/ops-math/merge_requests/6428

### TRN-0301 `scatteraddwithsorted_fp32_missing_sync_stale_row` ScatterAddWithSorted FP32 缺向量同步偶发混入前行累加

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：算子/内核 / cann / ScatterAddWithSorted FP32
- **原因行为**：FP32 路径初始化累加缓存后缺少向量流水同步，当前行可读到前一行残留值，相同输入重复执行 scatter_add_ 偶发错果
- **影响对象**：数值结果（不可复现）
- **影响详情**：910B3/CANN 9.1.0 上 FP32 scatter_add_ 使用行广播索引（由一维 expand 得 stride [1,0]）时，相同输入重复执行偶发输出与 CPU 参考不一致；首次差异轮次不固定，输入未变，无报错
- **改进措施**：检测 循环比对 NPU 输出与 CPU 参考（逐字节）；出错轮次不固定，单次校验不足；修复 待定（issue open；报告者按上游 commit 8ce9e83 头文件比对定位到 FP32 路径缺同步，修复未提交）
- **来源**：https://gitcode.com/cann/ops-nn/issues/6782；https://gitcode.com/cann/ops-nn/merge_requests/12144

### TRN-0302 `conv3d_dx_enlarge_partial_tail_oob_read` Conv3D 反向 enlarge 尾组越界读致尾通道系统性错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：算子/内核 / cann / Conv3D dx ENLARGE tiling
- **原因行为**：ENLARGE下multiple_extend不整除groups产生不完整尾放大组，尾组K轴C0对齐后A矩阵加载越界读dedy外内存；tailN为singleShapeN_正整数倍时%取余把尾组最后N块有效列数误置0致漏算
- **影响对象**：梯度（静默错误）
- **影响详情**：Ascend950分组转置卷积反向，groups不被enlarge整除（如24/16）时梯度输出尾放大组对应通道96-143系统性错误，原失败规格10/10随机种子33.3%元素超差，其余通道正确；相邻内存恰为零侥幸正确、脏数据则错，无crash、无告警
- **改进措施**：检测 按输出通道分组比对梯度（尾放大组通道整体超差是签名）；比对相邻内存清零与否会翻转结果的即为数据依赖错；修复 修复 MR !12064（open）：CalRealG 在 enlarge 不整除 groups 时回退 multiple_extend=1（ORIGIN 分组，无尾放大组）；CalBasicBlockCnt 尾块改减法式。实机 10/10 种子由 33.3% 元素超差转 bit-exact，11 例结构变体通过。https://gitcode.com/cann/ops-nn/merge_requests/12064
- **来源**：https://gitcode.com/cann/ops-nn/merge_requests/12064

### TRN-0303 `conv3d_dx_vec_fp32_refactor_precision_regression` Conv3D 反向 vec FP32 行计算重构后精度回归

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：算子/内核 / cann / Conv3D dx vec FP32 行累加
- **原因行为**：9.2.0 为消行数告警把 FP32 专用 ComputeRowBf16Vec 合并进共享函数并改运行期分支+三元缓冲选择，FP32 行累加路径被破坏
- **影响对象**：梯度（静默错误）
- **影响详情**：Ascend910B 上 FP32 NCDHW dx 用例最大绝对误差达 4.03e7~6.95e8（A_max）/1.68e5~6.21e5（A_rms），如 dx[1,7,32,32,256]/w[7,1,9,9,9]/p4 g7 规格整体梯度错误；bf16 不受影响；无报错，判例靠精度比对
- **改进措施**：检测 FP32 conv3d 反向用例 A_max/A_rms 比对（回归用例矩阵在 PR 内）；CI ST 白名单不含本算子（仅 mat_mul_v3/batch_mat_mul_v3），门禁测不到；修复 修复 MR !12084（open）：恢复 FP32 独立函数与显式分派（与整改前逐字一致），行数目标靠搬文件不改逻辑；修复后 3 例由 2.34e7/4.03e7/6.95e8 降到 0.04/0.02/1.56，14/145/169 判否转通过、213 例逐位不变、16 个内核 .o 与直接回退版逐字节一致。https://gitcode.com/cann/ops-nn/merge_requests/12084
- **来源**：https://gitcode.com/cann/ops-nn/merge_requests/12084

### TRN-0305 `foreach_list_pair_tiling_x2_unvalidated` arch35 foreach 二元 list tiling 不校验 x2 列表

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：算子/内核 / cann / foreach list tiling
- **原因行为**：arch35 foreach 二元 list tiling 仅按 x1 求取 tensorCount、偏移、totalElements，未获取 x2 信息；kernel 用 x1 偏移/dtype 索引 x2。
- **影响对象**：数值结果（静默错误）
- **影响详情**：图模式下 x2 列表与 x1 不匹配（长度短、tensor 小、dtype 不同）的 foreach 二元算子越界访存或结果静默错误，tiling 层无 GRAPH_FAILED 拦截（arch22 与 aclnn 入口均有校验）
- **改进措施**：检测 调用前自检两个张量列表逐项长度/dtype/shape 一致（框架层）；tiling 层无拦截；修复 修复 MR !12121（open）：共享 validator 新增 ValidateTensorListPair 一次性校验实例个数、逐 tensor dtype 与 storage shape，六个算子 arch35 tiling 接入并补失败/匹配四类单测；本机无昇腾工具链，host UT 未跑（-fsyntax-only 语法检查过），以仓库 CI 为准。https://gitcode.com/cann/ops-nn/merge_requests/12121
- **来源**：https://gitcode.com/cann/ops-nn/issues/6781；https://gitcode.com/cann/ops-nn/merge_requests/12121

### TRN-0313 `aten_gelu_approximate_attr_ignored_tanh_only` torch_npu ATen gelu 静默走 tanh 近似

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-19

- **原因对象**：算子/内核 / pytorch / ATen gelu 分发
- **原因行为**：ATen gelu 分发到无 approximate 参数的 tanh-only aclnnGelu，未按 'none' 路由到带 attr 的 aclnnGeluV2；正确的 erf 路径已在 CANN 包内存在但未被选用。
- **影响对象**：数值结果（静默错误）
- **影响详情**：F.gelu(none) 与 F.gelu(tanh) 在 NPU 逐位相同；4096 点 fp32 统计 |NPU(none)−CPU_erf|max=4.735e-4（vs CPU_tanh 仅 2.9e-7 噪声级）；fp16/bf16 同样按 tanh 式计算；无任何告警
- **改进措施**：检测 对比 F.gelu(x, approximate='none') 与 F.gelu(x, approximate='tanh') 是否逐位相同（相同即中招）；x=2.0 处 erf 期望 1.9544998；修复 用户侧 workaround 已核实：torch_npu.npu_gelu(x, approximate='none') 走正确 erf 路径（vs CPU erf 4.8e-7）；根治=ATen gelu 分发按 approximate 路由到 aclnnGeluV2 TPL_NONE（未实施，闭源二进制分发无法直接落 PR）
- **来源**：https://gitcode.com/cann/ops-nn/issues/6841
- **关联**：cross:INF-1439

### TRN-0314 `op_plugin_conv_family_hf32_silent_precision_loss` op-plugin fp32 conv 全族静默 HF32 降精度且污染梯度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-19

- **原因对象**：算子/内核 / pytorch / conv 族 aclnn 出口精度模式选择
- **原因行为**：fp32 conv 四算子的 aclnn 出口按 HF32 类低位宽执行，不遵循 high_precision 配置，前向与梯度同偏离；set_option（已废弃）与 jit_compile 均无法绕开。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：fp32 conv 前向 rel 误差 6.0e-4~1.8e-3（≈2^-10.5 量级），梯度同样被污染；双芯逐位相同（确定性非随机），无告警；fp16 同形态正常；matmul/bmm/einsum 同机达标可排除平台普遍性
- **改进措施**：检测 同机 matmul/bmm/einsum fp32 对照（逐位或 <2.7e-6 达标）排除平台普遍性；conv 形态矩阵与 CPU 双端逐位比对；修复 待定（issue open：要求 op-plugin 确认 conv 族 aclnn 出口选择是否遵循精度模式配置并文档化；high_precision 选项已废弃不生效）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/593
- **关联**：cross:INF-1434

### TRN-0315 `megamoe_sync_count_missing_dsb_barrier` MegaMoE 同步轮次 count 写后读缺 DSB 屏障致挂起

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-19

- **原因对象**：算子/内核 / 通用 / MegaMoE 同步轮次 count 旁路写
- **原因行为**：同步轮次旁路 GM 写后无 asc_sync_data_barrier(DSB_DDR)；后续重读同一 sequence 时 MTE3 事件不保证 Scalar 旁路写已完成，维测打点改变时序曾掩盖该依赖。
- **影响对象**：可用性/进度（挂起）
- **影响详情**：关闭维测（MC2_ENABLE_EXCEPTION_DUMP=0）后八卡 Static 停在 count epoch 校验：预期 0xE9，一个槽仍为 0xE8000012 旧值，接收端持续等待、Cube 等待 countReady；无报错、无 NaN，图整体挂起。
- **改进措施**：检测 复现配置 EP8、每卡 BS72、H5120、I2304、3 路由专家+1 共享、topk6、预量化 A8W4/共享 A8W8；关闭维测编译后观察 count epoch 校验停滞；修复 修复 MR https://gitcode.com/cann/ops-transformer/merge_requests/14046 （WIP open，未合入）：IncrementSyncCount 旁路写后补 asc_sync_data_barrier(mem_dsb_t::DSB_DDR)，反汇编确认 ST_DEV.b32 后、跨核通知前增加 DSB #1；八卡 1260 次调用与 30/30 用例通过，但 ON/OFF 数值对照未完成
- **来源**：https://gitcode.com/cann/ops-transformer/merge_requests/14046

### TRN-0320 `op_plugin_cross_entropy_oob_target_silent` op-plugin cross_entropy 越界 target 静默吞掉

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：算子/内核 / cann / cross_entropy 入口校验
- **原因行为**：cross_entropy NPU 入口缺少主机端 target 边界校验，越界值直接下发设备端；reduction=mean 时越界样本被静默排除，reduction=none 时越界槽位为真实越界读。
- **影响对象**：训练信号；数值结果（静默错误）
- **影响详情**：训练 batch 含越界/污染 target 时，NPU 上 loss 静默少算一个样本（mean）或该槽位返回跨芯不一致垃圾值（none：npu:0=0.624 vs npu:1=1.797）；CPU 同代码抛 IndexError。双芯一致复现。
- **改进措施**：检测 训练前在 host 侧断言 0<=target<C 且 target 无 NaN；或对照 CPU 前几个 batch 的 loss。；修复 待定（issue 2026-10-19 open 建议入口加主机端 target 边界校验对齐 CPU 抛 IndexError；无修复 MR）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/598；https://gitcode.com/Ascend/op-plugin/merge_requests/6055
- **关联**：cross:INF-1471

### TRN-0321 `op_plugin_embedding_bag_last_offset_double_count` op-plugin embedding_bag 末包重复累加致错值与梯度污染

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：算子/内核 / cann / embedding_bag 转换层
- **原因行为**：embedding_bag 转换层在 2D 输入 + include_last_offset=True 时末包偏移处理错误，最后一个 bag 被重复累计：sum/mean 末包输出=正确值+末包真实和，梯度同污染；max 正确。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：2D embedding_bag（include_last_offset=True）训练时每个样本最后一个 bag 的 sum/mean 前向输出错值、对应梯度同错；无报错，错值随训练静默传播。max 模式与不含 include_last_offset 的调用不受影响。双芯一致。
- **改进措施**：检测 对含末包的样本用 CPU embedding_bag 对照 forward/backward；或抽验末 bag 输出是否等于「正确和 + 末包和」的二倍关系。；修复 待定（issue 2026-10-19 open 建议核对 include_last_offset 偏移处理；无修复 MR）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/599

### TRN-0322 `op_plugin_pack_padded_pad_dirty_residual` op-plugin pad_packed_sequence 残留原输入脏数据

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：算子/内核 / cann / pad_packed_sequence 转换层
- **原因行为**：op-plugin 的 pad_packed_sequence 输出转换层对 pad 区域不清零，pack→pad 往返后 pad 填充区残留原输入同位置的旧值（恒等拷贝级错误）；索引面（sorted_indices 等）全对。
- **影响对象**：数值结果；跨请求/跨样本数据（静默错误）
- **影响详情**：变长序列训练/RNN 路径中，pad 位若参与池化或 loss 累计，pad 区旧值会静默污染训练数值，无报错。双芯一致复现。
- **改进措施**：检测 pack→pad 往返后断言 pad 区恒为 0；或对往返输出与 CPU 实现逐元素对照。；修复 待定（issue 2026-10-19 open 建议 pad_packed_sequence 输出转换层对 pad 区域清零；无修复 MR）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/604

### TRN-0326 `op_plugin_mul_cpu_scalar_premature_round` op-plugin mul CPU 标量提前舍入 1 ulp 偏差

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：算子/内核 / cann / mul 入口标量上卡
- **原因行为**：mul/mul_out 在 result_type 为 half/bfloat16 时，将 CPU 0-dim 浮点标量按输出 dtype 上卡，H2D 时被提前舍入到 half/bf16。
- **影响对象**：数值结果（静默错误）
- **影响详情**：GPU/NPU 混合精度精度对齐训练中，CPU 0-dim 浮点标量乘卡上 half/bfloat16 张量时，mul 结果与 GPU 差 1 个 bf16 ulp（0.8476 vs 0.8515）；无报错、无 NaN，逐层 dump 比对暴露。
- **改进措施**：检测 跨设备标量乘法与纯 CPU/GPU 参对照逐元素比对；精度对齐 dump 中 mul 节点单算子复测。；修复 修复 MR https://gitcode.com/Ascend/op-plugin/merge_requests/6062 （open 未合入未发布）：浮点标量且 result_type 为 Half/BFloat16 时改按 Float 上卡；mul(Tensor,Scalar) 与 mul_ 路径不受影响。910B2 + CANN 9.2.0 实测。
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5392；https://gitcode.com/Ascend/op-plugin/merge_requests/6062

### TRN-0327 `op_plugin_masked_scatter_small_src_oob_garbage` op-plugin masked_scatter src 不足静默填越界垃圾

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：算子/内核 / cann / masked_scatter 入口校验
- **原因行为**：masked_scatter 两条入口（opapi 与 aclops 兜底）都不校验 src 容量是否 ≥ mask 真值数，src 不足时静默接受，越界读设备内存垃圾填入结果。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：src.numel() < mask 真值数时，NPU 上 masked_scatter_ 不报错，超出 len(src) 的槽位填入越界读到的设备内存垃圾（确定性值、非 NaN），垃圾值随前向/反向传播扩散；双芯一致、上下文存活、无告警。
- **改进措施**：检测 入口断言 src.numel() >= mask.sum()；或与 CPU 实现对照。；修复 修复 MR https://gitcode.com/Ascend/op-plugin/merge_requests/6055 （open 未合入）：两条入口插入 check_source_capacity（快路径 numel 比较零同步、慢路径真值计数 TORCH_CHECK，报错语义与 CPU 对齐）；静态核验通过，真机验证未做（作者无本地 NPU）。
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/602；https://gitcode.com/Ascend/op-plugin/merge_requests/6055
- **关联**：cross:INF-1470

### TRN-0338 `mindspeed_te_rowparallel_noseq_ignores_gaf` 非序列并行 RowParallel 忽略梯度累积融合

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：算子/内核 / mindspeed / RowParallelNoSeq wgrad
- **原因行为**：非序列并行分支 RowParallelNoSeq 的 forward 未保存 gaf，backward 恒走分离 matmul；只有序列并行分支才按 gaf 走 fp32 融合累加。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：gaf=True 时 linear_proj/linear_fc2 的 wgrad 由 aclnnMatmul 产出 bf16 中间张量再累加，与融合路径的 fp32 累加差约 1e-4，经优化器传播后出现可见精度发散；另 patch 对 mcore 0.16 间接引用未生效。
- **改进措施**：检测 对比 gaf=True/False 两条路径同名参数的 wgrad 范数与差异量级；或检查 TERowParallelLinear patch 是否真的替换了 TESpecProvider 返回的类。；修复 issue 建议 RowParallelNoSeq 对齐 RowParallelSeq：forward 保存 ctx.gradient_accumulation_fusion、backward 增加走 npu_matmul_add_fp32 的分支；issue 已 closed，正文未给出合入 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed/issues/231
- **关联**：var:TRN-0118

### TRN-0343 `opsnn_bn_grad_kahan_inf_nan_accumulator` BN 梯度 Kahan 补偿位 Inf-Inf 成 NaN 毒化累加器

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：算子/内核 / cann / KahanAdd/KahanAddReg 累加路径
- **原因行为**：部分和为 ±Inf 时 Kahan 补偿位 c=(t-sum)-y 算得 Inf-Inf=NaN，y=src-c 变 NaN 并跨调用毒化累加器；无 NaN lane 防护。
- **影响对象**：梯度；数值结果（数值异常）
- **影响详情**：含 ±Inf 极值的 BN 反向梯度输入下，NPU 输出 NaN 而 golden/GPU 输出 ±Inf；该算子是 BN 训练梯度路径，输出 NaN 传播进反向梯度。
- **改进措施**：检测 三方校验 cross_check 对含 Inf 用例比对（golden/GPU ±Inf vs NPU NaN）。；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/12373（open）：c!=c 自比检出 NaN lane 并 Select 清零，非有限路径退化为 IEEE 普通加法（对齐 golden/torch.sum）；有限路径行为不变。
- **来源**：https://gitcode.com/cann/ops-nn/merge_requests/12373

### TRN-0344 `opsnn_gns_twopass_cross_call_x_buffer_race` GroupNormSwish 大 shape 跨调用 x 缓冲竞态输出不定

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：算子/内核 / cann / TWOPASS_PERF 模板 V_MTE2 握手
- **原因行为**：每核多次调用 CalNormalize 时 chunk 复用同一 x ping/pong UB 缓冲，但 V_MTE2 事件握手只在单次调用内配对，下一次调用的 MTE2 覆写与上一调用尾部 V 读并发。
- **影响对象**：数值结果；隐状态（不可复现）
- **影响详情**：N×G>114688 的大 shape（触发每核多次 CalNormalize）下 y 输出不确定：同输入多次执行二进制不一致，对 golden matched_ratio 约 98.99%（max_abs_err 5.74）；mean/rstd 不受影响。
- **改进措施**：检测 固定 seed 多次执行比对输出 MD5（修复前 5 次全不同）；TTK 逐位比对。；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/12395（open）：新增 isFirstNormalizeCall/isLastNormalizeCall 使跨调用 V_MTE2 握手配对（Wait 侧与 SetFlag 侧成对修改）；修复后 5 次 MD5 全同、精度 PASS 100%（max_abs_err 0.00195），小 shape 零影响。
- **来源**：https://gitcode.com/cann/ops-nn/merge_requests/12395

### TRN-0360 `msllm_li_cp_kvallgather_double_transpose` CP 融合 LI 算子重复转置致 S/B 互换

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：算子/内核 / mindspeed-llm / fused LI CP KV 包装
- **原因行为**：CP 的 compress+KV-allgather 分支先把 q/k/weights 从 SBND 转成 BSND 再调 npu_lightning_indexer，而该算子本身收 SBND 并在内部转 BSND，S 与 B 因此互换。
- **影响对象**：可用性/进度；数值结果（报错）
- **影响详情**：mbs=1、CP=2、S=4096 时 sub-chunk [1024,1,N,D] 被算子读成 B=1024，metadata 校验 batch_size 与 cmp_residual_k 的 1 不符即刻失败；CP=1 不走该分支故正常。
- **改进措施**：检测 开融合 LI 前先做 CP=1/CP=2 精度对齐；对传入 npu_lightning_indexer 的 q/k/weights 打印 shape 与 layout，确认上层没有再转置；修复 issue 标题即修复动作：去掉上层预转置、直接把 SBND 传入并让算子内部 rearrange（closed，正文为修复的根因说明，未附 MR 链接，未核实合入版本）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1564

### TRN-0365 `opsnn_cegrad_label_smoothing_uninit_out` CELossGrad label_smoothing 非 0 返回未初始化内存

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-22

- **原因对象**：算子/内核 / cann / CELossGrad 写回路径
- **原因行为**：kernel 在 labelSmoothing!=0 时无任何输出写回与拒绝路径，外层 CopyOutLog 把未初始化 UB 数据当结果写出；tiling/aclnn 层均未校验该取值。
- **影响对象**：梯度（不可复现）
- **影响详情**：labelSmoothing!=0 的 CE 反向输出为随机字节，同输入多次调用结果互不相同；直接污染训练梯度。
- **改进措施**：检测 出参预填哨兵值（如 12345）重跑比对；同输入连续 3 次调用比对原始字节是否一致。；修复 待定（issue open，期望非 0 时返回 161002 或实现 smoothing 项）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7135

### TRN-0366 `opsnn_cegrad_weight_dtype_reinterpret` CELossGrad weight dtype 未校验按 fp32 重解释

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-22

- **原因对象**：算子/内核 / cann / CELossGrad weight 读取
- **原因行为**：weightOptional 非法 dtype 不被 161002 拦截，kernel 固定按 float* 解释缓冲并按 C 个 float 读取，越界读且字节重解释成错值。
- **影响对象**：梯度（静默错误）
- **影响详情**：weight 传半精度（实测 fp16，bf16 常见）时梯度静默缩小 4~5 个量级（-0.268941→-8.22247e-06），loss 仍下降但收敛变慢或失效，无报错无日志；fp32 路径正常，仅 dtype 传错时触发且无拦截。
- **改进措施**：检测 对 weight dtype 做 fp32 断言或调用前自查；比对同输入 CPU 参考梯度量级。；修复 待定（issue open，期望 dtype 白名单返回 161002）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7134

### TRN-0367 `opsnn_cegrad_target_oob_weight_oobread` CELossGrad target 越界静默错值并越界读 weight

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-22

- **原因对象**：算子/内核 / cann / CELossGrad target 处理
- **原因行为**：target 越界/负值仅处理「负且等于 ignoreIndex」，其余直接当下标做 one-hot 减法，weight 路径 weightGm.GetValue(target) 越界读 GM。
- **影响对象**：梯度（静默错误）
- **影响详情**：target 含 padding(-1)/越界标注时 CE 反向不中断、梯度按错误位置计算，weight 越界读读到其他显存。
- **改进措施**：检测 训练侧在 loss 前断言 target∈[0,C) 或 ==ignoreIndex；golden 比对含越界 target 用例。；修复 待定（issue open，期望取值校验；关联 #7047 aclnnNLLLoss、#4837 同类不同算子）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7136

### TRN-0368 `opsnn_bcegrad_target_weight_broadcast_missing` BCE 反向 target/weight 广播未生效越界读错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-22

- **原因对象**：算子/内核 / cann / BCEBackward 广播处理
- **原因行为**：aclnn CheckShape 只校验可广播性不 expand，下游 TBE 动态内核只 broadcast grad_output，target/weight 按元素总数读取越界。
- **影响对象**：梯度（静默错误）
- **影响详情**：target=[1x4]/weight=[N] 等文档支持的广播输入下 BCE 反向输出 4/8~7/8 元素错，fp32 最大超容差 1.8e6 倍。
- **改进措施**：检测 训练前用小张量 CPU 对照 BCE 反向；检查 target/weight 是否为广播形状。；修复 待定（issue open，修复方向：aclnn 层 expand 后下发或 kernel 补广播）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7132；https://gitcode.com/cann/ops-nn/merge_requests/13119

### TRN-0369 `opsnn_flceg_maskedtarget_oob_gm_rw` 融合CE梯度 maskedTarget 越界 GM 读写静默错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-22

- **原因对象**：算子/内核 / cann / FusedLinearCEGrad 下标
- **原因行为**：高性能分支直接用 maskedTarget 值算目标下标，op_api 只校验长度不校验取值；-1 等越界值在 softmaxOptional 缓冲区外 4 字节非法读写。
- **影响对象**：梯度（静默错误）
- **影响详情**：maskedTarget 含 -1（词表并行惯例）时 inputGrad/weightGrad 各一整行与 CPU 标杆不符（maxabs≈1.5），rc=0。
- **改进措施**：检测 msSanitizer memcheck 检出 illegal read/write；golden 用例应覆盖 maskedTarget=-1。；修复 待定（issue open；仓内 golden 自身写 clamp(0,V-1)，实现需对齐夹取或显式校验）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7115

### TRN-0370 `opsnn_bn_backward_saveinvstd_as_variance` BN 反向把 saveInvstd 当方差致梯度静默偏差

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-22

- **原因对象**：算子/内核 / cann / BNBackward saveInvstd
- **原因行为**：kernel 把入参 saveInvstd 直接当方差参与梯度公式，与资料/参数名定义的 1/sqrt(Var+eps) 口径相反；无校验。
- **影响对象**：梯度（静默错误）
- **影响详情**：按 torch save_invstd 口径传入时 gradInput 偏 4.77%、gradWeight 偏 8.10%（fp64 参考对照），rc=0。
- **改进措施**：检测 分别传 invstd 与 var 跑 BN 反向，与 fp64 参考比对（偏差>4% 即命中）；对齐口径后再用。；修复 待定（issue open，实现改口径或资料/校验对齐）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7035

### TRN-0371 `opsnn_bnelemtgrad_counter_reducesum_divisor` None

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-22

- **原因对象**：算子/内核 / cann / BNElemtBackward 除数
- **原因行为**：MeanByCounter() 对 counter 先全轴 ReduceSum 再作除数，把资料公式的逐元素除法改成按总和除，多元素 counter 时除数放大 C 倍。
- **影响对象**：梯度（静默错误）
- **影响详情**：counter 多元素（如 [2,2]）时 gradInput 整体再除一次 2（实测 -1 vs 期望 -2），rc=0 无告警。
- **改进措施**：检测 多元素 counter 用例与 CPU 参考比对；检查 counter 形状是否 >1 维。；修复 待定（issue open，改逐元素除法）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7093

### TRN-0372 `opsnn_gns_grad_tiling_init_dropped_fp16bf16` GroupNormSwishGrad tiling 失败被丢弃梯度未写

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / GroupNormSwishGrad tiling
- **原因行为**：GetDataTypeSize 对 fp16/bf16 按 6 字节虚增 3 倍，UB 预算算错使 tiling Init 返回 GRAPH_FAILED，但返回值被丢弃仍下发半初始化 tiling 并报成功，kernel 空转
- **影响对象**：梯度；训练信号（数值异常）
- **影响详情**：C/G=4000（3999 亦命中）、HxW=1 且 fp16/bf16 时，dx 11360/12000 未写、dgamma/dbeta 出现 NaN，返回码仍为 0；host 日志有告警但未传到返回码；C=256000、G=64 时触发 507035 vector core 异常进程退出。
- **改进措施**：检测 训练侧对 GroupNorm+Swish 反向输出做 NaN/零占比抽检（dgamma NaN 计数、dx 零元素占比）；fp32 路径正常可作对照；修复 待定（issue 给出修复建议：检查 Init() 返回值失败即 GRAPH_FAILED；GetDataTypeSize 对 fp16/bf16 返回 2；无修复 MR）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7081
- **关联**：var:TRN-0344

### TRN-0373 `opsnn_ctc_loss_backward_blank_nonzero_grad_misplaced` CtcLossBackward blank!=0 修正项错写 c=0 梯度错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / CtcLossBackward kernel
- **原因行为**：blank 属性非 0 时 kernel 把 blank 修正项写到 c=0 而非 c=blank，相当于把 blank 当 0 使用，梯度分布整体错位
- **影响对象**：梯度；训练信号（静默错误）
- **影响详情**：blank!=0 的 CTC 训练每个 (t,n) 的梯度行和偏离 0 约 0.327（应≈2.8e-7 浮点噪声），log_probs 梯度错位分布，返回码 0 无告警；blank=0 时正确
- **改进措施**：检测 对 CTC 反向输出按行求 sum_c 验证 ≈0（softmax+CTC 自洽不变式，与标杆无关）；blank=0 对照；修复 待定
- **来源**：https://gitcode.com/cann/ops-nn/issues/7162

### TRN-0374 `opsnn_logit_grad_double_eps_narrowed_fp32` LogitGrad double eps 被窄化 float32 边界判错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / LogitGrad 入口与 tiling 链路
- **原因行为**：原型声明 double eps 但实现链路按 float32 承载（static_cast<float>(eps)），eps 与 x 的边界比较在比较前被舍入到 float32，次正规 eps 下溢为 0
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：eps=x+ulp32/8（double 下严格大于 x）时按资料应输出 0，实测输出与 eps==x 完全相同；eps=1e-320 输出与 eps=0.0 逐字节相同，x=0 时输出 inf 而非 0，返回码 0
- **改进措施**：检测 对 eps 邻近 x 的边界点做 fp64 标杆对拍（x+ulp32/8 / 1e-320 两档）；修复 待定（issue 建议 eps 全程 double 或把原型/资料改 float 二选一）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7163

### TRN-0375 `opsnn_thnn_fused_lstm_cell_global_state_mt_race` ThnnFusedLstmCell 全局状态多线程竞态错果崩进程

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / ThnnFusedLstmCell 全局状态
- **原因行为**：aclnn 入口 AclnnParams/AclnnInfo/BaseOpOutputs 与 tiling 的 info/TilingData 均为文件作用域全局对象、被隐式共享，host 侧并发不安全；根因未钉死为串写
- **影响对象**：数值结果；可用性/进度（不可复现）
- **影响详情**：8 线程×60 次并发调用（含同 shape 对照）出现 hy 输出失配 max_diff≈0.937、第一段 561103 共 61 次、段错误 rc=139；单线程 160 次全正常
- **改进措施**：检测 并发压测同算子（交替 shape + 同 shape 对照）；DoOpTiling 首尾加 atomic 计数 peak>1 即证重入；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/12590（open，2026-10-22）：全局对象改栈上 context/局部 tiling，辅助函数显式传参；MR 自述未附并发测试，需按 #7007 脚本验证
- **来源**：https://gitcode.com/cann/ops-nn/issues/7007；https://gitcode.com/cann/ops-nn/merge_requests/12590

### TRN-0376 `opsnn_kldiv_target_backward_overflow_empty_unwritten` KlDivTargetBackward 中间量溢出 inf 且空输入不写输出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / KlDivTargetBackward
- **原因行为**：公式改写为 g*log t - g*s + (g*t)/t，(g*t) 在 fp32 下先溢出再除回；空输入分支两段返回 0 但完全不去写 gradTarget 输出
- **影响对象**：梯度；数值结果（数值异常）
- **影响详情**：g=1e10、t=1e30 时 gradTarget=inf（真值 7.00776e11 有限）；合法空输入形态 self=[0,3] 时 gradTarget 保持预填 NaN 原样未被写入，返回码 0
- **改进措施**：检测 对极端幅度输入做有限性检查；空输入路径用 NaN 金丝雀预填输出验证写行为；修复 待定（issue 建议：避免 g*t 中间量/改 fp64 中间量/先除后乘；空输入写 0 或报 161002）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7168

### TRN-0377 `opstransformer_sparse_flash_mla_grad_oob_write_legal_input` SparseFlashMlaGrad 合法输入 GM 越界写 1060 处

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / SparseFlashMlaGrad arch22
- **原因行为**：A2 的 post.h 与 sfag_basic.h/smlag_basic.h 里 DataCopyPad 目标地址按 tile 步进直接计算，尾块/对齐无越界保护，写越界落在已映射内存时静默、落在未映射内存时 AI Core 异常
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：合法基线返回 0、结果可用，但 mssanitizer memcheck 报 1060 处 GM 写越界（单笔最大 896B），--padding 1024 后仍同样报；同族 #6534/#6535 在边界形态表现为 507057/507015 崩核
- **改进措施**：检测 mssanitizer -t memcheck --padding 1024 包住训练进程，统计 out of bounds 计数；越界落在未映射页时提前表现为 AI Core 异常；修复 待定（master 复核 arch22 post.h/sfag_basic.h 未见尾块越界保护，未修）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6537；https://gitcode.com/cann/ops-transformer/issues/6534；https://gitcode.com/cann/ops-transformer/issues/6535；https://gitcode.com/cann/ops-transformer/issues/6536

### TRN-0380 `triton_ascend_gather_rows_ep_rank_device_fault` Triton gather_rows EP 前向 rank1 设备越界静默楔死

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / triton / gather_rows kernel
- **原因行为**：Triton gather_rows 做 AutoEP token 重排，2-rank 下 rank1 两形态故障：多为前向静默楔死（3/3 复现），偶发 host 同步报 MTE 访问 DDR 越界（多核同 PC）；单进程不复现
- **影响对象**：可用性/进度；数值结果（挂起）
- **影响详情**：多数形态（3/3）为 rank1 流静默楔死、rank0 在下一个 collective 挂起约 600s 后 ACL ERR00100 超时；少数形态 host 同步直接报设备异常 dump。切回 torch fallback 同负载 29.87s 全通过
- **改进措施**：检测 EP 前向加 per-rank 心跳/进度探针区分静默楔死；设备异常 dump 的同 PC 多核特征；修复 规避：DeepSpeed permute 路径切回 torch fallback（issue 已验证因果对照）；上游修复待定（open，0 评论）
- **来源**：https://github.com/triton-lang/triton-ascend/issues/2648

### TRN-0383 `opstransformer_mrs_v2_attrs_silently_ignored` MatmulReduceScatterV2 非法 reduceOp 静默按sum

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / MatmulReduceScatterV2 校验
- **原因行为**：V1 有 reduceOp/commTurn 校验（非法值返回 561002），V2 缺失：reduceOp=max 或 commTurn=1 两段返回 0、执行成功，输出与 sum/0 逐元素一致——两个属性被静默忽略
- **影响对象**：梯度；数值结果（静默错误）
- **影响详情**：同一输入 V1 返回 561002、V2 返回 0；max 与 sum 输出不同元素数 0/2048。资料规定 reduceOp 仅支持 sum、commTurn 仅支持 0
- **改进措施**：检测 V2 调用前在框架层显式断言 reduceOp=sum/commTurn=0；对拍 V1 行为；修复 待定
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6524

### TRN-0386 `opsnn_clipped_swiglu_group_rows_uninit_training` ClippedSwiglu 组外输出行未初始化显存残影

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：算子/内核 / cann / ClippedSwiglu 适配层
- **原因行为**：传 group_index 且 sum(gi)<batch 时 kernel 只写 min(sum(gi),batch) 行，适配层用 at::empty 分配输出——范围外行是显存池残影，同一输入有时全 0 有时脏值
- **影响对象**：数值结果；梯度（不可复现）
- **影响详情**：MoE group 场景 batch=8、sum(gi)=5 时行 5-7 输出 32/32 非零残影（e-12~e-7 量级）；需先污染显存池才复现，干净环境碰巧全 0——随机复现的未定义行为
- **改进措施**：检测 预热污染显存池后对 group 场景输出范围外行做非零断言（仓内 golden 语义：范围外应为 0）；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/12603（open，2026-10-22）：has_group 时 at::zeros 初始化输出，非 group 路径保持 at::empty 零开销；12 项金标准对拍 PASS，group 场景修复后范围外行恒 0
- **来源**：https://gitcode.com/cann/ops-nn/issues/7223；https://gitcode.com/cann/ops-nn/merge_requests/12603
- **关联**：cross:INF-2136

### TRN-0388 `opstransformer_mhc_pre_sinkhorn_backward_fd_bias_race` mhcPreSinkhornBackward 梯度系统偏差与并发输出污染

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / MhcPreSinkhornBackward 归约
- **原因行为**：大 shape 反向梯度与前向有限差分存在 ~2e-2 系统偏差（偏差在 backward 侧）；kernel 侧归约读与清零构成跨调用 WAR 并伴 UB 越界读，共享 context 并发调用时输出被跨调用污染。
- **影响对象**：梯度（静默错误）
- **影响详情**：M·K≥2M 起 gradBias/gradPhi 与有限差分偏差达 1e-2~3e-2 且符号可反；8 线程共享 context 并发重放不同 shape 时 74 次输出位模式与单线程基准不一致（部分稳定错、部分随机错），单线程串行不可见。
- **改进措施**：检测 反向梯度与前向有限差分对拍（多 eps 平滑外推）；mssanitizer racecheck 检同 block WAR；并发多 shape 重放与单线程基准比位模式。；修复 待定（issue open 2026-10-23；master arch22 kernel 与 9.2.0 零功能改动，缺陷同存）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6619

### TRN-0389 `opsnn_matmul_bf16_fp16_mixed_nd_silent_low_precision` aclnnMatmul BF16×FP16 ND 路径静默低精度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / aclnnMatmul ND 路径校验
- **原因行为**：self/mat2 分别为 BF16 与 FP16/FP32 且均 ND 时，校验只在 mat2 为 NZ 时拦截混用，ND 路径无校验，两段返回 0 静默出结果；文档明确该组合应返回 161002。
- **影响对象**：数值结果（静默错误）
- **影响详情**：A2/910b 与 A3 文档均声明不支持 BF16+FP16/BF16+FP32 推导，实际 ND 路径静默执行；实测 16x16 cubeMathType=KEEP_DTYPE 返回 0/0 出结果，结果 dtype 语义未按文档拒绝。
- **改进措施**：检测 调用前在框架层断言两输入 dtype 一致；对拍文档约束矩阵。；修复 待定（issue open 2026-10-23，根因定位至 aclnn_matmul.cpp CheckInputParams/CheckWeightNzDtype 校验缺口）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7237

### TRN-0390 `opstransformer_block_sparse_attention_grad_leading_tokens_unwritten` BSA-Grad 首 blockShapeX/2 token 梯度未写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / BSA-Grad 反向输出搬运
- **原因行为**：BNSD+fp16 下 dq/dk/dv 每个 head 前 blockShapeX/2 个 token 行的梯度从未被写入，输出缓冲保留调用方传入内容；两段接口均返回 0，未写比例恒等于 blockShapeX/256。
- **影响对象**：梯度（静默错误）
- **影响详情**：稀疏注意力反向后，dq/dk/dv 每 head 头部 6.2%~50% 元素是输出缓冲残留（复用缓冲时为上一张量内容），无报错无 NaN；已写区域与标杆一致，错值集中在未写区间。
- **改进措施**：检测 输出缓冲预填互异 canary 两次调用比对；按未写比例=blockShapeX/256 抽查首 token 梯度。；修复 待定（issue open 2026-10-23，master e6106909 复现，未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6620

### TRN-0392 `opsnn_softplus_grad_sigmoid_overflow_inf_times_zero_nan` SoftplusGrad 大负输入 sigmoid 下溢 inf×0 出 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / SoftplusGrad sigmoid 计算
- **原因行为**：sigmoid=1/(1+exp(-features)) 在大负 features 时中间量溢出为 inf、sigmoid 下溢为 0；特定窗口内遇 inf 梯度时 inf×0=NaN，正确应为 ±inf。
- **影响对象**：梯度（数值异常）
- **影响详情**：softplus 反向在深负激活区（约 -103~- -89）遇到 inf 梯度时输出 NaN 而非 ±inf；修复前 375 条旧用例 374 PASS、唯一失败即此边界。
- **改进措施**：检测 对 features∈(-103.28,-88.73] × gradients=±inf 组合做边界单测；已写修复。；修复 修复 PR https://gitcode.com/cann/ops-nn/pull/12612（open 2026-10-23）：sigmoid 改 Compare/Select 双分支稳定实现（两分支 exp 参数均 ≤0）并叠加 fp32 最小正规数 1.17549435e-38 防 FTZ 刷 0；Kernel UT 13/13、Host UT 29/29、上板 83/83 PASS（PR 记录，未发布）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7268；https://gitcode.com/cann/ops-nn/pull/12612

### TRN-0394 `opsmath_clamp_max_scalar_wraps_bit_pattern` aclnnClampMax 标量越界按位环绕静默改写输出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / aclnnClampMax 标量类型转换
- **原因行为**：A2 分支 promoteType 直接取 out dtype，标量转换无范围校验无饱和：整数越界按补码截断（1000→-24），「上界」变小负数后 min(x,max) 静默算成另一结果；原地入口直接改写入参缓冲。
- **影响对象**：数值结果（静默错误）
- **影响详情**：int8 上界 1000 时全表输出 -24（期望原值）；反向 -200 时原样返回输入（期望全 -200），语义完全相反；uint8 300 时输出 0,44,44；原地入口把调用方输入数据直接覆盖，无法从返回值或输出察觉。PyTorch 同类调用直接 RuntimeError 拒绝。
- **改进措施**：检测 调用前校验标量在目标 dtype 可表示范围；对拍 CPU clamp 语义。；修复 待定（issue open 2026-10-23，根因定位至 conversion/clip_by_value_v2/op_api/aclnn_clamp.cpp:345-362 A2 分支，master efff3523 在位）
- **来源**：https://gitcode.com/cann/ops-math/issues/3849；https://gitcode.com/cann/ops-math/issues/3850
- **关联**：cross:INF-2217

### TRN-0395 `opsmath_exp_segsum_tail_stripe_column_calcount_oob_read` ExpSegsum 末条带误用列向长度 GM 越界读

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / ExpSegsum arch22 末条带搬运
- **原因行为**：末条带 CopyInBatch 搬运长度取列向钳位 calCount，搬运起点却按行向 inOffset 计算，两者不同源；tailDimSize>slideSize 且不整除时读窗口越过 x 张量末尾，末 batch 越出整块 GM。
- **影响对象**：数值结果（静默错误）
- **影响详情**：mssanitizer memcheck 实测 self=(1,1,13000) 报 illegal read fp16 22944B / fp32 45952B；多读数据不被消费，数值结果仍正确，属静默越界读。
- **改进措施**：检测 mssanitizer -t memcheck 扫 ExpSegsum kernel；T>slideSize 且 T%slideSize≠0 的形状单测。；修复 待定（issue open 2026-10-23；master efff3523 缺陷行原样在位，未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-math/issues/3845

### TRN-0400 `opsnn_lightning_indexer_kl_loss_example_nan_cross` LightningIndexerKLLoss 官方 example 输出 NaN

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / LightningIndexerKLLoss
- **原因行为**：官方 example 输入完全合法却输出 nan：最小用例 y=[2.0]、Y=[1.0]、K=1 期望 ≈-0.81 实测 nan；dtype/K/B/eps/weightType/确定性开关全维度排查均 nan，金丝雀排除未初始化内存。
- **影响对象**：训练信号（数值异常）
- **影响详情**：Lightning Indexer（Kimi K2 类 MoE 深层索引器）KL loss 训练损失恒为 nan，训练起步即坏；截至 2026-10-13 master 未见修复提交，若已修待告知 PR。
- **改进措施**：检测 首 step loss 断言有限；官方 example 作为冒烟金丝雀。；修复 待定（issue open 2026-10-23；报告者请求告知修复 PR 后重验）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6614

### TRN-0402 `opstransformer_fa_grad_v3_deterministic_dsink_unwritten` FA-Grad V3 确定性路径 dsink 输出未写出

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-24

- **原因对象**：算子/内核 / cann / FA-Grad V3 确定性 tiling
- **原因行为**：确定性计算=1 且 attenMask 为空时，非确定性 tiling 读 SINK_IN 判断 sink 维，确定性 tiling 无任何 sink/dsink 处理，dsinkOut 完全不写；sinkIn 非空时资料要求必须写出。
- **影响对象**：梯度（静默错误）
- **影响详情**：sinkInOptional 非空（fp32[headNum]）+确定性开关=1 时 dsinkOut 保持预填金丝雀 0xA5A5A5A5（重复执行同），开关=0 同输入正常写出；无报错，两段返回 0。
- **改进措施**：检测 确定性开关下对 dsinkOut 预填金丝雀 round-trip；与开关=0 的输出对拍。；修复 待定（issue open，master 复核确定性 tiling 无 sink 处理，未修）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6521
- **关联**：var:TRN-0273

### TRN-0405 `ops_math_concat_tree_desc_missing_silent_wrong` Concat >512 拆树缺树形 desc 推导真机静默算错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / Concat 拆树 desc 推导
- **原因行为**：输入分支数 >512 触发拆树时缺少树形 desc 推导，真机静默计算错误（修复 MR 标题自述，open）。
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：超过 512 个输入的 Concat（典型如超长 MoE 专家/分片汇聚路径）在真机上静默输出错误拼接结果，接口无报错；下游以错误张量继续训练。
- **改进措施**：检测 超多输入 Concat 与 CPU 参考 golden 对拍；>512 边界扫描用例。；修复 修复 MR https://gitcode.com/cann/ops-math/pull/6660（open，未合入未发布，未核实）。
- **来源**：https://gitcode.com/cann/ops-math/pull/6660

### TRN-0406 `ops_transformer_msa_index_score_kv_head0_only` MsaIndexScore N2>1 只读 KV head0 输出静默错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnMsaIndexScore KV hea
- **原因行为**：key 的 N2>1 时算子对所有 query head 都只读取第 0 个 KV head，未按 n2=n1/(N1/N2) 取对应 KV head，输出对 head1 以后的数据完全不敏感。
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：GQA/MQA 形态（N2>1，每 KV head 服务多个 query head）调用 MsaIndexScore 时，只改 head1 及以后的 KV 数据输出逐位不变（max|diff|=0 bitwise），其余 head 的信息全部丢失；接口返回 0 无报错。训练侧该算子输出直接作为前向结
- **改进措施**：检测 扰动单个非 0 KV head 数据检查输出是否变化（bitwise 对照）；与 CPU GQA 参考对拍。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6639
- **关联**：cross:INF-2161

### TRN-0407 `ops_transformer_chunk_kda_fwd_tail_rows_scale_missing` ChunkKdaFwd 尾块 33~47 行输出放大 sqrt(K) 倍

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnChunkKdaFwd 行块截断 sca
- **原因行为**：尾块长度落在 33~47 行时，chunk-relative row 32..l_c-1 的 aqkOut/attnOut 尾行块丢失 scale 乘法，被整体放大 sqrt(K) 倍（K=64 时恰 8 倍），比值随 1/scale 变化
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：chunked KDA/DeltaRule 线性注意力前向：尾块 l_c∈(32,48)（33~47 行）时，chunk 内 row 32..l_c-1 的 aqkOut/attnOut 放大 sqrt(K) 倍，其余行正常；单 chunk 与全长+尾块排布均复现，接口返回 0 无报错。
- **改进措施**：检测 尾块行数 33~47 的用例与 fp64 CPU 参考逐行比值对拍（比值恒 = 1/scale 即命中）。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6657

### TRN-0408 `ops_transformer_mhc_pre_alpha2_hres_unwritten` MhcPre alpha=(2) 且 hRes 非空时返回未写显存

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnMhcPre alpha=(2) 分支
- **原因行为**：alpha=[2]（无残差分支语义，资料称 hRes 输出为 0）且调用方给 hRes 传非空张量时，两段接口返回 0 但 hRes 一个字节都不写，保持调用方原有内容；alpha=[3] 对照组正常写满。
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：alpha=(2) 配置下消费 hRes 的下游读到调用前显存残留值（canary -777 原样保留），静默脏数据进入后续计算；接口无报错。训练侧残差分支张量被未初始化值污染。
- **改进措施**：检测 hRes 预填 canary 后调用检查是否被改写；alpha=(2) 分支读回对拍。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6658
- **关联**：cross:INF-2163

### TRN-0409 `ops_transformer_nsa_compress_grad_weightgrad_256_boundary` NsaCompressGrad weightGrad 乘积≥256 边界静默算错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnNsaCompressGrad weig
- **原因行为**：compressBlockSize*headNum≥256 时 weightGradOut 归约行/头索引错位，输出为别的 (row,head) 的归约值；同用例 inputGradOut 始终正确，两段与同步均返回 0。
- **影响对象**：梯度；数值结果（静默错误）
- **影响详情**：NSA（Native Sparse Attention）压缩算子反向，compressBlockSize 与 headNum 乘积≥256 时 weightGrad 静默错值（错误结构为其他行列的归约值，非全零），240 及以下全对；训练中权重梯度错误进入优化器。
- **改进措施**：检测 blockSize*headNum 跨 240/256 边界的梯度对拍 CPU 标杆；扫描 49 组配置（报告者已做）。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6666

### TRN-0411 `ops_math_addcmul_nan_value_treated_as_one` Addcmul 把标量 value=NaN 判为 1 静默输出有限值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnAddcmul IsEqualToOne
- **原因行为**：IsEqualToOne 判据 !(value>1 || value<1) 在 IEEE-754 下 NaN 比较恒 false，取反为 true，NaN 被判为等于 1，进入 AxpyV2 快路径不做 value 乘法，输出退化为 sel
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：标量 value=NaN 时按公式 out=self+value×t1×t2 应输出全 NaN，实际静默输出看似正常的有限值；训练中 value 来自已变 NaN 的量（如 loss scale、权重系数）时，本应立即暴露的 NaN 被吞成静默错值，训练继续但更新已错。
- **改进措施**：检测 对含 NaN 标量的 addcmul 调用检查输出是否 NaN；训练侧监控 value 来源（loss scale 等）是否为 NaN。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3894
- **关联**：cross:INF-2160

### TRN-0412 `ops_math_tan_large_input_stale_nan_guard` Tan |x|≥1e7 遗留 NaN 保护输出全 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / tan_simt.h LARGE_THRESHOL
- **原因行为**：arch35 tan_simt.h 保留旧手写 Cody-Waite 约化时代的 LARGE_THRESHOLD=1e7f 保护，|x|≥1e7 的有限输入被直接置 NaN；fb7fd5371 换 SIMT tanf 高精度范围约化后该保护
- **影响对象**：数值结果；训练信号（数值异常）
- **影响详情**：大参数 tan 输入（|x|≥1e7，如大坐标/未归一化特征）在 GEIR/aclnnTan/aclnnInplaceTan 三条通路输出全 NaN，torch/numpy 同输入输出有限值、同算子 aicpu fp64 通路亦输出有限值；训练中该位置激活/梯度变 NaN 传播。
- **改进措施**：检测 大值输入（1e7~FLT_MAX、±2^31）21 点精度探针对拍 torch.tan（修复 PR 已含）。；修复 修复 MR https://gitcode.com/cann/ops-math/pull/6661 （open，未合入未发布；删除 guard 后 21 点探针全 PASS、精准回归 71 例 FAIL→PASS 6/PASS→FAIL 0，未核实发布版本）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3871；https://gitcode.com/cann/ops-math/pull/6661

### TRN-0414 `ops_transformer_sparse_flash_mla_metadata_ignores_sequsedq` SparseFlashMlaMetadata 丢弃 sequsedQ 按满长调度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnSparseFlashMlaMetada
- **原因行为**：A2 上 sequsedQOptional（每 batch Q 侧有效 token 数）整条数据通路被丢弃，无论传什么值 metadata 与不传逐字节相同；同签名 sequsedOriKvOptional 生效（对照闭合），唯独 sequ
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：Q 侧有效长度被无视、分核按 maxSeqlenQ 满长切分（sequsedQ=0 仍产出满长 105 元素调度），下游 SparseFlashMla 按满长任务搬 KV 多算；接口返回 0 无报错。
- **改进措施**：检测 变 sequsedQ 值（1024/256/64/2/1/0）比对 metadata 指纹是否变化（应变化而不变）；与 KV 侧对照。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6625
- **关联**：cross:INF-2167

### TRN-0415 `ops_math_concat_empty_sorter_invalid_iterator` SearchSorted 空 sorter 空序列解引用末迭代器

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / SearchSortedKernel::Compu
- **原因行为**：GetInputAndCheck 在空张量短路前执行；sorted_sequence 与 sorter 均为空时 size 检查通过（0==0），对空范围取 std::max/min_element 返回的 end 迭代符立即解引用，读出有
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：sorted_sequence 与 sorter 元素数均为 0（文档允许空 shape 如 {2,0}）时带 sorter 调 SearchSorted，host 侧解引用空范围迭代器读到越界/null：可能段错误，或把垃圾值当边界输出错误结果；空 batch 偶发。无实机崩溃日志，训练面较窄。
- **改进措施**：检测 空序列 + sorter 用例回归；ASan/memcheck 落点 SearchSortedKernel:127-128。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3863

### TRN-0416 `ops_nn_layer_norm_unknown_rank_infershape_misjudge` layer_norm 未知秩 InferShape 误拒或矛盾输出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / layer_norm/layer_norm_v3
- **原因行为**：gert::Shape 以「1 维、值 -2」表示未知秩，GetDimNum() 返回 1，IsDimValid(1,axis) 按 [-1,0] 校验把合法多维 axis 判越界拒收；axis 恰过校验时 mean/var 被推导为 [1
- **影响对象**：可用性/进度；数值结果（报错）
- **影响详情**：动态图下 layer_norm/layer_norm_v3 收到未知秩（-2）输入（TTK geir 实测）：合法多维 axis 被判越界，构图失败并报 axis 非法；或构图通过但 mean/var 被推为 [1]，与 y 的未知秩矛盾仍放行至执行，训练后期才以形状错乱暴露。
- **改进措施**：检测 TTK geir 模式未知秩 4 组对照用例（修复 PR 已含 33 例/27 场景上板验证）。；修复 修复 PR head 567b4846（issue 附验证：未知秩时三输出统一置未知秩、marker 命中，真非法 axis 仍拒收；修复 MR 状态未核实）。
- **来源**：https://gitcode.com/cann/ops-nn/issues/7281

### TRN-0417 `ops_transformer_concat_final_tile_overrun` ops-transformer concat 末 tile 全量拷贝越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / concat kernel 末 tile 长度 c
- **原因行为**：TilingFunc 设 tileNum=ceil(posPerBlock/posPerTile)、tileLength=posPerTile*headDim，kernel 对每个 tile 恒用完整 tileLength 的 CopyIn
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：shape 使 posPerBlock 不能整除 posPerTile 时末 tile 必越界：相邻核数据被越界读写、末核读写越过张量边界上万元素（如 x[1,1024,128]、196608B UB 下末核越写 16128 元素），输出悄悄错或进程崩溃，随 shape 与 UB 容量浮动。
- **改进措施**：检测 memcheck/保护带定量（报告者给出越界元素数计算）；tile 边界 shape 扫描用例。；修复 待定（issue open；修复方向为末 tile 按剩余量 clamp）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6627

### TRN-0419 `ops_transformer_moe_backward_missing_value_range_validation_family` MoE 反向算子族缺值域校验静默吞错输入

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / MoE 反向算子 host 值域/枚举校验
- **原因行为**：MoeGatingTopKBackward、MoeTokenPermuteWithEpGrad、MoeTokenUnpermuteWithEpGrad、MoeTokenPermuteGrad、MoeTokenUnpermuteGrad 等
- **影响对象**：梯度；可用性/进度（静默错误）
- **影响详情**：上游路由产物被错配/改写时，越界或负的专家索引、负 numTopk、非法枚举、空张量、start>end 区间进入 MoE 反向算子：host 第一段校验不报参数错误，轻则接口成功返回 0、该项梯度被当 -1 静默丢掉，重则设备侧向量核异常 507035 打断作业；上游路由正常时不触发。
- **改进措施**：检测 上游路由产物 idx/numTopk 加值域断言；跨边界输入对拍 CPU 标杆（skip/clamp/mod 三语义）。；修复 待定（各 issue open，未见统一修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6690；https://gitcode.com/cann/ops-transformer/issues/6659；https://gitcode.com/cann/ops-transformer/issues/6672；https://gitcode.com/cann/ops-transformer/issues/6685；https://gitcode.com/cann/ops-transformer/issues/6693；https://gitcode.com/cann/ops-transformer/issues/6674；https://gitcode.com/cann/ops-transformer/issues/6691

### TRN-0421 `ops_math_searchsorted_cuSeq_shape_validation_family` 索引/可选输入 shape 与值域缺校验静默越界族

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / 搜索/元数据算子 host shape·值域校验
- **原因行为**：可选输入只校验非空不校验长度/值域：cuSeqLengths 未与 B 校验即按 b+1 索引越界读；argmax 零长归约轴返回成功；MaxDim indices dtype 未校验放行；LeScalar out dtype 白名单误用
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：变长/检索类算子收到 shape 与值域外的可选输入：越界读相邻显存当序列长度（total_task_num 33554432 垃圾值）静默产出错误调度/检索结果，或对非法输入返回成功、合法输入反被拒；无 host 拦截。
- **改进措施**：检测 可选输入长度与主维度的关系断言；metadata 字段与 CPU 标杆对拍。；修复 部分有修复：ArgMax !6667（open）、MaxDim !6668（open）；cuSeqLengths 校验未见修复 MR。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6647；https://gitcode.com/cann/ops-math/issues/3890；https://gitcode.com/cann/ops-math/issues/3879；https://gitcode.com/cann/ops-math/issues/3880；https://gitcode.com/cann/ops-transformer/issues/6643；https://gitcode.com/cann/ops-transformer/issues/6678；https://gitcode.com/cann/ops-transformer/issues/6634；https://gitcode.com/cann/ops-transformer/issues/6700

### TRN-0423 `ops_math_tiling_overflow_and_rank_guard_family` Tiling int64 溢出与 infershape rank 守卫缺失族

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / TileWithAxis/fatrelu_mul
- **原因行为**：tiling 乘积链缺 int64 溢出守卫、batchSize=前导维乘积无溢出保护；CeilDiv 空张量除 0/负回绕；infershape 无 rank 校验；rank=0 标量 tiles 超单缓冲容量 UB 越界写
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：极端 shape（乘积近 INT64_MAX）、空张量、rank<2 输入下：tiling 回绕致切分错乱、输出错值或越界写；rank=1 末维静默折半使输出 shape 错误；正常训练规模不触发
- **改进措施**：检测 2^63-1 邻域构造的溢出 UT（修复 PR 已含 RED→GREEN 3 例）；rank 0/1/未知秩 infershape UT 11 例。；修复 fatrelu_mul 修复 PR https://gitcode.com/cann/ops-nn/pull/12501 （open，含 UT 证据）；TileWithAxis 关联 PR https://gitcode.com/cann/ops-math/pull/6647 （open，未核实）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3874；https://gitcode.com/cann/ops-nn/issues/7274；https://gitcode.com/cann/ops-math/issues/3967

### TRN-0424 `ops_transformer_ffn_worker_batching_nullptr_ids_zero_output` FfnWorkerBatching 二级指针未填静默返回空批

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnFfnWorkerBatching Ff
- **原因行为**：FfnArea 的 expert_ids_buf/session_ids_buf/micro_batch_ids_buf/layer_ids_buf 四个二级指针未填 device 地址时，host/tiling 校验放行、两段返回 0，k
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：FFN worker 批处理算子在框架看不到内层缓冲的二级指针场景下静默产出空 token 批（actualTokenNum=0、空 groupList），接口成功返回；下游以为无活可干，训练 token 静默丢失或流水线空转。
- **改进措施**：检测 actualTokenNum 与预期 token 数对账；二级指针非空断言。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6670

### TRN-0425 `ops_math_replication_pad_negative_padding_device_fault` ReplicationPad 负 padding 设备侧 507035 假绿

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / ReplicationPad1d/2d/3d 负
- **原因行为**：op_api 的 SafePadSum() 明确实现负值裁剪语义并在 host 侧放行负 padding，但 FLOAT32/FLOAT16 负 padding 路径 kernel 存在缺陷：两段接口返回 0，aclrtSynchroniz
- **影响对象**：可用性/进度；数值结果（报错）
- **影响详情**：fp32/fp16 负 padding（裁剪，torch F.pad mode='replicate' 常用）在 A2 上作业崩溃于设备侧 507035，host 侧无拦截；三接口（1d/2d/3d）一致，复现 2/2。
- **改进措施**：检测 负 padding × dtype(fp32/fp16/int32) 矩阵回归；ASCEND_LAUNCH_BLOCKING=1 定位。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3878

### TRN-0426 `ops_transformer_nsa_compress_grad_overlap_nondeterministic` NsaCompressGrad overlap 输入梯度非确定违反默认确定性

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / aclnnNsaCompressGrad inpu
- **原因行为**：compressBlockSize>compressStride（overlap）时 inputGradOut 经原子累加，同输入重复 10 次几乎每次位模式都不同（8~9/9）；资料明确写「默认确定性实现」，实测冲突。
- **影响对象**：梯度；数值结果（不可复现）
- **影响详情**：compressBlockSize>compressStride（overlap）时 inputGradOut 每次运行不一样：同输入连跑 10 次几乎次次位模式不同；无 overlap（stride=64）0/9 全稳定。梯度对拍、数值验收、断点续训比对随机失败。
- **改进措施**：检测 同输入 10 次重复调用位模式比对（overlap vs 无 overlap 对照）。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6667

### TRN-0427 `ops_transformer_sla_kl_grad_metadata_numheads_boundary_delayed_aicpu` SLA KL Grad Metadata 边界头数假绿后异常

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / IndexerKLLossGradMetadata
- **原因行为**：A2 资料「numHeadsQ 仅支持 8/16/32/64」，取 1/7/128 时第一段不按 161002 拒绝而返回 0，第二段也返回 0，错误延迟到 aclrtSynchronizeStream 以 507018（AICPU 异常）
- **影响对象**：数值结果；可用性/进度（报错）
- **影响详情**：Lightning Indexer KL loss 反向 metadata 算子在不支持的头数下假绿：调用方拿到成功返回，metadata 未写（哨兵全残留），错误迟到同步点；训练在 loss 反向处崩或拿到未写 metadata。
- **改进措施**：检测 numHeadsQ 边界值（0/1/7/128/129）矩阵回归；metadata 预填哨兵校验写出。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6653

### TRN-0428 `ops_nn_bn_training_update_grad_kahan_determinism` BN 确定性归约跨核 1 ULP 偏差

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：算子/内核 / cann / bn_training_update_grad 跨
- **原因行为**：Phase2 确定性归约路径的跨核合并存在 1 ULP 偏差，修复 MR 改用 Kahan 累加消除（MR !12678，merged）。
- **影响对象**：梯度；数值结果（不可复现）
- **影响详情**：BN 训练梯度在确定性归约路径上存在 1 ULP 级跨核偏差：确定性对拍/双实现校验在该算子上随机失败，梯度值本身偏差有限。
- **改进措施**：检测 确定性归约路径 bit-exact 对拍（修复 MR 引入 Kahan 后消除）。；修复 修复 MR https://gitcode.com/cann/ops-nn/pull/12678 （merged，2026-10-24；发布版本未核实）。
- **来源**：https://gitcode.com/cann/ops-nn/pull/12678

### TRN-0431 `opsnn_deep_norm_meanout_rstdout_tail_dim_unchecked` DeepNorm meanOut/rstdOut 尾维形状不校验致越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnDeepNorm
- **原因行为**：aclnnDeepNorm 的校验（CheckDeepNormShapeValue）只校验 meanOut/rstdOut 的前导维与维数，不校验归约维（尾维）为 1；尾维非 1 或 0 时接口不报参数错误，仍继续执行输出写入。
- **影响对象**：数值结果；模型权重（静默错误）
- **影响详情**：meanOut=[3,1,2] 时只写 3/6；=[3,1,0] 时 0 元素声明仍被写入；mssanitizer 报 6 次 illegal write of size 4（DeepNorm_03_high_performance_18）。
- **改进措施**：检测 mssanitizer memcheck；出参形状变异扫描。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-nn/issues/7296

### TRN-0432 `opsmath_addlora_result_written_to_input_y` AddLora 结果写回输入 y 而 out 未写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnAddLora
- **原因行为**：kernel 结果写回输入 yGm_（add_lora_base.h:653），输出 youtputGm_ 仅有声明(:96)与绑定(:207)、无写回；310P 路径同样。
- **影响对象**：数值结果（静默错误）
- **影响详情**：两段返回 0：out[0] 保持金丝雀 7.0 未写，输入 y[0] 从 1.0 被改写为 257.0（结果正确值）；调用方读到未初始化内存。
- **改进措施**：检测 out 预填金丝雀 + 调用后校验输入 y 逐字节不变。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3902

### TRN-0433 `opsmath_isinf_tail_block_32b_oob_write` IsInf 尾块 32B 整块搬运越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnIsInf
- **原因行为**：尾块按 32 字节整块搬运，越过 out 的逻辑大小：numel=1（BOOL 1 字节）越界写 31 字节、numel=7/15 分别 25/17 字节，恰好写到 32B 边界；同形 aclnnIsNegInf 无此问题。
- **影响对象**：数值结果（静默错误）
- **影响详情**：out 逻辑区外被改写；mssanitizer 同 kernel 报 illegal read 28 / illegal write 31，与实测字节数吻合。
- **改进措施**：检测 out 缓冲预填哨兵统计越界改写；mssanitizer memcheck。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3925

### TRN-0434 `opsmath_all_uint8_truncates_not_bool` aclnnAll out=UINT8 输出数值截断非布尔真值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnAll
- **原因行为**：out dtype=UINT8（资料列为支持）时输出不是布尔真值 0/1，而是把 self 的数值截断成 UINT8 写入：[100,200,300,400]→[100,200,44,144]（300%256=44）。
- **影响对象**：数值结果（静默错误）
- **影响详情**：fp16[2x4] dim=0 归约：1..8→[1,2,3,4]，100..400→[100,200,44,144]，0.1..0.8→[0,0,0,0]；BOOL 出参正确 [1,1,1,1]。FLOAT/BF16/BOOL/INT32/INT64 等 self dtype 同样错，静默脏数据。
- **改进措施**：检测 out dtype 变异对照 BOOL vs UINT8，全非零输入结果必须全 1。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3963

### TRN-0436 `opsmath_randperm_dtype_boundary_whole_output_unwritten` Randperm n=dtype 上限输出整块未写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnRandperm
- **原因行为**：n 等于输出 dtype 上限值（INT8 128/UINT8 256/INT16 32768）时两段返回 0 但输出整块不写；n≤上限-1 全部正常，边界规律为 n==dtype_max+1 触发。
- **影响对象**：数值结果；训练样本流（静默错误）
- **影响详情**：INT8 n=128、UINT8 n=256、INT16 n=32768 均返回 0/0/0 且写入字节=0（预填 0xFF 全保留）；INT8 127、UINT8 255、INT16 32767、FP16 2049、BF16 257、FP32 5000 全部正确，缺陷值在资料声明支持面内。
- **改进措施**：检测 n 扫 dtype 边界 {max-1, max, max+1} + 金丝雀统计写入字节。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3911

### TRN-0438 `opstransformer_gbsa_metadata_maxqseqlen_mismatch_507018` BlockSparseAttnMetadata maxQSeqLen 设备错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / BlockSparseAttnMetadata
- **原因行为**：TND 下 maxQSeqLen 传非负但小于每 batch Q 存储长度时两段返回 0，kernel 以错误长度寻址，同步段报 507018 设备内存错误；资料允许该取值，校验缺失。
- **影响对象**：可用性/进度；数值结果（报错）
- **影响详情**：TND 下 maxQSeqLen 传非负但小于每 batch Q 存储长度时，两段均返回 0，同步报 507018 设备内存错误；传 -1 或 8（=每 batch 存储长度）则 0/0/0 且 metadata 头 magic 正常。batch=1、totalQBlocks=8 最小化仍复现。
- **改进措施**：检测 maxQSeqLen 扫 { -1, 1, 正确值 } 三点对照同步返回码。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6713

### TRN-0439 `opstransformer_gmm_v5_grouplist_last_value_unchecked` GroupedMatmulV5 groupList 末值越界不校验

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnGroupedMatmulV5
- **原因行为**：Tensor 版 groupList 末值不校验：V5/V4/V3/WeightNz 分支只查长度/dtype 后直接 return SUCCESS，末值≤x 第一维的约束只在 int-array 分支；末值>M 仍两段 0 并执行。
- **影响对象**：数值结果（静默错误）
- **影响详情**：groupList 末值 40>M=32 时 0/0 且输出被写出；kernel 按 groupList 取行区间越过 x 末行，同用例 memcheck 已见合法输入下 illegal read of size 256。
- **改进措施**：检测 groupList 末值变异扫描 + mssanitizer memcheck。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6708

### TRN-0440 `opsmath_randint_negative_from_bucket_shift` 整数随机 from<0 取值域整体右移一位

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / InplaceRandom/Uniform
- **原因行为**：整数 dtype 且 from<0 时取值域整体右移一位：from 桶计数 0、0 桶翻倍、均值抬高；多个整数 dtype 与 out-of-place 变体一致，负 from 未做映射修正。
- **影响对象**：数值结果；训练样本流（静默错误）
- **影响详情**：[-5,5) 采样 8192 次：from 桶 0、0 桶 1605（其余约 819）；[-1,0) 全部输出 0（期望全 -1）；均值 0.073 vs 期望 -0.50。
- **改进措施**：检测 from<0 直方图三桶对照（from 桶/0 桶/其余桶）+ 均值检验。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3910；https://gitcode.com/cann/ops-math/issues/3919

### TRN-0442 `opstransformer_dense_lightning_indexer_softmax_lse_bsnd_tail_unwritten` LightningIndexerSoftmaxLse BSND 尾部未写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / DenseLightningIndexer
- **原因行为**：BSND 分支在 actualSeqLengthsQuery[b]<S1 时不写 softmaxMaxOut/softmaxSumOut 尾部；同语义 TND 分支已补零，BSND 缺该行为。
- **影响对象**：数值结果（数值异常）
- **影响详情**：出参预填 NaN 后调用，尾部 8/16（asq=8）或 15/16（asq=1）元素保持 NaN；两段返回 0；TND 对照组正确补零。
- **改进措施**：检测 出参预填 NaN，对照 TND/BSND 两 layout 的尾部写入。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6711

### TRN-0443 `opsmath_cumsum_default_nondeterministic_bitpatterns` Cumsum 默认路径位模式非确定违反资料承诺

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnCumsum
- **原因行为**：默认确定性配置下同一输入连续 5 次执行输出 5 种位模式（FNV 哈希各不相同）；ACL_OPT_DETERMINISTIC=1 后 5 次同一哈希。资料约束写明「aclnnCumsum默认确定性实现」。
- **影响对象**：数值结果；数值结果（不可复现）
- **影响详情**：fp32[1024,8] dim=0 默认配置 5 次输出哈希 b336efea…/539fed0d…/e8a3a534…/3ed6d0f3…/7ef87852… 全不同；det=1 后 375ece58… ×5。
- **改进措施**：检测 同输入重复执行哈希比对（≥5 次）；确定性开关对照。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3907；https://gitcode.com/cann/ops-math/issues/3908

### TRN-0444 `op_plugin_foreach_noncontig_view_silent_noop_training` torch_npu _foreach_ 非连续视图静默不生效（训练侧）

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / torch_npu / _foreach_* 快路径门控
- **原因行为**：foreach 快路径门控只检查 is_non_overlapping_and_dense、不检查连续性，转置等非连续视图穿透进入 aclnn 快路径后就地加法静默不执行；修复 MR 收紧门控为非连续走慢路径。
- **影响对象**：模型权重；优化器状态（静默错误）
- **影响详情**：_foreach_add_ 对转置张量无报错、存储不变、maxabs 3.38；下游 fused 优化器/AMP 对非连续权重视图的更新静默丢失（权重冻结）；三芯逐位同错。
- **改进措施**：检测 非连续视图 foreach 前后 allclose 断言；95 格矩阵探针（修复 PR 附带 probe_foreach_nc.py）。；修复 修复 PR https://gitcode.com/Ascend/op-plugin/merge_requests/6099 （open，未合入）：门控加 is_contiguous 合取，非连续走上游慢路径；三芯验证 17/19 成员转置列转绿。
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/640；https://gitcode.com/Ascend/op-plugin/merge_requests/6099
- **关联**：cross:INF-2169

### TRN-0445 `op_plugin_sdpa_bool_mask_full_masked_row_uniform` SDPA bool 掩码全遮行输出均匀分布而非 0

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / torch_npu / SDPA bool 融合 kernel
- **原因行为**：bool 融合 kernel 对整行 max=-inf 做 clamp，softmax 退化为对该行 key 的均匀分布（≈v.mean）；CPU 语义为输出全 0 行。
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：bool attn_mask 有全遮 query 行（padding 等）时，NPU 该行输出非零实值＝对该行 key 的均匀 softmax（v.mean，allclose 5.96e-08），CPU 为全 0 行；加性 -inf 掩码遮 query 行两端一致全 0，仅 bool 路径受影响。
- **改进措施**：检测 构造全遮 query 行四象限对照（bool/additive × query/key）。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/642
- **关联**：cross:INF-2190

### TRN-0446 `opsmath_divmod_double_mode01_fp32_downgrade` DivMod DOUBLE mode=0/1 静默降级 FP32 计算

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：算子/内核 / cann / aclnnDivMod
- **原因行为**：CompatibleInferDivModeDtype 只有 FLOOR 分支保留 DOUBLE，mode=0/1 落入不含 DOUBLE 的白名单降到 DT_FLOAT：DOUBLE 输入被降级 FP32 计算，无报错。
- **影响对象**：数值结果（静默错误）
- **影响详情**：mode=0/1 时 1/3 输出 0.33333334（fp32 值）而非双精度 0.33333333333333331，与 fp32 结果逐位相同、与 fp64 差 1e-8 量级；同一接口 mode=2（floor）时 DOUBLE 结果正确。
- **改进措施**：检测 非整除用例（如 1/3）与 fp64 参考对拍；同一接口跨 mode 对比。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-math/issues/3946

### TRN-0454 `groupnorm_fp32_illconditioned_rstd_nan` GroupNorm 族 fp32 病态输入 rstd 抵消致整块 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：算子/内核 / cann / GroupNorm/GroupNormSilu
- **原因行为**：fp32 下组内方差远小于均值平方时，方差计算灾难性抵消成负或 0，rstdOut 变 NaN 或 1/sqrt(eps)，out 整块 NaN，两段接口返回 0 无错误码。
- **影响对象**：数值结果；隐状态；训练信号（数值异常）
- **影响详情**：合法 fp32 输入（如 x=1000±0.01，满足资料全部约束）下 GroupNorm/GroupNormSilu 输出整块 NaN 且无任何报错；同形状良态输入正常，激活分布漂移到病态区间即静默产出 NaN。
- **改进措施**：检测 监控 norm 层 mean²/var 比与输出 NaN；上游用例（50±0.001、1000±0.01）可作探针；修复 待定（#7334/#7347 均 open，未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7334；https://gitcode.com/cann/ops-nn/issues/7347
- **关联**：cross:INF-2203

### TRN-0455 `batchnorm_extreme_numeric_accuracy` BatchNormExt2/BN3D 极端数值三精度缺陷

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：算子/内核 / cann / BatchNormExt2、BN3DUpdate
- **原因行为**：三缺陷：rstd 中间量 v∈(8.5e37,3.4e38] 下 denormal 被 FTZ 清零；Welford 归约 x 与 mean 相等（含 ±inf）时 NaN 污染累加；BN3D 方差直接相减量级接近时抵消放大。
- **影响对象**：数值结果；隐状态；训练信号（静默错误）
- **影响详情**：极端数值输入下 BN 前向/训练更新精度崩坏：rstd 清零后输出 y 精确等于 offset；inf 输入把 NaN 写进滚动统计扩散到后续 batch；方差抵消使更新结果与 golden 不一致。无报错。
- **改进措施**：检测 BN 输出 golden 对拍覆盖 var+eps∈(8.5e37,3.4e38]、x==mean（含 ±inf）、square_sum≈(sum/num)² 三类输入；修复 修复 MR https://gitcode.com/cann/ops-nn/pull/12611 已 merged（2026-10-26，随 ops-nn 后续发布，版本未核实）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7314；https://gitcode.com/cann/ops-nn/pull/12611

### TRN-0456 `inplace_adagrad_v2_tail_accum_and_tiling_overflow` AdagradV2 尾块 accum 错值与 tiling 溢出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：算子/内核 / cann / InplaceApplyAdagradV2
- **原因行为**：kernel 端 accum UB 搬运用裸三参 DataCopy（按 32B 向下取整），numel%8≠0 时尾部元素被丢弃、回写取到错误数据；tiling 端 coreNum 计算另有有符号乘法溢出。
- **影响对象**：优化器状态；训练轨迹（静默错误）
- **影响详情**：参数元素数非 8 对齐时 accum（二阶矩）输出尾部 numel%8 个元素为错值（135/135 用例零例外，var 输出恒正确），单元素张量即触发；优化器状态静默错位后训练轨迹偏离。
- **改进措施**：检测 对 numel%8≠0 参数检查 accum 尾部与 golden；TTK/GEIR 双通路失败集逐名一致可定位 kernel；修复 待定（issue 给出修复方案：搬运长度向上取整到 32B、按真实长度回写；未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7427；https://gitcode.com/cann/ops-nn/issues/7428；https://gitcode.com/cann/ops-nn/merge_requests/12905

### TRN-0458 `block_sparse_mask_offset_uint32_wrap` BlockSparseAttention 超大掩码偏移回绕错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：算子/内核 / cann / block_sparse 偏移计算
- **原因行为**：超大 blockSparseMask 时偏移计算使用 32 位整型，掩码规模使偏移超过 2^32 后按模回绕，掩码索引错位、注意力输出精度劣化；修复 MR 提升整型宽度。
- **影响对象**：数值结果（静默错误）
- **影响详情**：超长序列/超大稀疏块掩码下 block_sparse_attention 输出精度劣化，无报错；训练使用长序列稀疏注意力时前向/反向静默错。
- **改进措施**：检测 大掩码 shape 与 golden 对拍；监控偏移量是否接近 2^32；修复 修复 MR https://gitcode.com/cann/ops-transformer/merge_requests/14632 （open 未合入，对应 issue #6766）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6766；https://gitcode.com/cann/ops-transformer/merge_requests/14632
- **关联**：cross:INF-2197

### TRN-0459 `acos_grad_tiling_dtype_check_and_wraparound` acos_grad tiling 混 dtype 错读与块参数回绕

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：算子/内核 / cann / acos_grad tiling（arch35）
- **原因行为**：tiling 只校验输入 y 的 dtype，dy/z 一致性未校验，kernel 按 y 的模板类型解引用 dy/z，混合 dtype 错读；块参数先运算后窄化 uint32，超大 shape 回绕只覆盖前 512 元素。
- **影响对象**：梯度（静默错误）
- **影响详情**：y=fp32、dy=fp16 的 AcosGrad 被静默放行产出错梯度；元素总数 ~2^41 量级时只算前 512 个元素其余保持旧值，均无报错。同族 asin_grad 已正确校验且全程 int64 可对照。
- **改进措施**：检测 对 dy/z dtype 组合与超大 totalLength 构造负例校验 tiling 拒绝；对照 asin_grad；修复 待定（建议对齐 asin_grad：校验 dtype 一致、块参数全程 int64 并校验值域，未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-math/issues/4085；https://gitcode.com/cann/ops-math/issues/4087；https://gitcode.com/cann/ops-math/merge_requests/6747
- **关联**：cross:INF-2201

### TRN-0474 `ascend_pytorch_scatter_add_race_loss` aclnnScatterAdd 多对一累加偶发丢失贡献

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / torch_npu / aclnnScatterAdd 多对一累加
- **原因行为**：NPU 上 Tensor.scatter_add_（aclnnScatterAdd）在多对一冲突写时偶发输出错误：固定种子输入多数运行通过、偶发失败（66519 用例 1 次）；根因为推断，竞态类最可能、设备级偶发计算错误次之，待复现确认。
- **影响对象**：梯度；数值结果（不可复现）
- **影响详情**：Embedding grad_sample 偶发整行 15 维偏差 0.0405，超容差约 400 倍，远超 ~1e-6 的累加顺序差；算子日志无 ERROR。触发：A3/CANN 9.2.0/torch_npu 77169f23 的 scatter_add_ 多对一冲突写，并发关联未证实。
- **改进措施**：检测 固定种子循环跑 per-sample 梯度对照（batch=1 循环 vs 整 batch）统计失败率；线上可对 embedding 梯度行做和校验；修复 待定（issue open 2026-10-27；CI 偶发 1/66519，未定位到算子提交）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5667

### TRN-0475 `opstransformer_block_attn_res_prepare_subnormal_nan` BlockAttnResPrepare eps 次正规数时输出全 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / aclnnBlockAttnResPrepare
- **原因行为**：eps 为 fp32 次正规数（0<eps<1.17549435e-38）且 blockRes 全 0（均合法、通过第一段校验）时三个输出全 NaN、两段返回 0；eps 下溢为 0 时第一段不报 161002 而 workspaceS
- **影响对象**：数值结果；隐状态（数值异常）
- **影响详情**：0<eps<fp32 最小正规数时输出静默全 NaN（实测 1.1e-38/1e-40/1e-45 三档均 NaN、1.2e-38 正常），ACLNN_SUCCESS 返回，NaN 沿下游 softmax/残差扩散。
- **改进措施**：检测 eps 接近 1e-38 的调用点对输出做 NaN 断言；两段返回 0 不代表输出正确；修复 待定（issue open 2026-10-27，master 2026-10-23 版本仍含此实现）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6785
- **关联**：cross:INF-2221

### TRN-0476 `opstransformer_fcel_vocab0_ub_overlap` FusedCEWithMaxSum 词表维 V=0 静默错值

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / fused_ce_with_max_sum
- **原因行为**：V=0 时 InitParams 的 else 分支只申请 sumExpLogits/predictedLogits 的 UB buffer、漏申请 logitsMax；BtCompute 仍无条件 GMToUB 搬 logitsMax
- **影响对象**：训练信号（静默错误）
- **影响详情**：V=0 时 lossOut = ln(logitsMax) - predictedLogits：实测 ln(0.5)-0.25=-0.943 而非期望 ln(2.0)-0.25=0.443（logitsMax 数值被当 sumExpLogits 用）；两段均返回 0，无告警。
- **改进措施**：检测 词表维为 0 的分片（VP 空分片）对 lossOut 抽查与解析公式对照；修复 待定（issue open 2026-10-27；第一段应返回 161002 或修 UB 分配）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7446；https://gitcode.com/cann/ops-nn/pull/13086；https://gitcode.com/cann/ops-nn/issues/7447

### TRN-0480 `opsmath_pdist_p_inf_all_nan_legacy_tbe` aclnnPdist p=+inf 返回 0 输出全 NaN（legacy 

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / pdist legacy TBE 内核
- **原因行为**：A2+CANN 9.2.0 只带 ops_legacy/pdist 旧 TBE 实现：pdist_sum_process 用 ln(sum)*(1/p) 收尾，p=+inf 时 1/inf=0、ln(sum)=inf
- **影响对象**：数值结果（数值异常）
- **影响详情**：p=+inf（切比雪夫距离，资料声明值域 [0,+∞] 内的合法语义）时 out 全 NaN、两段返回 0 无任何报错/日志；同输入 p=2 结果正确。NaN 向聚类/异常检测/loss 下游扩散。
- **改进措施**：检测 p=inf 调用后对 out 做 NaN 断言；torch_npu 2.14 交叉验证同现象；修复 待定（master AscendC 内核 ReduceMax 分档已存在，未随 9.2.0 发布到 A2；issue open 2026-10-27）
- **来源**：https://gitcode.com/cann/ops-math/issues/4104

### TRN-0481 `opsmath_floor_divides_int_float_silent_precision_loss` InplaceFloorDivides 整型配浮点标量静默降精度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / aclnn_floor_divide dtyp。
- **原因行为**：InferFloorDivTensorScalarDtype 在非 RegBase 平台返回 PromoteType(int,fp32)=fp32；CalcFloorDivides 先把整型输入 Cast 到 fp32（大整数降精度）、
- **影响对象**：数值结果（静默错误）
- **影响详情**：整型张量 floor_divide 浮点标量：int32 ±1 偏差、int64 偏差最大 89478485（相对 2^-25，恰落 fp32 表示精度）；同值整型标量精确。PyTorch CPU 对该组合抛 RuntimeError 前置拒绝，NPU 选择接受并降精度；两段返回 0 无告警。
- **改进措施**：检测 整型输入配浮点标量的 floor_divide 输出与整数下取整参考对照（|err| 检查）；修复 待定（issue open 2026-10-27；建议对齐 CPU 前置拒绝或按整型精度计算）
- **来源**：https://gitcode.com/cann/ops-math/issues/4123

### TRN-0482 `opsmath_pdist_forward_tail_oob_write` PdistForward 出参非 32B 对齐尾部越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / pdist_forward 尾块搬运
- **原因行为**：aclnnPdistForward 在出参字节数非 32B 对齐时尾部越界写（最多 20 字节），写坏 out 之后分配的内存；无报错。
- **影响对象**：数值结果（静默错误）
- **影响详情**：out 尾元素数使总字节数非 32B 对齐时，越界写最多 20 字节——静默破坏 out 之后分配的张量数据；无报错。
- **改进措施**：检测 out 缓冲后放置 canary 张量对比；非 32B 对齐 out 案例对照 CPU；修复 待定（issue open 2026-10-27，详情以正文为准）
- **来源**：https://gitcode.com/cann/ops-math/issues/4106

### TRN-0483 `opsmath_round_decimals_int_negative_wrong` InplaceRoundDecimals 整型负 decimals 结果错误

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / round_decimals 整型通路
- **原因行为**：aclnnInplaceRoundDecimals 在整数 dtype+负 decimals 下未按四舍五入到指定位数执行：INT32 通路忽略 decimals（输出恒等），INT64 通路输出不等于恒等/截断/半偶舍入且正负不对称。
- **影响对象**：数值结果（静默错误）
- **影响详情**：整型输入配负 decimals 的原地 round 结果静默错误：int32 恒等（该舍入的没舍）、int64 错值且正负不对称；无报错。
- **改进措施**：检测 整型+负 decimals 组合与 Python round 参考对照；修复 待定（issue open 2026-10-27）
- **来源**：https://gitcode.com/cann/ops-math/issues/4121

### TRN-0486 `opstransformer_pfa_310p3_fp16_o_acc_overflow` PFA 310P3 fp16 高性能模式 O 累加溢出 +Inf

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / prompt_flash_attention。
- **原因行为**：fp16+HighPerformance 下 mmOutputType/computeType 为 half，O 累加（未归一化加权和）超 FP16 上限 65504 溢出为 +Inf（实测 position 1871 处 1872×3
- **影响对象**：数值结果；梯度（数值异常）
- **影响详情**：长序列（累加元素数×幅值超 65504）时 O 输出 +Inf，经 softmax 归一化扩散为 NaN/错值；无报错。
- **改进措施**：检测 fp16 高性能模式 + 长序列时对 O 输出 Inf/NaN 断言；修复 修复 PR https://gitcode.com/cann/ops-transformer/merge_requests/14683（open，2026-10-27）——新增 oAccType：非 MSD 且 T==half 时为 float；O 累加迁 FP32 独立缓冲（oAccBuff_/oAccTmpF_），补两处 seed 与输出 cast，tiling 两处 UB 预算新增
- **来源**：https://gitcode.com/cann/ops-transformer/merge_requests/14683

### TRN-0487 `op_plugin_oob_index_family_no_indexerror` op-plugin 越界索引族无 IndexError 静默丢/污染

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / torch_npu / index_put_/embedding/ga。
- **原因行为**：越界索引在 torch 语义应抛 IndexError；NPU 全芯全族无一例同型抛错——写侧 index_put_(idx=99) 在 950PR/2.9.1 无异常且载荷凭空消失（哨兵 20/20 未触）
- **影响对象**：数值结果；训练样本流（静默错误）
- **影响详情**：用户常见笔误（索引越界）在 2.9.1（950PR）上=写侧载荷静默丢失，读侧=静默读回表外内存实值/静默零/张量内错位值；2.7.1 附加 index_select 设备死；embedding 越界三芯一致 NO-RAISED 返回表外实值；语法糖路径不受影响。
- **改进措施**：检测 数据管线入口对 index 做 min/max 断言（CPU/NPU 行为分叉）；embedding 输出抽样与权重行对照；修复 待定（issue open 2026-10-27，三芯×六变体证据矩阵；修复方向=API 路径对齐语法糖的边界检查）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/651
- **关联**：cross:INF-2219

### TRN-0488 `op_plugin_maxpool_indices_int8_wraparound` max_pool indices int8 三芯分裂环绕溢出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / torch_npu / max_pool1d/2d indices d。
- **原因行为**：max_pool1d/2d(return_indices=True) indices dtype 三芯分裂：CPU 契约 int64、950PR/2.9.1 int32、2.7.1 双芯 int8。
- **影响对象**：数值结果（静默错误）
- **影响详情**：2.7.1 双芯 64×64 输入 kernel2 下负索引 512/8320（6.2%，双芯 log 逐字一致）；224×224 输入几乎全部索引损坏；indices 是公开契约输出，检测头反查/特征定位拿到负索引引发错位或越界读，全程无报错。
- **改进措施**：检测 indices dtype 与 CPU 对照断言（int64）；大输入负索引计数；修复 A5 修复 PR https://gitcode.com/Ascend/op-plugin/merge_requests/6104（open，2026-10-27）——Ascend950 max_pool1d/2d indices 改 int64（前向 values/indices/反向梯度与 CPU 一致验证）；A2/A3 维持 int32、2.7.1 int8 未覆盖；同源 A5 issue #647
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/652；https://gitcode.com/Ascend/op-plugin/issues/647；https://gitcode.com/Ascend/op-plugin/merge_requests/6104
- **关联**：cross:INF-2220

### TRN-0490 `opsmath_sinc_subnormal_nan` sinc 算子 subnormal 输入产生 NaN 输出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / sinc SIMT kernel
- **原因行为**：950PR SIMT kernel（SincSimtCompute）原实现只对 x==0.0f 输出 1；当 |x| < 2^-126/π 时 PI*x 下溢为 fp32 次正规数
- **影响对象**：数值结果（数值异常）
- **影响详情**：接近 0 的次正规输入（|x|<2^-126/π）得到 NaN 而非 1.0；无报错，NaN 沿下游扩散。
- **改进措施**：检测 sinc 输出 NaN 断言（输入含极小值时）；修复 已修复：https://gitcode.com/cann/ops-math/pull/6625（关联 PR；issue #4096 已 closed，2026-10-27）
- **来源**：https://gitcode.com/cann/ops-math/issues/4096；https://gitcode.com/cann/ops-math/pull/6625

### TRN-0491 `opsmath_xlog1py_precision_uninit_const` xlog1py 精度问题与 constantValue 未初始化

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / xlog1py kernel
- **原因行为**：ops-math xlog1py 算子存在精度问题与 constantValue 未初始化问题（修复 PR 自述勾选 Bug 修复；细节未在正文展开）。
- **影响对象**：数值结果（静默错误）
- **影响详情**：xlog1py 输出精度偏差；constantValue 未初始化意味着特定路径下参与计算的常量可能是未定义值——静默错值风险。
- **改进措施**：检测 xlog1py 输出与 libm 参考对照（边界输入区）；修复 修复 PR https://gitcode.com/cann/ops-math/merge_requests/6723（open，2026-10-27）——修复精度问题与 constantValue 未初始化；细节未在 PR 正文展开
- **来源**：https://gitcode.com/cann/ops-math/merge_requests/6723

### TRN-0492 `opsmath_remainder_fractal_nz_silent_accept` Remainder 静默接受 FRACTAL_NZ 按 ND 解释

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / cann / remainder 格式校验
- **原因行为**：aclnnRemainderTensorTensor 资料声明「数据格式支持 ND」，实测 FRACTAL_NZ 被静默接受并按 ND 线性解释——NZ 分块布局内存被线性读取，输出系统性错值。
- **影响对象**：数值结果（静默错误）
- **影响详情**：NPU 上向 aclnnRemainderTensorTensor 传入 FRACTAL_NZ 布局张量时不报错不拒绝，接口返回成功，但分块布局内存被按 ND 线性语义解释计算，输出系统性错值；文档声明仅支持 ND，与实现分叉。
- **改进措施**：检测 NZ 布局输入的输出与稠密参考对照；调用前显式断言 format==ND；修复 待定（issue open 2026-10-27，Documentation 类但实测行为缺陷：要么校验拒绝要么文档声明支持）
- **来源**：https://gitcode.com/cann/ops-math/issues/4114；https://gitcode.com/cann/ops-math/issues/4126

### TRN-0493 `op_plugin_stft_gelu_error_over_budget` conv/Stft 融合内核近似致 gelu/stft 误差超预算

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：算子/内核 / torch_npu / conv/Stft 融合内核近似
- **原因行为**：op-plugin conv/Stft 融合内核采用近似实现，gelu→stft 级联累计误差超预算；eager 纯 stft 主路径 72/72 PASS（maxabs≤2.67e-05）不受影响。
- **影响对象**：数值结果（静默错误）
- **影响详情**：gelu/stft 级联输出误差超出容差预算，音频/谱特征类训练特征值偏差；无 crash。
- **改进措施**：检测 gelu→stft 链路输出与 CPU 参考逐点误差监控；修复 待定（issue open 2026-10-27，与 !6097（stft eager 注册+组合内核）关系为「正交」；数值策略待上游定夺）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/649

### TRN-0500 `trl_chunked_logprob_support_underflow_inf_grad` TRL chunked logprob 支持集远低于最大 logit 时下溢

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：算子/内核 / trl / ChunkedLogProbFunction
- **原因行为**：support_ids 的 support_sum_exp 相对全词表行最大值累加；support 全部远低于行最大值时 exp(z-max) 在 fp32 下溢为 0，log 项成 -inf。
- **影响对象**：训练信号；梯度（数值异常）
- **影响详情**：行内 support 全部远低于最高 logit（约 90+）时该行 logprob 输出 0.0 而非正确值（如 -log2=-0.6931），weight.grad 含 -inf/nan；梯度按全行累加，单行即污染整个 LM 头梯度。
- **改进措施**：检测 对 support_ids 输入统计 support 内最大 logit 与全词表最大值差距；监控 fused LM head 梯度 finite 检查；修复 修复 PR https://github.com/huggingface/trl/pull/7983（open，2026-10-28）——track 支持的最大值？以 issue 正文与 PR 标题 Track the support maximum in the chunked log-prob kernel 判定，状态 open 未合入，细节未逐行核
- **来源**：https://github.com/huggingface/trl/issues/7982；https://github.com/huggingface/trl/pull/7983
- **关联**：var:TRN-0451

### TRN-0501 `opsmath_fmod_remainder_large_magnitude_collapse` CANN fmod/remainder 大数值域结果塌 0 或 -inf

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：算子/内核 / cann / Fmod/Remainder 标量核
- **原因行为**：fp32/bf16/int32 路径大数值域精度塌陷：|self| 约 2^24 起出错、≥2^25 整片塌 0；other 极小时返回 -inf。fp16/int64/double 正确，910B 走 ops_legacy 内置实现。
- **影响对象**：数值结果（静默错误）
- **影响详情**：fmod 是 IEEE-754 精确运算，|self|≥2^25 后结果全 0（期望交替 2/1）；16128 点阶梯扫描 other=3 失败 10068、other=5 失败 11883；x=1e30/other=1e-20 返回 -inf 违反 |out|<|other| 与符号不变量。
- **改进措施**：检测 对含大数值取模的算子输出与 CPU torch.fmod/remainder 对照（2 的幂×小 other 是敏感探针）；修复 待定（两 issue 均 open；remainder 侧 ops-math 仓库 floor_mod 的 SUPPORT_COMPUTE_UNIT 不含 ascend910b，缺陷在 CANN 内置 ops_legacy 交付路径，仓库源码修复不覆盖 A2）
- **来源**：https://gitcode.com/cann/ops-math/issues/4181；https://gitcode.com/cann/ops-math/issues/4006

### TRN-0502 `opstransformer_dense_lightning_kl_grad_ws_overflow` Lightning Indexer KL 反向 workspace 越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：算子/内核 / cann / KL loss 反向 workspace 尺寸
- **原因行为**：第一段返回的 workspaceSize 小于 kernel 实际用量，kernel 写到 workspace 之外；越界写无报错（两段接口与同步均返回 0）。
- **影响对象**：数值结果；模型权重（静默错误）
- **影响详情**：B=1 S2=5 实测越界写 96 字节（首个偏移 32，连续 3 次一致）；越界量与 S2/B 相关：S2=1→28B、S2=2→56B、S2=5→140B（B=3），S2=8（8 对齐）→0B；mssanitizer memcheck 同配置报 GM 越界写命中本算子。
- **改进措施**：检测 按 workspaceSize+4096 分配、尾部预填 0x5A 哨兵执行后回读（issue 附 C++ 一键复现）；mssanitizer --tool=memcheck；修复 待定（issue open 2026-10-28；触发量与 S2/B 相关、S2 8 对齐时不越界——短期可按对齐规避，未核实）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6847
- **关联**：var:TRN-0377

### TRN-0503 `opsnn_bn_training_update_v2_ftz_subnormal_nan` BNTrainingUpdateV2 次正规域 FTZ 输出 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：算子/内核 / cann / BN 更新 arch35 预计算
- **原因行为**：arch35 预计算原生 vsqrt 把次正规方差 flush 为 0（multiplier=inf、addend=NaN）、vdiv 把次正规商 flush 为 0（y=inf×0=NaN）；IEEE 参考给有限值或 ±inf。
- **影响对象**：数值结果；梯度（数值异常）
- **影响详情**：次正规域（batch_variance≈6.53e-40、商≈1e-39~1.5e-40）y 输出全 NaN，ttk 报 NaN/Inf mismatch；L0_045/L1_505 seed=1234 稳定复现，L1_154 数据依赖偶发（随机 square_sum 落点决定商是否入次正规区）。
- **改进措施**：检测 ttk kernel 通路 seed=1234 跑 L0_045（稳定复现）；对 batch_variance 分布做次正规域检查；修复 修复 PR https://gitcode.com/cann/ops-nn/merge_requests/12961 已 merged（2026-10-29T07:13Z 批次快照）：sqrt/div 关闭 FTZ 消除次正规域 NaN/Inf，48/48 PASS→已合入，发布状态未核实
- **来源**：https://gitcode.com/cann/ops-nn/issues/7578；https://gitcode.com/cann/ops-nn/merge_requests/12961

### TRN-0514 `verl_fused_kernels_skip_lm_head_logit_scaling` verl fused kernel 丢 lm_head logit 缩放

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / verl / fused 线性 CE 路径
- **原因行为**：use_fused_kernels=True 时绕过 CausalLM.forward，取 pre-lm_head hidden states 与 lm_head.weight 直接调融合核，不执行模型自带的 logit 缩放/bias
- **影响对象**：输出分布；训练信号（静默错误）
- **影响详情**：Granite（logits_scaling 3~16×）/Cohere（logit_scale 0.0625~0.8333）/Falcon-H1（1/25.6~1/51.2）等家族的 logprob、PPO/GRPO loss 与 KL 全部按错误尺度的 logits 计算，无报错
- **改进措施**：检测 对比 fused 与非 fused 路径的 logprob/loss；检查模型 config 中 logits_scaling/logit_scale/lm_head_multiplier 是否非默认；修复 修复 PR https://github.com/verl-project/verl/pull/8441（open，未合入）：把缩放因子折进 fused 核的 temperature 并拒绝带 lm_head.bias 的模型
- **来源**：https://github.com/verl-project/verl/pull/8441

### TRN-0517 `meg_te_fused_mlp_ignores_clamp_options` Megatron TE 融合 MLP 静默忽略 SwiGLU clamp 配置

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / megatron-lm / TEFusedMLP 系激活构造
- **原因行为**：TEFusedMLP/GroupedLinear/FusedSharedExpertMLP 构造激活时不读 clamp 选项，配置了 clamp 也静默按普通 SwiGLU 运行
- **影响对象**：数值结果；训练轨迹（静默错误）
- **影响详情**：DeepSeek-V4（clamp=c 的 silu(min(g,c))*clamp(u,±c)）与 Kimi-K3 SiTU-GLU 配置在三个融合类下输出与参考实现不同，模型 MoE/MLP 输出错且训练不报错；routed experts 路径行为正确
- **改进措施**：检测 对融合与非融合路径做同权重数值对比；检查模型输出 vs transformers 参考实现；修复 修复 PR https://github.com/NVIDIA/Megatron-LM/pull/8640（open，未合入）：TEFusedMLP/GroupedLinear 用 TE clamped SwiGLU 算子，三类对 SiTU-GLU 显式 raise ValueError
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/8640

### TRN-0518 `op_plugin_batch_norm_inference_saved_stats_uninitialized` torch_npu BN 推理保存量未初始化污染 backward

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-30

- **原因对象**：算子/内核 / torch_npu / native_batch_norm 保存量
- **原因行为**：推理模式保存量值未按 mean/rstd 填充；no_stats 未注册 NPU 内核走 CPU 回退返回 rstd，而 NPU backward 按 variance 消费
- **影响对象**：梯度（静默错误）
- **影响详情**：混合精度/推理态 BN 前向后接反向时梯度数值错误；修复前 8 项保存量检查全失败（fp16/fp32 × default/out × JIT 两设置）
- **改进措施**：检测 对 BN 前向保存量与 running_mean/rsqrt(running_var+eps) 对拍；CPU 参考对比梯度；修复 见 issue 修改方案（ACL/OpAPI 推理调用后填充保存量、低精度 fp32 中间计算、新增 no_stats NPU 内核并拒绝 training=True 以外的推理请求）；op-plugin 原生回归 20/20、torch-npu 严格编译回归 42/42 通过（issue 报告，未见独立修复 PR 链接）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/661
- **关联**：var:TRN-0149

### TRN-0519 `fast_gelu_grad_fp32_large_input_nan` CANN FastGeluGrad fp32 大有限输入返回 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / fast_gelu_grad arch35
- **原因行为**：arch35 反向实现先算 -1.702*x 再乘 sigmoid(x)-1，有限 fp32 输入接近最大值时中间量上溢 ±Inf，0*Inf 得 NaN，而该处导数数学上仍有限可表示
- **影响对象**：梯度（数值异常）
- **影响详情**：x=±finfo(float32).max、dy=1 时输出 NaN（参考值 1/0）；331 元素实测 150 个数值不符；训练梯度被 NaN 污染
- **改进措施**：检测 对激活值大的样本监控梯度 NaN；golden 对拍（golden.py 同样运算顺序会漏检，需修 golden）；修复 修复 PR https://gitcode.com/cann/ops-nn/pull/13091（open）：先形成有界乘积 s*(s-1) 再乘有限 x 和 -1.702，并同步修 golden 与 UT 生成顺序；修复树 96 用例通过（报告者验证）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7727；https://gitcode.com/cann/ops-nn/pull/13091

### TRN-0521 `aclnn_rsub_int64_alpha_int32_narrowing` CANN Rsub int64 alpha 窄化丢系数

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / aclnnRsub IsScalarOne 判等
- **原因行为**：IsScalarOne 对整型 alpha 用 ToInt32()==1 判等，ACL_INT64 alpha 数值超 int32 范围但低 32 位恰为 1 时返回 true，算子走快路径丢弃 alpha，输出塌成 other-self
- **影响对象**：数值结果（静默错误）
- **影响详情**：误差量级 self_i*(alpha-1)，实测 1.29e11；A2 910B2、CANN 9.2.0、ops-math 1b415030
- **改进措施**：检测 int64 alpha 大值调用后与参考对比；扫描调用侧 alpha 来源；修复 待定（issue open；同文件 #4247 Rsubs 变体同病，待修）
- **来源**：https://gitcode.com/cann/ops-math/issues/4254；https://gitcode.com/cann/ops-math/issues/4247
- **关联**：cross:INF-2277

### TRN-0524 `gelu_mul_noncontiguous_out_silent_wrong_write` GeluMul 非连续 out 静默错写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / gelu_mul 输出布局处理
- **原因行为**：aclnnGeluMul 的 out 传非连续 Tensor（资料声明不支持）时不拒绝也不转换，kernel 按连续布局写入，调用方按自己的 stride 读回错位值；两段接口均返回 0
- **影响对象**：数值结果（静默错误）
- **影响详情**：out stride=[16,2] 时 max|diff|=1.556（strided[1]=contig[2]、strided[2]=contig[4] 模式对上）；Ascend910B3、CANN 9.2.0
- **改进措施**：检测 以非连续 out 调用后按原 stride 读回与连续基线对比；修复 待定（issue open：期望第一段 161002 或先转连续；当前行为是两者之外最差的第三种）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7668
- **关联**：cross:INF-2261

### TRN-0529 `fa_score_v4_undeclared_attr_silent_default` FA Score V4 未声明属性静默默认

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / FA ScoreV4 参数校验
- **原因行为**：sparseMode=-1、innerPrecise=3 等未声明值第一段返回 0 不拒绝，-1 按 dense 执行、3 按默认处理，输出与调用意图不符
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：传错/越界属性值时注意力按默认语义静默执行：稀疏模式意图不生效（-1→dense）、精度模式不生效（3→默认），结果无报错但与调用意图不同；Ascend950PR、CANN 9.2.0-beta.2
- **改进措施**：检测 对非法属性值探针调用（sparseMode=7 应 161001）验证校验链路；比对预期稀疏/精度行为；修复 待定（issue open，期望第一段返回 161002）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6879

### TRN-0533 `ops_math_std_mean_correction_zero_var_inf` CANN StdMeanCorrection 零方差返 Inf

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / StdMeanCorrection 零方差分支
- **原因行为**：N<=correction 且归约段方差为 0 时 stdOut 返回 +Inf；资料公式与 PyTorch 同输入均为 NaN（0/0 语义），算子把 0/0 处理成 +Inf
- **影响对象**：数值结果（数值异常）
- **影响详情**：N<=correction 且方差为 0 的归约段输出 +Inf 而非 NaN；下游把 Inf 当有效值继续算，符号语义错（NaN 可被 isnan 捕获、Inf 会静默传播）
- **改进措施**：检测 构造 N=1/correction=0 方差 0 用例对拍 torch.std；修复 待定（issue open）
- **来源**：https://gitcode.com/cann/ops-math/issues/4246

### TRN-0534 `reduce_mean_leaves_vector_mask_register_dirty` ReduceMean 残留 VECTOR_MASK 污染后核

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / ReduceMean high_precision
- **原因行为**：4 个 high_precision aiv kernel 结束后不复位 VECTOR_MASK 寄存器（残留 1/16/0），后续复用该 core 的 kernel 其余 lane 被屏蔽
- **影响对象**：数值结果（静默错误）
- **影响详情**：msSanitizer memcheck 每个变体稳定检出（910B3、CANN 9.2.0、master ebc07f7b9）；同仓 #4223/#4201 同型已两单，疑族级问题
- **改进措施**：检测 msSanitizer memcheck 检出 VECTOR_MASK 未复位；对 mean 后接向量算子的输出对拍；修复 待定（issue open；建议 kernel 结束前复位到默认全掩码并排查族级问题）
- **来源**：https://gitcode.com/cann/ops-math/issues/4259；https://gitcode.com/cann/ops-math/issues/4223；https://gitcode.com/cann/ops-math/issues/4201

### TRN-0535 `fa_prefill_310p_fp16_softmax_sum_overflow_inf` PromptFA 310P fp16 归一化前溢出 Inf

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / prompt FA UpdateOutput
- **原因行为**：310P fp16 高性能路径先把未归一化 fp32 累加 O cast 成 fp16 再除，均匀 softmax 时 O=n*35 超 fp16 上限溢出 +Inf
- **影响对象**：数值结果；隐状态（数值异常）
- **影响详情**：长序列均匀注意力下注意力输出变 +Inf（tiling key QINT8_KVFP16_OUTBF16_BSH_HIGHLEVELAPI_MDL_310TILING 触发路径）
- **改进措施**：检测 均匀 softmax 长 seq fp16 路径对拍 fp32 参考；监控注意力输出 Inf；修复 修复 PR https://gitcode.com/cann/ops-transformer/merge_requests/14827（open）：先广播 l 在 fp32 域完成 O/l 归一化再 cast 回 fp16
- **来源**：https://gitcode.com/cann/ops-transformer/merge_requests/14827

### TRN-0536 `mhc_sigmoid_one_minus_catastrophic_cancellation` CANN mhc 1-σ(z) 灾难性消去

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / mhc sigmoid 互补计算
- **原因行为**：mhc 相关 kernel 用 1-σ(z) 直接相减，大 z 时 σ(z)→1、1-σ(z) 有效位大规模丢失（灾难性消去）；数学等价式 σ(-z) 无此损失
- **影响对象**：数值结果（静默错误）
- **影响详情**：大 z 输入下泛化用例精度失败；修复改用 σ(-z) 后原失败输入通过（PR 泛化用例验证）
- **改进措施**：检测 大 z 输入泛化用例对拍 fp64 参考；修复 修复 PR https://gitcode.com/cann/ops-transformer/merge_requests/14812（merged 2026-10-29）：1-σ(z) 替换为 σ(-z)
- **来源**：https://gitcode.com/cann/ops-transformer/merge_requests/14812
- **关联**：var:TRN-0510

### TRN-0537 `topk_v2_multicore_template_flaky_precision` CANN TopkV2 多核模板偶现精度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / topk_v2 多核模板
- **原因行为**：TopkV2 多核模板存在偶现精度问题（标题级信息；PR !6831 模板未填根因细节，open 待合入）
- **影响对象**：数值结果（不可复现）
- **影响详情**：多核场景下 topk 输出偶现错值（训练侧 MoE 路由/top-p 采样依赖 topk）；具体触发面与错误形态 PR 未述
- **改进措施**：检测 待定；修复 修复 PR https://gitcode.com/cann/ops-math/pull/6831（open，模板未填细节）
- **来源**：https://gitcode.com/cann/ops-math/pull/6831

### TRN-0540 `pytorch_npu_masked_load_padding_zero_maxpool` torch_npu masked load 补 0 坏 maxpool

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / torch_npu / NPU masked load 填充值
- **原因行为**：NPU masked load 忽略上游传入的填充值、固定补 0，最大池化 padding 应使用 -inf 却拿到 0，窗口内全 padding 时最大值与索引计算错误
- **影响对象**：数值结果（静默错误）
- **影响详情**：maxpool 边界窗口含 padding 时输出与索引静默错（-inf 哨兵被 0 替代）；PR 标题与叙事为修复描述
- **改进措施**：检测 对含 padding 的 maxpool 与 CPU 参考对比；边界窗口全 padding 用例；修复 修复 PR https://gitcode.com/Ascend/pytorch/pull/48730（open，未合入）：masked load 尊重上游填充值使 padding 用 -inf
- **来源**：https://gitcode.com/Ascend/pytorch/pull/48730

### TRN-0541 `dynamic_stitch_cross_tensor_waw_race` CANN DynamicStitch 跨张量散射 WAW

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / dynamic_stitch arch35 散射写
- **原因行为**：y 写地址由 indices 决定而核按输入张量切分，无原子操作，跨张量重复 index 由不同核并发写同一地址产生 WAW，结果取决于写序
- **影响对象**：数值结果（不可复现）
- **影响详情**：跨张量重复 index + usedCoreNum>1 时输出非确定（同输入多次运行可不同）；越界 index 造成任意偏移写；arch35 dynamic_stitch_scatter_simd.h:100-130
- **改进措施**：检测 同输入多次运行对比；构造跨张量重复 index 用例验证 WAW；修复 待定（issue open，建议加原子或按 dst 划分核；越界校验一并补）
- **来源**：https://gitcode.com/cann/ops-math/issues/4226

### TRN-0552 `opsmath_kldiv_empty_input_none_out_unwritten` KlDiv 空输入 none 模式 out 未写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / aclnn_kl_div 空输入早退分支
- **原因行为**：输入为空 tensor 且 reduction=none 时走 aclnn_kl_div.cpp:190 早退分支，整段跳过 out 形状校验（仅存在于非空路径 :264），两段均返回 0 而 out 一个元素都不写
- **影响对象**：数值结果；训练信号（静默错误）
- **影响详情**：调用方按「返回 0 即成功」读 out 拿到未初始化/上次残留 device 内存（非 0 非 NaN 的任意值）；空 batch（尾批、动态切片）常见边界；非空对照正确返回 161002
- **改进措施**：检测 空 batch 用例读回 out 并断言全零/与 CPU 一致；监控空批次后 loss 突变；修复 待定（issue open：早退分支应同样校验 out 形状或显式写零）
- **来源**：https://gitcode.com/cann/ops-math/issues/4331

### TRN-0553 `opsnn_squaredrelu_out_contract_missing` SquaredRelu out 契约缺失错写越界

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / squared_relu out 校验/布局
- **原因行为**：out 与 input shape 不一致（[4x8]→[4x4]）不校验不拒绝，内核按 input 32 元素写完越界 16/24 元素；out 非连续（strides [8,1]）被放行且按连续写，逻辑视图 4 元素未写
- **影响对象**：数值结果（静默错误）
- **影响详情**：910B3/CANN 9.2.0/master 59c0720c：out=[4x4]（16 元素）时两段返回 0，内核写 32 元素越界 16（out=[1x8] 越界 24）；out [2,4]/strides [8,1] 返回 0，按连续写 8 元素，第二行 4 元素仍为初始化哨兵
- **改进措施**：检测 out shape/strides 契约用例 + msSanitizer；非连续视图读回对拍；修复 待定（issue open：期望第一段 161002 或按 stride 写）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7756；https://gitcode.com/cann/ops-nn/issues/7757
- **关联**：var:TRN-0524

### TRN-0554 `opsnn_swiglu_small_out_oob_write` SwiGlu 偏小 out 越界写 64B

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / swi_glu out 形状校验
- **原因行为**：out 形状小于由 x 推导的输出形状时无任何校验：GetWorkspaceSize 与 Execute 均返回 0，kernel 仍按 x.numel()/2 写 out 的 GM 地址越过缓冲尾部
- **影响对象**：数值结果（静默错误）
- **影响详情**：x=[2,32] dim=-1、out=[2,8]（16 元素，应 32）：msSanitizer illegal write of size 64（SwiGlu_2_high_performance_0）；out 偏大时只写前段、其余保持调用前内容，同样 rc=0；910B2/CANN 9.2.0
- **改进措施**：检测 msSanitizer memcheck；out numel 与推导值断言；修复 待定（issue open：第一段应校验 out 与推导形状一致）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7760
- **关联**：var:TRN-0524

### TRN-0555 `opsnn_scewithlogits_mismatch_labels_oob_write` SCEWithLogits labels 不一致越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / SCEWithLogits 入参校验
- **原因行为**：features/labels 形状不一致时两段接口均返回 0（非法入参被接受），内核按 labels 的行数计算，向按 features 分配的 loss/backprop 缓冲越界写
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：labels=fp32[109x1]、features=fp32[1x47] 时向 4B/188B 的 loss/backprop buffer 越界写，msSanitizer 报 72 处 illegal_write（最大 564B）（P0）；相邻内存（其他张量）被静默破坏
- **改进措施**：检测 msSanitizer memcheck；对 labels/features shape 断言一致；修复 待定（issue open，P0；期望第一段返回 161002）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7747
- **关联**：cross:INF-2298

### TRN-0556 `opsnn_swiglu_odd_split_axis_flat_offset` SwiGlu 奇数切分轴静默扁平半切

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / swi_glu_tiling 奇偶校验
- **原因行为**：切分轴奇偶校验判的是「切分轴×后续所有轴乘积」：切分轴奇数但乘积偶数被放行，kernel 按扁平化 numel/2 偏移切分（B 半起点落在行中间），与资料「按 dim 轴对半切」不符且返回 0
- **影响对象**：数值结果（静默错误）
- **影响详情**：x=[3,4] dim=0 实测 out=silu(x[0..3])*x[6..9]（应按行对半）；x=[2,3,32] dim=1 同样扁平半切；奇乘积输入被拒但错误码 561002≠资料 161002；910B2/CANN 9.2.0
- **改进措施**：检测 奇数切分轴用例对拍 CPU 参考；校验 out 与按 dim 切分语义一致；修复 待定（issue open：校验应改为 inShape.GetDim(splitDim) 判偶）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7763

### TRN-0558 `opstransformer_prompt_fa_fp16_softmax_numerator_inf` PromptFA fp16 softmax 分子溢出 inf

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / PromptFA fp16 分子累加
- **原因行为**：fp16 + HighPerformance 模式 softmax PxV 分子用 fp16 累加存储：Q/K 全零（logits≈0、softmax 均匀、exp=1）时分子=(i+1)*V 随序列长线性增长，超 65504 溢出 inf
- **影响对象**：数值结果（数值异常）
- **影响详情**：退化输入（Q/K 全零+causal+长 V 序列）输出连续 inf；修复 MR 验证 V∈{1000..16} 8 档全恢复正确值；与 TRN-0535（310P 归一化前溢出）同面不同根因
- **改进措施**：检测 Q/K 全零退化用例回归；输出有限性断言；修复 修复 MR https://gitcode.com/cann/ops-transformer/merge_requests/14989（open：tiling 层把 fp16 输入强制切 HighPrecision fp32 累加，V 8 档验证无 inf）
- **来源**：https://gitcode.com/cann/ops-transformer/merge_requests/14989
- **关联**：var:TRN-0535

### TRN-0559 `opsmath_reducesum_bool_int64_negative_axis_missing` ReduceSum bool→INT64 负轴丢末位

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / reduce_sum 负轴 promote
- **原因行为**：BOOL→INT64 分支 reduceDims 累乘未做负轴归一，负索引 size_t 越界得错值 → 误判 <2^24 → promoteType 选 fp32 累加 1670 万级布尔计数，超 2^24 后丢末位
- **影响对象**：数值结果（静默错误）
- **影响详情**：dims 用负轴（如 [-2,-1]）时和 16785409 实测 16785408；bool→int64 正轴对、负轴错；bool→int32、int32→int64 不走分支全对；和为偶数或 2^24 附近可精确表示时错误被掩盖；keepDims 无关；重复 3 次一致
- **改进措施**：检测 bool→int64 归约用正/负轴双写对拍；和大数时断言精确；修复 待定（issue open：循环内对 (*dims)[i] 做 GetPosDim 归一）
- **来源**：https://gitcode.com/cann/ops-math/issues/4298
- **关联**：cross:INF-2295

### TRN-0562 `opsmath_amp_update_scale_fp16_growth_overflow_inf` AmpUpdateScale fp16 增长溢出输出 inf

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / amp_update_scale fp16 溢出
- **原因行为**：fp16 增长分支（tracker+1==interval）currentScale*growthFactor 超 fp16 范围时 updatedScale 输出 inf；资料要求保持当前 scale（≥32768 一律 inf）
- **影响对象**：数值结果；优化器状态；训练轨迹（数值异常）
- **影响详情**：fp16 currentScale≥32768 且 tracker+1==interval 时 updatedScale 输出 inf，此后每步 scale 判定与梯度 skip 都在 inf scale 下运行，训练突然大面积丢梯度/回退且无明确报错，日志仅 scale 数值异常（A3 实测）
- **改进措施**：检测 监控 updatedScale 有限性；growth 分支断言输出≠inf；修复 修复 MR https://gitcode.com/cann/ops-math/merge_requests/6903（open WIP：对存储用 half 转换后检查 finiteness，CPU 差分 6 用例通过、NPU 资格待做）
- **来源**：https://gitcode.com/cann/ops-math/issues/4344；https://gitcode.com/cann/ops-math/merge_requests/6903
- **关联**：cross:INF-2307

### TRN-0563 `opstransformer_compressor_autograd_grad_all_garbage` compressor 公开入口反向梯度全错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / compressor autograd 中间量
- **原因行为**：autograd.Function.forward 内 is_grad_enabled() 恒 False，判据结构性恒 False → kernel 不写 softmax_score/kv 中间量 → backward 消费未初始化显存
- **影响对象**：梯度（静默错误）
- **影响详情**：经公开入口训练态梯度为垃圾值/NaN（实测 rel 1.1~2.8 或大形状 nan；直调内部 op rel 2.5e-3~3.5e-3 正常）；引入于 MR !13855；A3/910_93 bf16
- **改进措施**：检测 公开入口 vs 内部 op 双调用梯度对拍；backward 输出有限性断言；修复 待定（issue open：一行补丁验证通过；建议为公开入口 autograd 路径补测试——现有 pytest 三通路均直调内部 op 未覆盖）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6962
- **关联**：cross:INF-2316

### TRN-0564 `opsnn_bn3dtrainingreduce_fp16_kahan_loss` BN3DTrainingReduce FP16 归约丢补偿量

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：算子/内核 / cann / BN3DTrainingReduce 归约
- **原因行为**：FP16 短行（N≤64、R0=1）直接累加无补偿；分核路径只传 FP32 部分和、补偿量在根核合并前丢失——跨核相消输入下求和/平方和精度塌陷
- **影响对象**：数值结果（静默错误）
- **影响详情**：Ascend 950 FP16 下，53×5 固定输入稳定超三方 L1 RMSE 比值门槛（比值超判据 2~3 倍，相消求和差 2e-3 量级）；相消输入 NPU=-1 vs CPU/GPU=-0.998046875；仓内 Golden 平方和另有独立参考累加误差
- **改进措施**：检测 FP16 相消输入（±1 对称）对拍 GPU；短行 N∈[53,64] RMSE 比值回归；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/13131（merged：短行复用 TwoSum 补偿、分核 K=8 双链并传主值+补偿量；扩展 32 条 30 PASS/2 FAIL（1 ULP 既有问题未解））
- **来源**：https://gitcode.com/cann/ops-nn/issues/7762；https://gitcode.com/cann/ops-nn/merge_requests/13131
- **关联**：cross:INF-2308

## 编译器

### TRN-0016 `triton_autotune_rank_divergent_tiling` Triton autotune 使各 rank 归约 tiling 分叉

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-09-04 · 旧号 NUM.07

- **原因对象**：编译器 / megatron-lm / Triton autotune 配置与缓存
- **原因行为**：Triton autotune 按现场计时选 kernel config，计时噪声使各 rank 对同一 kernel 选出不同归约 tiling；deterministic-mode 下 autotune 缓存目录未共享，各节点各自调优。
- **影响对象**：数值结果；梯度（不可复现）
- **影响详情**：无 NaN、无 crash、loss 正常；DP allreduce 平均的是不同累加序的结果，run 间与 rank 间 bit 级不复现，A/B 对照、bitwise resume、RL π_old 重算失效；实测 8-rank 中 22 个条目 13 个 winner 不一致。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6966
- **关联**：var:TRN-0012

### TRN-0036 `autotp_compile_drops_tp_collectives` AutoTP 编译 pass 不进检查点子图，漏插 TP collective

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-31 · 旧号 PAR.08

- **原因对象**：编译器 / deepspeed / AutoTP 图 pass 子图遍历
- **原因行为**：AutoTP 关掉 TP 层的模块级 collective 交由图 pass 补插，但该 pass 只遍历顶层图，不进入 activation checkpointing 提升出的子图，row-parallel 输出保持部分和。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：开梯度检查点 + autotp pass 时前向与梯度静默错误、exit 0，fullgraph=True 也无 graph break 或警告，插入可能只是部分的；2×H200 实测 HF Llama 0/14 collective 插入。禁用 dynamo 时同样无 collective。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8357

### TRN-0134 `training_kernel_sync_semantic_wrong_value` Triton 同步语义错误使训练 GEMM/attention 吃到有界错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 KER.03

- **原因对象**：编译器 / triton / MMA 同步范围与 inline_asm 副作用
- **原因行为**：Triton 合法 API 下同步范围错：MMA 未完成就读，或 inline_asm_elementwise 对复制元素多次执行副作用；Megatron 同型实例中 normalization 先于 FC1 参数同步 hook 读旧存储。
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：训练 GEMM/attention 得到有界错值，无 crash、数字合理但错，像轻度 SDC；Megatron TP=1 开 distributed-optimizer 参数 gather 时，validation loss 有限、无 NaN、无 assert，只有确定性事件序回归测试抓得住。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6654

### TRN-0137 `torch_compile_float_kwarg_stale_constant` torch.compile 固化 float 标量致 SwiGLU 错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-28 · 旧号 KER.06

- **原因对象**：编译器 / pytorch / torch.compile float 标量捕获
- **原因行为**：clamped_swiglu 经 torch.compile 后，float kwarg clamp_value 在 specialize_float=False 下被当作编译期常量，首个值固化进生成代码，传入新值仍执行旧 kernel。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：无 crash、无 NaN、无警告，SwiGLU 前向、反向输出系统性偏移、训练曲线照常；按层或按专家类型使用不同 clamp 值（如 Step-3.5-Flash、K-EXAONE-2.0）时，第二组层起全部用旧 clamp 值训练。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/6918；https://github.com/pytorch/pytorch/issues/194976；https://arxiv.org/abs/2606.19348

### TRN-0280 `triton_ascend_static_rnumel_miscompile` triton-ascend 常量特化 r-numel 致行 max 归约误编译

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：编译器 / triton / 归约轴长度编译期常量特化
- **原因行为**：归约轴长度 r0_numel 被作为 ASTSource 级编译期常量烧入，导致 fused softmax（行 max+exp+sum 归约）内核误编译。
- **影响对象**：数值结果（静默错误）
- **影响详情**：triton_experimental 后端 torch.compile 下 SDPA+attn_mask（fp16）约 97% 元素与 eager 不符，5/5 确定性复现；同内核同配置下，r0_numel 常量 96 烧入约 97% 错，运行时 i32 传参 mismatch=0/36864。
- **改进措施**：检测 编译前后数值对账（eager vs compiled）；ASTSource constants 是否含 r0_numel 可静态检查。；修复 本源未修（triton-ascend 内部出错 pass 未定位）。临时规避：torch_npu 侧去掉静态 r-tree numel 的常量注入（codeg/triton.py），令 r0_numel 回到运行时 i32 传参，放弃 R0_BLOCK==rnumel 时消 r0_mask 边界检查的编译期收益，本源修复后应撤除。同文件 rsplit 组合核 constants:{r0_numel: total_cores} 疑似同型风险。
- **来源**：https://github.com/triton-lang/triton-ascend/issues/2531；https://gitcode.com/Ascend/pytorch/issues/5366
- **关联**：cross:INF-1375

### TRN-0281 `inductor_mod_eliminate_noncontig_reduction` torch_npu Inductor 取模消除错致非连续归约错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：编译器 / torch_npu / eliminate_modular 取模消除
- **原因行为**：eliminate_modular 处理乘积时只用其中一个变量的长度判断取模是否多余：对 (7*r)%7 按 5%7==5 误判可消除，化简为 7*r（实际恒为 0），小归约展开后第一列 load 地址错误。
- **影响对象**：数值结果（静默错误）
- **影响详情**：Inductor default 后端、shape[5,7]/stride[14,1] 非连续输入小归约（unroll_reductions_threshold=8）：amax 期望 62 实得 84、amin 同错；地址错非浮点误差，Triton 源码中地址已错。
- **改进措施**：检测 非连续输入下编译前后 amax/amin 对账；生成 Triton 源码检查首列地址表达式。；修复 待定（issue open，2026-10-08；修复方向：coeff*(numel-1)<divisor*modulus 才消除并返回 FloorDiv，多变量/负系数/未知范围保留原式）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5295

### TRN-0287 `trl_torch_compile_chunked_loss_zero` trl torch<2.11 编译 chunked loss 全程 0

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：编译器 / trl / Inductor 变异张量分析失败
- **原因行为**：#7600 把 kernel 标量参数 cast 成 fp32；torch<2.11 的 Inductor 以 constexpr/float 追踪无 .to() 可调→分析抛异常→按全变异假设生成错误图。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：SFT/蒸馏等用 chunked logprob/divergence kernel 的训练在 torch<2.11 + torch_compile=True 下：无报错、loss 恒 0.0、grad_norm 恒 nan；不编译时 loss 约 10.7。CI 因用新 torch 不覆盖。
- **改进措施**：检测 torch<2.11 + torch_compile=True 且用 chunked loss kernel 时，第 1 步即查 loss 是否 0.0、grad_norm 是否 nan；kernel 测试 TestChunkedLogProbFunction::test_torch_compile 在 2.6–2.10 均失败可作回归探针。；修复 kernel 侧 #7600 的 fp32 cast 引入此不兼容；torch 2.11 起分析器支持 scalar .to() 后测试通过（issue 已 closed；修复落地状态未逐 commit 核实，未确认是否单独 backport）
- **来源**：https://github.com/huggingface/trl/issues/7687；https://github.com/huggingface/trl/pull/7600

### TRN-0288 `torchair_autotune_dlclose_icache_stale` torchair autotune dlclose 致 icache 不一致

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：编译器 / cann / release 即时 dlclose
- **原因行为**：autotune 选优后对落选 kernel .so 立即 dlclose 释放 HBM 代码段；落选 kernel 已执行、device 代码在 icache，芯片无一致性校验，地址被复用后 HBM 与 icache 代码不一致。
- **影响对象**：数值结果；可用性/进度（不可复现）
- **影响详情**：偶发精度异常或 aic error：同一输入同一 kernel 时对时错，或直接 aic error 退出；取决于 dlclose 后该地址是否被复用。
- **改进措施**：检测 autotune 后偶发精度异常/aic error 且关 autotune 即消失时怀疑此机制；对比固定 kernel（关 autotune）输出。；修复 修复已合入：MR !3844（master）与 !3845（26.2.0 分支）均 merged——release() 将落选句柄登记进 retired_kernel_handles 延迟到进程退出统一 dlclose，选优语义不变。issue #868 已 closed。https://gitcode.com/Ascend/torchair/merge_requests/3844
- **来源**：https://gitcode.com/Ascend/torchair/issues/868；https://gitcode.com/Ascend/torchair/merge_requests/3844；https://gitcode.com/Ascend/torchair/merge_requests/3845

### TRN-0385 `torchair_cache_compile_pass_state_digest_collision` torchair cache_compile 忽略自定义 pass 状态复用旧图

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：编译器 / torch_npu / cache_compile code digest
- **原因行为**：_get_code_digest 只哈希反汇编指令：捕获值/默认参/partial 绑定不同的 pass 产生相同 digest（partial 可 dis 为空、全部变体折叠成空文本 MD5），改 pass 行为后命中旧缓存图
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：NPU 上用 torch.compile + cache_compile 缓存编译自定义 post-grad pass 时，改 pass 行为（如调整捕获的偏移量）后重新编译不报错，实际复用先前编译的图而非应用新 pass，训练图静默用旧逻辑；只有清缓存或改函数体指令才恢复，改绑定状态无效。
- **改进措施**：检测 改 pass 绑定状态后断言 cache miss；对关键 pass 输出做图 hash 抽查；修复 修复 MR https://gitcode.com/Ascend/torchair/merge_requests/3886（open，2026-10-22）：digest 纳入闭包 cells、defaults、partial 绑定、实例状态；探针红转绿，回归覆盖 closure/default/partial/callable；NPU 端到端编译未跑
- **来源**：https://gitcode.com/Ascend/torchair/issues/890；https://gitcode.com/Ascend/torchair/merge_requests/3886

### TRN-0396 `triton_ascend_num_stages_loop_carried_store_misched_training` triton-ascend num_stages>1 携带态存储错调度（训练侧）

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：编译器 / triton / 软件流水携带态存储调度
- **原因行为**：带 loop-carried 值且循环体内 store 的 kernel 在 num_stages>1 软件流水下被错调度：in-loop store 读到陈旧流水级，kernel 跑完并返回看似合理的错数——非崩溃非编译错误。
- **影响对象**：数值结果；梯度（不可复现）
- **影响详情**：Mamba-2 SSD 状态传递 kernel（fwd/bwd 同模式）约 25%~46% 新起进程输出 bit 级一致错值；固定 num_stages=1 全部消失（16/16 PASS，梯度 bit 一致）；进程内稳定、跨进程翻转。
- **改进措施**：检测 多进程重跑对比输出 bit 一致性；对携带态 kernel 固定 num_stages=1 做 A/B。；修复 待定（issue open，3.6.0+dev20260921 与 3.2.2 均复现；规避：相关 config 固定 num_stages=1）
- **来源**：https://github.com/triton-lang/triton-ascend/issues/2662
- **关联**：cross:INF-1769

### TRN-0398 `pytorch_npu_inductor_reduction_mask_bias_grad_axis_flatten` NPU Inductor 归约 mask 缺失污染 bias 梯度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：编译器 / torch_npu / Inductor 归约 mask/layout
- **原因行为**：GPT2/BERT 派生归约实际长度 768、tile 扩展到 1024，越界值置零后减均值、平方仍使无效 lane 非零污染归约；BERT 反向 bias 梯度的轴压平把应保留的输出轴一并归约。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：NPU 上用 torch.compile(backend=inductor) 训练 GPT2/BERT 时，均值、方差、bias 梯度等归约被 padding lane 非零中间值污染，或 bias 梯度按错误轴归约致维度语义丢失；训练不报错、loss 可能只轻微偏离，需 eager 对照才见差异。
- **改进措施**：检测 编译前后 amax/amin/bias-grad 与 eager 对账；dump Triton 源码检查归约 mask 处理。；修复 修复 PR https://gitcode.com/Ascend/pytorch/pull/48448（merged 2026-10-23）：保留不能证明恒真的轴 mask 并在融合表达式计算后选择归约单位元；多轴 reduction 只压平 reduction axes；负索引/Load 生存期/tiling 搜索/符号 group 匹配/stride 证明/range 拆分拒绝协议共八类修复（issue !48387 关联）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5625；https://gitcode.com/Ascend/pytorch/pull/48448
- **关联**：cross:INF-2198

### TRN-0401 `triton_ascend_onehot_gather_fold_masked_max_wrong_value` triton-ascend one-hot gather 折叠错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：编译器 / triton / FoldOneHotGather pass
- **原因行为**：masked max-with-index 归约后的 one-hot gather 被折叠为被 mask 的最大值本身，尽管 gather 求和的是原始未 mask logits：pass 匹配接受了含 logits 的分支。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：最小复现（单 NPU）：每行 logits 为 -(arange(32)+3)、列 1 被 mask，argmax 选列 1，one-hot 回取原始 logits 应得 -4，实际输出 0.0（被 mask 的最大值）；错值静默进前向与梯度。
- **改进措施**：检测 该模式（masked argmax + one-hot gather 回原始 logits）编译前后对拍；检查生成 TTGIR 中 FoldOneHotGather 变换。；修复 待定（issue open 2026-10-15，源码定位至 third_party/ascend/lib/TritonToLinalg/ArgMinMaxConverter.cpp）
- **来源**：https://github.com/triton-lang/triton-ascend/issues/2585

### TRN-0413 `ascend_npu_inductor_pixel_shuffle_dynamic_reduction` Ascend Inductor pixel_shuffle 索引与动态归约漏算

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：编译器 / torch_npu / torch_npu Inductor 索引拆轴与
- **原因行为**：channels-last pixel_shuffle 拆轴用相对 divisor 做根坐标查找并错误复用旧坐标，宽度索引取模被消去；动态 persistent 归约用首次输入尺寸 hint 选块，归约长 31→33 后仍用 32 块漏算有
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：torch.compile 下 channels-last pixel_shuffle 输出与参考不一致（原用例 54758/73728 超差，最大绝对差约 3.9）；dynamic=True 归约输入尺寸跨 32 边界时漏算元素。训练前后向经该图时数值静默错误。
- **改进措施**：检测 test_pixel_shuffle_channels_last_npu 与 test_dynamic_persistent_reductions 回归（31×127/32×128/33×129 与 CPU 对比）。；修复 修复 MR https://gitcode.com/Ascend/pytorch/pull/48472 （open，未合入；拆轴改用根坐标 divisor、复用上游 _get_persistent_RBLOCK 按上界选块，未核实发布版本）。
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5632；https://gitcode.com/Ascend/pytorch/pull/48472
- **关联**：cross:INF-2159

### TRN-0452 `concat_to_concatd_tree_default_desc` ConcatToConcatD 拆树中间节点默认 desc 错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：编译器 / cann / ConcatToConcatD 融合 pass
- **原因行为**：输入数超 kMaxConcatDInputs(512) 时拆成多级 ConcatD 树，除顶层外中间层节点没有任何手动 desc 处理，保留 ES 默认 desc（dtype FLOAT、空 shape）下发真机，静默计算错误。
- **影响对象**：数值结果（静默错误）
- **影响详情**：输入数 >512 的 Concat/ConcatV2 图经自动融合后真机输出错误且无报错；训练图模式与推理图模式同路径，影响超宽拼接图（如超长专家列表拼接）。
- **改进措施**：检测 对 >512 输入 Concat 图做端到端 golden 对拍；检查融合后中间节点 desc；修复 待定（issue closed，未见关联修复 MR，落地版本未核实）
- **来源**：https://gitcode.com/cann/ops-math/issues/3974
- **关联**：cross:INF-2206

### TRN-0478 `torchair_cat_fusion_axis_size_mismatch` torchair Cat 融合跳过逐维 size 检查致错误融合

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：编译器 / torch_npu / torchair concat 融合 pass
- **原因行为**：concat 融合组跳过同秩节点与公共轴的逐维 size 检查，公共轴相同但其他轴 size 不一致的同秩节点仍可能按位置绑定轴被融合。
- **影响对象**：数值结果（静默错误）
- **影响详情**：torchair 图模式下含 Cat 的模型，当同秩节点公共轴相同但其他轴 size 不一致时被错误融合，输出数值与 eager 不一致且无报错；等尺寸节点不受影响。issue 截图显示不同轴被融到一起。
- **改进措施**：检测 图模式 vs eager 输出对照；融合组节点逐维 size 审计；修复 修复 PR https://gitcode.com/Ascend/torchair/merge_requests/3906（open，2026-10-27）——补齐已有校验：同秩节点逐维 size 不一致时拒绝融合；补静态/动态轴不匹配回归用例
- **来源**：https://gitcode.com/Ascend/torchair/issues/902；https://gitcode.com/Ascend/torchair/merge_requests/3906

### TRN-0484 `torchair_atan2_swapped_args` torchair atan2 lowering x/y 入参顺序互换

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-10-28

- **原因对象**：编译器 / torch_npu / torchair ASCIR atan2 lo。
- **原因行为**：torchair 图模式下 atan2 的 x 与 y 入参顺序不正确：AF.atan2(x,y) 结果等于 EAGER.atan2(y,x)；512 点对照匹配 atan2(x,y) 512/512（即互换）
- **影响对象**：数值结果（静默错误）
- **影响详情**：图模式 atan2 输出系统性等于交换参数的真值：除 y==x 对角线（64/512）外全错，无报错；eager 正常。
- **改进措施**：检测 图模式 vs eager 的 atan2 输出对照（非对角线输入）；修复 已修复：https://gitcode.com/Ascend/torchair/merge_requests/3905（merged，fix atan2 input order for ASCIR）；issue #901 closed
- **来源**：https://gitcode.com/Ascend/torchair/issues/901；https://gitcode.com/Ascend/torchair/merge_requests/3905

### TRN-0485 `ge_hostcpu_const_fold_desc_attr_loss` GE HostCPU 常量折叠丢失输出描述符属性

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：编译器 / cann / GE HostCPU 常量折叠
- **原因行为**：HostCPU 自定义算子常量折叠的输出从 gert::Tensor 转回 GeTensor 时重建描述符，丢失 shape_range、origin_shape_range 等 GE 属性
- **影响对象**：数值结果（静默错误）
- **影响详情**：GE 图模式训练中，HostCPU 自定义算子常量折叠后，下游 MirrorPad 等算子的动态 shape 范围可能在重推导时退化；无显式报错，表现为特定输入形状下结果错或后续 shape 校验异常。
- **改进措施**：检测 含 HostCPU 常量折叠 + 动态 shape 算子的图与关闭常量折叠对照；修复 已修复：https://gitcode.com/cann/ge/merge_requests/5608（merged，2026-10-27）——以节点原 output desc 为基础仅覆盖 gert 返回的 shape/origin_shape/dtype/format/placement，保留范围与扩展属性；补 bottom 多输出 UT
- **来源**：https://gitcode.com/cann/ge/merge_requests/5608

### TRN-0530 `triton_ascend_noop_permute_ub_overflow` triton-ascend 空 permute UB 溢出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：编译器 / triton / getTransposedValue 降级
- **原因行为**：tl.permute 无条件降为 linalg.transpose，只移动 size-1 维的空排列被当真转置 bufferize，NZ 分形布局放大 UB 8 倍触发编译期 ub overflow
- **影响对象**：可用性/进度（报错）
- **影响详情**：特定 reshape/permute 组合（size-1 维移动）在 Ascend 上编译期报 ub overflow 而无法运行（上游 #1640 载体）；GPU 语义等价路径无此问题
- **改进措施**：检测 编译期 ub overflow 报错自带定位；修复 修复 PR https://github.com/triton-lang/triton-ascend/pull/2848（open）：getTransposedValue 检测空排列降为 tensor.collapse_shape+expand_shape 纯 reshape
- **来源**：https://github.com/triton-lang/triton-ascend/pull/2848；https://github.com/triton-lang/triton-ascend/issues/1640

## 运行时/执行

### TRN-0020 `fsdp_cpu_offload_rng_tracker_device_mismatch` CPU offload 下 RNG tracker 设备错配致随机值重复

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-09 · 旧号 NUM.11

- **原因对象**：运行时/执行 / pytorch / DTensor RNG tracker 设备谓词
- **原因行为**：DTensor RNG tracker 以 CUDA 设备 fork_rng 包裹随机操作；CPU offload 下 mesh 仍为 CUDA 而存储在 CPU，CPU 随机操作被错路由，退出时无条件恢复 CPU 生成器状态。
- **影响对象**：数值结果；模型权重；可用性/进度（静默错误）
- **影响详情**：FSDP2 开 CPU offload 时触发：offload 后的 CPU 随机操作产生完全相同的值，初始化/dropout 等去相关失效，训练期无 crash、无 NaN；torchtitan 中 lm_head 的 trunc_normal_ 反复得到相同越界值，初始化挂死。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/pytorch/pull/196072；https://github.com/pytorch/torchtitan/issues/4511

### TRN-0048 `lazy_clone_materialization_unordered_on_stream` PyTorch _lazy_clone 物化拷贝不按 stream 排序

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-09 · 旧号 PAR.20

- **原因对象**：运行时/执行 / pytorch / Tensor._lazy_clone 物化拷贝
- **原因行为**：copy-on-write 张量在首次请求可变指针（如 data_ptr()）时才物化拷贝，该拷贝不在当前 CUDA stream 上排序，CUDA graph capture 时也不被录进图。
- **影响对象**：数值结果；输出内容（数值异常）
- **影响详情**：非默认 stream 上物化先于生产 kernel、读到陈旧内存：eager 下随机 CUDA error 与错文本，full CUDA graphs 下确定性 NaN 与错文本；命中链路为 torchtitan vLLM generator + Dist-MoE。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/issues/5125

### TRN-0095 `wrapper_signature_probe_drops_packed_boundaries` verl 能力探测误判 wrapper，critic 丢 packed 边界

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-20 · 旧号 DATA.13

- **原因对象**：运行时/执行 / verl / value 引擎 cu_seqlens 能力探测
- **原因行为**：引擎按外层模块 forward 显式签名探测 cu_seqlens 支持；TRL value-head wrapper 只有 **kwargs，探测为 False，critic 输入被静默省略 cu_seqlens。
- **影响对象**：跨请求/跨样本数据；隐状态（静默错误）
- **影响详情**：Qwen3.5 线性注意力 critic + TRL value-head + FSDP 引擎，SP=1 即触发：同一 microbatch 内独立打包的样本在 critic 线性注意力状态上互相可见；无 crash，数值影响未测量。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7931

### TRN-0124 `replay_graph_diverges_from_train_graph` Megatron CUDA graph 默认捕获范围被静默收窄

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-21 · 旧号 ACT.03

- **原因对象**：运行时/执行 / megatron-lm / CUDA graph attn 捕获范围；重计算/卸载 / megatron-lm / mHC 重算管理器与 MLP tail 检查点
- **原因行为**：#5841 把 ['attn'] 默认 capture range 从整个 _forward_attention 静默收窄为 layernorm+attention，新 gate 误拒旧配置；旧 replay 路径另有三处重算缺陷。
- **影响对象**：隐状态（静默错误）
- **影响详情**：CUDA graph replay 的是另一段子计算，replay 图与训练图结构性分叉，无 NaN、无 crash，只有 golden values 对照才暴露；cuda_graph_modules=['attn'] 的默认配置即受影响，以前合法的配置被新 gate 误拒。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6661

### TRN-0256 `eval_replays_training_captured_graph` Megatron 验证在 eval 下重放训练态 CUDA graph

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-09-04 · 旧号 OBS.07

- **原因对象**：运行时/执行 / megatron-lm / CUDA graph 在 eval 下的重放判定
- **原因行为**：训练态捕获的 CUDA graph 冻结了分支走向与 buffer 写；eval+no_grad 的普通验证仍重放该 graph 而未回退 eager，MoE router token-count 累积等 buffer 写被带入验证前向。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：无 crash、无 NaN；val loss/metrics 混入训练态副作用，据此做早停、lr 决策或回滚判断时信号源本身是错的。显式推理捕获与 ckpt-forward replay 不在此列。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6992

### TRN-0272 `d2h_dma_madvfree_page_reclaim` NPU D2H 拷贝不清 MADV_FREE 脏标记页被回收清零

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：运行时/执行 / torch_npu / aclrtMemcpy D2H 与分配器交互
- **原因行为**：aclrtMemcpy DMA 写 CPU 内存不经 CPU MMU：不设 PTE_DIRTY、不清 MADV_FREE 标签；kswapd 视这些页为干净直接回收，数据清零。
- **影响对象**：数值结果（静默错误）
- **影响详情**：aarch64+NPU+mimalloc2.x下npu_tensor.cpu()间歇性得0；内存压力回收MADV_FREE且DMA写过页；MIMALLOC_PURGE_DECOMMITS=0+madvise(MADV_PAGEOUT)秒级87.6%清零；真实kswapd需root；C直调100%复现
- **改进措施**：检测 D2H 后校验和/CRC；复现脚本监测 LazyFree 页变化。；修复 上游未修。临时规避：用 torch.zeros+copy_ 替代 .cpu()（CPU memset 写入会清 MADV_FREE 标签）；修复建议为 DMA 后对目标页标脏。关联 PyTorch 上游同机制 issue：https://github.com/pytorch/pytorch/issues/200756
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5396；https://github.com/pytorch/pytorch/issues/200756

### TRN-0292 `megatron_gdn_graph_fla_tensor_cache_uaf` Megatron GDN 图回放读已释放 chunk 元数据致错值/越界

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：运行时/执行 / megatron-lm / FLA tensor_cache 元数据生命周期
- **原因行为**：FLA 经 tensor_cache 构建 chunk 元数据：warmup 在捕获外算好，捕获命中缓存录下地址；后续图捕获逐出缓存项且无引用，存储归还池（106 个捕获元数据 98 个已释放），回放时把复用后的字节当索引用。
- **影响对象**：KV状态；数值结果；可用性/进度（静默错误）
- **影响详情**：prefill/mixed 图回放非法内存访问崩溃（确定性，cu_seqlens[10 亿级]）；保活元数据后仍有静默面：h 状态缓冲按 dummy 布局分配，kernel 按活 cu_seqlens 循环越界写 h，512 次回放 52-61 次越界写进图池，无报错。
- **改进措施**：检测 graph 回放后对 h 状态/输出做有限性与已知容量校验；compare-address 审计捕获张量是否已被池回收。；修复 待定（issue open 无评论；方向=捕获期间持有元数据引用（如 pool-external 持久分配）并按活 cu_seqlens 分配 h，未核实上游进展）
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/8151

### TRN-0295 `ge_big_hbm_logic_addr_overlap_silent_corruption` GE 大 HBM 机型逻辑地址区间重叠致变量区被误判静默损坏

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：运行时/执行 / cann / GE 逻辑地址基址按 32GB 时代比例硬编码
- **原因行为**：逻辑地址基址按 32GB 时代硬编码（FM 64GB/SVM 128GB/Var 128GB），HBM fm 区间按 26/32 比例增长（192GB 卡上限 156GB），GetRtAddress 反查内存类型时误判重叠。
- **影响对象**：数值结果（静默错误）
- **影响详情**：大HBM单卡192/256GB训练/推理，feature map用量越过旧边界>62GB或>126GB，或同图用Host SVM与变量时，变量地址被误判为fm地址，输出错值无报错；特定内存水位以上出现，小规模复现不出，非确定性。
- **改进措施**：检测 大 HBM 卡上出现无法解释的内存类型相关错值时，检查各内存类型用量是否越过 62/126GB 旧区间边界。；修复 修复 MR !5414（open 未合入）：按 256GB 步长重划逻辑基址（Host FM 256GB、Host SVM 512GB、var 768GB），var 判定宽度优先用 OM 记录值，新增 HBM 区间上界断言；UT 39/39 等通过、需真机 CI 验证。https://gitcode.com/cann/ge/merge_requests/5414
- **来源**：https://gitcode.com/cann/ge/merge_requests/5414

### TRN-0403 `msswift_grpo_liger_mm_double_vision_encoder_hang` ms-swift GRPO+Liger 多模态双跑挂起

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：运行时/执行 / ms-swift / GRPO Liger 前向重定向
- **原因行为**：Liger 前向重定向：hook 先在所有 rank 转好 inputs_embeds，lambda 又用原始 pixel_values 再跑一次，vision encoder 被 rank 间不一致地执行两遍。
- **影响对象**：可用性/进度（挂起）
- **影响详情**：混合 text/image batch 下 image rank 两次进 vision encoder、text rank 已前进，默认超时下静默挂起；短超时后 watchdog 显示 4 rank 卡同一 allgather 序号但张量大小两两分组（1769472 vs 24）。
- **改进措施**：检测 首 step 后 rank 间 vision encoder 调用计数对账；watchdog NumelIn 差异模式识别；小 ddp_timeout 冒烟。；修复 待定（issue open 2026-10-22，根因链定位至 _forward_redirection 双跑；规避：--use_liger_kernel false）
- **来源**：https://github.com/modelscope/ms-swift/issues/10410

### TRN-0418 `ascend_pytorch_task_queue_fatal_error_downgrade` torch_npu 任务队列致命错误被降级后续计算假成功

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：运行时/执行 / torch_npu / Repository 异步任务队列错误状态机
- **原因行为**：异步算子失败后原实现首次抛异常时把 ERROR_EXIT 转 CAN_EXIT；消费者退出后后续任务可能被丢弃，但提交与同步不再报告原始错误，上层误用未经计算的输出；重试也假成功。
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：任一异步算子设备侧失败后，队列进入半死状态：后续提交/同步不报错，训练继续跑但输出是未计算显存残留；重试同样假成功。实机复现（#4738）以提交不存在的算子触发真实异步错误验证。
- **改进措施**：检测 故障注入（提交不存在算子）后检查后续提交/同步是否持续报错；输出 canary 校验。；修复 修复 MR https://gitcode.com/Ascend/pytorch/pull/48474 （open 未合入：Repository 增加持久故障标志，故障后提交/同步持续抛异常；6 组配置实机验证通过；未核实发布版本）。
- **来源**：https://gitcode.com/Ascend/pytorch/issues/4738；https://gitcode.com/Ascend/pytorch/pull/48474

### TRN-0467 `torchnpu_910_pageable_d2h_sync_contract_break` 经典 910 pageable D2H 同步契约失效读垃圾值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：运行时/执行 / torch_npu / pageable D2H copy_ 同步
- **原因行为**：copy_(npu, non_blocking=False) 的同步契约（返回即数据完整）在进程此前执行过 pinned 分配与 Event/Stream 序列后失效：返回即读 pageable 目标拿到未就绪垃圾值；上下文依赖。
- **影响对象**：数值结果（静默错误）
- **影响详情**：经典 910（CANN 9.1.0/torch_npu 2.7.1）上嵌入 pin/event 序列后的 D2H copy_ 即读得 -1.05e-21 级垃圾值；950PR（torch_npu 2.9.1）同探针 0 发现。训练 host 读 loss/指标/权重快照可能拿到部分传输值。
- **改进措施**：检测 关键 D2H 读数前显式 torch.npu.synchronize() 对比；pageable 读回值做 sanity 校验；修复 待定（issue 期望契约不因进程历史失效或文档明示需显式 synchronize；源码定位未给出，open）
- **来源**：https://gitcode.com/Ascend/op-plugin/issues/644

### TRN-0538 `ge_half_precision_numpy_view_shape_lost` GE 半精度 numpy 视图 shape 丢失

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：运行时/执行 / cann / GE llm 数据半精度 numpy 视图处理
- **原因行为**：GE llm 路径对半精度 numpy 视图的 shape 恢复缺失（PR !5680 标题级：恢复半精度 numpy 视图的 shape 并支持 Unicode 字符串编码，关联 #631/#632）
- **影响对象**：训练样本流（静默错误）
- **影响详情**：半精度数据经 numpy 视图进 GE llm 管线时 shape 信息丢失，样本被错误重塑（标题级信息，具体形态见关联 issue #631/#632）
- **改进措施**：检测 待定；修复 修复 PR https://gitcode.com/cann/ge/merge_requests/5680（open，关联 issue #631/#632）
- **来源**：https://gitcode.com/cann/ge/merge_requests/5680

### TRN-0546 `torch_npu_lazy_call_race_drops_callbacks` torch_npu _lazy_call 竞态静默丢回调

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：运行时/执行 / torch_npu / npu._lazy_call 初始化队列
- **原因行为**：_lazy_call 先查 _initialized 再入队，与 _lazy_init 不共用 _initialization_lock：初始化线程遍历完队列后、置位前，另一线程回调被追加进已消费队列，此后无人消费
- **影响对象**：训练样本流（不可复现）
- **影响详情**：manual_seed/set_rng_state 等经 _lazy_call 延迟执行：多线程首次初始化并发时随机种子或 RNG 状态设置被静默丢失，数据顺序/初始化偏离预期且不可复现；持有初始化锁的模拟复现可稳定构造
- **改进措施**：检测 初始化后断言 _queued_calls 为空；对 seed 生效性做两次采样一致性检查；修复 待定（issue open：建议 _lazy_call 与 _lazy_init 共用 _initialization_lock，重入不死锁）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5744

## 集合通信

### TRN-0030 `allreduce_silent_wrong_value` all-reduce 完成但 payload 已错的静默集合通信错误

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 PAR.02

- **原因对象**：集合通信 / 通用 / 集合通信 payload 数值完整性
- **原因行为**：集合通信正常完成、无 timeout，但 payload 已错（坏 NIC、静默传输损坏、错误的 process group）；NCCL watchdog 只检查活性，不校验数值。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：所有 rank 同步拿到同一份错误梯度，loss 仍平滑，无 timeout 报警；比单个坏 GPU 更难排查。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2407.21783

### TRN-0270 `ccu_allreduce_rank_slot_nondeterminism` CCU AllReduce 槽位随 rank 落位致跨卡归约不一致

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-15

- **原因对象**：集合通信 / cann / CCU GroupReduce 归约槽位落位
- **原因行为**：CCU 引擎 GroupReduce 将本卡输入固定垫底于 GO 内存末槽、远端按 rank 升序占槽 0..N-2，硬件按槽序归约：各卡浮点加法操作数序列随本卡 rank 漂移，同输入不同卡输出 bitwise 不一致。
- **影响对象**：数值结果（不可复现）
- **影响详情**：CCU AllReduce one_shot/2die 浮点 SUM 下同输入各卡输出 bitwise 不相等（2die 两分支计算序列也不同）；整型与 MIN/MAX 不受影响。训练侧表现为跨卡归约结果分叉、不可复现。
- **改进措施**：检测 同输入跨卡 AllReduce 输出 bitwise 对账；确定性模式训练对比。；修复 修复 MR !3607（open）：归约槽位按 rank 落位，各卡操作数序列恒为 (s_0..s_{N-1}) 与 rank 无关；合入后 CCU allreduce one_shot/2die 浮点 SUM 输出将发生预期 bitwise 变化（对齐全卡一致）。https://gitcode.com/cann/hccl/merge_requests/3607
- **来源**：https://gitcode.com/cann/hccl/issues/825；https://gitcode.com/cann/hccl/merge_requests/3607
- **关联**：var:TRN-0012

### TRN-0277 `allgather_recursive_hd_peer_offset` AllGather Recursive HD 非 2 次幂接收偏移读错 peer

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：集合通信 / cann / AllGather Recursive HD 偶数
- **原因行为**：GatherInPartOneToEven 偶数接收分支用本端 rank 而非 peerRank 计算接收切片与远端读取偏移；TransportP2p 接收端发起读时读错 peer 的输出切片并覆盖本端自己的切片。
- **影响对象**：数值结果（静默错误）
- **影响详情**：Recursive HD、非 2 次幂 rank 数（3/5/6/7）、接收端发起读的 P2P/HCCS 链路时 AllGather 输出数据缺失或来源错误；RoCE 路径因发送端写正确切片而掩盖。修复前 HCCS 8 个组合全报内存语义错误。
- **改进措施**：检测 仓库 ST 算法检查器（Checker::Check 内存/数据来源语义校验，DEV_TYPE_910B）；AllGather 结果与参考布局对账。；修复 修复 MR !6017/!6018（open）：偶数接收分支三处 rank→peerRank（本端接收切片、日志偏移、ExecuteRxSync 远端源偏移），并补 HCCS/RoCE ST 回归。https://gitcode.com/cann/hcomm/merge_requests/6017
- **来源**：https://gitcode.com/cann/hcomm/issues/1046；https://gitcode.com/cann/hcomm/merge_requests/6017；https://gitcode.com/cann/hcomm/merge_requests/6018

### TRN-0299 `hccl_single_rank_v_op_displacement_ignored` HCCL 单 rank 路径 V 算子忽略位移错位读写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：集合通信 / cann / SingleRankProc 单 rank 拷贝
- **原因行为**：单 rank 分支对 AllGatherV/ReduceScatterV/AlltoAllV 只按 count 拷贝、直接用原始地址，未应用 displacement，拷贝成功不报错但结果不符算子语义
- **影响对象**：数值结果（静默错误）
- **影响详情**：单 rank 调带非零位移的 V 算子时数据写到错误下标（如 recvDispls={3} 实写到 0、1）或读错片段；缓冲区足够、拷贝成功、无报错，仅数值与语义不符
- **改进措施**：检测 单 rank 单测覆盖三个 V 算子的非零位移用例并检查未涉及区域不变；现有测试未覆盖该组合；修复 待定（issue open，建议按算子类型计算有效源/目的地址后再同址判断与本地拷贝，并补三个 V 算子单 rank 非零位移回归；源码逻辑分析定位，无修复 MR）
- **来源**：https://gitcode.com/cann/hccl/issues/827
- **关联**：cross:INF-1425

### TRN-0351 `msllm_mc2_allgather_base_mm_nan` MC2 融合 all-gather 输出 NaN 污染 loss

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：集合通信 / mindspeed / npu_all_gather_base_mm
- **原因行为**：开 --use-ascend-mc2 后，MC2 列并行线性层里 npu_all_gather_base_mm 的输出整体为 NaN，通信与矩阵乘融合这条路径把中间结果污染成 NaN。
- **影响对象**：数值结果；训练信号（数值异常）
- **影响详情**：qwen3-32b 32k LoRA 训练 loss 变 NaN，改并行度与超参均复现；msprobe 溢出检测首个 NaN 为该算子输出（4096×75968 bf16）；关闭 use-ascend-mc2 后精度正常。
- **改进措施**：检测 msprobe 溢出检测看 npu_all_gather_base_mm 输出；或 A/B 开关 use-ascend-mc2；修复 issue #1393（closed）只给规避：关闭 use-ascend-mc2；未给修复 PR
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1393

### TRN-0361 `msllm_batch_p2o_comm_hccl_group_unbalanced` 开 batch_p2o_comm 后 HcclGroupEnd 未配对

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：集合通信 / mindspeed-llm / optimize_p2p_comm 批量下发
- **原因行为**：推断批量下发路径与 PP 调度实际收发次数/分支不一致，导致 HCCL group 调用不成对，HcclGroupEnd 缺少 HcclGroupStart。
- **影响对象**：可用性/进度（报错）
- **影响详情**：DSv4 整网训练在 recv_forward 的同步点抛 Inner error，PLOG 记 HcclGroupEnd: not in a group call，进程直接退出；关掉该开关即恢复。
- **改进措施**：检测 打开前后对比各 rank 的 HcclGroupStart/End 计数与 P2P 收发次数；PLOG 里筛 hccl_group.cc 的 group 配对告警；修复 issue 只提交复现与 PLOG 定位（closed，未附修复 PR，未核实）；规避是不开 config.batch_p2o_comm
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1525

### TRN-0384 `hccl_nhr_broadcast_uint32_slice_index_underflow` HCCL NHR Broadcast 切片索引 uint32 下溢收发错位

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：集合通信 / cann / NHR Broadcast 切片索引
- **原因行为**：接收切片索引 (rankIdx - deltaRank + N) % N 在 rankIdx < deltaRank 时 uint32 减法先下溢再提升，非 2 次幂 NHR 组接收切片编号算错，Tx 与 Rx slice 不一致
- **影响对象**：可用性/进度；数值结果（挂起）
- **影响详情**：一端跳过发送、另一端持续等待造成 Notify/CQ 超时；提交者已全量核对该模板内同型下溢风险（未给实机数值对照，无关联 issue）
- **改进措施**：检测 非 2 次幂 rank 数的 broadcast allgather 回归测试（hccl_test rdv）；修复 修复 MR https://gitcode.com/cann/hccl/merge_requests/3724 已 merged（批次状态 merged，2026-10-22；发布版本未核）
- **来源**：https://gitcode.com/cann/hccl/merge_requests/3724

### TRN-0404 `hcomm_allreduce_deterministic_pipeline_misaligned_split` HCCL allreduce 确定性 pipeline 数据切分阈值用错设备数

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：集合通信 / cann / AllReduceOperator::Determ
- **原因行为**：确定性 allreduce 判断数据切分是否对齐的阈值使用每聚合域设备数 deviceNumPerAggregation_，而切分应按参与通信的总 rank 数 userRankSize_ 对齐，特定规模下切分对齐判断错误。修复将阈值判断改
- **影响对象**：梯度；数值结果（静默错误）
- **影响详情**：使用确定性 allreduce 的分布式训练作业，在聚合域设备数与参与通信总 rank 数不同的部署（如多 die/多聚合域组网）下，特定机器/rank 规模时运行正常无报错，但梯度归约结果与正确值有偏差，loss 曲线可能无突变而模型更新方向偏离。
- **改进措施**：检测 同规模确定性 allreduce 与 CPU/单机参考对拍归约结果；跨 rank 一致性校验。；修复 修复 MR https://gitcode.com/cann/hcomm/pull/6258 与 https://gitcode.com/cann/hcomm/pull/6259（均 open，未合入未发布，未核实发布版本）。
- **来源**：https://gitcode.com/cann/hcomm/issues/1122；https://gitcode.com/cann/hcomm/pull/6258；https://gitcode.com/cann/hcomm/pull/6259

### TRN-0520 `hccl_reduce_scatter_v_prod_missing_barrier` HCCL ReduceScatterV 缺 barrier 静默错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：集合通信 / cann / ReduceScatterV AICPU 模板
- **原因行为**：ReduceScatterV 的 RDMA 写后仅 host 线程同步无 device DMA barrier，LocalReduce 可能读到未落盘 slot；非 V 版已修 V 版漏同步
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：多卡训练 ReduceScatterV 做 PROD 或 INT64/UINT64/FP64 归约时结果静默错误，梯度被污染致数值漂移，无报错无超时、随时序偶发；16 卡 INT32 PROD countSize=2097152 实测 exp:2147483647、act:-501334399
- **改进措施**：检测 规约结果与单卡参考对比；对 64 位/PROD 场景跑一致性自检；修复 修复 PR https://gitcode.com/cann/hccl/merge_requests/3805（open，未合入）：与非 V 版 !154 对齐补 HcommBatchModeEnd+Start+HcommThreadJoin barrier 并补 UINT64/FP64 判断
- **来源**：https://gitcode.com/cann/hccl/merge_requests/3805
- **关联**：cross:INF-2263

## 并行切分

### TRN-0014 `gtp_wgrad_dtype_breaks_fp32_reduce_contract` GTP 回退 wgrad 以 BF16 归约，破坏 FP32 梯度契约

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-08-19 · 旧号 NUM.05

- **原因对象**：并行切分 / megatron-lm / GTP 回退路径的 wgrad dtype
- **原因行为**：GTP 关闭梯度累积融合后 wgrad 走朴素 matmul 回退，dtype 跟随计算精度而非 main_grad，reduce-scatter 在 BF16 中跨 rank 求和后才进 FP32 累加器。
- **影响对象**：梯度（静默错误）
- **影响详情**：开启 --accumulate-allreduce-grads-in-fp32 时无 crash、无 NaN，梯度精度静默劣化，多卡与单卡结果系统性偏差。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6624

### TRN-0027 `simplefsdp_grad_reduce_rounds_fp32_sum_to_bf16` SimpleFSDP 把复制参数梯度的 fp32 和截回 bf16

`故障` · `active` · `pretrain` · `verified` · `NEW` · 发现 2026-10-10 · 旧号 NUM.18

- **原因对象**：并行切分 / torchtitan / SimpleFSDP 非分片参数梯度归约
- **原因行为**：pytorch#194434 令 FSDP2 非分片参数梯度默认取 reduce_dtype（torchtitan 下即 fp32），SimpleFSDP 以 fp32 求和却把和 round 回 bf16，router gate 梯度同。
- **影响对象**：梯度（静默错误）
- **影响详情**：无 crash；GraphTrainer 与 eager FSDP2 的 TP-replicated 参数（SP norm 权重、router gate）梯度系统性精度分叉，同 ckpt/seed 下 dense 与 MoE 模型从 step 2 起静默不同，A/B 对照结论被污染。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/5171

### TRN-0029 `zero2_bf16_multi_subgraph_incomplete_reduce` ZeRO-2 子模块复用时按计数提前触发归约，多卡静默丢梯度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 PAR.01

- **原因对象**：并行切分 / deepspeed / ZeRO-2 backward 参数计数触发归约
- **原因行为**：0.18.3 起用参与参数计数推断 backward 结束并触发 ZeRO-2 跨 rank 归约；同一 backward() 中子模块被主损失与辅助损失复用两次时，hook 触发次数与预测计数不符，归约在该参数梯度攒完前开火。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 warning；单卡 bitwise 正确，多卡静默丢一半子图梯度。LR=0 时 loss 与好版本一致，LR 一起主损失约翻倍、辅助项塌向退化解，需单卡对照才能发现。0.18.3–0.19.3 仍受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8224

### TRN-0031 `dp_consensus_washes_out_bad_rank` DP AllReduce 共识把单个坏 rank 的梯度洗进全局更新

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-08-17 · 旧号 PAR.03

- **原因对象**：并行切分 / 硬件 / DP 中单个坏 rank 的梯度
- **原因行为**：单个坏 rank 产出错误梯度，DP AllReduce 将其平均进全局更新；没有副本对照时，错误被「共识」合法化。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：预训练 DP 场景下，全局 grad norm 仅略有偏移，没有任何 rank-local 报警。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2608.11034
- **关联**：var:TRN-0007

### TRN-0032 `stale_placeholder_wgrad_poisons_main_grad` GTP placeholder wgrad 未清零，陈旧值进 main_grad

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-19 · 旧号 PAR.04

- **原因对象**：并行切分 / megatron-lm / GTP placeholder wgrad
- **原因行为**：GTP 给无梯度参数返回共享 dummy buffer 视图作 wgrad 且不清零；zero_out_wgrad 置位时 DDP post-hook 把它加进 main_grad，上次 backward 的陈旧值混入本 step。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：MTP 共享 embedding 场景下先静默产生错误梯度，dummy buffer 脏到一定程度才出现 NaN；Nemotron-next mxfp8 收敛 A/B 已见差异。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6565

### TRN-0033 `fsdp_degenerate_dp_group_grad_doubling` Megatron-FSDP 退化 DP 组归约使梯度按 2^N 放大

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-20 · 旧号 PAR.05

- **原因对象**：并行切分 / megatron-lm / 退化 DP 组的每 microbatch 归约
- **原因行为**：optim_grads_params 下每 microbatch reduce 对退化为单 rank 的 DP 组（EP=DP 时的 expert-DP 组或 DP=1）也归约，累加 g_k 变成乘 2 再累加，buf_N≈2^N·g。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：N≤约64 时方向正确但巨幅的梯度被 clip 归一，训练看似正常而 expert 更新已错；N=128 时 grad norm=inf，clip 把所有梯度乘约 0，run 以零梯度训练且 skipped iterations=0。关 clip 甚至表面收敛。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/6660

### TRN-0034 `fsdp_size1_mesh_shape_rank_confound` verl fsdp_size=1 致 FSDP1 不同步梯度

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-21 · 旧号 PAR.06

- **原因对象**：并行切分 / verl / device mesh 分片策略推导
- **原因行为**：fsdp_size=1 被表达为 2-D mesh，sharding 策略按 mesh 的 rank 数而非形状推导：FSDP 组 size=1 被判为无需分片，而 FSDP1 的梯度同步寄生在分片 allreduce 中，于是从不同步。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：多 GPU trainer 上 run 正常跑完，loss 下降，grad_norm/entropy/KL 全正常；ckpt 的 rank-0 副本只见过 1/world_size 的数据。生产中 2 个月未察觉：3 个 trainer rank 每次更新只用 48 条采样序列中的 16 条。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7493

### TRN-0035 `sp_kv_head_global_locks_first_model` Ulysses SP 进程级 kv 头数全局锁定为首个模型的值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-23 · 旧号 PAR.07

- **原因对象**：并行切分 / deepspeed / Ulysses SP 进程级 kv 头数全局
- **原因行为**：Ulysses SP 维护进程级全局 _ulysses_num_kv_heads，首次走 uneven-head all-to-all 时按第一个模型的头数 memoize，此后同进程头数不同的模型都按该值切分 all-to-all 布局。
- **影响对象**：隐状态；梯度（静默错误）
- **影响详情**：合法配置、无报错；同进程第二个模型（RL 参照策略或蒸馏 teacher）开 SP 时，其激活/梯度在 SP 边界被错误布局的 all-to-all 静默污染，参照 logprob 已坏，KL 探针与 TIM 校正失真。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8291

### TRN-0037 `cpu_typestring_bucket_skips_allreduce` ZeRO CPU 张量类型串不匹配，梯度 allreduce 被静默跳过

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-04 · 旧号 PAR.09

- **原因对象**：并行切分 / deepspeed / ZeRO 梯度类型串分桶
- **原因行为**：ZeRO-1/2 非连续梯度归约按 torch.{device}.FloatTensor 类型串分桶，CPU 张量类型串 torch.FloatTensor 无设备前缀，永不匹配，bucket 恒空，梯度 allreduce 整体被跳过。
- **影响对象**：梯度（静默错误）
- **影响详情**：CPU 多进程（gloo）路径触发，GPU 不受影响；无 crash、无警告，各 rank 用本地梯度更新。gradient_allreduce_op=mean 时完全不可见，sum 时结果错 world_size 倍，CPU 参考实现/测试会把错值当基线。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8382

### TRN-0038 `traced_all_to_all_zero_backward` compile 下 Ulysses all-to-all 断依赖致零梯度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-12 · 旧号 PAR.10

- **原因对象**：并行切分 / deepspeed / Ulysses SP all-to-all 交换
- **原因行为**：Ulysses SP 交换以写出参、不返回值的 all_to_all_single 填充 empty_like 输出；torch.compile inline 后无法建模该依赖，导数为零，手写 backward 不运行。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：仅在开 torch.compile 时触发：forward 数值完全正确，无 crash、loss 有限、无警告；q/k/v 投影零梯度，一步更新后参数逐位不变、optimizer moments 为 0，attention 静默停止学习，输出投影/MLP/残差流照常更新。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8491

### TRN-0039 `gtp_expert_grad_overscaled_by_gtp_egtp` Megatron GTP 下 expert 梯度被放大 GTP/EGTP 倍

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-09-12 · 旧号 PAR.11

- **原因对象**：并行切分 / megatron-lm / GTP 下 expert 梯度缩放因子
- **原因行为**：GTP 下 dense 参数经 gtp_remat 组 AVG 补回 DDP 的 1/DP 缩水，expert 参数只得到 EGTP 轴补偿，残留 GTP/EGTP 伪因子；expert 梯度 prescale 也用了缩小的 DP 组大小。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 NaN、无 crash；默认 EGTP=1 时每个 expert 更新放大 GTP 倍、方向不变，开全局 clip 时被归一掩盖，MoE 与 dense 学习率平衡被打破，只表现为收敛差距；A3B_30B GTP64 实测 grad-norm 偏 8.4×、params-norm 偏 8.7×。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7160；https://github.com/NVIDIA/Megatron-LM/pull/7165
- **关联**：var:TRN-0033

### TRN-0041 `liger_gate_skips_ddp_reducer_hooks` trl DPO/KTO 开 liger 时 DDP 梯度从不同步

`故障` · `active` · `sft` · `verified` · `NEW` · 发现 2026-09-17 · 旧号 PAR.13

- **原因对象**：并行切分 / trl / compute_loss liger 分支
- **原因行为**：开 liger 时 compute_loss 在未包装模型上前向，仅 ZeRO-3/FSDP 走 redirect；plain DDP 下 DDP.forward 不执行，reducer hooks 早退、从不 all-reduce。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：无 error/warning；2×H100 下 liger 开时 25/25 参数跨 rank 梯度不同，N 卡 DDP 退化为 N 个独立单卡跑，保存的 ckpt 只是 rank 0 的，收敛表象正常；分布式测试只断言 exit 0 而漏检。v1.10.0–v1.12.0 受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7245

### TRN-0042 `explicit_pg_collection_group_fallback` Megatron 显式进程组多路径静默回落全局 MPU 组

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 PAR.14

- **原因对象**：并行切分 / megatron-lm / MTP 重算/MoE/LLaVA/CP 进程组选择
- **原因行为**：传入非全局的显式进程组集合时，MTP 重算、MoE padding_mask scatter、CrossAttention、LLaVA embedding 仍用全局组；attention 还把 cp 组覆写回 build-time 组。
- **影响对象**：跨请求/跨样本数据；隐状态（静默错误）
- **影响详情**：无 crash/NaN：重算激活、SP all-gather、eval 分片拿到别的 replica 数据（4-rank 下 MTP 重算得 [0,1,12,13] 而非 [0,1,2,3]）；eval 首 batch 吻合、batch 2/3 误差 0.51/0.29，首 batch 掩盖问题。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452

### TRN-0043 `bridge_wan_gather_default_grad_sums_tp_copies` Bridge Wan SP gather 默认 grad 模式致梯度 ×TP

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 PAR.15

- **原因对象**：并行切分 / megatron-bridge / Wan decoder SP gather
- **原因行为**：Wan decoder 的 SP gather 用默认 tensor_parallel_output_grad=True，backward 做 reduce-scatter，但各 TP rank 算同一完整 loss，相同梯度被求和。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 crash、无 NaN，forward 输出与 loss 下降正常；decoder 权重梯度恰为 TP 倍（TP=2 时范数 7.89 vs 3.94），有效学习率 ×TP，收敛动态随 TP 度不可比；H100 Wan recipe（TP=2、CP=4、SP）默认中招。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452

### TRN-0045 `gradient_reduce_preprocessing_ignores_scaling_factor` MFSDP v1 忽略 scaling_factor 致梯度恒 ×DP

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-19 · 旧号 PAR.17

- **原因对象**：并行切分 / megatron-lm / MFSDP v1 梯度归约预处理
- **原因行为**：MFSDP v1 gradient_reduce_preprocessing 在 average_in_collective=True 时忽略 scaling_factor：梯度平均折进集合通信后，预处理阶段应配平的缩放不再施加。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 crash；DP=2 repro 中 expert 梯度为 [6,10] 而非 [3,5]（恒 ×2），有效学习率恒 ×DP，loss 照常下降但收敛动态随 DP 度不可比；经 Qwen3.5-35B-A3B MFSDP recipe（EP=2）真实可达。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452

### TRN-0047 `sp_gradient_avg_divisor_splits_across_zero_paths` DeepSpeed SP>1 时 ZeRO 梯度平均除数随归约路径分叉

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-29 · 旧号 PAR.19

- **原因对象**：并行切分 / deepspeed / ZeRO-3 非连续路径梯度除数
- **原因行为**：SP>1 时 ZeRO-1/2 与 ZeRO-3 连续桶路径除以 world_size/sp，ZeRO-3 非连续路径 __avg_scatter_grads 却除以整个 SP-DP 组；#4530 补 SP 因子时漏了后者。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无crash；sp=2时reduce_scatter路径梯度为其余0.5×，ZeRO-3默认走此；contiguous_gradients:true+reduce_scatter:false下超reduce_bucket_size单参数与其余参数除数不同；ALST时ZeRO-1/2步长sp×过量。
- **改进措施**：检测 待定；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8854 （2026-10-18 open 未合入）：__avg_scatter_grads 的 averaging_world_size 除以 sequence_parallel_size，与连续桶路径及 ZeRO-1/2 对齐；修复内含非重复查重说明
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8692；https://github.com/deepspeedai/DeepSpeed/pull/8854

### TRN-0049 `qgz_two_stage_weight_grad_scaled_by_local_ranks` DeepSpeed ZeRO++ qgZ 跨节点权重梯度被放大 L 倍

`故障` · `active` · `shared` · `verified` · `var` · 发现 2026-10-10 · 旧号 PAR.21

- **原因对象**：并行切分 / deepspeed / all_to_all_quant_reduce
- **原因行为**：ZeRO++ qgZ 跨节点 quantized_reduction 对 L 个本地 rank 与 N 个节点两级求和后只除以 N，2-D 权重梯度放大 L 倍；1-D 梯度走 fallback 返回真平均。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 crash；多节点 qgZ 下权重参数有效学习率放大 L 倍而 bias/norm 不放大，同一 step 内参数间更新尺度分裂、权重量级随节点数漂移，训练曲线无专属信号。4-rank repro：权重返回 −5.0、bias −2.5。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8729
- **关联**：var:TRN-0047

### TRN-0094 `sp_shard_cuts_causal_lm_labels` AutoSP 切 labels 丢边界监督，分片 loss 等权平均

`故障` · `active` · `pretrain；sft` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 DATA.12

- **原因对象**：并行切分 / deepspeed / AutoSP labels 序列分片；损失计算 / deepspeed / AutoSP 分片 loss 聚合
- **原因行为**：AutoSP 按序列维切 input_ids 时对 shift-by-one 的 labels 朴素同维切分，每片丢最后一个 token 的监督并在边界错位；各分片独立 mean 后等权平均，忽略各片有效 token 数。
- **影响对象**：训练信号；训练样本流（静默错误）
- **影响详情**：SP>1 时无 crash：每个分片边界丢监督、边界 token 监督错位、分片 loss 加权错值，预训练 loss 带结构性 bias，与 SP=1 基线不可比。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8457；https://github.com/deepspeedai/DeepSpeed/pull/8811

### TRN-0117 `tp_sharded_param_unmarked_skipped_by_grad_norm_filter` softmax_offset 未标 TP 分片致 grad norm 少算

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 OPT.17

- **原因对象**：并行切分 / megatron-lm / softmax_offset 的 TP 分片标记
- **原因行为**：softmax_offset 逐本地 head 创建、实为 TP 分片参数，却未标 tensor_model_parallel；_filter_grads_for_norm 只在 TP rank 0 保留它，其余 rank 梯度被漏计。
- **影响对象**：梯度；指标/日志（静默错误）
- **影响详情**：GPT-OSS learnable attention sink + TP>1 时 grad norm 偏小（2-rank repro 得 3 而非 5），该触发的 clip 被跳过，全部参数裁剪强度漂移；相对误差约 1e-3、随 head 分布变化，无 crash、无 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452；https://github.com/NVIDIA/Megatron-LM/pull/7530

### TRN-0118 `gdn_shared_out_norm_missing_tp_grad_sum` Megatron GDN out_norm 在 SP 关闭时漏做 TP 梯度求和

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 OPT.18

- **原因对象**：并行切分 / megatron-lm / GDN out_norm TP 梯度求和
- **原因行为**：GDN 的 out_norm 是作用于所有 TP 切分 head 的共享向量；finalize_model_grads 只在 SP 开启或名含 q/k_layernorm 时做 TP 梯度求和，SP 关时它从不 all-reduce。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：GDN + TP>1 + SP 关时各 TP 副本只持部分和，out_norm 权重自第一步起确定性分叉并偏小（20 步 Adam 后两副本差 0.0039）；无 crash、无 NaN，下游 loss 无即时信号。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452；https://github.com/NVIDIA/Megatron-LM/pull/7613

### TRN-0286 `zero2_overlap_comm_stream_race_nan_weights` DeepSpeed 0.18.5-9 ZeRO-2 overlap 竞态 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：并行切分 / deepspeed / IPG bucket swap 前的双向流同步被删
- **原因行为**：v0.18.5 起 PR #7805 删掉 IPG bucket swap 前的双向流同步，异步 reduce-scatter 在飞时 buffer 被回收复用；正解 record_stream v0.19.0 才合入。
- **影响对象**：梯度；模型权重；训练信号（数值异常）
- **影响详情**：第 1 步 backward 梯度即 NaN；第 1 个 optimizer step 把 NaN 写进权重，第 2 步起 loss=0。grad_norm 恒 √2（NaN 范数被掩成 -1 后合并），伪值掩盖真实 NaN。
- **改进措施**：检测 grad_norm 恒等于 √(param_group 数)（2 组即 √2）即可判定底层梯度 NaN；或第 2 步起 loss 塌 0。；修复 上游修复 PR #7965 已随 v0.19.0 发布（#8061/#8080 于 v0.19.3 补 torch.compile 多流 producer 场景）；规避：overlap_comm=false 或升级 deepspeed >= 0.19.3。ms-swift install_all.sh 的 "deepspeed<0.19" 约束会精确装进受影响窗口，issue 建议提升约束（open 未合）。https://github.com/deepspeedai/DeepSpeed/pull/7965
- **来源**：https://github.com/modelscope/ms-swift/issues/10372；https://github.com/deepspeedai/DeepSpeed/pull/7965；https://github.com/deepspeedai/DeepSpeed/pull/7805

### TRN-0324 `megatron_fsdp_v1_grad_acc_fusion_wgrad_overwrite` Megatron-FSDP v1 梯度累积融合覆写未分片 wgrad

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：并行切分 / megatron-lm / FSDP v1 local Linear 反向
- **原因行为**：ColumnParallelLinear 在 gradient_accumulation_fusion=True 且 FSDP v1 下，FSDP 反向把 wgrad 写入持久未分片缓冲，覆盖此前 microbatch 已累积值。
- **影响对象**：梯度（静默错误）
- **影响详情**：多 microbatch 梯度累积下权重梯度只保留最后一个 microbatch 的贡献，前一 microbatch 分量被静默覆盖；无报错、无 NaN，梯度数值看似合理但错。单卡 16x16 Linear 双 microbatch（各贡献 8/96）实测应为 104 实得 96。
- **改进措施**：检测 对照关闭 gradient_accumulation_fusion 或启用真实分片的运行，比对逐步 wgrad（issue 提供 16x16 单卡确定性 repro，control 全部通过）。；修复 待定（issue 2026-10-19 open，@mcore-oncall，无修复 PR；repro 脚本带 --fix 对照）
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/8332

### TRN-0328 `mindspeed_llm_sp_grad_reduce_scatter_residual_chunk_bf16` SP 梯度 reduce-scatter 残块 bf16 归约精度发散

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：并行切分 / mindspeed-llm / SP 梯度 reduce-scatter 残块归约
- **原因行为**：grad reduce-scatter 沿序列维切分；seq_len 不整除 SP world_size 时尾部 residual chunk 单独 allreduce，bf16 多一次 cast 损失，边界 grad 跨 rank 不齐。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：训练 seq_len 从 4096 扩到 4608、开 SP、bf16 时，序号 4096~4608 的 grad 在各 SP rank 间出现量级差异，update 后参数沿 SP 维不统一，loss 逐步发散；日志无异常，需逐 chunk allclose 才看得到。
- **改进措施**：检测 对 _reduce_scatter_along_first_dim 的输出按 chunk 做跨 rank allclose 比较；或临时改 fp32 归约复跑同一 step 对比 loss。；修复 issue 建议把 residual chunk padding 到 align_size 再 allreduce、之后 strip，或 SP 归约改用 fp32；issue 已 closed，未在正文给出对应 PR 与合入版本（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1598
- **关联**：var:TRN-0014

### TRN-0329 `mindspeed_llm_cp_rope_position_offset_tp1_zero` CP+TP=1 时 RoPE position offset 恒为 0

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：并行切分 / mindspeed-llm / CP 下 RoPE position id 初始化
- **原因行为**：cp_rank 的序列偏移依赖 tp_size 分支：TP>1 才按 cp_rank*(seq_len//cp_size) 算，TP=1 时置 0，两个 CP rank 的 rope cos/sin 都从 position 0 起。
- **影响对象**：数值结果；隐状态；训练轨迹（静默错误）
- **影响详情**：CP=2、TP=1 且启用带 RoPE 的 sequence parallel attention 时，两个 rank 的 attention 输出在 CP 切分边界附近对不上；训练不报错、不出 NaN，精度与单卡/CP=1 对齐不上，长序列位置语义整体错位。
- **改进措施**：检测 打印各 CP rank 首个 token 的 position id 与 rope cos/sin 头部值，按 cp_rank*(seq_len//cp_size) 对账；或对比 CP=2 与 CP=1 的 token 级 hidden state。；修复 issue 建议把 cp_offset 的计算与 tp_size 解耦，只由 cp_rank 与 cp_size 决定；issue 已 closed，正文未给出对应 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1599

### TRN-0336 `mindspeed_te_rowparallel_parallel_mode_none_still_comm` parallel_mode 置空后仍做 TP 通信

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：并行切分 / mindspeed / TE RowParallel 通信判定
- **原因行为**：TERowParallelLinear 未处理 parallel_mode=None：非序列并行仍调 matmul_all_reduce、序列并行仍调 matmul_reduce_scatter，而置 None 的语义是不做 TP 通信。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：开 moe_shared_expert_overlap 时 mcore 把共享专家的 linear.parallel_mode 置 None 期望跳过 TP 通信，实际仍重复 all-reduce/reduce-scatter，共享专家输出被多归约一次导致结果错，无报错。
- **改进措施**：检测 开 moe_shared_expert_overlap 后比对该层的通信次数与关闭 overlap 的等价配置；对比 TP=1 与 TP>1 的共享专家输出。；修复 issue 建议在 TERowParallelLinear.forward() 中检测 self.parallel_mode is None，切到无 TP 通信的 matmul 路径；issue 已 closed，正文未给出合入 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed/issues/209
- **关联**：cross:INF-0373

### TRN-0347 `mindspeed_cp_pad_data_negative_seq_len` CP 长序列 pad_data 把 -1 填充算进序列长度

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：并行切分 / mindspeed / context_parallel pad_data
- **原因行为**：pad_data 对含 -1 占位的 actual_seq_len 直接 torch.diff，算出 -166 这类负段长，再用它构造 arange(start,end) 时上下界与 step 符号矛盾。
- **影响对象**：可用性/进度；训练样本流（报错）
- **影响详情**：长序列 + CP=4 的 SFT 取 batch 时崩：actual_seq_len=[19,165,-1,...] 使 per_seq_lens 出现 -166，start=192/end=26，抛 upper bound 与 step 符号矛盾。
- **改进措施**：检测 在 pad_data 打印 per_seq_lens，检查是否出现负段长（actual_seq_len 尾部 -1 占位）；修复 issue #165（open）未给修复；须在 torch.diff 前剔除 -1 padding 项
- **来源**：https://gitcode.com/Ascend/MindSpeed/issues/165

### TRN-0355 `msllm_tnd_cp_empty_rank_collective_desync` TND+CP 空 rank 跳过 indexer 反传致挂起

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：并行切分 / mindspeed-llm / DSv4 CSA indexer CP 分支
- **原因行为**：CP 下某 rank 的 KV 段全短于 compress_ratio 就跳过 indexer/compressor 与索引 loss 反传，非空 rank 仍发 CP all_gather，两边梯度 bucket 不一致。
- **影响对象**：可用性/进度；梯度（挂起）
- **影响详情**：空 rank 场景下 backward collective 顺序不一致直接 hang；空 rank 还缺 indexer/compressor 的 grad hook 与 bucket，用 dummy KV 硬闯会 shape 校验失败或非法索引。
- **改进措施**：检测 统计各 rank 的 compressed KV 段数，空 rank 与非空 rank 的 loss tracker key、grad bucket 顺序比对；修复 issue #1895（closed）给出方案：_ZeroGradientAnchor 造显式零梯度、_EmptyIndexerLossCommunicationAnchor 让空 rank 参与 CP collective、gather_tnd_local_num() 统一 dtype/shape/process group
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1895

### TRN-0468 `mindspeed_cp_eod_zigzag_layout_mismatch` MindSpeed CP EOD zigzag 切分布局不一致致 loss/

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：并行切分 / mindspeed / CP KV all-gather 切分
- **原因行为**：reset-attention-mask+causal+all_gather+CP>1 组合下 batch 路径用 zigzag 切分，而 TENPU THD all-gather 要求各 rank 持连续分片。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：loss 与梯度偏差，部分数据下 grad_norm 接近 CP=1 基线的一半；无报错，训练持续运行。
- **改进措施**：检测 CP>1 与 CP=1 基线对比 loss/grad_norm；EOD 多文档数据下 grad_norm 偏差可观察；修复 已修复：https://gitcode.com/Ascend/MindSpeed/merge_requests/4109（merged，2026-10-27）+ !4110（26.2.0 分支）——该组合回退顺序切分，同步处理 tokens/labels/loss_mask/position_ids；修复后 CP=4 vs CP=1 连续 50 步 loss 最大绝对差 6.8e-4、grad_norm 最大相对差 0.169%
- **来源**：https://gitcode.com/Ascend/MindSpeed/merge_requests/4109

### TRN-0472 `deepspeed_autotp_mq_kv_replica_drift` DeepSpeed AutoTP 多查询 K/V 副本梯度不归约致漂移

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：并行切分 / deepspeed / AutoTP fused QKV 切分
- **原因行为**：_bigcode_type_transpose 给每 rank 返回其 query 切片拼接整块共享 K/V 行；各 rank 对复制 K/V 行算出部分梯度，column-parallel 的权重梯度留本地
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：TP>1 下 c_attn.weight/bias 的 K/V 行在各 rank 间漂移：实测 TP2 一步后 rank0/rank1 的 K/V 行梯度与单卡相对误差 0.81/0.61（rank 求和后 2.7e-7 证明梯度本可对齐）；训练静默发散于单卡结果。
- **改进措施**：检测 对比 TP>1 与单卡的 c_attn K/V 行梯度；各 rank K/V 行参数逐 step all-gather 对比；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8928（merged 2026-10-30T01:04:53Z，issue 同刻 closed）；发布版本未核实
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8927

### TRN-0504 `megatron_expert_wgrad_overlap_ddp_stale_grad` Megatron 专家 wgrad overlap 下 DDP 旧梯度重复累加

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：并行切分 / megatron-lm / get_megatron_ddp_config
- **原因行为**：专家 wgrad overlap 使 DDP 挂 autograd 钩子而非 backward_dw 钩子：专家 param.grad 永不清零，旧梯度下次迭代再累加进 main_grad。
- **影响对象**：梯度（不可复现）
- **影响详情**：Nemotron 3 Nano 2×GB200 EP8 HybridEP：开该选项后每次运行自第 2 迭代起 grad norm 都不同（该选项时才现）；旧梯度重复进 main_grad，专家权重梯度错。
- **改进措施**：检测 对比开/关该选项的逐步 grad_norm（第 1 迭代一致、第 2 迭代起分歧为指纹）；检查专家参数 param.grad 是否跨迭代残留；修复 修复 PR https://github.com/NVIDIA/Megatron-LM/pull/8613（open，2026-10-28）——DDP 在 backward_dw 处注册专家梯度钩子（对齐 --delay-wgrad-compute 既有机制）
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/8613

### TRN-0513 `mfsdp_v2_backward_prefetch_stale_weights` Megatron MFSDP v2 预取错序静默用旧权重

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：并行切分 / megatron-lm / MFSDP v2 prefetch
- **原因行为**：MFSDP v2 按静态注册序预取，模块执行序与注册序不同时反向序预测错误，对已完成 post_backward 的模块重复预取且不释放 gather，step 后该模块权重不换新也不报错
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：从第二步起部分模块用 step 前的旧全量权重做前向/反向，loss 逐步漂移（2 GPU fp32 SGD 实测 5 步 max|Δloss| 2.27e-3），无任何报错或警告
- **改进措施**：检测 对比 prefetch 关闭前后的 loss/梯度；检查 step 后 Parameter 是否仍为 unsharded 状态；修复 修复 PR https://github.com/NVIDIA/Megatron-LM/pull/8687（open，未合入）：FsdpContext 用 weak set 记录本趟已完成 post_backward 的模块并跳过对其预取
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/8687

### TRN-0550 `deepspeed_sequence_tiled_compute_inplace_grad_division` SequenceTiledCompute 原地除共享入梯度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：并行切分 / deepspeed / TiledCompute backward
- **原因行为**：SequenceTiledCompute.backward 对传入梯度原地 /= shards：tiled+other 复合 loss 下 autograd 把同一张量发给两分支，另一项梯度也被除 shards 倍
- **影响对象**：梯度（静默错误）
- **影响详情**：把 sequence_tiled_compute 输出与任何其他项相加且 output_reduction=mean 时，另一项梯度被静默除以 shards；TiledMLP 不改写入梯度、TiledFusedLogitsLoss 只除自己的张量，无此缺陷；CPU 测试修前失败、修后 26 通过
- **改进措施**：检测 对 tiled+other 复合 loss 与单卡参考对拍梯度；检查 autograd 传入梯度是否被原地修改；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8960（open，改为 out-of-place 除法，未合入）
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8960

## KV缓存

### TRN-0346 `msllm_kvcompress_fp32_compressor_recursed_cast` MindSpeed-LLM kv-compress 误压 fp32 权重

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：KV缓存 / mindspeed-llm / Float16Module 与 wkv/wgate
- **原因行为**：开 --kv-compress 时 Float16Module.__init__ 对整个模块递归 cast 到 bf16，把按 fp32 构造的 compressor wkv/wgate 一并降精（设计计算保持 fp32）。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：--kv-compress 训练 DeepSeek-V4 时 compressor 的 wkv/wgate 以 bf16 参与计算，与设计的 fp32 计算路径偏离，精度静默损失；无报错。
- **改进措施**：检测 训练初始化后打印 compressor wkv/wgate dtype（应为 fp32）。；修复 修复 MR https://gitcode.com/Ascend/MindSpeed-LLM/merge_requests/5176（open）：新增 compressor2fp32_fp16module_init_wrapper，在 Float16Module.__init__ 后把 compressor wkv/wgate 重新 cast 回 fp32，经 CSAFeature.register_patches 按 --kv-compress 门控注册（沿用 dsa_indexer/mhc fp32-init wrapper 同款机制）；验证 py_compile + patch 叠加，NPU 端到端未运行。
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/merge_requests/5176；https://gitcode.com/Ascend/MindSpeed-LLM/issues/1933

### TRN-0479 `opstransformer_indexer_quant_cache_neg_slot_stomp` IndexerQuantCache 负 slotMapping 静默踩写其它

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：KV缓存 / cann / aclnnIndexerQuantCache。
- **原因行为**：aclnnIndexerQuantCache 的 host/tiling 对 slotMapping 无值域校验（资料声明 [-1,num_slots-1]）：负值被 kernel 当合法 slot 参与地址计算
- **影响对象**：KV状态；数值结果（静默错误）
- **影响详情**：上层 padding/掩码算出 -2 类 slot 时静默写坏其它 token 的 KV Cache：两段返回 0、4 字节落点固定（首错下标 8184），模型输出漂移难定位；64/65 越界正 slot 则静默丢弃。
- **改进措施**：检测 slotMapping 直方图断言（全部 ∈ {-1} ∪ [0, num_slots)）；KV cache 写后读校验；修复 待定（issue open 2026-10-27；建议对齐 aclnnScatterPaKvCache 的 tiling 值域校验：x==-1 || 0<=x<blockNum*blockSize 否则 161002）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6812

## 调度/服务

### TRN-0318 `trl_gemma3_server_mode_image_features_misplaced` trl vLLM server 模式 Gemma3 图像特征错位被静默忽略

`故障` · `active` · `rl；sft` · `documented` · `NEW` · 发现 2026-10-19

- **原因对象**：调度/服务 / trl / VLLMGeneration 图像特征定位
- **原因行为**：_place_features 以 processor 的 image_token_id（Gemma3/5.x 为 255999）定位特征 run，实际替换的 placeholder 是 262144，特征放错位置与长度。
- **影响对象**：输入编码；训练样本流（静默错误）
- **影响详情**：vLLM 生成完全忽略图像（纯红图+颜色提问→回答『无法判断颜色』而非『Red』）；GRPO/RLOO/Distillation/GOLD/SDFT/SDPO/IW-OPD 所有 server 模式 trainer 中招；无任何报错
- **改进措施**：检测 固定纯色图 +『What color』提示 + 贪心解码，检查 rollout completion 是否描述图像；对比 model.config.image_token_id（262144）与 processor.image_token_id（255999）的 run 长度；修复 修复 PR https://github.com/huggingface/trl/pull/7773 已于 2026-10-19 closed 且未合入（merged_at=None），缺陷仍在 main；无替代修复。
- **来源**：https://github.com/huggingface/trl/issues/7772；https://github.com/huggingface/trl/pull/7773

## 输出解析

### TRN-0549 `trl_parse_response_qwen35_unclosed_think_region` TRL parse_response 未闭合 think 吞工具调用

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：输出解析 / trl / parse_response 前缀区解析
- **原因行为**：Qwen3.5 模板预填 <think>\n；模型跳过思考直接输出正文+<tool_call> 且不闭合 </think> 时整段留在 reasoning_content：无 tool_calls、不抛异常
- **影响对象**：输出内容；训练信号（静默错误）
- **影响详情**：GRPO/agent RL 训练中，模型某轮跳过思考时 rollout 解析出的消息 tool_calls 为空，reward 按无工具调用给分，该批样本训练信号静默错误；解析不报错，需抽查解析结果才能发现；早期轮次无思考的对话常见（OpenAI 客户端回传历史时剥 reasoning）
- **改进措施**：检测 对含预填 <think> 前缀的样本断言解析结果 reasoning_content 为空或闭合；统计无 tool_calls 比例突变；修复 待定（issue open：需解析器在 completion 未闭合 region 时按正文处理或报错）
- **来源**：https://github.com/huggingface/trl/issues/8050

## 解码/采样

### TRN-0379 `vllm_ascend_rl_sampler_q_premature_reuse` RL 采样 q 显存异步除完成前被复用训推不一致

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：解码/采样 / vllm / sampler probs.div_(q)
- **原因行为**：异步原地除 probs.div_(q) 完成前 q 的 NPU memory 被提前复用/再分配，采样分布与训练侧重算 logprob 的输入分叉
- **影响对象**：输出分布；训练信号（静默错误）
- **影响详情**：DeepSeek v4 Flash RL post-training（NPU、rollout 与训练同进程/同卡池）中，rollout 采样与训练侧重算的 logprob/分布不一致，重要性比值漂移、策略更新方向异常，reward 不涨或策略慢慢跑偏；无报错无 NaN、单测都绿，修复前难定位。
- **改进措施**：检测 RL 回路内对 rollout 采样 logprob 与训练侧重算做 KL/比例抽检；修复 修复 PR https://github.com/vllm-project/vllm-ascend/pull/19461（open，2026-10-22，release/v0.23.0 backport）：对 q 记录当前 stream 防止提前再分配；作者自述 DeepSeek v4 Flash RL 端到端验证修复、sampler UT 通过
- **来源**：https://github.com/vllm-project/vllm-ascend/pull/19461；https://github.com/vllm-project/vllm-ascend/pull/13394

### TRN-0505 `vllm_ascend_v1_sampler_logprobs_mode_rl` vllm-ascend V1 runner 不透传 logprobs 模式

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：解码/采样 / vllm / V1 runner 构造采样器
- **原因行为**：V1 runner 构造 AscendSampler 时不转发 logprobs_mode，配置 processed 等模式的引擎仍以默认 raw 模式初始化采样器。
- **影响对象**：输出分布；训练信号（静默错误）
- **影响详情**：V1 runner 下配置 processed_logprobs 等非 raw_logprobs 模式时，Ascend 采样器静默以默认 raw 口径工作，rollout 侧报告的概率/logit 语义与配置不符，RL 训推一致性度量（MiniMax-M3.1-Flash）随之漂移；无报错。
- **改进措施**：检测 断言 AscendSampler 的模式字段与 model_config.logprobs_mode 一致；比对训练侧与 rollout 侧 logprob 口径；修复 修复 PR https://github.com/vllm-project/vllm-ascend/pull/20146（open，2026-10-28）——runner→sampler 边缘转发模式；构造回归覆盖四模式+缺省回退（未修复代码四断言全失败）
- **来源**：https://github.com/vllm-project/vllm-ascend/pull/20146
- **关联**：cross:INF-2250

## 量化

### TRN-0010 `fp8_bias_invariant_martingale_divergence` FP8 训练乘法噪声打破全 1 方向抵消致鞅式发散

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 NUM.01

- **原因对象**：量化 / 通用 / FP8 低精度梯度下降算术
- **原因行为**：Softmax-CE/LayerNorm 输入沿全 1 向量的梯度在精确算术下抵消，低精度乘法噪声打破抵消，使行均值 mₜ 成为无漂移鞅，累积能量趋于无穷。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：loss 尚未分叉时 Ēₜ 已比 BF16 高一个数量级，有效秩向个位数塌缩，weight decay 挡不住，参数最终几乎必然发散；本实验室 gpt-size E4 上见 realized_var 提前抬升。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：Zheng, Huang, Liang, "Mean-Square Divergence of Low-Precision Gradient Descent"（华为）。

### TRN-0018 `mixed_precision_cast_sweeps_quantized_params` DeepSpeed 混精 cast 把冻结的 FP8/MX 权重转成 bf16

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 NUM.09

- **原因对象**：量化 / deepspeed / engine 混精 cast 的浮点判定
- **原因行为**：engine 混精转换按 is_floating_point() 一刀切，FP8/MX/NVFP4 均判为浮点，冻结的量化权重被整体 cast 成 bf16；MX 的 e8m0 scale 存的是指数，cast 后不能还原。
- **影响对象**：模型权重；数值结果（静默错误）
- **影响详情**：frozen 量化基座 + LoRA 场景在 initialize 即触发：FP8/MX 面完全静默，训练照常但量化表示与 scale 语义被毁、权重占用翻倍，LoRA 产物对量化部署不可用；NVFP4 面直接 NotImplementedError。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8414

### TRN-0023 `qdora_magnitude_vector_downcast_silent_noop` trl QLoRA 路径把 QDoRA magnitude 降为 BF16

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 NUM.14

- **原因对象**：量化 / trl / SFTTrainer QLoRA 参数下转型
- **原因行为**：SFTTrainer 的 QLoRA 路径在 setup 时统一下转型参数，把 DoRA/QDoRA 的 lora_magnitude_vector 从 FP32 降到 BF16，其每步更新量小于 BF16 精度，被舍入吞掉。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：无 crash、无 warning：参数保持 trainable、optimizer 正常 step，但 magnitude 全程逐位不变，只剩方向分量更新；loss 可能照常下降，质量偏差延迟可见，只能显式 diff 前后值发现。DoRA（FP32）对照正常更新。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7268

### TRN-0058 `mxfp8_roundtrip_requant_scale_drop` MXFP8 ckpt 往返重量化非幂等，block scale 掉指数

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-20 · 旧号 CKPT.09

- **原因对象**：量化 / megatron-lm / fp8-param-gather ckpt 存取
- **原因行为**：fp8-param-gather 的 ckpt 只存 BF16 反量化权重、不存 MXFP8 scale；load 重量化时 block max ≤ 224·s 则 scale 掉一个 E8M0 指数，该 block 全部 code 翻倍。
- **影响对象**：模型权重（静默错误）
- **影响详情**：加载成功、训练继续，GEMM forward/dgrad 0 差异；但量化编码逐元素差 −1 code（GB300 单 tensor 1664/32768），零容差 ckpt parity check 失败，resume 后量化编码与 fp32 master 的派生关系断裂。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6666

### TRN-0142 `precision_override_never_reaches_fused_grouped_mlp` per-layer 精度覆盖到不了 fused grouped MLP

`故障` · `active` · `pretrain` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 KER.11

- **原因对象**：量化 / megatron-lm / op-fuser grouped-MLP 融合判定
- **原因行为**：grouped-MLP fused kernel 仅支持 FP8/NVFP4 且从全局 autocast 取 recipe，_with_fused_impl 不检查 fc1/fc2 是否 opt-out，per-layer 精度覆盖到不了。
- **影响对象**：数值结果（静默错误）
- **影响详情**：经 --te-precision-config-file 把 grouped expert 层设为 bf16 时，纯 TE 路径下该层仍按全局 autocast 跑 FP8/NVFP4，无日志无报错；GTP 路径下 backward 报 AttributeError。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7212

### TRN-0156 `quantized_expert_layout_republish_breaks_sync` verl DSv4 RL 量化专家布局被 SGLang 重发布，破坏同步

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-09-05 · 旧号 MOE.07

- **原因对象**：量化 / verl / 训练→rollout 量化专家权重同步
- **原因行为**：SGLang 加载后做 CUTLASS interleave，把专家参数重发布为新 Parameter，丢失 weight_loader 等属性；rollout 端为 interleave 后布局，与训练端 packed 布局不一致。
- **影响对象**：模型权重；输出分布（静默错误）
- **影响详情**：每次训练→rollout 权重同步在 deepseek_v4.py 抛 AttributeError；若布局差异被静默容忍（如 sentinel 协议回退），rollout 将采样自按错误 interleave 解释的专家权重。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7747
- **关联**：var:TRN-0050

### TRN-0244 `fp8_moe_repack_blind_to_same_shape_rewrite` verl FP8 refit 对同形状 MoE 重排失明，权重按错误布局写入

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-28 · 旧号 RL-RO.22

- **原因对象**：量化 / verl / FP8 refit MoE 重排检测
- **原因行为**：staging 检测用的 shape/dtype 与 is_shuffled 信号对同形同 dtype 的 MoE 重排（如 swap_w13_to_w31）失明，refit 把 canonical 布局权重写进重排后的 buffer。
- **影响对象**：模型权重；输出分布（静默错误）
- **影响详情**：修复前无 crash：每次 refit 后 rollout 侧 FP8 MoE 专家权重按错误布局解释，分布静默偏离训练侧；触发于 rollout.quantization=fp8 + Hopper + EP>1（自动选 FlashInfer CUTLASS MoE）。端到端影响未量化。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7986
- **关联**：var:TRN-0232

### TRN-0312 `opstransformer_swiglu_mx_scale_tail_pad_stale` CANN SwiGLU MX scale 行尾填充槽残留旧值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-18

- **原因对象**：量化 / cann / SwiGLU MX scale 写回
- **原因行为**：SwiGLU MX scale 每行按 64 输出元素存一对 K32 scale；有效 K32 分组数为奇数时，行尾完整填充槽未被覆盖，输出缓冲区旧值残留。
- **影响对象**：数值结果；模型权重（静默错误）
- **影响详情**：无报错。下游按行读取 scale 时把残留旧字节当成合法 scale 编码消费，量化权重/激活 scale 在奇数 K32 分组的行上来自未定义的旧内存；主机级验证为 padding 槽保留非零哨兵，硬件端到端数值精度未验证。
- **改进措施**：检测 将 scale 输出缓冲区预填非零哨兵，跑奇数有效 K32 分组宽度（outputN=32/96）检查行尾 padding 槽是否为零。；修复 修复 MR https://gitcode.com/cann/ops-transformer/merge_requests/14006（open）：HasSwigluMxScalePadding 判定尾块归属，尾 tile 清零 staging 并把写回长度加一字节；主机单测覆盖 outputN=1~1024×tileSize=32/64/128/256，未验证设备数值精度
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6247；https://gitcode.com/cann/ops-transformer/merge_requests/14006

### TRN-0350 `msllm_fsdp2_mxfp8_quantizeconfig_field_mismatch` FSDP2 mxfp8 配置字段名不匹配致量化静默跳过

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：量化 / mindspeed-llm / QuantizeConfig 字段映射
- **原因行为**：本地 QuantizeConfig 传给 FSDPTurbo 的 build_model_converter，recipe_name 对不上 quant_recipe 使量化门控恒 None，converters 字段也不匹配。
- **影响对象**：性能/资源；模型权重（性能退化）
- **影响详情**：mxfp8 训练要么在 ModelConvertersContainer 初始化就崩，要么门控提前返回、整条 mxfp8 量化路径没生效而训练照常跑完；quant_format/block_size/fsdp_world_size 缺失时 get_mxfp8linear_config 报错。
- **改进措施**：检测 训练启动后确认 build_model_converter 真正产出了 mxfp8 converter，而不是门控返回 None；修复 MR !4962（open，未发布）：把 QuantizeConfig 字段名适配到 FSDPTurbo 的 mxfp8 定义
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1783；https://gitcode.com/Ascend/MindSpeed-LLM/merge_requests/4962

### TRN-0364 `msllm_low_precision_opt_duplicate_router_bias_patch` 低精度优化器重复打 router bias 补丁致导入失败

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：量化 / mindspeed-llm / 低精度优化器 patch 注册
- **原因行为**：MoE 特性已给 _update_router_expert_bias 打过补丁，低精度优化器在 register_patches 里再打一次，MindSpeed 的 patch 校验发现重复就抛错。
- **影响对象**：可用性/进度；优化器状态（报错）
- **影响详情**：MoE（已打 router bias 补丁）模型下启用--quant-states/--quant-grads，import阶段即报RuntimeError: the patch of _update_router_expert_bias exist，低精度优化器与MoE组合完全不可用。
- **改进措施**：检测 apply_features_patches 前打印已注册 patch 列表；对同一 orig_func 的重复注册做去重与告警；修复 issue 已提修复 PR https://gitcode.com/Ascend/MindSpeed-LLM/pull/4473，做法是去掉重复注册的那次补丁（PR 状态未核实）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1371

### TRN-0387 `opsnn_dequant_swiglu_quant_no_group_mode0_training` DequantSwigluQuant 无 group 变体模式静默按 mode0

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：量化 / cann / DequantSwigluQuant tiling
- **原因行为**：变体 SwiGLU 适配只覆盖 Dsk 路径（group 场景），无 group 时路由至通用 tiling 链路，该链路无 mode/clamp_limit/glu_alpha/glu_bias 参数管道、内核硬编码标准 SwiGLU
- **影响对象**：数值结果（静默错误）
- **影响详情**：A2(910B) 不传 group_index 时 swiglu_mode 1/2/3 静默按 mode0：clamp_limit/glu_alpha/glu_bias 全丢失，int8 与 golden 一致率 24%/44%/56%，mode2 输出与 mode0 100% 相同，无报错
- **改进措施**：检测 no-group 调用后对拍文档公式 golden（clamp 语义丢失误配立即显形）；或带 group_index=[T] 对照；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/12598（open，2026-10-22）：no-group+mode≠0+int32/bf16 路由至 Dsk Base kernel；连带修复 shape 未初始化（blockDim=0）、mode1 gather 偏移表未建 UB 越界、bf16 WITHOUT_GROUP 分支缺失；fp16 x + mode≠0 改显式拒绝（原静默错算）；33 用例 910B3 实测全过
- **来源**：https://gitcode.com/cann/ops-nn/issues/7225；https://gitcode.com/cann/ops-nn/merge_requests/12598
- **关联**：cross:INF-2138

### TRN-0397 `opsnn_add_rms_norm_quant_multi_defects_large_number_overflow` AddRmsNormQuant 大 epsilon 下溢与大数中间溢出错量化

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：量化 / cann / AddRmsNormQuant V1/V2 数值
- **原因行为**：PERF 路径大 epsilon 下 Newton-Raphson 中间倒数下溢，应非零的归一化结果变 0；有限大数输入因加法/平方或 norm*gamma 中间溢出产出错误量化结果。
- **影响对象**：数值结果（静默错误）
- **影响详情**：大 epsilon（如 FLT_MAX）时 y1/resOut 为 0（参考 5/5.421）；x1=1e20 级输入量化输出 0 或错值；dst_type int64 属性按 int32 读取、rstd 32B 缓冲区按每核行号索引越界等多重缺陷并存。
- **改进措施**：检测 大 epsilon 与大数有限输入边界用例对拍 FP64 参考；dst_type 属性回读校验。；修复 待定（issue open 2026-10-23，Ascend950PR/CANN 9.3.0 weekly，基线 e3f2542，含 kernel 验证记录但未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7272

### TRN-0420 `ops_transformer_gmsq_quant_param_validation` GMSQ 量化融合算子参数静默忽略与延迟异常

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：量化 / cann / aclnnGroupedMatmulSwigluQ
- **原因行为**：A8W8 场景传非空 bias 被完全忽略（输出与不传逐字节相同，资料要求报 161002）；groupList 只校验长度不校验取值，负值/非单调/末值越界/全零均两段返回 0，错误延迟到 sync 以 507015 暴露。
- **影响对象**：数值结果；可用性/进度（静默错误）
- **影响详情**：MoE 量化 FFN 融合算子在非法参数组合下：bias 被静默丢弃（输出错值无报错）或设备侧 AICore 异常延迟炸出；host 侧不拦截，作业中断点远离根因。
- **改进措施**：检测 bias 置大值（如 1e6）对比输出 hash 是否变化；groupList 单调性/末值断言。；修复 待定（两个 issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6695；https://gitcode.com/cann/ops-transformer/issues/6696

### TRN-0422 `ops_math_turboquant_centroids_unvalidated` TurboQuant 乱序/NaN centroids 静默输出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：量化 / cann / aclnnTurboQuant centroids
- **原因行为**：CheckShape() 只校验 centroids 形状 [16]，未校验升序与有限性：首尾对调（非升序）或含 NAN 的 centroids 两段返回 0，kernel 照常写出 y/scale。
- **影响对象**：数值结果；模型权重（静默错误）
- **影响详情**：centroids 非升序（首尾对调）或含 NaN 时（A2 910B2 / CANN 9.2.0 实测），两段接口均返回 0，kernel 照常写出 y 与 scale，量化编码静默错误；错误量化输出无告警流入下游权重/激活，量化训练或量化感知流程产物质量悄悄变差。
- **改进措施**：检测 centroids 单调性与 isfinite 断言；量化输出与参考对拍。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-nn/issues/7291

### TRN-0430 `opstransformer_moe_init_routing_v4_quant_round_boundary_1lsb` MoeInitRoutingV4 静态量化取整边界多进 1 LSB

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：量化 / cann / aclnnMoeInitRoutingV4
- **原因行为**：quantMode=0 静态量化对 |x-trunc(x)|∈[0.49,0.5) 的边界值多进 1 LSB：round(x*scale+offset) 的取整方向在该区间系统性偏移，与资料公式不一致。
- **影响对象**：数值结果（静默错误）
- **影响详情**：边界值如 9.49774 被量化为 10 而非 9（+1 LSB）；设计用例 125 条静态量化用例共 162 处偏差，单条最多 72/16384 元素（0.44%）。
- **改进措施**：检测 构造 |x-trunc(x)|∈[0.49,0.5) 边界值与 fp64 公式对拍。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6716

### TRN-0453 `matmul_emu_split_weight_layout_mismatch` MatmulEmuSplitWeight 混合布局权重静默算错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：量化 / cann / aclnnMatmulEmuSplitWeight
- **原因行为**：转置标志只从 wHigh 推导却同时决定 wLow 的读取方式；两权重内存布局不一致时 kernel 按列主序读连续的 wLow。两层形状校验只比较 view 形状，混合布局下仍相等，校验全过。
- **影响对象**：数值结果（静默错误）
- **影响详情**：wHigh 转置而 wLow 连续的合法输入下，y 与 fp64 参考最大相对误差 4.26（对照组 4.5e-8），两段接口返回 0；资料未声明两权重必须同布局。
- **改进措施**：检测 wHigh/wLow 布局不一致负例对拍 fp64 参考；检查 strides 而非 view 形状；修复 待定（建议从各自 strides 推导 layoutTag，未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7392
- **关联**：cross:INF-2194

### TRN-0457 `weightquant_bmm_v2_l1_budget_nondet` WeightQuantBatchMatmul tiling L1 缺陷非确定错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：量化 / cann / WeightQuantBMM tiling
- **原因行为**：tiling 三处 L1 预算校验缺陷：A 预载未扣 WeightL1/bias 占用（预载越界踩 WeightL1 与 AIV 反量化竞态）；baseN 扩展检查无符号下溢误放行；A 全载准入低估占用。
- **影响对象**：数值结果（不可复现）
- **影响详情**：Ascend950 perchannel int4 转置权重 + bf16 输入下多组形状输出非确定性错误：同输入多次执行 rel_l2 在 0.2~1.4 漂移（阈值 3.9e-3），图模式限核与 eager 均可触发。
- **改进措施**：检测 同输入多次执行比对（非确定性特征）；限核 16/22 配置跑 rel_l2 回归；修复 修复 PR https://gitcode.com/cann/ops-nn/pull/12304 （issue 注明；状态未核实）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7357；https://gitcode.com/cann/ops-nn/pull/12304
- **关联**：cross:INF-2215

### TRN-0506 `opsmath_fake_quant_cachemask_int32_wraparound` FakeQuant Cachemask 越界值 int32 回绕错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：量化 / cann / Cachemask int32 落地
- **原因行为**：资料声明 quantMin/quantMax 为 INT64，实现 kernel 侧 static_cast<int32_t>，越界合法取值静默回绕，夹取区间整体负移。
- **影响对象**：数值结果（静默错误）
- **影响详情**：quantMin=3000000000/quantMax=3000000100 时 out=(clamp(qval)-zp)*scale 输出 -1.29497e9 而非 +3.0e9（符号反、量级近似）；两段接口返回 0；#2988 同点曾登记 2026-06 关闭后 master 仍可复现。
- **改进措施**：检测 对大数值 quant 边界（>INT32）输入与 CPU 参考对照；静态审查 tiling→kernel 的 quantMin/quantMax 位宽；修复 待定（issue open 2026-10-28；910B2+CANN 9.2.0 实测，master a2b7042）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7550

### TRN-0507 `opsmath_fake_quant_cachemask_fp16_mask_compare` FakeQuant Cachemask fp16 掩码半精比较失真

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：量化 / cann / fp16 模板掩码比较
- **原因行为**：kernel fp16 模板把整数 qval 转 half 后再与 quantMin/quantMax 比较，half 只能精确表示 |x|<=2048 的整数，超出后越界元素 mask 判 True。
- **影响对象**：数值结果（静默错误）
- **影响详情**：quantMax=32767、qval=32770/32800 实测 mask=1（期望 0），期望 1 0 0 0 实测 1 1 1 0；quantMax=4096、qval=4097~4099 同样误判；同一组输入 out 钳位正确（32767），fp32 输入同参数 mask 正确。
- **改进措施**：检测 fp16 输入下用越界 qval 对照 mask=(qval>=min)&&(qval<=max) 公式；int16/uint12 大区间量化重点检查；修复 待定（issue open 2026-10-28，910B3+CANN 9.2.0，master a2b7042 实测）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7535
- **关联**：var:TRN-0506

### TRN-0523 `dynamic_quant_arch35_bf16_range_overflow` DynamicQuant arch35 bf16 极差溢出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：量化 / cann / dynamic_quant arch35 极差
- **原因行为**：arch35 向量寄存器路径上非对称量化行极差 (max-min) 在 fp32 中间量溢出为 inf，scaleOut=inf、yOut 全饱和；与 A2 标量路径 #7533 同根因，未随 !13078 修复
- **影响对象**：数值结果（数值异常）
- **影响详情**：950/A3 上 bf16 行内交替 ±极值（|x|>1.70e38）时 scale=inf、y 全饱和且两段返回 0；6-8 处 regbase 模板同病
- **改进措施**：检测 量化输出对拍 fp32 参考；检查 scaleOut 是否 inf；修复 A2 标量路径修复 https://gitcode.com/cann/ops-nn/pull/13078（closed，注明未覆盖 arch35）；arch35 向量级 guard（Select/Greater 组合改两端分别除）待单独立项，issue open 无修复 PR
- **来源**：https://gitcode.com/cann/ops-nn/issues/7721；https://gitcode.com/cann/ops-nn/issues/7533
- **关联**：cross:INF-2255

### TRN-0539 `quant_grouped_matmul_32core_precision` QuantGMM 32 核精度问题

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：量化 / cann / QuantGroupedMatMul 32核
- **原因行为**：QuantGroupedMatMulAlltoAllv 在 32 核配置下存在精度问题（PR !14895 为 temp/repro：支持环境变量强制 blockDim 复现 32 核精度问题，尚无根因修复）
- **影响对象**：数值结果（静默错误）
- **影响详情**：32 核下量化 grouped matmul 输出错值，专家结果静默偏离参考，loss 曲线无显式异常但模型质量受损；强制其他核数（如 16）输出正常，可用 PR !14895 环境变量定向复现，根因未公开。该算子是 NPU MoE 量化训练（量化感知/低精度 MoE）核心 GEMM。
- **改进措施**：检测 环境变量强制 32 核复现（PR !14895 提供复现开关）；与 16/8 核输出对拍；修复 待定（!14895 为 temp repro PR 非修复；另 !14822 同算子 apace 通路 AIC 核间同步改 CrossCore 屏障，open）
- **来源**：https://gitcode.com/cann/ops-transformer/pull/14895；https://gitcode.com/cann/ops-transformer/pull/14822

### TRN-0545 `verl_nvfp4_qat_scale_export_mismatch` verl NVFP4 QAT 量表导出错配

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：量化 / verl / NVFP4 QAT scale 导出
- **原因行为**：NVFP4 量表收集器用首个数字型模块路径段当 layer ID（PP 上局部层号重置）、SequentialMLP 专家坍缩一份、Bridge 广播而各 rank 只留本 stage 量表——可导出错专家量表或 1.0 fallback
- **影响对象**：模型权重（静默错误）
- **影响详情**：verl Megatron QAT+NVFP4（#8287 ModelOpt 导出路径）、PP 多 stage/SequentialMLP 专家时，导出文件里的激活 scale 可能来自错误的专家/层或仍是未观测的 1.0 初值；加载与推理正常，精度静默劣化无报错，需逐专家对拍 scale 才发现
- **改进措施**：检测 导出后逐专家核对 activation scale 与观测记录一致；断言非 fallback 值；修复 修复 PR https://github.com/verl-project/verl/pull/8467（open，用全局 layer_number、保留 SequentialMLP 全局专家 ID、PP 组 gather 观测元数据，未合入）
- **来源**：https://github.com/verl-project/verl/pull/8467

### TRN-0557 `opsnn_swigluquant_v2_rank1_dynamic_quant_wrong` SwiGluQuantV2 rank1 动态量化输出错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：量化 / cann / swi_glu_quant rank1 寻址
- **原因行为**：smoothScales传rank1 [G]（per-tensor）+dynamic时量化输出错误；疑似（issue自述未改码验证）：kernel按basicColLen做向量乘，smooth仅G个float，越界读后rowmax
- **影响对象**：数值结果（静默错误）
- **影响详情**：实测 y 仅 1 个元素非 0、scale=20.62（应 86.86，对应 amax 6.16 vs 1.46）；同 x 改 rank2 [1,32] 后 64/64 一致；与 V1 #7770 同机理（共用 op_kernel/swi_glu_quant.h），910B3/CANN 9.2.0
- **改进措施**：检测 rank1 smooth + dynamic 组合与 CPU 标杆全量对拍；或第一段直接拒绝该组合；修复 待定（issue open：若 rank1 只允许静态量化应在 GetWorkspaceSize 拒绝；动态需按标量乘）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7774；https://gitcode.com/cann/ops-nn/issues/7770
- **关联**：cross:INF-2311

### TRN-0560 `opsnn_apply_adam_w_quant_zero_block_nan` ApplyAdamWQuant 零块 0/0 出 NaN

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：量化 / cann / apply_adam_w_quant 归一化
- **原因行为**：量化归一化 Div(state, absmax) 在 block absmax=0 时 0/0=NaN（golden 有特判），NaN 进二分查找/CheckSign 后量化码值与 golden 分歧
- **影响对象**：优化器状态；训练轨迹（数值异常）
- **影响详情**：gnormScale=0（grad 全零）触发；TTK 169 用例修前 156 PASS、4 个 gnormScale=0 组 FAIL；mRef/vRef/absmax 输出错；arch35（950PR/DT）路径
- **改进措施**：检测 gnormScale=0 / 全零梯度步回归；输出 NaN 断言；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/13012（merged：Div 前除数取 max(absmax, FLT_MIN)，169→全 PASS；issue #7736 closed）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7736；https://gitcode.com/cann/ops-nn/pull/13012
- **关联**：cross:INF-2320

### TRN-0561 `opsnn_fakequant_perchannel_inverted_equal_channel_semantics` FakeQuantPerChannel 倒置/相等通道语义异于 TF

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：量化 / cann / FakeQuantPerChannel 通道语义
- **原因行为**：倒置通道（min>max）clamp 顺序与 TF 相反；相等通道（min==max≠0）kernel 输 0 而 TF 为 NaN（inv_scale=inf→0×inf）；round 0.5 边界 ±1 量化级失配
- **影响对象**：数值结果（静默错误）
- **影响详情**：TTK geir L0 精度比对 22 例 FAIL（matched_ratio≈0.48 起步，倒置域偏差达量程全跨度如 max_abs_error≈200）；Ascend950PR、cann/golden/ttk 20261013；训练 QAT 伪量化激活偏离 TF 参考实现
- **改进措施**：检测 含倒置/相等通道的 per-channel QAT 用例与 TF 参考对拍；min==max 通道输出 NaN 断言；修复 修复 MR https://gitcode.com/cann/ops-nn/merge_requests/13097（open：精度/健壮性修复 + ascend350 适配）
- **来源**：https://gitcode.com/cann/ops-nn/issues/7791；https://gitcode.com/cann/ops-nn/pull/13097
- **关联**：cross:INF-2309

## 位置编码

### TRN-0055 `config_default_swallows_cli_override` Megatron VLM 入口漏传 --rotary-base

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-08-18 · 旧号 CKPT.06

- **原因对象**：位置编码 / megatron-lm / pretrain_vlm.py 参数转发
- **原因行为**：pretrain_vlm.py 构造 LLaVAModel 时转发了兄弟参数却漏传 --rotary-base，CLI 值被静默丢弃，语言模型恒用 dataclass 默认 10000。
- **影响对象**：隐状态；训练轨迹（质量退化）
- **影响详情**：无 crash、无日志；LM 的 RotaryEmbedding 以错误 base 训练（如 Llama 3.x 应为 500000），长上下文质量静默受损，视觉侧不受影响使归因更难；错在保存之前，加载侧检查救不回。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/6585

### TRN-0078 `hf_rotary_inv_freq_uninitialized_after_to_empty` torchtitan HF 后端 RoPE inv_freq 未初始化

`故障` · `active` · `pretrain；sft；rl` · `documented` · `NEW` · 发现 2026-09-16 · 旧号 CKPT.29

- **原因对象**：位置编码 / torchtitan / HF 后端 inv_freq 初始化
- **原因行为**：在 meta 设备建模后 to_empty()，缓冲区 inv_freq 未初始化；兼容补丁依赖 Transformers 5.x 已移除的 rope_init_fn 属性，覆写的 _init_weights 又漏掉 rotary 分支。
- **影响对象**：隐状态（静默错误）
- **影响详情**：模型初始化与 checkpoint load 都不恢复正确的 RoPE 频率且无异常；CPU 复现中 to_empty 后填为 NaN 的 inv_freq 初始化后仍为 NaN。错误频率污染位置编码与前向，当前版本的端到端训练影响未实测。
- **改进措施**：检测 待定；修复 修复 PR #5214 已 merge（2026-10-13）：RotaryEmbedding 分支委托 HF PreTrainedModel._init_weights（import 时捕获），删除依赖 rope_init_fn 的死循环；regression 测试 NaN 预填 4/4 red→green；bit-identical logits 对照正常构造模型 max diff 0（main 上 5.6e-4）。https://github.com/pytorch/torchtitan/pull/5214（尚未核实发版）
- **来源**：https://github.com/pytorch/torchtitan/issues/4783；https://github.com/pytorch/torchtitan/pull/5214

### TRN-0140 `triton_block_local_mask_oob_rope_write` MLA YaRN RoPE Triton kernel 掩码过宽致越界写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-08 · 旧号 KER.09

- **原因对象**：位置编码 / megatron-lm / MLA YaRN RoPE Triton 掩码
- **原因行为**：RoPE apply 的四个 Triton kernel 用块内 head 坐标比较全局 head 数作边界掩码，pid_head>0 的块掩码过宽，head_num 不整除 BLOCK_H 时幻影 lane 在 bwd 越界写。
- **影响对象**：梯度；数值结果（静默错误）
- **影响详情**：head_num 非 2 的幂即触发：有分配 slack 时进程存活、下一 token 的 rope 切片与分配外内存被静默写坏，数百 step 后才出现与根因解耦的 NaN 或 illegal access；autotune 首次调用即执行越界。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7103

### TRN-0148 `fused_rope_inplace_alias_breaks_autograd` Megatron 就地 fused RoPE 别名绕过 autograd 记账

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-28 · 旧号 KER.17

- **原因对象**：位置编码 / megatron-lm / DSv4 注意力的就地 fused RoPE
- **原因行为**：apply_rope_fusion=True 时 Q/KV 用就地 fused RoPE，KV 同时作 key 和 value（别名），kernel 直写内存绕过 autograd version 追踪，依赖记录与实际内存历史不一致。
- **影响对象**：梯度；模型权重（数值异常）
- **影响详情**：iter 1 无告警完成但梯度已错，坏权重使 iter 2 前向 NaN；关闭 apply_rope_fusion 可正常训练。单测 fused kernel 数值正确，仅完整 attention 图别名组合下显形；未过溢出阈时可能持续错梯度而不 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/5317；https://github.com/NVIDIA/Megatron-LM/pull/7643

### TRN-0264 `gpt_oss_builder_dual_channel_position_embedding` Megatron GPT-OSS 位置编码双通道分叉，叠加随机位置表

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-10-09 · 旧号 OBS.15

- **原因对象**：位置编码 / megatron-lm / gpt-oss builder 位置编码传参
- **原因行为**：--enable-gpt-oss 时 builder 把 config 位置编码类型设为 yarn，却把 CLI 默认 learned_absolute 传给构造器；embedding 层按实参建位置表并在 forward 相加。
- **影响对象**：隐状态；训练轨迹；性能/资源（静默错误）
- **影响详情**：官方 gpt-oss-20b recipe 默认即命中，无 crash 无 warning：ckpt 不含该表，随机初始化位置表叠加到每个 token 的 embedding，训练静默降质（幅度未量化）；多占约 236 MB，SP 的 reduce_scatter_embeddings 被静默禁用。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7900；https://github.com/NVIDIA/Megatron-LM/pull/7850

### TRN-0342 `mindspeed_mla_yarn_original_max_pos_misforwarded` MindSpeed MLA YaRN 原始长度参数传错致长序列退化

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：位置编码 / mindspeed / MLA YaRN 初始化
- **原因行为**：构造 YarnRotaryEmbedding 时把扩展后的 max_position_embeddings 当作 original_max_position_embeddings 传入，YaRN 缩放范围按错误的原始长度计算。
- **影响对象**：隐状态；训练轨迹（质量退化）
- **影响详情**：长上下文模型（如 Kimi-k2.5：original 4096 / 扩展 128000）启用 MLA+YaRN 时缩放区间错位，长序列前向精度静默退化；两值相等的模型不受影响。
- **改进措施**：检测 对 YarnRotaryEmbedding 收到的 original_max_position_embeddings 断言等于 config.original_max_position_embeddings（PR 已加该单测）。；修复 修复 MR https://gitcode.com/Ascend/MindSpeed/merge_requests/4103（open）：改传 config.original_max_position_embeddings，新增单测断言转发值（4096 vs 128000 用例）；端到端 Kimi-k2.5 长序列验证需 NPU 环境未本地运行。Fixes #185（issue 正文批次内无缓存，机制以 PR 为准）。
- **来源**：https://gitcode.com/Ascend/MindSpeed/merge_requests/4103

### TRN-0496 `msformers_pynative_scaling_factor_alias_dropped` MindFormers 配置转换静默丢弃 scaling_factor

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：位置编码 / mindformers / ConfigConverter 键映射
- **原因行为**：DeepseekV3Config 接收 scaling_factor，但 ConfigConverter 未映射到 rotary_scaling_factor；源键在未映射白名单不提示，静默回落默认值 40。
- **影响对象**：输入编码；训练轨迹（静默错误）
- **影响详情**：源 YAML 写 scaling_factor: 1.0 或 2.0 实际解析均为 40；单卡诊断中 MLA softmax scale 实际 0.13523（factor=40）而非期望 0.07217（factor=1），FP64 参考支持该差异改变输出。
- **改进措施**：检测 构造 config 后断言 convert_to_transformer_config().rotary_scaling_factor == 源值；打印 attention scale 与 mscale/factor；修复 修复 PR https://atomgit.com/mindspore/mindformers/merge_requests/8888（open 草稿，2026-10-28）——透传 scaling_factor 到目标字段
- **来源**：https://atomgit.com/mindspore/mindformers/issues/2619；https://atomgit.com/mindspore/mindformers/merge_requests/8888

## 分词/模板

### TRN-0086 `tokenizer_train_infer_id_mismatch` tokenizer 前后不一致或 vocab 填充错，embedding 行错位

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 DATA.04

- **原因对象**：分词/模板 / 通用 / tokenizer 与 vocab 填充配置
- **原因行为**：训练用 tokenizer A 且只保存权重，后续 SFT/RL/评测换成 tokenizer B；或 padded-vocab-size 与真实 vocab 不一致，导致 embedding 行错位。
- **影响对象**：输入编码；输出内容（静默错误）
- **影响详情**：一切都能正常运行、无报错，生成结果与 loss 表现得像近邻词被替换。例：本地 Qwen3 须设 --padded-vocab-size 151936，自然长度 151680 会对不齐。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：本实验室 Qwen3 必须 `--padded-vocab-size 151936`（自然长度 151680 会对不齐）。

### TRN-0098 `tiktoken_double_special_token_offset` Megatron TikToken id 查询重复加特殊 token 偏移

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-09-28 · 旧号 DATA.16

- **原因对象**：分词/模板 / megatron-lm / TikToken token_to_id 与逆词表
- **原因行为**：TikToken 实例初始化时已把 rank 偏移 num_special_tokens，token_to_id()/tokens_to_ids() 却再加一次，逆词表 inv_vocab 构键时同样多加一次。
- **影响对象**：输入编码（静默错误）
- **影响详情**：tokens_to_ids(text_to_tokens(t)) 与 text_to_ids(t) 分叉，默认配置下 id 整体 +1000、指向别的 token；特殊 token 查询、token 级掩码/过滤等消费路径静默拿到错 id，端到端症状未列明。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7543
- **关联**：var:TRN-0086

### TRN-0178 `chat_template_train_serve_mismatch` SFT 训练与上线使用不一致的 chat template

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 SFT.01

- **原因对象**：分词/模板 / ms-swift / 训练模板与工具参数 formatter
- **原因行为**：训练模板（generation prompt、系统角色、tool 头）与上线模板不同；ms-swift 实例中 formatter 只对 dict/list 做 JSON 序列化，bool/None 工具参数落回 Python repr。
- **影响对象**：输入编码；输出内容（质量退化）
- **影响详情**：SFT 验证 loss 正常，对话/工具调用一上线即退化；ms-swift 实例中训练语料的工具参数格式与 Qwen 原生模板静默分叉，部署侧解析不了模型生成的参数。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/pull/9968

### TRN-0188 `auto_processor_ignores_model_revision` trl 自动创建 processor 时忽略模型 revision

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-08-30 · 旧号 SFT.11

- **原因对象**：分词/模板 / trl / 自动 processing_class 加载
- **原因行为**：按 revision 加载时权重取指定 revision，自动创建的 processing_class 却不带 revision 调 AutoProcessor，tokenizer/chat template 取自默认 revision。
- **影响对象**：输入编码；训练轨迹（静默错误）
- **影响详情**：checkpoint revision 与默认 revision 的 chat template 不同时，各 stable trainer 全程用错模板格式化对话，无任何警告；显式传 processing_class 可绕开。verl 未 pin revision 时有同类漂移。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6974；https://github.com/verl-project/verl/pull/7658

### TRN-0190 `per_message_tokenization_drops_think_block` verl 多轮 SFT 逐消息渲染模板丢失 think 块

`故障` · `active` · `sft` · `documented` · `var` · 发现 2026-09-10 · 旧号 SFT.13

- **原因对象**：分词/模板 / verl / 逐消息 apply_chat_template
- **原因行为**：MultiTurnSFTDataset 逐条消息 apply_chat_template 再拼接，而 Qwen3 模板渲染 reasoning_content 依赖完整前缀，含 tool_call 的轮次丢失 <think> 块。
- **影响对象**：输入编码；输出内容（静默错误）
- **影响详情**：Qwen3 多轮 SFT 在 ignore_input_ids_mismatch=True 压掉检查时照常训完，loss mask 按错位序列监督；训后模型把最终答案写进 reasoning 通道，vLLM 返回 content=None。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7807；https://github.com/verl-project/verl/pull/7844
- **关联**：var:TRN-0178

### TRN-0238 `response_prefix_role_flips_prompt_to_completion` ms-swift GRPO 的 response_prefix 被计入补全

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-12 · 旧号 RL-RO.16

- **原因对象**：分词/模板 / ms-swift / 模板层 response_prefix
- **原因行为**：生成侧把 prefix 拼进 prompt，vLLM 输出不含它；Template.decode() 又拼回 prefix 并整串编码为 response，prefix 的 labels 被置位、落入 completion_mask。
- **影响对象**：训练信号；训练样本流（静默错误）
- **影响详情**：无报错；vLLM 对 N 个 token 算 log-prob，trainer 对 len(prefix)+N 个算，模型认为 prefix 不太可能时其主导序列 log-prob，本应≈1 的 ppl_ratio 爆炸，优势与 KL 均含非采样 token。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10106；https://github.com/modelscope/ms-swift/pull/10107

### TRN-0266 `tokenizer_rebuild_drops_pre_tokenizer_spaces` AutoTokenizer 重建忽略 pre-tokenizer 致空格丢失

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-10-13 · 旧号 SFT.17

- **原因对象**：分词/模板 / transformers / AutoTokenizer 构建
- **原因行为**：AutoTokenizer 对可由类配方重建的 tokenizer 类忽略 tokenizer.json 中存储的 pre-tokenizer，按类默认行为重建，空格/换行在 encode/decode 中被丢弃。
- **影响对象**：输入编码；训练轨迹（静默错误）
- **影响详情**：无 crash、无 NaN：prompt、验证文本与解码回复变为粘连文本；训练侧与 rollout 侧用同一套错误 token ids，一致性检查对两侧同错失明，训练在错误 token 序列上正常推进，训后模型静默劣化。transformers 5.5.3/5.12.0/5.17.0 复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/8193
- **关联**：var:TRN-0178

### TRN-0551 `verl_continuous_token_default_builder_no_check` verl Continuous Token 回退默认 builder 无校验

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：分词/模板 / verl / Token builder 回退
- **原因行为**：未注册 model_type 回退默认 builder（不处理边界 token），训练中无 comparator 校验合并流与模板渲染一致性；sanity check 自 #4422 起 no-op
- **影响对象**：输入编码；训练样本流（静默错误）
- **影响详情**：GLM-4.7-Flash（glm4_moe_lite）、Qwen3-Next（qwen3_next）等 ChatML 型模型多轮 rollout 的合并 token 流与模板渲染不一致（边界 token 重复/丢失），rollout↔train 一致性成立但相对模板语义静默错位
- **改进措施**：检测 训练中运行 scripts/chat_template_checker.py 对比合并流与模板渲染；注册表外 model_type 显式告警；修复 待定（issue open：#6719 pitfall 4 的 comparator 以独立脚本落地未接入训练；未注册 model_type 仍静默回退）
- **来源**：https://github.com/verl-project/verl/issues/8462

## 模型定义

### TRN-0097 `sparse_attn_window_crosses_packed_document_boundary` torchtitan DSV4 稀疏注意力窗口跨越 packed 文档边界

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-09-23 · 旧号 DATA.15

- **原因对象**：模型定义 / torchtitan / DSV4 get_attention_masks
- **原因行为**：DSV4 重写的 get_attention_masks() 丢弃 positions、padding 与文档边界元数据，按整条扁平 token 流的偏移构建 sparse attention 窗口，无视 position id 重置。
- **影响对象**：跨请求/跨样本数据；隐状态（静默错误）
- **影响详情**：无 crash，packed 训练中第二文档首 token（query 64）可 attend 第一文档末 token（key 63），文档隔离静默失效；CPU 复现中 DSV4 mask 为 True、共享 mask 为 False，对训练 loss 的影响未量化。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/issues/4801

### TRN-0149 `module_cast_silently_converts_purpose_built_buffers` torchtitan module.to() 静默转型专用 buffer

`故障` · `active` · `pretrain；shared` · `documented` · `var` · 发现 2026-10-10 · 旧号 KER.18

- **原因对象**：模型定义 / torchtitan / 模型自有浮点 buffer 的 dtype 保护
- **原因行为**：nn.Module.to(dtype) 等把浮点 buffer 连同参数一起转型，而 RoPE cache、inv_freq、MoE 专家计数/偏置等 buffer 是刻意按固定 dtype 构建的 cache/累加器，转型无保护。
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：调用 .to(bf16) 等后触发：ComplexRoPE 只留实部（仅一条 UserWarning），CosSinRoPE/inv_freq 被 round 无警告，q·k spread 由 2.3e-3 升到 24.6；MoE 每专家计数超 256 后不再精确，负载均衡 bias 更新读错数据。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/5153
- **关联**：var:TRN-0017

### TRN-0165 `unscaled_embedding_grad_spike` 子层范数大、embedding 未缩放致梯度范数突跳与 loss 尖峰

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 LOSS.01

- **原因对象**：模型定义 / 通用 / 子层初始化与 embedding 缩放
- **原因行为**：子层谱范数上界大而残差捷径相对小时梯度范数会突然跳变；缺少用标准 LLM 初始化压低子层，或缺少 embedding scale/embed-LN 使 embedding 标准差接近 1。
- **影响对象**：训练轨迹；梯度（质量退化）
- **影响详情**：出现 loss 尖峰，严重时毁掉整段预训练；尖峰前常先出现 grad norm 跳变。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2312.16903

### TRN-0166 `attention_logit_growth_without_qk_norm` 缺 QK-norm 时注意力 logits 增长致 loss 尖峰

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 LOSS.02

- **原因对象**：模型定义 / 通用 / QK-norm/logit softcap 缺失
- **原因行为**：没有 QK-norm 或 logit softcap 时，attention logits 随深度和长度增长，softmax 趋于单峰，反传出现尖峰。
- **影响对象**：训练轨迹；隐状态（质量退化）
- **影响详情**：周期性 loss spike，有时能恢复，有时进入重复/乱码 attractor；在 NoPE 等消融配置上尤其明显。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：QK-Norm / PaLM-scale 训练稳定性实践；

### TRN-0167 `post_ln_vanishing_then_explode` Post-LN 深网梯度消失、加大 LR 即爆炸，LN 位置配错

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 LOSS.03

- **原因对象**：模型定义 / 通用 / 残差 LN 位置（Post-LN/Pre-LN）
- **原因行为**：Post-LN 残差结构在深网上梯度消失，加大学习率即爆炸；用 Post-LN 权重按 Pre-LN 计算图训练（或反之）属配置层错误。
- **影响对象**：训练轨迹；梯度（质量退化）
- **影响详情**：要么训不动，要么出现一次 spike 后不可恢复。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：Spike No More 附录对 Post-LN 的对照；

### TRN-0171 `zero_init_final_norm_blanks_first_backward` Muse Glimmer final norm 零初始化，首步梯度全零

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-06 · 旧号 LOSS.07

- **原因对象**：模型定义 / torchtitan / final norm 的 weight 初始化
- **原因行为**：final output norm 用 gain_center=0.0 并继承 _gain_norm 的零初始化 weight，有效 scale 为 0；内部 norm 零初始化是有意语义，final norm 复用同一初始化路径则是错的。
- **影响对象**：隐状态；梯度（静默错误）
- **影响详情**：无 crash、无 NaN：final hidden states 与 logits 全零，首个 backward 中 decoder/lm_head 梯度全零、首步更新为零；warmup 期 loss 曲线看似正常，起步期被浪费。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/4489

### TRN-0294 `mindspeed_llm_mtp_dsa_indexer_layer_mapping` MindSpeed-LLM MTP 层 DSA indexer 层号映射错且静默

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：模型定义 / mindspeed-llm / MTP 层号到全局层元数据的映射
- **原因行为**：MCore 对 MTP 层按预测深度从 1 编号而非接续 decoder 层号；MindSpeed-LLM 未传 is_mtp_layer，MTP 层映射到错误全局层元数据、错误参与 Compute/Share 分组。不抛异常。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：同时开 MLA+MTP+DSA indexer（DeepSeek-V3、GLM5/GLM5.2 同路径，glm5_744b 示例脚本默认开启）时：MTP 层 indexer 层号/共享关系错误、DSA indexer loss 按错误层号记录，无堆栈无报错，训练正常跑但结构语义已错。
- **改进措施**：检测 核对 MTP 层 indexer 的全局层号与 Compute/Share 分组；开 DSA indexer 训练后检查 indexer loss 按层分布是否与结构一致。；修复 修复 MR !5153（merged）：_with_mtp_self_attention_spec 克隆 spec 注入 is_mtp_layer=True、resolve_dsa_indexer_build_config 把 MTP 深度映射到 decoder 层之后、DualPipeV+MTP 场景改用 dualpipev_mtp_model_provider_wrapper。端到端 DeepSeek-V3 SFT（16×910）跑通验证问题二/三与 layer-spec 路径；问题一（DSA indexer 改动）未被该用例覆盖（用例中 indexer 关闭），仍需开 indexer 的 GLM5 验证。https://gitcode.com/Ascend/MindSpeed-LLM/merge_requests/5153
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1925；https://gitcode.com/Ascend/MindSpeed-LLM/merge_requests/5153

### TRN-0319 `mimo_whisper_encoder_attends_padded_mel_tail` MiMo Whisper 冻结塔前向泄漏 padded mel 尾部特征

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-19

- **原因对象**：模型定义 / megatron-lm / hf_whisper_encoder 包装
- **原因行为**：Wrapper 跑完整 3000 帧 encoder 后才按 seq_lengths 掩码；WhisperEncoder 忽略 attention_mask，各 query 仍 attend 到 pad 尾（0.0 非静默值）。
- **影响对象**：隐状态；输入编码（静默错误）
- **影响详情**：掩码后完整前向与未 pad 主体输出不同（CPU tiny encoder 复现）；published AVLM recipe 默认冻结 Whisper 塔取第一 clip，pad 泄漏特征静默进入训练主干，无报错
- **改进措施**：检测 CPU tiny WhisperEncoder 注入对照：3000 帧（前 13 帧真实前缀+尾垃圾）wrapper 输出 vs 未 pad 主体 vs masked full forward；修复 issue 给出期望实现（未落地）：按行裁剪 input_features[i,:,:mel]（1<=mel<=time）只跑真实帧，S=(mel-1)//2+1 须等于 seq_lengths，不同长度分开 forward 后拼接；issue open（mcore-oncall 已呼叫，无维护者回应）
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/8324

### TRN-0357 `msllm_mamba3_scratch_loss_zero_init` Mamba3 从零训练 loss 与 grad norm 骤降为 0

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：模型定义 / mindspeed-llm / Mamba3 in/out_proj 初始化
- **原因行为**：Mamba3 FSDP2 Demo train_from_scratch 缺少 in_proj/out_proj Kaiming 初始化处理
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：Mamba3 FSDP2从零训练：initializer_range=0.1随机初始化开训即数值异常、loss为0；改0.02并去掉额外Kaiming初始化后前150step正常，约150step又loss突然归零，155起lm、mtp loss及grad norm为0，进程不报错不退出，显存不变
- **改进措施**：检测 监控 lm loss 与 grad norm 是否同时恒为 0；对 SSM 分支参数记录初始化 std 与是否全零；修复 issue 里 initializer_range 改 0.02 只恢复前 150 step；正文建议给 Mamba3 in_proj/out_proj 补 Kaiming 初始化并做长步数稳定性验证（closed，未附修复 PR，未核实）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1836

### TRN-0508 `megatron_absorbed_mla_softmax_scale_override_ignored` AbsorbedMLA 忽略 softmax_scale 显式覆盖

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：模型定义 / megatron-lm / AbsorbedMLA softmax_scale
- **原因行为**：__init__ 无条件按 mscale*mscale*(1/sqrt(q_head_dim)) 计算，忽略显式 config.softmax_scale；MultiLatentAttention 自身会使用覆盖值。
- **影响对象**：隐状态（静默错误）
- **影响详情**：muP 开启时 AbsorbedMLA 的 softmax scale 与标准 MLA 静默不同（所查案例约 11 倍），而文档与 docstring 声明两者数学等价；无报错，注意力输出直接偏离。
- **改进措施**：检测 同 config 构造 AbsorbedMLASelfAttention 与 MLASelfAttention 断言 softmax_scale 相等（修复 PR 附该测试）；修复 修复 PR https://github.com/NVIDIA/Megatron-LM/pull/8649（open，2026-10-28）——镜像 MultiLatentAttention 的表达式，override 存在时使用之；附单测 test_softmax_scale_respects_explicit_config_override
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/8649

### TRN-0531 `torchtitan_dsv4_swiglu_limit_missing` torchtitan DSV4 缺 swiglu_limit 偏差

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：模型定义 / torchtitan / DSV4 flavor MoE 激活
- **原因行为**：deepseek_v4_flash/pro flavor 对两类专家用普通 SwiGLU，不带官方 config swiglu_limit=10.0 clamp，与参考推理代码及 HF transformers 行为不同
- **影响对象**：数值结果；训练轨迹（静默错误）
- **影响详情**：gate 或 up 激活超过 10 时 MoE 输出与参考实现不同；同一 checkpoint 在 torchtitan 训练路径与 transformers 参考路径算出不同结果，静默无报错
- **改进措施**：检测 同权重与 transformers DeepseekV4MLP 对拍（PR 自带 reproducer：同随机权重比 shared expert 输出）；修复 修复 PR https://github.com/pytorch/torchtitan/pull/5646（merged 2026-10-29）：新增 LimitedSwiGLU 用于两 flavor 的路由/共享专家，MTP 块深拷贝继承；dist_moe 对不支持的激活显式 TypeError
- **来源**：https://github.com/pytorch/torchtitan/pull/5646

## 权重/检查点

### TRN-0046 `named_children_dedup_drops_shared_submodule_params` DeepSpeed ZeRO ckpt 重建缺别名子模块参数

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-28 · 旧号 PAR.18

- **原因对象**：权重/检查点 / deepspeed / _get_shared_params 子模块遍历
- **原因行为**：_get_shared_params() 用按对象身份去重的 named_children() 遍历，子模块被第二个属性名别名时其子树不被访问、参数不记为 shared，与 state_dict() 的遍历结果不一致。
- **影响对象**：模型权重（静默错误）
- **影响详情**：ckpt 无错写出；zero_to_fp32.py 等重建的 state_dict 缺别名子模块（如 self.layer2 = self.layer1）参数；之后 load_state_dict 报错，或容忍 missing keys 时静默加载成不完整模型。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8686

### TRN-0050 `expert_reshard_id_permutation` 专家重分片或排序约定不一致，router expert-id 指向错专家权重

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 CKPT.01

- **原因对象**：权重/检查点 / deepspeed / 专家权重重分片与排序映射
- **原因行为**：以不同于保存时的 EP degree 加载、num_experts % ep_size != 0，或 Megatron↔HF 专家排序约定不同时，router 的 expert-id 指向另一组专家权重。
- **影响对象**：模型权重；输出内容（质量退化）
- **影响详情**：加载成功无报错；MoE 模型输出流畅但能力像换了一批专家，router 熵可能仍看起来健康。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/5794

### TRN-0051 `zero_optimizer_state_partition_mismatch` ZeRO 换并行布局后优化器矩分片错位

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 CKPT.02

- **原因对象**：权重/检查点 / deepspeed / ZeRO 优化器状态分片映射
- **原因行为**：ZeRO-1/2/3 按 rank 切分 Adam 矩；换 world size、ZeRO stage 或 TP 后恢复时权重对上但矩没对上，或 universal checkpoint 的几何分片图与当前并行布局不一致。
- **影响对象**：优化器状态；训练轨迹（静默错误）
- **影响详情**：resume 后 loss 先跳一下再继续下降，实为矩错位后的另一次优化；或静默以零矩作为新 Adam 状态继续训练。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8230

### TRN-0052 `from_pretrained_silent_random_init` from_pretrained 键名不匹配时静默随机初始化

`故障` · `active` · `sft；shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 CKPT.03

- **原因对象**：权重/检查点 / 待定 / from_pretrained 权重键名匹配
- **原因行为**：键名对不上时加载器不报 missing key，未命中的参数保持随机初始化。
- **影响对象**：模型权重；训练轨迹（质量退化）
- **影响详情**：加载无报错；SFT/RL 从错误起点微调，loss 曲线照常下降但拟合的是随机子模块，评测远低于同数据应有水平。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：交叉：`inference_error_review` **12.2** `from_pretrained_silent_random_init`。
- **关联**：cross:INF-1118

### TRN-0053 `te_grouped_empty_extra_state_misdecode` TE grouped-linear ckpt 误解码空 extra state

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 CKPT.04

- **原因对象**：权重/检查点 / megatron-lm / TE grouped-linear ckpt 适配
- **原因行为**：无状态 FP8 recipe 把「无 extra state」存成空 byte tensor，grouped-linear ckpt 适配器在 FP8 开启时仍当序列化元数据解码，得到空状态后索引失败或丢 per-expert 键布局。
- **影响对象**：模型权重；可用性/进度（静默错误）
- **影响详情**：保存/恢复 grouped TE 专家时 FP8 元数据错位，按路径不同表现为硬失败或静默丢 extra state；128 卡 DeepSeek V4 上必须修复后才能稳定 resume。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6509

### TRN-0054 `dist_ckpt_strictness_assume_ok` Megatron dist-ckpt 默认吞掉 unexpected key

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 CKPT.05

- **原因对象**：权重/检查点 / megatron-lm / dist-ckpt-strictness 默认值
- **原因行为**：Megatron 分布式 ckpt 的 dist-ckpt-strictness 默认可取 assume_ok_unexpected，多出的键被当作无事，并行布局演进后本应报错的 unexpected key 被吞掉。
- **影响对象**：模型权重（静默错误）
- **影响详情**：加载「成功」无报错，部分新模块或旧布局残留参数被忽略或错配。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://docs.nvidia.com/megatron-core/developer-guide/0.15.0/api-guide/moe.html

### TRN-0061 `fsdp_merger_concatenates_replicated_buffers` verl FSDP merger 把复制 buffer 拼成 N 倍大小

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-08-31 · 旧号 CKPT.12

- **原因对象**：权重/检查点 / verl / FSDPModelMerger 复制条目合并
- **原因行为**：FSDP ckpt 中复制条目（persistent buffer、未 wrap 参数）以普通 tensor 存储，merger 对无 placement 条目走 torch.cat(dim=0)，把 N 份相同拷贝拼接而非取其一。
- **影响对象**：模型权重（静默错误）
- **影响详情**：merged ckpt 形状错误（8-rank Gemma4 中 layer_scalar [1]→[8]、std_scale [1152]→[9216]），加载通常 shape mismatch 报错；形状碰巧兼容时静默改写 buffer 数值排布。多模态/复合模型重灾区。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7612

### TRN-0063 `quantized_extra_state_silently_dropped_on_load` Megatron GPT 加载丢弃 output_layer 量化 state

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 CKPT.14

- **原因对象**：权重/检查点 / megatron-lm / GPT sharded_state_dict
- **原因行为**：GPTModel.sharded_state_dict 无条件 pop output_layer._extra_state 并 assert 为空，而量化 state 正存于 _extra_state；该方法同时决定 load plan。
- **影响对象**：模型权重（静默错误）
- **影响详情**：save 侧对多元素 byte tensor 做 and 判断直接崩；load 侧 saved 量化 state 被忽略，量化 lm_head 静默恢复成未量化权重，训练/推理权重路径分叉。MambaModel 无此规则，故只有 GPT 系不能 ship 量化 lm_head。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7086

### TRN-0064 `parallel_ckpt_reader_swallows_shard_errors` ms-swift 并行 ckpt reader 吞掉 shard 读取异常

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-09-06 · 旧号 CKPT.15

- **原因对象**：权重/检查点 / ms-swift / 并行 ckpt reader patch
- **原因行为**：并行 ckpt reader patch 中 concurrent.futures.wait() 只等 worker 不取结果，读 shard 的异常被吞掉，reader 无条件返回成功的 torch.futures.Future。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：dcp.load() 报成功，未加载的 tensor 停在 sentinel 值；resume「成功」后训练从 sentinel/旧值出发静默跑偏，无 crash 无日志。缺数据文件或注入 corrupted shard 异常均被吞。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/pull/10045
- **关联**：var:TRN-0054

### TRN-0066 `converter_stale_mapping_omits_experts` gpt_oss HF 适配器映射过期，导出 ckpt 静默缺专家权重

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-09-06 · 旧号 CKPT.17

- **原因对象**：权重/检查点 / torchtitan / gpt_oss HF 适配器专家参数映射
- **原因行为**：grouped expert 参数改名加 shape 后缀后，HF state-dict adapter 的四条映射仍指向旧名；导出侧对不存在的目标静默跳过，导入侧指向不存在的参数，转换器既不报错也不计数。
- **影响对象**：模型权重（静默错误）
- **影响详情**：导出的 HF 格式 ckpt 缺失全部 routed expert 权重；下游宽松加载会随机初始化整组专家，严格加载才报错。由上游参数改名触发，无版本对照的用户难以发现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/4475

### TRN-0068 `class_name_allowlist_leaves_weights_on_meta` DeepSpeed AutoTP 按类名白名单加载，norm 权重留在 meta

`故障` · `active` · `pretrain；sft` · `documented` · `var` · 发现 2026-09-07 · 旧号 CKPT.19

- **原因对象**：权重/检查点 / deepspeed / is_load_module 类名白名单
- **原因行为**：AutoTP 用硬编码的 26 项类名白名单决定是否从 ckpt 加载模块权重；norm 类无子模块、递归探不到，不在名单上就永不加载，meta 设备路径上的参数留在 meta。名单只能随模型家族手工增补。
- **影响对象**：模型权重（静默错误）
- **影响详情**：模块替换完成后无报错、无缺失计数，名单外 norm 层（transformers 5.16.1 中 233 个 norm 类有 219 个不在名单，如 Gemma/GLM/Granite 系）参数仍在 meta；后续 ZeRO init 或首次前向决定是崩溃还是得到随机值。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8447
- **关联**：var:TRN-0052

### TRN-0069 `v1_trainer_esi_force_save_unwired` verl V1 trainer 丢失 ESI 强制保存，配置静默无效

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-09 · 旧号 CKPT.20

- **原因对象**：权重/检查点 / verl / V1 trainer 保存条件（ESI）
- **原因行为**：V1 trainer 的保存条件只有 last-step 与 save_freq 整数倍，从不调用 should_save_ckpt_esi；V0 等路径已实现的 ESI force-save 在 V1 迁移时丢失。
- **影响对象**：可用性/进度；性能/资源（静默错误）
- **影响详情**：trainer.esi_redundant_time 配置被接受、run 正常推进且无报错；容量块在两个 save_freq tick 之间到期被抢占后，才发现 ckpt 停在最近 tick，整个未落盘窗口内的 step 作废。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7757；https://github.com/verl-project/verl/issues/7820；https://github.com/verl-project/verl/issues/7815

### TRN-0070 `shard_filename_lexical_sort_loads_wrong_rank` DeepSpeed 流水线 ckpt 分片按字典序排序，加载错 rank

`故障` · `active` · `shared` · `verified` · `var` · 发现 2026-09-12 · 旧号 CKPT.21

- **原因对象**：权重/检查点 / deepspeed / pipeline ckpt 读侧分片文件名排序
- **原因行为**：分片文件名的 rank 字段只填充两位，并行度到 100 时溢出；两个读侧调用点把 glob 结果按字符串序排序后按 model-parallel rank 位置索引，model_100 落在 model_10 与 model_11 之间。
- **影响对象**：模型权重（静默错误）
- **影响详情**：并行度 ≥100 的 pipeline ckpt resume/load 时 rank 11 加载 rank 100 的分片，形状匹配、无异常、无日志，相当于一次未声明的 TP 重排；下游微调从错误权重出发。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8452
- **关联**：var:TRN-0050

### TRN-0073 `zero3_tag_load_reads_latest_weights` DeepSpeed ZeRO-3 按 tag 加载实际读入 latest 权重

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-14 · 旧号 CKPT.24

- **原因对象**：权重/检查点 / deepspeed / FP32 重建分支 tag 透传
- **原因行为**：_load_checkpoint 的 FP32 权重重建分支调用 get_fp32_state_dict_from_zero_checkpoint 时不透传 tag，helper 内部重新解析 latest 指针。
- **影响对象**：模型权重（静默错误）
- **影响详情**：指定 tag 且 load_optimizer_states=False 加载、latest 指向其他版本时，返回路径与 client_state 指向请求版本，实际进模型的却是 latest 的权重，无报错无警告；目录无 latest 文件时反而 ValueError。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8499

### TRN-0074 `mfsdp_ckpt_stage_local_layer_keys_pp_resize` Megatron MFSDP ckpt 用局部层号，PP 变更后层错位

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 CKPT.25

- **原因对象**：权重/检查点 / megatron-lm / MFSDP state_dict 层键
- **原因行为**：TransformerBlock 按 stage 局部索引注册层，仅 sharded_state_dict 加全局偏移；MFSDP adapter 把保存用 state dict 别名到普通 state_dict，其元数据不含层位。
- **影响对象**：模型权重（静默错误）
- **影响详情**：fsdp_dtensor ckpt 以 PP=1 保存、PP=2 加载时 strict DCP load 成功，但后续 stage 都被第一阶段的层填充，训练照常进行，loss 不一定立刻异常；4-MLP 复现输出 max err 1.0328。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452

### TRN-0076 `async_save_skips_tracker_write_non_megatron_scratch_restart` verl async_save 漏写 tracker，重启后从头训练

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-21 · 旧号 CKPT.27

- **原因对象**：权重/检查点 / verl / trainer async_save 跳过分支
- **原因行为**：async_save=True 时 _save_checkpoint 无条件跳过写 tracker、不检查 actor.strategy；只有 Megatron manager 会补写 tracker，FSDP 系未实现。
- **影响对象**：可用性/进度；模型权重（静默错误）
- **影响详情**：非 Megatron 后端下 ckpt 完整落盘、只有一条 INFO 日志；重启时 find_latest_ckpt_path 返回 None，resume_mode=auto 判为无 ckpt，静默从 step 0 重训并覆写盘上完好的 ckpt。SFT 不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7952

### TRN-0077 `swiglu_interleave_layout_unconverted_on_load` Megatron-LM 加载不做 SwiGLU 交织转换，通道错配

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-09-23 · 旧号 CKPT.28

- **原因对象**：权重/检查点 / megatron-lm / 原生 ckpt 加载 SwiGLU 交织转换
- **原因行为**：--moe-mlp-glu-interleave-size 32 让激活侧按交织解释 FC1 的 gate/up，但原生加载 contiguous ckpt 时不做对应的权重重排。
- **影响对象**：模型权重；训练信号（质量退化）
- **影响详情**：无 crash、无 warning，SwiGLU 配对错误通道，训练照常推进；MXFP8+CuTeDSL 配置下 initial LM loss 约 2.2，正确路径约 0.2，报告者确认为布局错配而非 FP8 舍入。Megatron-Bridge 加载时显式转换，不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7576

### TRN-0081 `cli_resume_arg_never_reaches_train` trl CLI 不转发 resume_from_checkpoint，从头重训

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-09-28 · 旧号 CKPT.32

- **原因对象**：权重/检查点 / trl / CLI 入口 trainer.train 调用
- **原因行为**：七个训练 CLI 入口把 resume_from_checkpoint 解析进 training config，但调用 trainer.train() 时不转发该参数，而 Trainer.train() 不会自动从 config 读取。
- **影响对象**：可用性/进度（静默错误）
- **影响详情**：通过 CLI 传 --resume_from_checkpoint 的用户以为在续训，run 实际从 step 0 重新训练，无 crash 无警告，进度条从零起步是唯一可见信号；复现中 step 2 存 ckpt 后以 max_steps=3 resume 执行了三步。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/7391
- **关联**：var:TRN-0056

### TRN-0082 `explicit_ckpt_step_overridden_by_release_or_newer_nonpersistent` Megatron 显式 --ckpt-step 被自动发现逻辑覆盖

`故障` · `active` · `shared` · `verified` · `var` · 发现 2026-10-12 · 旧号 CKPT.33

- **原因对象**：权重/检查点 / megatron-lm / checkpointing ckpt 选择逻辑
- **原因行为**：显式 ckpt 选择有三处被覆写：真值检查吞掉 ckpt_step=0；tracker 为 release 时只改 iteration 不重置 release；non-persistent iteration ≥ 请求值时优先加载它。
- **影响对象**：模型权重；指标/日志（静默错误）
- **影响详情**：rollback 与按步评估静默加载错误 ckpt，无 crash 无警告：tracker=100 时请求 0 实选 iter_0000100，tracker 为 release 时请求 100 实选 release；数据进度与模型状态错配，评估指标归因到错误步。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/8110
- **关联**：var:TRN-0056

### TRN-0101 `adam_moment_not_resumed` resume 未恢复 optimizer state，Adam 以零矩接续训练

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-08-17 · 旧号 OPT.01

- **原因对象**：权重/检查点 / 通用 / resume 的优化器状态加载
- **原因行为**：resume 只加载 model 权重而不加载 optimizer，或加载了但 key 对不上，Adam 矩为零却接在已训练很久的权重上，等效突然更换优化器状态。
- **影响对象**：优化器状态；训练轨迹（质量退化）
- **影响详情**：resume 后前几百 step 表现得像重新 warmup，随后可能出现 spike；权重本身正确。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：分布式 resume 常规事故；
- **关联**：var:TRN-0051

### TRN-0125 `async_ckpt_worker_failure_strands_peers` Megatron 持久化 ckpt worker 异常导致全 rank 挂死

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 ACT.04

- **原因对象**：权重/检查点 / megatron-lm / 持久化 ckpt worker 异常传播
- **原因行为**：persistent ckpt worker 子进程异常或硬退出时不发布 completion record，父进程只轮询 completion queue、不把 worker 错误转成分布式错误，失败状态也不清理。
- **影响对象**：可用性/进度；模型权重（挂起）
- **影响详情**：开启 --use-persistent-ckpt-worker 时单 rank worker 故障即把全部分布式 peer 挂死在 ckpt finalize，step 计数冻结；若 watchdog 重启 job 并 resume，可能静默接上写了一半的 ckpt。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/6970；https://github.com/NVIDIA/Megatron-LM/pull/6971

### TRN-0151 `expert_weight_id_misbind` EP 运行时布局与 ckpt/HF 转换专家序号不一致，专家错绑权重

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-08-17 · 旧号 MOE.02

- **原因对象**：权重/检查点 / 通用 / EP 布局与 ckpt 专家序号约定
- **原因行为**：运行时 EP 布局与 ckpt / HF 转换使用的专家序号约定不一致，router 选中 expert k 时实际计算的是另一套专家权重。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：无报错，训练在错绑的专家上自洽地继续，评测结果像换了一个模型。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：同 CKPT.01。
- **关联**：var:TRN-0050

### TRN-0184 `lora_target_modules_silent_partial_match` TRL 示例 LoRA target_modules 静默欠匹配

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-24 · 旧号 SFT.07

- **原因对象**：权重/检查点 / trl / LoRA target_modules 选择器
- **原因行为**：未匹配模块的 target_modules 条目被静默跳过且无告警；官方示例对 NemotronH 给出 Llama 式 MLP 名，Mamba-2 与 MoE 层名不同，adapter 只挂上 56 层中的 4 层 attention。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：DPO LoRA 25 步 loss 钉在 0.6931=ln(2)、模型行为不变；SFT 场景只训了约 7% 的层，loss 会降但远弱于预期，曲线上无法区分。全程无 crash、无 warning，复制官方示例即触发。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6773；https://github.com/huggingface/trl/issues/7765

### TRN-0193 `teacher_model_rebuilt_fp32_default_attn_mismatch` trl SDFT/SDPO teacher 回落 fp32 与默认 attn

`故障` · `active` · `sft` · `verified` · `var` · 发现 2026-10-10 · 旧号 SFT.16

- **原因对象**：权重/检查点 / trl / SDFT/SDPO teacher 构建参数
- **原因行为**：policy 以实例传入时 model_init_kwargs 为空，create_model_from_path 重建 teacher 时回落 float32 与默认 attention 实现，未继承 student 的设置。
- **影响对象**：训练信号；输出分布（静默错误）
- **影响详情**：teacher 与 student 从 step 0 起 dtype/attention 双重不一致（如 policy bf16+eager → teacher fp32+sdpa），KL/JSD 蒸馏信号系统性偏差、随 SDPA 后端漂移，fp32 teacher 多占显存；日志无提示。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7618；https://github.com/huggingface/trl/pull/7597
- **关联**：var:distillation_teacher_dtype_mismatch_jsd_sign_flip

### TRN-0235 `teacher_engine_never_receives_real_weights` verl 多教师蒸馏的教师引擎继承 dummy 加载，始终用随机权重

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-06 · 旧号 RL-RO.13

- **原因对象**：权重/检查点 / verl / 教师配置 load_format 缺省继承
- **原因行为**：多教师 OPD 经 sparse Hydra override 构造教师配置时，缺省 inference 字段从 RolloutConfig 继承 load_format=dummy，而教师引擎没有任何后续权重同步纠正。
- **影响对象**：模型权重；训练信号（静默错误）
- **影响详情**：受影响教师整段训练都用随机初始化权重给出蒸馏信号；蒸馏 loss 正常计算、正常下降，学生被拉向随机教师的输出分布，无 crash、无警告，唯一线索是蒸馏收益远低于预期。单教师 YAML 路径缺省为 auto。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7742
- **关联**：var:TRN-0052

### TRN-0237 `fsdp2_to_empty_unties_tied_embeddings` verl FSDP2 加载 to_empty() 断开 tied 权重绑定

`故障` · `active` · `rl` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 RL-RO.15

- **原因对象**：权重/检查点 / verl / FSDP2 全量 state dict 加载
- **原因行为**：fsdp2_load_full_state_dict 用 to_empty() 物化非零 rank 参数，为每个参数分配全新存储，tied lm_head 与 embedding 的别名就此断开，之后未重新 tie。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：无 crash、无指标异常，loss 照降；tied 模型走 FSDP2 meta init 加载后，非零 rank 静默按 untied 训练，embedding 只收 input 侧梯度（实测 grad norm 0.3548→0.2271）。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7835；https://github.com/verl-project/verl/issues/7834

### TRN-0278 `lora_ckpt_missing_moe_routing_rng` mindformers LoRA 续训 ckpt 漏存 MoE 路由态与 RNG

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：权重/检查点 / mindspore / LoRA ckpt 保存范围
- **原因行为**：save_trainable_only 只存 LoRA A/B，漏存每步更新且影响下一步专家路由的 MoE expert_bias/tokens_per_expert，也不存各 rank RNG 状态。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：8 卡 PyNative LoRA 微调第 40 步仅存 LoRA 参数与优化器后续训，第 41-50 步与连续训练不对齐：loss 最大绝对误差 3.89e-4，grad norm 最大绝对误差 0.0435、最大相对误差 27.4%；无报错。
- **改进措施**：检测 断点续训与连续训练在重叠步做 loss/grad norm 对账；隔离实验分别恢复 RNG 与 MoE 状态定位偏差来源。；修复 修复 MR !8868（open）：LoRA trainable-only ckpt 追加 MoE expert_bias/tokens_per_expert，ckpt I/O 前按 rank 原子保存 RNG sidecar（加载优化器续训时恢复，老断点缺 sidecar 兼容告警）；修复后第 41-50 步 loss/grad norm 误差 0.0/0.0%。https://atomgit.com/mindspore/mindformers/merge_requests/8868
- **来源**：https://atomgit.com/mindspore/mindformers/merge_requests/8868；https://gitcode.com/mindspore/org-issues/issues/43525

### TRN-0306 `mswift_last_ckpt_symlink_shared_tmp_race` ms-swift last-checkpoint 符号链接共享 tmp 路径竞态

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：权重/检查点 / ms-swift / last-checkpoint 符号链接更新
- **原因行为**：update_last_checkpoint_symlink 用固定暂存路径 last-checkpoint.tmp：并发保存回调互删对方暂存链接，os.replace 后发布别人的目标且返回成功，另一方丢暂存链接
- **影响对象**：模型权重（静默错误）
- **影响详情**：并发 checkpoint 保存（如多进程训练各自更新 last-checkpoint，或保存与导出重叠）时，训练完成后 last-checkpoint 链接可能指向另一个（旧的或别人的）checkpoint 目录，且一个调用方收到成功返回；按该链接恢复训练会静默加载错检查点，无任何报错。
- **改进措施**：检测 发布后 readlink 校验目标等于自身 checkpoint 名；并发保存时对链接做轮询比对；修复 待定（issue open：给出确定性双线程 barrier 复现与修复方向——每次更新用唯一暂存名（如 mkstemp 风格/pid 后缀）；swift 侧修复 PR 未见）
- **来源**：https://github.com/modelscope/ms-swift/issues/10336

### TRN-0352 `msllm_mg2hf_grouped_qkv_plain_unpack` MCore→HF 拆 grouped QKV 错位致导出模型乱码

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：权重/检查点 / mindspeed-llm / convert_mg2hf QKV unpack
- **原因行为**：convert_mg2hf 的 unpack 分支按 [Q,K,V] 顺序切 fused linear_qkv，而 GQA 模型在 MCore 里存的是 [Q 组,K,V] 交错布局，切完 q/k/v_proj 全错位。
- **影响对象**：模型权重；输出内容（静默错误）
- **影响详情**：Qwen3-0.6B（TP=PP=EP=1）无训练 round-trip 后 311/311 键齐全，但仅 q_proj/k_proj/v_proj 有差（max_abs 0.42~0.67），其余为 0；生成 aseña/Glish/ature 类重复碎片，原 HF 权重同脚本正常。
- **改进措施**：检测 转换后逐 tensor 对比原始 HF ckpt，重点看 q/k/v_proj 的 mean_abs 是否非零；修复 issue #1532 建议新增 _split_grouped_qkv_weight，按 num_attention_heads/num_query_groups 分组拆分（issue closed，正文未附修复 PR，未核实）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1532

### TRN-0356 `msllm_ms_ckpt_missing_qkv_bias_strict_false` MindSpore 加载 ckpt 缺键被 strict=False 吞掉

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：权重/检查点 / mindspore / MindSpore load_state_dict
- **原因行为**：MindSpore 路径转换出的 ckpt 缺 linear_qkv.bias 与 linear_fc1.layer_norm_weight，加载报 Missing key；改 strict=False 后缺键被跳过、参数保持随机初始化。
- **影响对象**：模型权重；训练轨迹（报错）
- **影响详情**：按 install_guide 与 quick_start 做完权重转换后训练起不来（load_state_dict 报 missing key）；改 strict=False 能跑，但缺失键对应参数保持初始化值、等于部分随机初始化继续训练，对结果影响未知
- **改进措施**：检测 加载后逐层比对 missing/unexpected 清单，必须为空才继续；对 qkv bias 与 fc1 layernorm 参数做加载前后指纹比对；修复 issue #1337 只给出把 strict 改 False 的规避（closed，无修复 PR，未核实）；正解是让权重转换补齐或映射这两个键，不要用 strict=False 掩盖
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1337

### TRN-0359 `msllm_hf2mg_convert_ckpt_path_mismatch` hf2mg 自动转换与切分策略不对齐致加载失败

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：权重/检查点 / mindspeed-llm / hf2mg convert + VPP 切分
- **原因行为**：示例脚本默认带 --enable-hf2mg-convert，会就地把 CKPT_LOAD_DIR 的 HF 权重转成 mg；README 却让人先转换再传转换后目录，且转换脚本未给 VPP 而预训练脚本给了。
- **影响对象**：可用性/进度；模型权重（报错）
- **影响详情**：按 README 填转换后路径启动，报 AssertionError: cannot find safetensor, please check load dir；对齐转换与 VPP 后仍可能以 KeyError: model0 退出，预训练拉不起来。
- **改进措施**：检测 启动前断言 CKPT_LOAD_DIR 内是否含 HF safetensors 与 --enable-hf2mg-convert 是否同时成立；核对转换脚本与训练脚本的 tp/pp/ep/vpp；修复 issue 建议文档提醒：带 --enable-hf2mg-convert 时不要先做转换；并在切分脚本补 VPP 参数或从预训练脚本移除 VPP（closed，未附修复 PR，未核实）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1299

### TRN-0499 `trl_fsdp2_ref_model_zero_shards` TRL FSDP2 参考模型非 rank0 分片全零

`故障` · `active` · `rl；sft` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：权重/检查点 / trl / prepare_fsdp
- **原因行为**：cpu_ram_efficient_loading 下其余 rank 填零并期待 broadcast；TRL prepare_fsdp 只调 fully_shard（无 broadcast），非本地 rank0 分片保留零。
- **影响对象**：模型权重；训练信号（静默错误）
- **影响详情**：FSDP2+cpu_ram_efficient_loading 时 DPO/KTO/RLOO/GRPO(beta>0) 参考模型与 SDFT/SDPO 教师在非 rank0 分片全零：ref logprob/KL 按错误参考计算，静默产出偏置 loss；无 crash。
- **改进措施**：检测 加载后比对 ref 模型 full_tensor() 与 checkpoint 权重（issue 附最小复现断言）；对比 FSDP1 同配置 ref logprob；修复 待定（issue open 2026-10-28；FSDP1 的 sync_module_states 不受影响；需 TRL 在 FSDP2 包装前 broadcast 或等 transformers#45649 meta 方案配套）
- **来源**：https://github.com/huggingface/trl/issues/7993

### TRN-0542 `deepspeed_zero_reexport_stale_index_loads_old_weights` DeepSpeed ZeRO 二次导出残留旧索引加载旧权重

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：权重/检查点 / deepspeed / zero_to_fp32 导出索引清理
- **原因行为**：向已有输出目录再次导出 ZeRO 检查点时不清理旧 index/shard：先分片 FP32 后单文件 BF16 导出返回成功，目录加载器仍按残留旧索引读旧分片
- **影响对象**：模型权重（静默错误）
- **影响详情**：第二次转换本身写对，但 stale index 让 loader 读到旧权重：后续训练或推理静默使用旧模型，无报错；DeepSpeed master 8d4f29c7、含无 mock 复现脚本
- **改进措施**：检测 导出后校验 index 文件时间戳与权重 dtype/数值指纹（如 tag 值断言）；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8954（open，Retire stale checkpoint artifacts after replacing a ZeRO export，未合入）
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8952；https://github.com/deepspeedai/DeepSpeed/pull/8954

## 数据管线

### TRN-0057 `epoch_boundary_resume_silent_skip` verl SFT 在 epoch 边界 resume 静默跳过下一 epoch

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-19 · 旧号 CKPT.08

- **原因对象**：数据管线 / verl / dataloader epoch 迁移恢复
- **原因行为**：多 epoch SFT 在 epoch 边界存 ckpt 后 resume，dataloader/sampler 状态恢复路径错过「进入下一 epoch」的迁移，静默跳过整个下一 epoch。
- **影响对象**：训练样本流；训练轨迹（静默错误）
- **影响详情**：run 以 status 0 正常退出，所请求数量的更新从未发生，欠训模型被当作完成的 run，操作员/调度器看到的是绿色；生产 CheckpointHandler + StatefulDataLoader 可确定性复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7401

### TRN-0062 `wrong_rng_object_checkpointed` DeepSpeed curriculum sampler 存错 RNG，采样重放

`故障` · `active` · `pretrain；sft` · `verified` · `var` · 发现 2026-09-04 · 旧号 CKPT.13

- **原因对象**：数据管线 / deepspeed / DeepSpeedDataSampler RNG
- **原因行为**：DeepSpeedDataSampler 用自有 np_rng 采样，state_dict()/load_state_dict() 却存取全局 np.random 状态；resume 时自有 RNG 被重新播种且从不恢复。
- **影响对象**：训练样本流；训练轨迹（静默错误）
- **影响详情**：resume 后 curriculum 难度调度与 cluster shuffle 从头重放，后半程重复前半程样本序，训练看似正常推进；恢复全局 RNG 还会牵动进程内其他使用 np.random 的组件。修复 PR #8460 未合入，#8787 独立重报同一失效。
- **改进措施**：检测 待定；修复 修复 PR #8460 closed unmerged；新修复 PR #8788 open（2026-10-09 后无更新），主干缺陷仍在
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8405；https://github.com/deepspeedai/DeepSpeed/pull/8460；https://github.com/deepspeedai/DeepSpeed/issues/8787
- **关联**：var:TRN-0083

### TRN-0067 `resume_rebuilt_sampler_loses_epoch_seed` ms-swift resume 丢失 epoch 种子致样本重复与遗漏

`故障` · `active` · `pretrain；sft` · `documented` · `var` · 发现 2026-09-07 · 旧号 CKPT.18

- **原因对象**：数据管线 / ms-swift / _patch_skip_first_batches
- **原因行为**：_patch_skip_first_batches 重建的 BatchSamplerShard 其 curr_seed 重置为 base_seed 且从未 set_epoch()，恢复后按 epoch-0 排列跳前 N 批。
- **影响对象**：训练样本流；训练轨迹（静默错误）
- **影响详情**：epoch≥1 内 resume 才暴露：resume“成功”、loss 正常甚至更低，已训样本重复计权、该 epoch 尾部样本从未见过；实测恢复后 86 步 per-step loss 与原 pass 的 Pearson 为 −0.23，模拟 81% 样本重复、15% 语料未训练。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10050
- **关联**：var:TRN-0062

### TRN-0072 `onpolicy_resume_offset_counted_in_rollout_rows` ms-swift on-policy 续训 offset 错算跳过数据

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-09-13 · 旧号 CKPT.23

- **原因对象**：数据管线 / ms-swift / on-policy 续训 offset 与种子
- **原因行为**：ckpt 的 consumed_train_samples 计的是 rollout 行数，dataloader 却按 query 行索引并原样使用该 offset；sampler 只用 epoch 作种子、忽略 data_seed。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：Megatron 后端 GRPO/GKD 在 n 路 generation 下 resume 无报错，但跳过 n 倍过远，从数据集错误位置继续：部分 query 从未训练、部分重复训练，梯度与 loss 曲线正常；配置的 data_seed 对 on-policy 数据序无效。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10099；https://github.com/modelscope/ms-swift/pull/10113
- **关联**：var:TRN-0067

### TRN-0075 `async_resume_cursor_pinned_by_stale_dropped_group` trl AsyncGRPO resume 游标被 stale 丢弃组钉死

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-19 · 旧号 CKPT.26

- **原因对象**：数据管线 / trl / 异步 GRPO/蒸馏 resume 游标
- **原因行为**：_save_checkpoint 取不在 _trained_groups 中的最小 group id 作 resume 位置，但被 staleness 检查丢弃的 group 永不进入该集合，游标被钉死；蒸馏 trainer 同病。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：有 group 因超过 max_staleness 被丢弃时，ckpt 正常写出、无报错、指标正常；resume 后从被钉住的位置重启，近全量数据被重复训练（复现中 150 行有 147 行训练两次）。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7274；https://github.com/huggingface/trl/pull/7294；https://github.com/huggingface/trl/pull/7786
- **关联**：var:TRN-0065

### TRN-0079 `cyclic_sharded_resume_dp_resize_reorder` Megatron cyclic 分片 sampler 换 DP 续训致样本错乱

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-25 · 旧号 CKPT.30

- **原因对象**：数据管线 / megatron-lm / cyclic 分片 sampler 重建
- **原因行为**：默认 data sharding 下 ckpt 只存标量 consumed_train_samples；resume 用新的 DP 尺寸重建 sampler，而各 rank 的 bucket 大小、偏移与起点都依赖 DP 尺寸。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：换 DP 尺寸 resume 后无 error 无 warning，已消费样本被重放、未消费样本被跳过，此后每个 epoch 都从错误 offset 开始（DP4→2 时 58 条重复、58 条未抽到）；single 类型不受影响，端到端影响未实测。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7645；https://github.com/NVIDIA/Megatron-LM/pull/7648

### TRN-0080 `cyclic_unsharded_resume_epoch_boundary_dp_remainder` Megatron 非分片 sampler 换 DP 续训 epoch 边界错位

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-09-25 · 旧号 CKPT.31

- **原因对象**：数据管线 / megatron-lm / RandomSampler epoch 边界推导
- **原因行为**：--no-data-sharding 下 sampler 以 total_samples 减 total%(mbs×dp) 推导 epoch 边界，epoch 长度含 DP 尾数，而 ckpt 只存消费样本数。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：数据集大小不能被 mbs×dp 整除时换 DP resume，当前 epoch 尾部被重放或跳过，此后每个 epoch 从错误 offset 开始（DP1→8 时 19 条重复、19 条丢失）；整除组合不受影响，无 crash 无 warning，端到端影响未实测。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7646；https://github.com/NVIDIA/Megatron-LM/pull/7649
- **关联**：var:TRN-0079

### TRN-0083 `rank_shuffle_seed_desync` DP rank 间 shuffle 种子不一致，batch 混入无关语料

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 DATA.01

- **原因对象**：数据管线 / 通用 / 各 DP rank 的 shuffle 种子
- **原因行为**：各 DP rank 使用了不同的 shuffle 种子，或部分 rank 忘了设种子，使同一 global batch 的切片不是同一文档的不同分片，而是不同语料。
- **影响对象**：训练样本流；梯度（质量退化）
- **影响详情**：无 crash，loss 仍下降、token/s 正常，但评测方差异常大。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：Megatron/DeepSpeed 数据加载常见事故（本实验室 `verify_dataset.py` / MMIDIDX 校验动机之一）。

### TRN-0084 `packing_cross_document_attention` packing 未按文档边界切断 attention，后一条样本可见前一条

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 DATA.02

- **原因对象**：数据管线 / 通用 / packing 文档边界 mask 与位置 id
- **原因行为**：把多条样本 pack 进同一序列以提高利用率时，attention mask 与 position id 没有按文档边界切断。
- **影响对象**：跨请求/跨样本数据；训练轨迹（质量退化）
- **影响详情**：后一条样本的 token 能看见前一条的内容，模型学会“抄下一条的答案”；验证集单条样本分数虚高，真实对话掉点。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：SFT packing 的标准正确性陷阱；

### TRN-0085 `loss_mask_includes_prompt` completion-only 训练 loss mask 误含 prompt

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 DATA.03

- **原因对象**：数据管线 / 通用 / SFT loss mask 构造
- **原因行为**：completion-only 训练把 prompt token 的 CE 也计入 loss，或没有 mask chat template 的 special token。
- **影响对象**：训练样本流；训练轨迹（质量退化）
- **影响详情**：SFT loss 看起来健康且更低（prompt 更好预测），但模型被训练成复述用户的话，指令遵循变差。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：TRL / ms-swift / llama-factory 反复出现的 mask 配置错误。

### TRN-0087 `mmididx_wrong_magic_silent_garbage` 非 MMIDIDX 数据被当作 MMIDIDX 读取，产出垃圾 token

`故障` · `active` · `pretrain` · `verified` · `NEW` · 发现 2026-08-17 · 旧号 DATA.05

- **原因对象**：数据管线 / megatron-lm / MMIDIDX 数据集读取与格式校验
- **原因行为**：把 nanoGPT 的 .bin/.idx 或未完成的分片当成 Megatron MMIDIDX 读取，阅读器不总是立即崩溃，可能吐出合理范围内的垃圾 token id。
- **影响对象**：输入编码；训练轨迹（静默错误）
- **影响详情**：无格式错误；训练起步 loss 就在随机基线附近打转，或能降但降不动。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：`opensource_training_megatron` CLAUDE.md / `verify_dataset.py`。

### TRN-0088 `padding_free_boundary_merges_sequences` ms-swift padding_free 漏判长度 1 序列，样本标签错位

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-18 · 旧号 DATA.06

- **原因对象**：数据管线 / ms-swift / revert_padding_free 边界推断
- **原因行为**：padding_free 还原侧靠 position_ids 的下降沿推断序列边界；前一序列长度为 1 时不存在下降沿（0 | 0 1 2 中 0<0 为假），两条独立序列被静默合并。
- **影响对象**：训练样本流；跨请求/跨样本数据（静默错误）
- **影响详情**：实测单 batch 的 sentence embedding 从 516 条错减为 260 条而 labels 数量不变，样本与标签错位；轻度时不报错但 InfoNCE 学错配对，重度时报 InfoNCE zero negative 崩溃。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/9903

### TRN-0089 `seqlen_packer_off_by_one_drops_last_sample` DeepSpeed batch_by_seqlens 差一错误，末样本永不入批

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-08-30 · 旧号 DATA.07

- **原因对象**：数据管线 / deepspeed / batch_by_seqlens 切片上界
- **原因行为**：batch_by_seqlens 贪心扩展切片时 range(batch_init + m, len(metrics), m) 的独占上界使 batch_end 取不到 len(metrics)，尾样本被当作“没数据了”而 break。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：无报错、训练曲线正常；sequence_picking_order 为 dataloader/seqlen 时同一尾样本每个 epoch 都被丢弃，为 random 时每个 epoch 丢不同样本。复现：seqlens=[1,2,3,4,5] 只产出样本 [0,1,2,3]。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8347

### TRN-0090 `loss_mask_cache_aliasing_leaks_first_sample` GPTDataset loss_mask 缓存别名致 pad 掩码污染

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-31 · 旧号 DATA.08

- **原因对象**：数据管线 / megatron-lm / GPTDataset loss_mask 缓存
- **原因行为**：FILL 路径把 loss_mask 的引用存入 cached_loss_mask，随后对 pad 位置就地置零写穿缓存；缓存单槽且每个数据集只 FILL 一次，第一个被服务的样本若含 pad 位，其零掩码永久进入之后每个样本的 mask。
- **影响对象**：训练样本流；跨请求/跨样本数据（静默错误）
- **影响详情**：静默，loss 按 mask sum 归一化仍看似合理；哪个样本执行 FILL 取决于进程，从头启动与 resume 的 run 对同一样本使用不同 mask，ckpt 与输入 bitwise 一致时梯度仍从 resume 后第一步分叉。pad id 出现在数据中即可触发。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6981

### TRN-0099 `preprocessed_map_cache_cross_version_reuse` ms-swift 预处理 cache 缺代码版本，升级后复用旧 schema

`故障` · `active` · `sft` · `verified` · `var` · 发现 2026-10-09 · 旧号 DATA.17

- **原因对象**：数据管线 / ms-swift / 预处理数据集 map cache 命名
- **原因行为**：预处理 map cache 只以输入指纹命名，预处理代码版本不在 cache 身份中；datasets 对显式 cache_file_name 只查文件存在，语义跨版本变化时同一输入命中旧 cache。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：升级 ms-swift（如 v4.0.0→v4.4.0）后静默加载旧版本 cache，以旧 schema 训练（loss 列为 float64、缺 loss_scale），新版预处理修复对已缓存数据集失效；日志仅显示 Loading cached processed dataset，无警告。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/pull/10301
- **关联**：var:TRN-0056

### TRN-0100 `gkd_off_policy_eos_supervision_dropped` ms-swift GKD 离线蒸馏样本不加 EOS，终止监督缺失

`故障` · `active` · `sft` · `documented` · `var` · 发现 2026-10-10 · 旧号 DATA.18

- **原因对象**：数据管线 / ms-swift / GKDSample 的 add_eos 默认值
- **原因行为**：GKD 离线蒸馏（--lmbda 0）的数据集样本沿用 rollout 默认 add_eos=False，response 不带字面 EOS 时不追加 EOS，蒸馏 KL loss 与辅助 SFT loss 均缺终止监督。
- **影响对象**：训练样本流；训练轨迹（静默错误）
- **影响详情**：离线蒸馏训出的学生学不到何时停止：终止概率漂移、生成不停止或过早停止，蒸馏 loss 曲线完全正常、无 crash。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10282；https://github.com/modelscope/ms-swift/pull/10285
- **关联**：var:TRN-0092

### TRN-0179 `packed_next_sample_as_completion` packing 时 label 不在文档边界断开，模型学到下一条样本

`故障` · `active` · `sft` · `documented` · `var` · 发现 2026-08-17 · 旧号 SFT.02

- **原因对象**：数据管线 / 通用 / packing 文档边界 label 构造
- **原因行为**：packing 时 label 在文档边界不断开，下一条样本的 token 被当作本条 completion 参与监督。
- **影响对象**：训练样本流；跨请求/跨样本数据（质量退化）
- **影响详情**：训练 CE 异常偏低；上线后模型出现「回答下一题」的行为。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：与 DATA.02 成对。
- **关联**：var:TRN-0084

### TRN-0180 `assistant_mask_drops_last_turn` 多轮 SFT 的 assistant mask 漏掉末轮或误学 tool 结果

`故障` · `active` · `sft` · `documented` · `var` · 发现 2026-08-17 · 旧号 SFT.03

- **原因对象**：数据管线 / 通用 / 多轮 assistant loss mask
- **原因行为**：多轮 mask 逻辑漏掉最后一轮 assistant，或把 tool 结果当作 assistant 内容监督，有效监督信号被砍掉或角色标错。
- **影响对象**：训练样本流；训练轨迹（质量退化）
- **影响详情**：多轮对话能力明显弱于单轮，训练 loss 上看不出异常。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：chat template + 多轮 SFT 的边界 bug 族。
- **关联**：var:TRN-0085

### TRN-0181 `preference_pair_swapped_or_identical` 偏好对 chosen/rejected 对调或两条相同

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 SFT.04

- **原因对象**：数据管线 / 通用 / 偏好数据 chosen/rejected 列
- **原因行为**：DPO/ORPO 偏好数据的 chosen 与 rejected 列被对调，或两条内容完全相同。
- **影响对象**：训练样本流；训练信号（静默错误）
- **影响详情**：梯度符号反转或为零但训练仍照常进行；reward margin 变负或钉在 0，模型风格往差的一侧偏移。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：偏好数据管道的经典静默错误。

### TRN-0183 `truncation_forges_identical_preference_pair` OpenRLHF RewardDataset 独立截断造出相同偏好对

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-08-21 · 旧号 SFT.06

- **原因对象**：数据管线 / openrlhf / RewardDataset 截断与 EOS 覆写
- **原因行为**：RewardDataset 对 chosen/rejected 各自独立截断到 max_length 并把末位 token 覆写为 EOS；差异在截断边界后或末位时两条输入完全相同，变换后无校验，坏 pair 被保留训练。
- **影响对象**：训练样本流；训练信号（静默错误）
- **影响详情**：RM/DPO 的 pair loss 恒为 ln(2)、偏好梯度精确为 0，常数损失样本稀释 batch 梯度、扭曲 accuracy 口径；默认 max_len=512 下长答案数据集必然渗入。无 crash、无 NaN，loss 只是降得慢。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/issues/1311
- **关联**：var:TRN-0181

### TRN-0186 `nondiverging_pair_prompt_split_off_by_one` trl extract_prompt 对不分歧偏好对切分差一位

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-08-30 · 旧号 SFT.09

- **原因对象**：数据管线 / trl / extract_prompt 分歧点切分
- **原因行为**：extract_prompt 找 chosen/rejected 首个分歧点，两者从不分歧（前缀包含或相同）时循环无 break，idx 停在 min(len)-1 而非 min(len)，最后一条公共消息被挤出 prompt。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：被挤出的消息逐字复制进 chosen 与 rejected 两侧，prompt 边界错位，DPO/KTO 在错位的对比目标上训练；无 crash、无 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/6960
- **关联**：var:TRN-0181

### TRN-0187 `zero_diff_probe_slice_drops_system_prompt` verl 前缀探针长度差为 0 时切片丢失 system prompt

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-30 · 旧号 SFT.10

- **原因对象**：数据管线 / verl / system prompt 前缀探针切片
- **原因行为**：initialize_system_prompt 用两次 probe 渲染的长度差切前缀 token1[:-diff]；模板渲染不增长时 diff 为 0，token1[:-0] 得到空表，system prompt 被丢成 []。
- **影响对象**：训练样本流；输入编码（静默错误）
- **影响详情**：在只渲染首条消息类的合法模板下，MultiTurnSFTDataset 对每个非首轮 turn 剥离 0 个 leading token，每轮都被塞进重复的 system+首轮前缀；训练无报错、loss 正常。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7592；https://github.com/verl-project/verl/pull/7756

### TRN-0189 `trajectory_split_default_scale_reweights_turns` ms-swift 多轮轨迹拆分时默认 loss_scale 重复计权前段轮次

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-09-03 · 旧号 SFT.12

- **原因对象**：数据管线 / ms-swift / 多轮调度器轨迹拆分 loss_scale
- **原因行为**：多轮调度器把同一轨迹按轮拆成多条训练样本时，默认 loss_scale 让每轮 assistant 内容都全权计入 loss，前几轮在多条样本中被重复训练；默认值不随拆分模式切到 last_round，也无警告。
- **影响对象**：训练样本流；梯度（静默错误）
- **影响详情**：不叠加序列并行时无报错：前段/中间轮次 token 的有效梯度权重按拆分轮数放大，训练静默偏向对话前段行为；叠加 SP 时非整除维度直接 AssertionError。需显式 loss_scale=last_round 规避。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/9996

### TRN-0254 `train_loader_geometry_reused_for_val` verl SFT 验证集沿用训练 batch，val/loss 为 NaN

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-22 · 旧号 OBS.05

- **原因对象**：数据管线 / verl / SFT trainer 验证 loader 构造
- **原因行为**：两个 SFT trainer 用训练全局 batch 构造验证 loader，sampler 与 dataloader 均 drop_last=True；注释所称的 val batch 字段在 val 路径从未被读。
- **影响对象**：指标/日志（数值异常）
- **影响详情**：val 集小于每 rank 训练 batch 时 loader 产出 0 个 batch，空张量取均值得 val/loss=NaN，无警告且 exit 0；val 集略大于 batch 时静默丢尾部样本（300 样本丢 5）。Ray 路径 200 样本×batch 256 即复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7464

### TRN-0267 `kto_unpaired_single_label_blocks` trl KTO 成对数据集拆成单标签整块 batch

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-14

- **原因对象**：数据管线 / trl / KTO 成对数据集 unpair 分组
- **原因行为**：成对 KTO 数据集按文档路径进入 trainer 时被 unpair 成 desirable/undesirable 各自连续的大块，数据加载层未打散标签块，绝大多数 micro-batch 内只有一种标签。
- **影响对象**：训练样本流；训练信号（质量退化）
- **影响详情**：配对数据集按文档用法训练时 300 batch 仅 2 个混合双标签；多数步无 rewards/margins，块内 KTO 对比统计退化；训练静默完成无报错；手工 unpair+shuffle 后 295/300 混合、指标恢复。
- **改进措施**：检测 在数据加载层检查每个 micro-batch 的标签构成（含两种标签的 batch 占比），0% 混合即报警。；修复 修复 PR #7684（2026-10-13 closed unmerged，未落地）：unpair 后按 args.seed shuffle 打散标签块（IterableDataset 无 shuffle 保持原样）。当前 workaround：构造 trainer 前自行 unpair_preference_dataset + shuffle。https://github.com/huggingface/trl/pull/7684
- **来源**：https://github.com/huggingface/trl/issues/7682

### TRN-0268 `loss_mask_probe_ignores_enable_thinking_default` verl loss mask 探针不感知 thinking 默认值

`故障` · `active` · `sft` · `verified` · `NEW` · 发现 2026-10-14

- **原因对象**：数据管线 / verl / MultiTurnSFTDataset 探针
- **原因行为**：loss mask 探针不接收 enable_thinking_default，按模板内置默认测 generation_prompt 长度，与逐消息渲染的 thinking 模式不一致。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：显式设 enable_thinking_default 且模板两种模式前缀长度不同时，assistant turn 的模板前缀 token 被误计入 loss（或反向误 mask 丢梯度）；训练无报错、loss 正常。
- **改进措施**：检测 对每条样本分别以两种 thinking 设置渲染探针并比对 loss mask 边界 token 是否均被 mask；或核对 loss_mask==1 段首是否含模板控制 token。；修复 PR #8086 描述的第二处修复（extract_system_prompt_and_generation 接收 enable_thinking_default）未进入 merge diff：该 PR 最终只合入 YAML 默认值 none→null 一行（https://github.com/verl-project/verl/pull/8086/files），截至 2026-10-14 main 代码 verl/utils/dataset/multiturn_sft_dataset.py:180-182 仍不传该参数，缺陷仍在 HEAD。
- **来源**：https://github.com/verl-project/verl/pull/8086

### TRN-0269 `streamed_shards_repeat_window_mismatch` trl 流式数据集分片下静默跳过/重复训练 prompt

`故障` · `active` · `rl；sft` · `documented` · `NEW` · 发现 2026-10-14

- **原因对象**：数据管线 / trl / GRPO/RLOO 流式数据加载分组
- **原因行为**：repeat_iterable_dataset按全局prompt数构造窗口内同一batch重复，_prepare_inputs只对首个batch生成；独享shard时进程窗口含多个不同batch。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：流式数据集且dispatch_batches=False，Accelerate分配独享shard（1.14起n_shards≥进程数、此前>进程数）时，仅窗口首个batch生成并训练，其余batch的prompt静默跳过，其余步重复训练；2进程16prompt实训8，无报错警告且训练正常完成。
- **改进措施**：检测 训练步数×每步 prompt 数与数据集总 prompt 数对账；或按 uid 统计被生成 prompt 集合。；修复 修复 PR #7697（open 未 merge）：各进程只按自己份额（generation_batch_size // num_generations // num_processes）分组，份额切不开时 ValueError；修复后 16/16 prompt 全训。https://github.com/huggingface/trl/pull/7697
- **来源**：https://github.com/huggingface/trl/issues/7690；https://github.com/huggingface/trl/pull/7697

### TRN-0290 `mswift_lazy_dataset_resume_fallback_divergence` ms-swift LazyLLMDataset resume 后超长替换样本选错

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：数据管线 / ms-swift / LazyLLMDataset 替换游标
- **原因行为**：LazyLLMDataset 用自建 _idx/_idx_list 游标选超长删除后的替换样本，_idx 为实例内部状态；resume 重建实例后 _idx 归零，跳过已消费行不复放此前的编码失败，后续替换选择与连续训练分叉。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：固定 seed、sampler 位置正确、编码确定的前提下，resume 后再次触发超长删除时替换样本不同：64 行实验 row20 连续选 58、重建后选 52；真实 ckpt 实验步 5-8 最大 loss 差 0.0025。
- **改进措施**：检测 对比 resume 与连续训练的 consumed batch 序列；对触发替换的样本记录替换来源做审计。；修复 issue 给出方向：为每个发生替换的样本现场生成只依赖全局 seed 与样本序号的候选列表，使数据集无状态（未核实修复 PR 状态；issue open）
- **来源**：https://github.com/modelscope/ms-swift/issues/10374

### TRN-0293 `trl_diffusion_gemma_sliding_prefix_eviction` trl DiffusionGemma SFT 滑窗逐出被 mask 的前缀

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：数据管线 / trl / 示例 decoder mask 与滑窗缓存交互
- **原因行为**：示例 compute_loss 先为 encoder AR co-loss 编码完整序列，再用 decoder mask 限制上下文到 prefix；native 滑窗缓存在 mask 生效前可能已把该 prefix 逐出。
- **影响对象**：梯度；隐状态（静默错误）
- **影响详情**：滑窗逐出 prefix 时 diffusion loss 偏移（4.3688 vs 4.3668）、decoder 可见 cached prefix 从 128 token 变 0，最大参数梯度差 0.146（相对 L2 77%）；384-token 不逐出对照差 2.38e-7。SFT 静默训错。
- **改进措施**：检测 对照独立编码 prefix 的 loss/梯度（issue 附 CPU 复现脚本）；检查滑窗保留位置与 mask 窗口的覆盖关系。；修复 待定（issue open 5 评论；参考修法=decoder 侧单独编码 sampled prefix、保留完整 encoder pass，示例代码修正未核实合入）
- **来源**：https://github.com/huggingface/trl/issues/7734

### TRN-0331 `mindspeed_llm_packing_mbs_gt1_precision_collapse` packing 下 MBS>1 首 loss 偏高并乱码

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：数据管线 / mindspeed-llm / packing 样本边界与 MBS>1
- **原因行为**：开启 --append-eod packing 且 MBS>1 时训练后模型精度异常，MBS=1 不复现；报告未确认代码级根因。
- **影响对象**：训练样本流；训练轨迹（质量退化）
- **影响详情**：qwen3-8b 预训练 MBS=4/GBS=128/seq 8196/tp8pp1 时首 loss 约 6（正常约 2），一个 epoch 后回答乱码；同数据 MBS=1 首 loss 约 2、回答正常。2.1.0 分支在 MBS>4 复现同类现象。
- **改进措施**：检测 开 packing 后用同一份数据跑 MBS=1 与 MBS>1 的短程对照，比首 step loss 与样本级 attention reset 结果。；修复 待定（issue 已 closed，正文未给出修复 PR；报告仅给出 MBS=1 规避）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/983

### TRN-0333 `mindspeed_llm_resume_not_restore_data_order` 断点续训不恢复数据顺序致精度偏移

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：数据管线 / mindspeed-llm / 断点续训的数据加载进度
- **原因行为**：断点续训只恢复模型参数与优化器状态，不恢复数据加载顺序与消费进度；恢复后从数据集头部重新加载，已训过的部分被跳过或重复。
- **影响对象**：训练样本流；训练轨迹（质量退化）
- **影响详情**：中断恢复后数据分布偏移，最终模型精度下降约 0.2%；长训练任务中断概率高，多次恢复偏差累积、损失逐步变大，日志无异常。
- **改进措施**：检测 恢复后核对 consumed samples 与 dataloader 实际起点，与未中断基线比同 step loss 和数据顺序。；修复 待定（issue 以 fix 形式提出需求，正文未给出落地 PR 与合入版本，未核实）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1734
- **关联**：var:TRN-0067

### TRN-0335 `mindspeed_llm_alpaca_ranking_rejected_index_asymmetry` alpaca 偏好数据 rejected 取 [1] 致偏好对错位

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：数据管线 / mindspeed-llm / alpaca ranking 分支
- **原因行为**：ranking=True 且 chosen 列为 list 时，convert_alpaca_to_intermediate 构造 response 时 chosen 取第 0 个元素，rejected 却取第 1 个元素，候选索引不对称。
- **影响对象**：训练样本流；训练信号（静默错误）
- **影响详情**：rejected 为单元素 list（偏好数据最常见形态）时必现 IndexError 中断数据处理；多元素时 chosen[0] 与 rejected[1] 配对错位，DPO/SimPO 训练的是错误偏好对，无报错。
- **改进措施**：检测 处理 ranking 数据后抽查若干样本的 chosen/rejected 内容是否成对；对 rejected 单元素 list 做一次试处理。；修复 issue 给出改法：把 rejected 的 [1] 改为 [0]，并像 sharegpt 分支那样在取索引前对 list 类型做防御性检查；issue 已 closed，正文未给出合入 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1718

### TRN-0358 `msllm_tft_rollback_dataloader_worker_loss` TFT 回滚重建 DataLoader 时丢 worker

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：数据管线 / mindspeed-llm / TFT 回滚 DataLoader 重建
- **原因行为**：TFT 高可用回滚时无条件重建 DataLoader 与迭代器，num_workers>0 下新旧 worker 生命周期切换，worker 异常退出后父进程只在 gc.collect 处报错。
- **影响对象**：可用性/进度；训练样本流（报错）
- **影响详情**：num_workers=2 时约十余次回滚出现一次 DataLoader worker exited unexpectedly(exit code 1)，父进程在 gc.collect 里抛 RuntimeError 退出；num_workers=0 未复现，worker stderr 丢失。
- **改进措施**：检测 回滚前后记录 worker pid 与 consumed_train_samples，对 single/cyclic sampler 状态做一致性断言；修复 issue 给出方案：仅在开高可用时对标准 map-style DataLoader 启用 persistent_workers，回滚时重置 single/cyclic 采样器并复用现有 worker（closed，未核实是否已合入）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1911

### TRN-0363 `msllm_packed_prefix_double_suffix_glob` DATA_PATH 带 _packed 后 glob 双后缀取空数据集

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：数据管线 / mindspeed-llm / packed 数据集 glob 拼接
- **原因行为**：预处理固定输出 {prefix}_packed_*_document*，训练侧又给 data_prefix 追加 _packed 再 glob，用户按输出名填 DATA_PATH 就变成 _packed_packed，匹配不到文件。
- **影响对象**：可用性/进度；训练样本流（报错）
- **影响详情**：glob 结果为空字典，decoder_packed_mtf_dataset.py:82 对 values()[0] 取长度抛 IndexError: list index out of range，报错完全不提路径或 _packed 后缀。
- **改进措施**：检测 启动时断言 packed_indexed_dataset 非空并打印实际 glob 模式；预处理后核对输出文件名与 DATA_PATH 是否一致；修复 issue 建议：文档写明 DATA_PATH 取 --output-prefix 原值、空数据集抛带 glob 模式的 ValueError、检测到 _packed 结尾自动去后缀并告警（open，未核实修复）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1792

### TRN-0399 `verl_agent_loop_prompt_cap_ignores_truncation_policy` verl agent loop 忽略 truncation 策略截头

`故障` · `active` · `rl；sft` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：数据管线 / verl / AgentLoop prompt cap
- **原因行为**：agent_loop 共享 prompt cap 对超长文本 prompt 无条件左截断，data.truncation 配置完全不生效；#4759 移除策略执行后未迁入 agent loop，无条件 cap 由 caf9fee 引入。
- **影响对象**：输入编码；训练样本流（静默错误）
- **影响详情**：配置 error 的用户预期报错拒绝，实际静默左截断：system prompt/头部指令被丢弃、训练在残缺 prompt 上进行；CPU 可复现（4 种策略输出全相同 [6,7,8,9]），agent-loop 文本 prompt 路径（SingleTurn/ToolAgentLoop）。
- **改进措施**：检测 对 max_prompt_length 边界样本断言截断方向与配置一致；训练前 dump 首个 batch prompt 首部核对 system prompt。；修复 待定（issue open 2026-10-19，verl 0.10.0.dev 4b26c78；关联 #4600 针对旧 tokenization 路径，未覆盖 agent loop）
- **来源**：https://github.com/verl-project/verl/issues/8281

### TRN-0463 `trl_orpo_cpo_prompt_fills_maxlen_nan` ORPO/CPO 满长 prompt 除零写 NaN 入参数

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：数据管线 / trl / ORPO/CPO 平均 logprob
- **原因行为**：prompt 独自达到 max_length 时 completion 截成 0 token；平均 logprob 0/0 得 NaN（ORPO/CPO simpo/ipo），NaN 梯度写进参数；sigmoid 变体静默记 0。
- **影响对象**：梯度；模型权重；训练信号（数值异常）
- **影响详情**：数据集中存在 prompt≥max_length 的行时，ORPO/CPO(simpo/ipo) 单步把 NaN 写入全部参数；CPO sigmoid 变体静默按 logprob 0 打分空 completion。#6588 只交付截断+警告，未交付丢弃满 prompt 行。
- **改进措施**：检测 训练前统计 tokenized prompt≥max_length 行数；逐步参数 NaN 检查；修复 待定（#6548 计划的丢弃满 prompt 行未随 #6588 交付，issue open）
- **来源**：https://github.com/huggingface/trl/issues/7912

### TRN-0477 `mindformers_static_batch_resume_epoch_repeat` MindFormers 静态 batch 恢复后跨 epoch 重复数据

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：数据管线 / mindformers / Trainer 恢复偏移清除
- **原因行为**：PyNative Trainer 从 checkpoint 恢复时设置的初始跳过步数在静态 batch 路径 epoch 耗尽重建迭代器前不清除（只在 dynamic_batch 时 set_init_step(0)）
- **影响对象**：训练样本流（静默错误）
- **影响详情**：恢复训练后第 2 个 epoch 再次从 checkpoint 位置读起：10 条 batch2 偏移 3 复现实际 [6,7][8,9][6,7][8,9]（期望含 [0,1]）；8040 样本实测 epoch 边界重复恢复后首微批。
- **改进措施**：检测 恢复训练后检查第二个 epoch 首 batch 是否等于恢复后首 batch；样本 id 日志对比；修复 修复 PR https://atomgit.com/mindspore/mindformers/merge_requests/8886（open，2026-10-27）——首个 epoch 结束时清除一次性偏移；独立候选 7c1cf12a 回归 2 passed、集成后 11 passed
- **来源**：https://atomgit.com/mindspore/mindformers/issues/2618；https://atomgit.com/mindspore/mindformers/merge_requests/8886

### TRN-0495 `mindspeed_mtp_packed_first_segment_no_shift` MindSpeed MTP packed 边界语义错配致首段标签未左移

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：数据管线 / mindspeed / PackedSeqParams 边界构造
- **原因行为**：MindSpeed 的 actual_seq_len 是不含起始 0 的结束位置列表，未转换直接写入 PackedSeqParams.cu_seqlens_q；Megatron MTP packed Roll 按相邻边界处理区间，首段漏。
- **影响对象**：训练信号；训练样本流（静默错误）
- **影响详情**：开启 MTP + reset-attention-mask + packing 时第一个子序列的 MTP 输入/标签/loss mask 不移位：每个位置预测目标仍是自身 token，段尾未清零，有效 token 数与 loss 归一化错；训练无报错继续跑。
- **改进措施**：检测 在 process_mtp_loss 打印首段移位结果对照（issue 附最小打印验证）；对比首段与后续段的标签移位一致性；修复 修复 PR https://gitcode.com/Ascend/MindSpeed/merge_requests/4115（open，2026-10-28）——创建 PackedSeqParams 时标记 MindSpeed 结束位置格式并在 CP=1 packed Roll 内局部补起始 0，附参数化回归 UT（修复前失败、修复后通过）；FB overlap 变体修复 !4123（open）——分段移位并清零段尾；issue #369 同时披露 012/016 版本边界语义不匹配与 FB overlap 适配缺失
- **来源**：https://gitcode.com/Ascend/MindSpeed/issues/369；https://gitcode.com/Ascend/MindSpeed/merge_requests/4115

### TRN-0548 `msswift_disabled_augment_still_consumes_rng` ms-swift 关闭增强仍消耗共享 RNG

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：数据管线 / ms-swift / load_dataset 种子消耗时序
- **原因行为**：load_dataset 在 init_decision_augment 前先求值 get_seed：增强关闭（config=None 立即返回）时也推进共享 NumPy RandomState，下游切分/shuffle 被改变
- **影响对象**：训练样本流（静默错误）
- **影响详情**：关闭数据增强时 train/valid 切分顺序与后续 shuffle 行为被静默改变（相对不调用 load_dataset 种子路径的期望），可复现性破坏；修复把种子抽取移入 enabled 分支
- **改进措施**：检测 对同一数据集配置两次加载断言切分行序一致；固定全部 RNG 种子做回归；修复 修复 PR https://github.com/modelscope/ms-swift/pull/10468（open，仅 decision_augment_config 非 None 时初始化并抽种子，未合入）
- **来源**：https://github.com/modelscope/ms-swift/pull/10468

## 优化器

### TRN-0013 `loss_scaler_swallows_overflow` 动态 loss scaler 把 SDC 引起的 inf 当普通溢出跳过

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 NUM.04

- **原因对象**：优化器 / 通用 / 动态 loss scaler 溢出跳过
- **原因行为**：动态 loss scaling 把出现 inf 的 step 丢弃并缩小 scale；偶发 SDC/内核尖峰表现为 inf 时被合法跳过，与普通溢出无法区分，且只拦 NaN/Inf，拦不住有限值坏梯度。
- **影响对象**：指标/日志；模型权重（静默错误）
- **影响详情**：日志里只有 overflow/skipped，看起来像一次普通 skip，没有坏节点信号；该更新的权重没有更新，坏的有限值仍被吃进 Adam。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2605.04213

### TRN-0019 `bf16_static_scaler_silent_skip_all_steps` DeepSpeed bf16 下非有限梯度每步静默跳步，权重从不更新

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-09-05 · 旧号 NUM.10

- **原因对象**：优化器 / deepspeed / ZeRO step 溢出跳步与静态 scaler
- **原因行为**：ZeRO-1/2 step() 检出非有限梯度时 zero_grad 并提前返回，无日志；bf16 拿到不打日志的静态 LossScaler，skipped_steps 仅在设了 steps_per_print 时上报，默认永不触发。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：bf16 + check_grad_overflow=True 的 RL run 每个 step 被静默跳过：step 正常返回、lr scheduler 照走、loss/reward 曲线合理，唯一症状是下游同步的权重逐字节相同；设为 False 时 Inf 梯度把 NaN 写进参数。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8415；https://github.com/deepspeedai/DeepSpeed/issues/8461
- **关联**：var:TRN-0013

### TRN-0025 `invalid_group_norm_sentinel_squared_to_healthy` DeepSpeed 无效组范数哨兵 −1 被平方成 1.0，溢出被当健康放行

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-09-28 · 旧号 NUM.16

- **原因对象**：优化器 / deepspeed / 组范数 −1 哨兵与平方组合
- **原因行为**：DeepSpeed 把 inf/NaN 组范数编码为 −1 哨兵，但 combine_grad_norm_groups 等组合路径把哨兵与 vector_norm 一起平方，(−1)²=1.0，溢出组与范数 1.0 的健康组不可区分。
- **影响对象**：模型权重；优化器状态（静默错误）
- **影响详情**：无 crash；含 inf/NaN 梯度的组本应跳步并降 scale，却拿到有限范数：clip 放行 unclipped step、overflow 检查不触发、loss scaler 照常推进，坏梯度进入权重。涉及 ZeRO-3、SuperOffload、ZenFlow、FP16/BF16。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8638
- **关联**：var:TRN-0013

### TRN-0026 `onecycle_rebuilds_betas_hardcodes_beta2` DeepSpeed OneCycle 把 beta2 硬编码为 0.99

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-10 · 旧号 NUM.17

- **原因对象**：优化器 / deepspeed / OneCycle 动量初始化（betas）
- **原因行为**：OneCycle 在 cycle_momentum=True（默认）时于构造和每次 step() 把各 param group 的 betas 整对重建为 (mom, 0.99)，配置的及 per-group 的 beta2 被无条件替换。
- **影响对象**：优化器状态；训练轨迹（静默错误）
- **影响详情**：无 crash、无 warning、无日志：默认配置用 1Cycle 的 run 从构造起即以不同的二阶矩系数训练，momentum 窗口与方差衰减速率偏移，训练曲线无异常；repro 中 betas (0.9,0.999) 初始化后变 (0.8,0.99)。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8750；https://github.com/deepspeedai/DeepSpeed/pull/8751
- **关联**：var:TRN-0112

### TRN-0028 `invalid_grad_norm_check_ungated_overrides_opt_out` DeepSpeed 无效范数跳步判定绕过 check_grad_overflow

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-10-12 · 旧号 NUM.19

- **原因对象**：优化器 / deepspeed / ZeRO-1/2 step 无效范数溢出判定
- **原因行为**：PR #8638 在 ZeRO-1/2 step() 引入的无效范数→overflow=True 判定落在 check_grad_overflow 门控之外；开 gradient_clipping 时范数被强制计算，关闭开关后仍会跳步。
- **影响对象**：训练轨迹；模型权重（静默错误）
- **影响详情**：无 crash、无警告：bf16 用户显式设 check_grad_overflow: False 且开 clipping 时，仍回到静默跳步，两种配置训练动力学不可区分（skipped_steps 相同）；单 rank CI 跳过 world_size=2 用例而恒绿，≥2 rank 可复现。
- **改进措施**：检测 待定；修复 修复 PR #8818（open 未 merge）：invalid-norm overflow 判定改为受 bf16.check_grad_overflow 门控；双 H200 ZeRO-1/2 八配置修复前 4 组失败、修复后全过。https://github.com/deepspeedai/DeepSpeed/pull/8818
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8805；https://github.com/deepspeedai/DeepSpeed/pull/8818

### TRN-0060 `resume_resets_first_microbatch_flag` resume 重置 TE 首微批 flag，MTP 丢一个 depth 梯度

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-30 · 旧号 CKPT.11

- **原因对象**：优化器 / megatron-lm / TEGroupedLinear 首微批 flag
- **原因行为**：is_first_microbatch 是进程局部 flag、不入 ckpt，resume 后重置为 True；MTP 跨 depth 复用同层时首次调用由 accumulate 变 overwrite，丢一个 depth 的梯度。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：resume 后一步 grad-norm 分叉而 loss 暂时跟得上，resume 训练与不中断训练从此分叉；两个 fresh 进程错得一致，A/A 复查抓不住，需三进程对照。触发：MTP 层跨 depth 复用 + 梯度累积融合，关 grad-accum fusion 分叉即消失。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6965；https://github.com/NVIDIA/Megatron-LM/pull/7186

### TRN-0071 `cached_optimizer_state_stale_scalar_lr` TorchFT 缓存的优化器状态 LR 陈旧，加入副本以错误 LR 恢复

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 CKPT.22

- **原因对象**：优化器 / torchtitan / TorchFT 优化器状态缓存、LR 恢复
- **原因行为**：optimizer state dict 被缓存，标量 LR 是值拷贝，scheduler 更新后缓存 LR 陈旧；恢复 scheduler state 时不回写 optimizer param groups 的 LR。
- **影响对象**：优化器状态；模型权重（静默错误）
- **影响详情**：TorchFT 拓扑变化或 replica 加入后，scheduler get_lr() 报告正确而各副本实际以不同 LR 更新，梯度 all-reduce 一致但权重静默分叉；无 crash、无 NaN，只有与不中断 run 的零偏差对齐能发现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/4598

### TRN-0102 `grad_clip_absorbs_sdc_spike` 全局 grad clip 吸收 SDC 梯度尖峰，范数正常但方向已污染

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 OPT.02

- **原因对象**：优化器 / 硬件 / 计算硅 SDC 致单步梯度尖峰
- **原因行为**：SDC 造成单步梯度扰动；全局 grad clip 把这次异常大梯度压回阈值，范数日志看似正常，但更新方向已被尖峰污染。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：无 NaN、无 scaler skip，grad norm 日志正常；权重被沿错误方向推了一小步。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：Ma et al. 2502.12340（SDC 可表现为单步梯度扰动）；

### TRN-0103 `lr_zero_phase_hides_bad_gradients` warmup LR=0 阶段掩盖错梯度，前 N step 一致被误读为实现正确

`结论` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 OPT.03

- **原因对象**：优化器 / 通用 / N/A
- **原因行为**：warmup 阶段 LR 被钉在 0，错误梯度不进入权重更新，梯度实现缺陷在此期间被掩盖。
- **影响对象**：梯度；测试判定（静默错误）
- **影响详情**：LR=0 阶段训练曲线与健康 run 重合，排障时「前 N step 完全一致」被误读为实现没问题；LR 一离开 0 故障才显形（DeepSpeed #8224 以此作对照）。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8224

### TRN-0104 `global_clip_rescales_corrupted_grad_norm` 全局 clip_grad_norm 把损坏梯度重缩放回阈值，抹掉幅值证据

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-08-20 · 旧号 OPT.04

- **原因对象**：优化器 / megatron-lm / 全局 clip_grad_norm
- **原因行为**：clip_grad_norm 只看整体 L2 范数，把被抬高范数的损坏梯度（如 PAR.05 的 2^N 倍 expert 梯度）按 clip_coef 重缩放回阈值，不校验方向与逐参数幅值，不触发 skipped iteration。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：clip 开启时 grad_norm 图正常、skipped iterations=0（实测 ×2^16 expert 梯度被重缩放）；N≤~64 时幅值假的更新持续写入权重，N=128 时范数溢出为 inf、clip_coef≈0，run 零梯度空转。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/6660
- **关联**：var:TRN-0102

### TRN-0105 `module_replacement_orphans_optimizer_params` DeepSpeed AutoEP 替换 MoE 模块后专家参数脱离优化器被冻结

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-08-30 · 旧号 OPT.05

- **原因对象**：优化器 / deepspeed / AutoEP 替换后 param group 绑定
- **原因行为**：_configure_expert_parallel 先于优化器配置替换 MoE 模块且不重映射 param group；调用方自建优化器仍持旧 expert/router 张量，新 GroupedExperts 权重不在任何组。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：HF Trainer/Accelerate 在 ds_config 无 optimizer 块时的默认路径 + zero3_init_flag:true 下完全静默：attention/norm 正常训练、loss 正常下降，全部专家与 router 不更新，ckpt 中专家权重等于预训练原值。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8354；https://github.com/deepspeedai/DeepSpeed/pull/8377

### TRN-0106 `unscaled_grad_divided_by_loss_scale` DeepSpeed fp16 ZeRO-0 梯度未放大却被除 scale

`故障` · `active` · `sft` · `verified` · `var` · 发现 2026-09-04 · 旧号 OPT.06

- **原因对象**：优化器 / deepspeed / ZeRO-0 fp16 loss scale 路径
- **原因行为**：fp16 + ZeRO stage 0 下 engine.backward() 直接调用 loss.backward()，未先乘 loss scale；FP16_Optimizer.step() 却无条件把梯度除以 cur_scale。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：仅 fp16 非 ZeRO 组合触发：有效参数更新比预期小约 cur_scale（典型 32768）倍，无 NaN、无 crash，loss 微降后停滞在高位（CIFAR-10 MoE 基准 acc 22–28%，修复后 49%），易被误判为超参问题。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8393
- **关联**：var:TRN-0013

### TRN-0107 `zerograd_set_to_none_unbinds_graph_bound_grads` CUDA graph 下 zero_grad 解绑 MFSDP 梯度，权重冻结

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 OPT.07

- **原因对象**：优化器 / megatron-lm / zero_grad 的 set_to_none
- **原因行为**：MFSDP v2 只在 Python 侧把 .grad 绑到 main_grad，CUDA graph replay 不重放该绑定；zero_grad() 默认 set_to_none=True 解绑后 .grad 恒为 None。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：MFSDP v2 + CUDA graph 时优化器跳过每个参数，权重冻结且 grad norm 恒为 0.0；无 crash、无 NaN、无报错，grad norm 0.0 易被当作正常的小梯度。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7075

### TRN-0108 `fused_gated_fc1_single_matrix_orthogonalization` Muon 把融合 gate/up fc1 当单一矩阵正交化

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 OPT.08

- **原因对象**：优化器 / megatron-lm / Muon NS 对融合 linear_fc1 处理
- **原因行为**：Muon/NorMuon 做 Newton-Schulz 正交化时把 gated MLP 融合的 linear_fc1（[gate; up] 物理拼接）当单一矩阵处理，两个独立投影被联合正交化，耦合本应独立的更新。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：SwiGLU/GEGLU 模型用 Muon 训练时无 crash、无 NaN，照常收敛但每步更新几何被污染；同类的 DeepSpeed AutoTP 对 shard 做 NS 使 update 随 TP 度变化（Llama tp=2 相对差 3.9e-01）。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6688；https://github.com/NVIDIA/Megatron-LM/pull/7085；https://github.com/deepspeedai/DeepSpeed/issues/8437；https://github.com/pytorch/torchtitan/issues/4692

### TRN-0109 `clip_dispatch_ignores_fsdp_owner_grad_location` Megatron MFSDP v2 下 clip 读错梯度张量而失效

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-09-06 · 旧号 OPT.09

- **原因对象**：优化器 / megatron-lm / clip_grad_norm 梯度位置判据
- **原因行为**：clip_grad_norm 按优化器是否 precision-aware 判梯度在 decoupled_grad，而 MFSDP v2 恒 reduce 进 .grad；判据不看参数归属哪版 FSDP，clip 读错张量。
- **影响对象**：梯度（静默错误）
- **影响详情**：use_precision_aware_optimizer=True + MFSDP v2 时 clip_grad 完全失效：梯度保持未裁剪范数（实测 213.6 vs clip=1.0），loss 曲线与 clip_grad=0.0 bit 级相同；训练继续，异常梯度不再被截住。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7074
- **关联**：var:TRN-0104

### TRN-0110 `muon_update_applied_per_microbatch` ZeRO-3 下 Muon 每个 micro-batch 都执行更新

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-07 · 旧号 OPT.10

- **原因对象**：优化器 / deepspeed / ZeRO-3 IPG 路径 Muon 更新
- **原因行为**：ZeRO-3 把 Muon 的 Newton-Schulz 与 momentum 更新挂在每个 micro-batch 都执行的 IPG bucket reduce 路径上，缺少梯度累积边界守卫，NS 作用于部分梯度。
- **影响对象**：模型权重；优化器状态（静默错误）
- **影响详情**：梯度累积 gas=n 时 momentum 每步推进 n 次（β=0.95、gas=4 有效保留率 0.81），NS 计算量 ×n；stage3 gas=1 vs 4 权重相对差 1.0e-01（stage2 仅 3.3e-04）；无 crash、无 NaN、loss 正常。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8443

### TRN-0111 `muon_zero_stage0_skips_newton_schulz` DeepSpeed ZeRO-0 Muon 不做 NS，实际退化为 SGD

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-08 · 旧号 OPT.11

- **原因对象**：优化器 / deepspeed / Muon 非 flat 参数路径
- **原因行为**：DeepSpeed Muon 只在 flat/ZeRO 分片参数路径上执行 Newton-Schulz；ZeRO stage 0 下参数以 2-D 原样交给优化器、不进该路径，NS 从不执行，且无报错或回退日志。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：默认 ZeRO-0 配置 Muon() 时，自 step 1 起实际训练的是带动量的 SGD 加缩放；loss 照降、无 crash，以为是 Muon vs Adam 的对照实为 SGD vs Adam。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8441

### TRN-0112 `scheduler_override_rewrites_group_lr_bounds` Megatron 覆盖 scheduler 时把全局 LR 界写进每个参数组

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-10 · 旧号 OPT.12

- **原因对象**：优化器 / megatron-lm / ckpt 加载后参数组 LR 界赋值
- **原因行为**：--override-opt-param-scheduler 加载 ckpt 后的赋值段把全局 args.max_lr/min_lr 直接写进每个参数组的 LR 界，覆盖显式配置的 per-group max_lr/min_lr。
- **影响对象**：优化器状态；训练轨迹（静默错误）
- **影响详情**：带参数组 LR 分界的训练（MoE 冻结层、LoRA 高 LR 组等）resume 即静默换界，如 max_lr=5.0 的组按 1.0 训，warmup/decay 边界错位、分组语义被抹平；无 crash、无警告、无日志。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7173

### TRN-0113 `clip_averages_norms_across_disjoint_expert_owners` DeepSpeed FP32 梯度裁剪在 EP 下平均互不相交的专家范数

`故障` · `active` · `pretrain` · `verified` · `var` · 发现 2026-09-12 · 旧号 OPT.13

- **原因对象**：优化器 / deepspeed / clip_fp32_gradients 范数归约
- **原因行为**：FP32 梯度裁剪路径结尾把各 rank 局部范数在 DP 组上 all-reduce 取平均，假设各 rank 持有相同参数；AutoEP 下各 rank 拥有不同专家，局部范数对应互不相交的参数集。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：MoE + AutoEP 且裁剪生效时，clip_coef 取决于专家落在哪些 rank 而非梯度本身：sqrt(20) 与 sqrt(100) 平均得 7.24 而非 sqrt(120)=10.95，换布局 clip 系数差达 0.20；跨 EP 拓扑实验不可比，无 crash。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8475；https://github.com/deepspeedai/DeepSpeed/pull/8476；https://github.com/deepspeedai/DeepSpeed/pull/8478
- **关联**：var:TRN-0109

### TRN-0114 `fused_adam_shared_step_counter_bias_correction` FusedAdam 共享 step 计数器致偏差校正错值

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 OPT.14

- **原因对象**：优化器 / deepspeed / FusedAdam step 计数器
- **原因行为**：FusedAdam 每 dtype 只维护一个 step 计数器，只递增最后一个活跃参数的计数器并用于该 dtype 全部张量；参数间歇无梯度时计数漂移，多 dtype 组还重复递增，bias correction 按错误 t 计算。
- **影响对象**：优化器状态；模型权重（静默错误）
- **影响详情**：LoRA 冻结/解冻、条件分支、MoE 冷专家等间歇梯度场景下 moment 估计产生平滑偏差，有效 LR 随参数训练历史分叉；无 crash、无 NaN，config/log 正常，纯 fp32 下也发生。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8471

### TRN-0115 `muon_scale_counts_alignment_padding_rows` Megatron Muon 谱缩放把 GTP 对齐填充行计入形状

`故障` · `active` · `pretrain` · `verified` · `var` · 发现 2026-09-12 · 旧号 OPT.15

- **原因对象**：优化器 / megatron-lm / Muon 谱缩放因子形状
- **原因行为**：GTP 行数不能等分时先补零行再切，Muon 谱缩放因子却按填充后的本地形状计算，把 padding 行计入逻辑行数，而非用 local_rows×gtp_size−pad_length。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：GTP 行数不对齐的矩阵 Muon 更新带 layout 相关缩放偏差（TP4×GTP2 [32,8]→逻辑 [20,8] 时 5.657 vs 4.472，约 27%）；无 crash、无 NaN，不同 GTP 度下有效更新幅度不同，跨并行度实验不可比。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7236
- **关联**：var:TRN-0110

### TRN-0116 `mixed_dtype_grad_list_single_multi_tensor_launch` 混 dtype 梯度共用一次 multi_tensor 调用致范数错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-16 · 旧号 OPT.16

- **原因对象**：优化器 / megatron-lm / clip_grads 梯度范数与裁剪
- **原因行为**：把 bf16 decoupled_grad 与 keep-in-fp32 参数的 fp32 梯度放进同一 TE multi_tensor launch 求范数/裁剪，kernel 按首张量 dtype 派发读全部张量。
- **影响对象**：梯度；指标/日志（静默错误）
- **影响详情**：precision-aware optimizer + bf16 梯度 buffer 下：bf16 梯度排前时 fp32 梯度被按 2 字节读，grad norm 与 clip 系数静默错值；fp32 排前时首次求范数即 illegal memory access crash，易误诊为通信故障。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7338；https://github.com/NVIDIA/Megatron-LM/pull/7279

### TRN-0119 `muon_update_rescaled_by_loss_scale` DeepSpeed fp16 Muon 更新被误按 loss scale 缩小

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-09-28 · 旧号 OPT.19

- **原因对象**：优化器 / deepspeed / unscale_and_clip_grads 路径
- **原因行为**：Newton-Schulz 输出的更新量与 loss scale 无关，但无 offload 的 fp16 step 路径把它当已放大梯度：unscale 时除以 loss scale、global norm 也按放大值计。
- **影响对象**：模型权重；训练轨迹（质量退化）
- **影响详情**：无 crash、无 NaN，fp16 Muon 参数几乎不动，loss 下降显著慢于 bf16 对照、接近停滞，表象与 lr 太小无法区分；fp16+Muon+ZeRO-1/2/3 且不带 CPU offload 时触发，PR 实测一步更新范数缩水约 1023 倍。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8655
- **关联**：var:TRN-0111

### TRN-0120 `stage0_fp16_hysteresis_config_dropped` ZeRO stage 0 fp16 丢弃 hysteresis 配置

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-09-28 · 旧号 OPT.20

- **原因对象**：优化器 / deepspeed / stage0 fp16 loss scaler
- **原因行为**：stage 0 fp16 的 loss scale 配置丢掉 delayed_shift 与 consecutive_hysteresis，_update_scale 也无 hysteresis 逻辑，每次溢出 scale 直接减半。
- **影响对象**：优化器状态；训练轨迹（静默错误）
- **影响详情**：无 crash，stage 0 fp16 的 loss scale 衰减比配置快 hysteresis 倍，频繁溢出时 scale 提前触底、被跳过的 step 增多，有效训练步数静默缩水；同配置在 ZeRO 1/2/3 正常，跨 stage 对照的 scaler 动力学不可比。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8647
- **关联**：var:TRN-0013

### TRN-0139 `overflow_grad_poisons_muon_momentum` DeepSpeed Muon 溢出梯度永久毒化 momentum

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-09-07 · 旧号 KER.08

- **原因对象**：优化器 / deepspeed / ZeRO-1/2 的 Muon 更新时序
- **原因行为**：ZeRO-1/2 的 Muon 路径在溢出检查之前对累积梯度执行 muon_update，momentum.lerp_ 把 inf/NaN 折进 momentum 且此后无人重置，nesterov 分支再把 NaN 原地写回梯度。
- **影响对象**：优化器状态；模型权重；测试判定（报错）
- **影响详情**：fp16+Muon+ZeRO-1/2 下首次溢出后每个 step 必然再溢出，loss scale 降到最小值后 Exception 退出，全程零参数更新；官方单测在 fp16 cast 前克隆参数，断言恒通过，run 太短的验证都报告成功。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8432
- **关联**：var:TRN-0013

### TRN-0169 `weight_norm_criticality_spike` 归一化 × weight decay 的权重范数临界性引发 loss spike

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-19 · 旧号 LOSS.05

- **原因对象**：优化器 / 通用 / weight decay × 尺度不变权重
- **原因行为**：归一化使权重尺度不变，weight decay 持续收缩其参数范数，接近临界边界时 loss landscape sharpness 快速抬升；这是与学习率临界性（EoS）正交的第二条临界轴。
- **影响对象**：训练轨迹（质量退化）
- **影响详情**：临界前曲线完全正常，随后突发 loss spike，可恢复但反复出现；weight decay 系数再大一点就跨界，可用尺度不变权重的范数轨迹检验。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2607.21005

### TRN-0262 `fp32_zero0_global_grad_norm_none` DeepSpeed fp32 ZeRO-0 丢梯度范数，grad_norm 缺失

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-26 · 旧号 OBS.13

- **原因对象**：优化器 / deepspeed / engine 梯度裁剪后的范数记录
- **原因行为**：fp32+ZeRO-0 裁剪时 clip_fp32_gradients() 返回的范数被丢弃；engine 只读 optimizer._global_grad_norm，基础优化器不设它，故 grad norm 恒为 None。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：max_grad_norm>0 时 HF Trainer 经 Accelerate 读到 None，grad_norm 从日志静默消失；gradient_clipping 默认改为 1.0 后普通配置即触发，autocast+stage 0 同样命中。裁剪与更新不受影响，事后诊断缺范数序列。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8660；https://github.com/deepspeedai/DeepSpeed/issues/7255

### TRN-0263 `autocast_z0_overflow_skip_miscounted_as_applied` DeepSpeed autocast fp16 ZeRO-0 溢出跳步记为已应用

`故障` · `active` · `shared` · `verified` · `var` · 发现 2026-10-09 · 旧号 OBS.14

- **原因对象**：优化器 / deepspeed / _take_model_step 溢出探测
- **原因行为**：_take_model_step 只查 optimizer.overflow 属性探测溢出，该路径为裸 torch.optim、无此属性，overflow 恒 False；GradScaler 已跳过 step，engine 仍记已应用。
- **影响对象**：优化器状态；训练轨迹；指标/日志（静默错误）
- **影响详情**：溢出步 was_step_applied() 为 True、skipped_steps 恒 0、lr_scheduler 照常推进而参数未变；GradScaler 默认 init_scale 65536 使前几步常溢出，warmup 被静默烧掉、schedule 相位前移。fp16 配置块路径正常。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8723
- **关联**：var:TRN-0262

### TRN-0311 `ascend_fused_adamax_w_fp16_amp_storage_size_mismatch` NpuFusedAdamW BN 梯度 storage 与描述符长度失配

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-18

- **原因对象**：优化器 / pytorch / NpuFusedAdamW unscale_ 拼接
- **原因行为**：FP16 AMP 下 BN 小通道梯度 storage 容量(16)与 NPU 描述符长度(8)分叉；NpuFusedAdamW 按 storage().size() 累计 266、NPU 口径 250，首次 unscale_ 越界报错。
- **影响对象**：可用性/进度；优化器状态（报错）
- **影响详情**：首个反向后首次 GradScaler.unscale_ 抛 RuntimeError(266>250)，训练无法进入首个 optimizer step；910B2 单卡小模型可复现；报错指向 combined_tensor 越界而非 BN 梯度本身。
- **改进措施**：检测 对每个梯度张量比对 storage().size() 与 torch_npu.get_storage_size()，不一致即预警。；修复 待定（issue 2026-10-17 报于 Ascend/pytorch #5501，open；issue 提到 --bn-format3 强制 BN 参数 format 3 时两种长度一致、不触发，可作规避参考，作者未声称已验证为通用规避）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5501

### TRN-0317 `deepspeed_bf16_safe_set_full_grad_wrong_buffer` BF16 safe_set_full_grad 写错缓冲致梯度掩蔽失效

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-19

- **原因对象**：优化器 / deepspeed / safe_set_full_grad 分支
- **原因行为**：safe_set_full_grad() 对 BF16 写 staging param.grad，而 BF16_Optimizer 从独立累加缓冲 step；backward 与 step 之间的梯度掩蔽/替换被静默忽略。
- **影响对象**：梯度；优化器状态（静默错误）
- **影响详情**：BF16 训练下，backward 后、optimizer.step 前经 safe_set_full_grad 掩蔽/置零/替换梯度会被静默丢弃，更新用未修改梯度；梯度手术/掩蔽/替换类方法（如梯度裁剪定制、对抗训练、调试注入）失效。开启 immediate 累积且参数跨优化器分区时抛形状错误。
- **改进措施**：检测 回归含两真实 DP rank、双累加模式、BF16 ZeRO-1 与 ZeRO-2 兄弟路径、矩阵/偏置参数、双累加微批、零/非零替换梯度，检查公开 getter 与 SGD 参数更新；CPU repro 脚本随 PR 附带（无需编译 DeepSpeed ops）；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8856 （open 2026-10-18 未合入）：setter 改写既有的完整累加缓冲，匹配 getter 的 BF16 检测；普通梯度与 ZeRO 分片梯度分支不变
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8856

### TRN-0323 `megatron_chained_optim_loss_scale_divergence` Megatron 链式优化器 loss scale 分叉静默错误反缩放

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：优化器 / megatron-lm / 链式 FP16 loss scaler 更新
- **原因行为**：FP16 链式优化器 backward 用第一个优化器的 scale，但各优化器用各自 overflow 结果独立更新 scaler；只一侧溢出时 scale 分叉，后续 update 按错 scale 反缩放部分模型。
- **影响对象**：梯度；优化器状态（静默错误）
- **影响详情**：FP16 MoE 链式优化器训练中，一侧溢出后 dense/expert 的 loss scale 静默分叉，后续步部分参数按错误 scale 反缩放（实测 64 步后 32768 vs 1048576，expert 梯度被多除 32 倍）；无报错。
- **改进措施**：检测 监控各 scaler 的 scale 值是否始终相等；对 unscale 后梯度与 backward scale 对账。；修复 修复 PR https://github.com/NVIDIA/Megatron-LM/pull/8249 （open，未合入未发布）：推迟 scaler 更新至全部优化器完成梯度检查后按合并 overflow 结果统一更新；嵌套链同理；ckpt 格式不变。含 64 步 EP2 FP16 复现与 AdamW 参考对照（两卡 RTX 5090）。
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/8249

### TRN-0349 `msllm_fsdp2_epochs_lr_total_steps_default` 只填 num_train_epochs 时 LR 调度按 100000 步算

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：优化器 / mindspeed-llm / FSDP2 lr scheduler
- **原因行为**：只配置 num_train_epochs、不配 max_steps 时，cosine scheduler 用默认 100000 当 total_steps，而 dataloader 按样本量实际只排 609 步。
- **影响对象**：训练轨迹；训练信号（静默错误）
- **影响详情**：同一次启动里 scheduler 打印 total_steps=100000、训练器打印 609 步；cosine 只走 0.6%，lr 从 2.000000E-05 到 1.999993E-05，等效恒定学习率跑完 3 个 epoch。
- **改进措施**：检测 启动后比对 scheduler 打印的 total_steps 与 Total optimization steps 是否一致；修复 issue #1294（closed）未给修复 PR；规避是显式配置 max_steps
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1294

### TRN-0354 `msllm_reuse_fp32_param_fp16_convert_nan` reuse-fp32-param 的 fp32→fp16 转换溢出成 NaN

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：优化器 / mindspeed / reuse_param fp32→fp16 转换
- **原因行为**：reuse-fp32-param 的 fp32→fp16 转换在 optimizer step 里做 view(-1,2).transpose(1,0).reshape，第一环就出 NaN。
- **影响对象**：模型权重；训练信号（数值异常）
- **影响详情**：qwen3-4b 32k LoRA 在 CP=4 下精度溢出（ulysses 与 megatron CP 都溢出，CP4→TP4 不溢出）；msprobe 首个 NaN 在该 transpose 输入，关掉 reuse-fp32-param 即正常。
- **改进措施**：检测 msprobe 精度溢出 dump 定位首个 NaN 算子，或直接对比开/关 reuse-fp32-param 的 loss；修复 issue #1404（closed）只给规避：关闭 reuse-fp32-param；未给修复 PR
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1404

### TRN-0382 `msformers_muon_ns_schedule_spectral_divergence_nan` mindformers Muon 分段 NS 谱爆炸写 NaN 入参数

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：优化器 / mindformers / Muon Newton-Schulz 分段系数
- **原因行为**：8 步分段 NS 系数下，归一化输入（谱≤1）经首步过冲至 σ≈1.3~1.97，中段负二次项交替放大，谱轨迹 1→1.30→1.97→4.52→588→2.4e13→inf，inf 参与后续迭代得 inf-inf=NaN 写入参数
- **影响对象**：模型权重；优化器状态；训练轨迹（数值异常）
- **影响详情**：形状选择性：8 组形状中 6 个近方阵形状触发、扁长矩阵不触发，与生产任务「仅特定层参数爆炸」吻合；12B 生产任务 step 37342 稳定复现参数 NaN→下一步前向全 NaN，重跑同位置复现，日志仅见 NaN、无 optimizer 内部异常
- **改进措施**：检测 监控 Muon update 谱半径/有限性（NS 迭代中间量 σ）；参数 NaN 告警前置到 optimizer step 后；修复 修复 MR https://atomgit.com/mindspore/mindformers/merge_requests/8882（open，2026-10-22）：双层防护——非有限输入清洗为零 + NS 输出非有限回退归一化输入；对收敛迭代 bitwise 恒等；8×910B3 deterministic 40 步端到端 loss/grad_norm 逐步 bitwise 一致
- **来源**：https://atomgit.com/mindspore/mindformers/merge_requests/8882

### TRN-0450 `deepspeed_universal_ckpt_resume_cpu_step_fused_adamw` DeepSpeed universal ckpt 恢复 step 留 CPU

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：优化器 / deepspeed / load_hp_checkpoint_state
- **原因行为**：universal checkpoint 恢复直接写 optimizer.state['step']=CPU 张量，绕过设备迁移；且 param_group 设置随 ckpt 写回，fused 标志被强制还原。
- **影响对象**：可用性/进度；优化器状态（报错）
- **影响详情**：universal ckpt 恢复后 fused AdamW 第一步报设备不一致 RuntimeError；换非 fused 无效；torch>=2.8、config 无 optimizer 段时 transformers 默认 adamw_torch_fused，HF Trainer 开箱即撞。
- **改进措施**：检测 resume 后首步 optimizer.step() 冒烟；检查 state['step'].device。；修复 待定（issue open，未见修复 PR；规避：resume 构建非 fused 优化器也无效，需等上游修恢复循环）。
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8884

### TRN-0462 `deepspeed_lowprec_optimizer_init_step` DeepSpeed 低精度优化器构造期推进 Adam

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：优化器 / deepspeed / FP16/BF16 优化器包装初始化
- **原因行为**：FP16/BF16 包装在初始化时对零梯度执行真实 optimizer.step()：计数器被推进、weight decay 在首步 backward 前修改 master 权重，首步用错 bias correction。
- **影响对象**：模型权重；优化器状态（静默错误）
- **影响详情**：FP16/BF16 训练构造包装后未见过任何数据，master 权重已被 weight decay 改动（实测 0.5→0.4995）、Adam step=1；首步更新与独立初始化的 FP32 优化器不一致。静默。
- **改进措施**：检测 构造包装后立即比对 master 权重与 step 计数（应 0.5/0）；首步与 FP32 参考对照；修复 待定（issue 提出移除合成 step、改用不改参数的状态分配例程，open）
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8910

### TRN-0494 `opsnn_inplace_apply_adagrad_da_l1_polarity_denormal` AdagradDA l1=NaN 极性反转与软阈值 t<0 失效

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：优化器 / cann / inplace_apply_adagrad_da
- **原因行为**：l1T_/l2Tlr_ 推导与主分支按 l1<=0 判定：l1=NaN 时比较为 false 误入 l1>0 稀疏截断分支，l1T_=NaN·T 泄漏至全部元素输出全 NaN（TF 语义 if(l1>0) 应走直通）。
- **影响对象**：优化器状态；模型权重（静默错误）
- **影响详情**：l1=NaN 时输出全 NaN；global_step<0（t=l1·T<0）时输出偏离软阈值公式含 2g/NaN；denormal 输入下与 TF CPU 结果不一致且被放大；Host 校验缺失使非法 shape/dtype/负维不 fail-fast。
- **改进措施**：检测 AdagradDA 更新后权重 NaN 断言；与 TF raw_ops.ApplyAdagradDA 参考对照；修复 修复 PR https://gitcode.com/cann/ops-nn/pull/12578（open，2026-10-27）——kernel 503/503+GEIR 56/56+UT 41/41 全绿、NPU vs GPU A100 vs CPU 三方一致 534/534、CPU/GPU 参考 bitwise 一致 108/108 组
- **来源**：https://gitcode.com/cann/ops-nn/issues/7453；https://gitcode.com/cann/ops-nn/pull/12578

### TRN-0515 `deepspeed_zero_init_casts_rope_inv_freq_bf16` ZeRO-3 init 把 fp32 RoPE inv_freq 算成 bf16

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：优化器 / deepspeed / zero.Init 构造器包装
- **原因行为**：zero.Init 的 fp tensor constructor 包装把显式 dtype=torch.float 的构造结果也 cast 到 bf16，RoPE inv_freq 计算落 bf16
- **影响对象**：数值结果；隐状态；梯度（静默错误）
- **影响详情**：ZeRO-3 下 RoPE 角度=位置×频率，误差随位置增长；Qwen3.8-27B LoRA 单条 65k token 实测 grad norm 0.78 vs 单卡 7.91（差一个量级），ZeRO-0/2 与单卡 bit-identical
- **改进措施**：检测 对比 ZeRO-3 与 ZeRO-0/2/单卡的 grad norm 与 loss；检查 inv_freq buffer dtype 是否 bf16；修复 部分规避：data_types.keep_in_fp32_modules=["rotary_emb"]（#8699，0.19.8 起 opt-in，默认 "auto" 不覆盖 RoPE）；修复 PR 未出（issue open，讨论是否 "auto" 应保留显式 fp32 非 persistent buffer）
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8948

### TRN-0525 `deepspeed_zero12_boundary_drops_request_gradients` ZeRO-1/2 请求边界提前丢梯度

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：优化器 / deepspeed / stage_1_and_2 梯度生命周期
- **原因行为**：非 offload 路径每个累积边界清空 all_grad_tensors 丢弃 step 前各请求梯度；offload 路径边界兼首 backward 不刷新 host 累积器混入上一步存量
- **影响对象**：梯度；优化器状态（静默错误）
- **影响详情**：调用方对多个请求各设梯度累积边界、把 engine.step() 推迟到所有请求贡献完毕时，非 offload 路径更新静默缺少部分请求的梯度，offload 路径静默混入上一步存量梯度；权重更新方向错但 loss 无异常、无报错；标准单边界即 step 的用法不受影响
- **改进措施**：检测 多请求单 step 模式下对比单请求逐步 step 的权重轨迹；检查边界后梯度张量是否仍保留；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8949（open，未合入）：非 offload 保留累积张量到既有 step 清理点；offload 路径在每个边界首 backward 刷新 host 累积器
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8949；https://github.com/deepspeedai/DeepSpeed/pull/8749

### TRN-0526 `deepspeed_autoep_bf16_folding_rounds_fp32_before_accum` AutoEP BF16 折叠多一次舍入边界

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：优化器 / deepspeed / _update_hp_grad 折叠
- **原因行为**：BF16 折叠+FP32 累积下 _update_hp_grad 把 FP32 折叠结果先写回 BF16 再 cast 回 FP32 参与累积，插入可避免的 BF16 舍入边界
- **影响对象**：梯度；优化器状态（静默错误）
- **影响详情**：首 router 梯度、FP32 master 权重与 Adam 矩与数值参考不一致（实测两 exact BF16 输入 1 与 1.0078125 应均值为 1.00390625，绝对误差 0.00390625）
- **改进措施**：检测 对比 BF16 折叠路径与纯 FP32 参考的首步 master 权重/矩；两 exact BF16 输入均值回归（abs err 0.00390625）；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8920（open，未合入）：折叠校正作用于临时 FP32 staging 直接累积，镜像值回写 BF16 梯度维持既有契约
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8920；https://github.com/deepspeedai/DeepSpeed/issues/8913

### TRN-0528 `sparse_apply_proximal_adagrad_extreme_param_false_inf` SparseProximalAdagrad 极值虚假 inf

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：优化器 / cann / sparse_proximal_adagrad
- **原因行为**：var 更新链按未缩放次序计算 f32 中间量：accum 处于下界（~1e-6）且 lr 位于 f32 上限邻域（~3.4e38）时 lr/sqrt(accum) 远超 1，grad 乘积越过 f32 上限输出虚假 ±inf
- **影响对象**：模型权重；优化器状态（数值异常）
- **影响详情**：lr 位于 f32 上限邻域（~3.4e38）、accum 接近下界（~1e-6）时 var 通道成规模元素输出 ±inf（单用例数百元素），golden f64 真值有限；常规参数域不受影响，TTK e2e 比对可检出但训练日志无异常
- **改进措施**：检测 TTK e2e 精度比对（eager 与 graph static 均可检出）；对极值参数域跑 f64 参考对比；修复 修复 PR https://gitcode.com/cann/ops-nn/pull/13028（open）：var 更新链极值域虚假 ±inf 消除
- **来源**：https://gitcode.com/cann/ops-nn/issues/7682；https://gitcode.com/cann/ops-nn/pull/13028

### TRN-0543 `deepspeed_onecycle_first_adam_min_momentum` DeepSpeed OneCycle 首步 Adam 用最小动量

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：优化器 / deepspeed / OneCycle 动量调度初始化
- **原因行为**：OneCycle 开启动量循环时把 optimizer 初始 beta1 设为 cycle_min_mom，而调度器 get_mom() 报 cycle_max_mom：首个 Adam 更新消费的动量与反带动量计划相反
- **影响对象**：优化器状态；训练轨迹（静默错误）
- **影响详情**：首个更新的一阶矩按 min 动量累积，偏差修正可掩盖第一步，第二步起权重偏离调度参考（实测 actual 0.7388 vs reference 0.7878）；fp64 双优化器对照脚本稳定复现
- **改进措施**：检测 断言 optimizer.param_groups beta1 与 scheduler.get_mom() 首步一致；双优化器对照训练；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8953（open，Initialize OneCycle momentum at the upper bound，未合入）
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8951；https://github.com/deepspeedai/DeepSpeed/pull/8953

## 损失计算

### TRN-0015 `low_precision_absorption_slingshot` 低精度浮点吸收使正确类梯度归零，引发 Slingshot loss spike

`故障` · `active` · `pretrain；shared` · `documented` · `NEW` · 发现 2026-08-19 · 旧号 NUM.06

- **原因对象**：损失计算 / 通用 / 交叉熵梯度的低精度表示
- **原因行为**：高置信阶段正确类与其余 logit 之差超出浮点吸收阈值，正确类梯度被舍入为恰好 0 而错误类梯度仍非零，破坏类间梯度零和约束，形成分类器均值与特征均值指数增长的正反馈。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：训练进入高置信阶段后触发：完全吸收时出现周期性 Slingshot 式 loss spike；部分吸收时完全无可见 spike，但参数范数仍在持续疯长。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2605.06152

### TRN-0022 `gkd_jsd_mixed_precision_sign_flip` ms-swift GKD jsd_loss 混精输入致 loss 符号翻转

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-09-17 · 旧号 NUM.13

- **原因对象**：损失计算 / ms-swift / Megatron GKD 的 jsd_loss
- **原因行为**：jsd_loss 接受 student FP32 / teacher BF16 混精 logits，温度 scaling 前不统一提升精度，BF16 logits 进 log-softmax 时精度不足，使恒非负的 JSD 算出负值。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：无 crash、无 NaN；同输入仅把 loss 计算提到 FP32 得 +0.000509（与 FP64 参照吻合），原混精路径得 −0.000170，符号翻转、幅度错约 3×，日志只显示一个小负数 loss；gkd_logits_topk=64 稀疏化进一步放大敏感性。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10156；https://github.com/modelscope/ms-swift/pull/10102

### TRN-0044 `ddp_normalization_shrinks_aux_loss_grad_dp_factor` Megatron global aux loss 梯度被 DDP 缩小 DP 倍

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-09-19 · 旧号 PAR.16

- **原因对象**：损失计算 / megatron-lm / global-aux-loss 梯度归约
- **原因行为**：--global-aux-loss 把已全局归一化的 aux loss 梯度交给 DDP 归约，DDP 按 1/DP 平均；该梯度是各 rank 同份的标量损失梯度，应 SUM 却被 AVG。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 crash，loss 曲线无异常；DP=2 时 aux 梯度 norm 0.3794 vs 正确 0.7588。aux loss 有效系数随 DP 度缩小，负载均衡压力不足、专家分布漂向不均衡，DP 扩容即改变训练目标；Qwen3-Next Bridge recipe 走该路径。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452
- **关联**：var:aux_loss_normalization_domain

### TRN-0144 `chunked_ce_backward_inplace_overwrites_logits` ms-swift 分块 CE 反向就地覆写调用方 logits

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-15 · 旧号 KER.13

- **原因对象**：损失计算 / ms-swift / ChunkedCrossEntropyLoss
- **原因行为**：序列并行 ChunkedCrossEntropyLoss 为省显存把每个梯度 chunk 就地写进前向保存的 logits，并把该输入张量原样作为梯度返回，违反 autograd 保留 saved input 的契约。
- **影响对象**：数值结果（静默错误）
- **影响详情**：CELOSS_PARALLEL_SIZE>0 的 SP 训练中，单一 logits 消费者时静默跑通，但 backward 后调用方 logits 已被梯度覆写，后续依赖前向 logits 的计算拿到梯度值；复用前向图或带 aux loss 时 crash；单次 backward 梯度本身正确。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10129

### TRN-0145 `vocab_parallel_ce_label_smoothing_local_shard` 词表并行 CE 的 label smoothing 只算本地分片

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 KER.14

- **原因对象**：损失计算 / megatron-lm / vocab_parallel CE 平滑项
- **原因行为**：vocab_parallel_cross_entropy 的 label smoothing 尾项用 TP 本地分片宽度作 vocab_size、只在本地 shard 平均 log_probs，未归约就与完整 CE 基项相加。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：开启 label smoothing 且 TP>1 时无 crash，各 TP rank 打出不同 loss、梯度带 0.1 量级误差，单卡与 TP>1 的 run 从第一步起不可比；per-rank loss 差异常被误当数值噪声或归约顺序。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452；https://github.com/NVIDIA/Megatron-LM/pull/7466；https://github.com/NVIDIA/Megatron-LM/issues/7464

### TRN-0146 `gathered_logits_fed_to_vocab_parallel_ce` Megatron 全词表 logits 被当作 TP 分片计算 CE

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 KER.15

- **原因对象**：损失计算 / megatron-lm / language_module 的 CE 调用
- **原因行为**：输出层 gather 出 TP replicated 全词表 logits 时，带 labels 的 loss 路径仍无条件调 vocab-parallel CE，把最后一维当本地词表分片求和归一；非 fused 路径无 assert。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：无 crash、能训，但 loss 恒偏高 log(TP)，梯度中 target 项消失；TP=2、logits [0,1,2,3]、label 3 时 loss 为 1.1333，正确值 0.4402。两个触发项都是公开模型选项，「loss 略高」易被归因为超参或数据。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452

### TRN-0164 `sft_aux_loss_scaled_by_worldsize_and_gas` trl SFT 的 MoE aux loss 被卡数与累积步双重放大

`故障` · `active` · `sft` · `verified` · `var` · 发现 2026-10-10 · 旧号 MOE.15

- **原因对象**：损失计算 / trl / SFTTrainer 的 aux loss 缩放
- **原因行为**：compute_loss 把微批级 aux loss 并入 token 归一的 CE 后再乘 num_processes：aux 项未除以卡数；用 num_items_in_batch 时又不除以累积步，跨微批被求和。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：无 crash；aux 项放大 num_processes × gas 倍，router 更新实测 1 GPU 为 4.94、2 GPU 为 9.88、2 GPU+gas2 为 19.76，修复后均为 4.94；aux 系数效果随并行配置漂移。DPO/KTO 不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/7570
- **关联**：var:TRN-0044

### TRN-0172 `gkd_mean_of_means_token_reweighting` ms-swift GKD 损失取均值的均值，token 权重随长度偏移

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-09-10 · 旧号 LOSS.08

- **原因对象**：损失计算 / ms-swift / Megatron GKD loss 归约
- **原因行为**：GKD loss_func 先在每个微批内除以自身有效 token 数，scheduler 再对各微批等权平均，且 calculate_per_token_loss 默认 False，token 梯度权重随所在微批长度变化。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 crash/NaN，蒸馏 loss 正常下降；micro_batch_size=1 时 10 与 1000 token 回复的 per-token 权重差 100×，训练被短回复支配；改全局 token 归一后 loss 0.499→0.396、grad norm 42.77→25.21。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10076

### TRN-0173 `dapo_family_gas_double_scaling` ms-swift DAPO 族 loss 在梯度累积下被二次除以 G

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-13 · 旧号 LOSS.09

- **原因对象**：损失计算 / ms-swift / GRPO dapo 族 loss 归一化
- **原因行为**：dapo/cispo/fipo loss 已按整个梯度累积窗口的 completion token 数归一，Trainer.training_step 在 backward 前又除以梯度累积步数且无补偿，形成二次缩放。
- **影响对象**：梯度；训练信号（静默错误）
- **影响详情**：loss_type=dapo 且梯度累积步数 G>1 时 loss 与梯度被缩小 G 倍（G=4 时更新量为 G=1 的 1/4），有效学习率随 G 漂移、日志 loss 也被除以 G；无 crash、无 NaN。grpo/bnpo/dr_grpo 不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10117
- **关联**：var:TRN-0172

### TRN-0174 `cp_local_loss_means_averaged` Megatron CP 下默认 loss 按分片本地均值再平均致梯度方向偏

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 LOSS.10

- **原因对象**：损失计算 / megatron-lm / CP-local loss 均值归一
- **原因行为**：默认 calculate_per_token_loss=False 时，每个 CP rank 把 masked loss 和除以本 rank 有效 token 数，DDP 再跨 DP×CP 平均梯度，得到均值的均值而非全局均值。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：各 CP 分片有效 token 数不等时触发（--eod-mask-loss、任意 loss masking），梯度方向而非仅尺度改变（repro 梯度与参照明显不同），优化目标系统性偏离全局均值；无 crash、无 NaN。开启 per-token loss 时不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452；https://github.com/NVIDIA/Megatron-LM/pull/7513

### TRN-0175 `mtp_per_token_loss_local_token_ratio` Megatron MTP loss 用 rank 本地 token 比率缩放

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 LOSS.11

- **原因对象**：损失计算 / megatron-lm / MTP loss token 比率缩放
- **原因行为**：MTP 路径把每个 MTP loss 乘 original_num_tokens/num_tokens_safe，两个计数都取 rank 本地值；该非线性比率先作用于 loss，后续全局归一无法还原。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：MTP + calculate_per_token_loss=True 且各 DP/CP rank 有效 token 数不均时，MTP 梯度被本地比率加权（repro 4.67 vs 参照 4.0），MTP 损失权重随 rank 分布漂移，多卡与单卡 run 不可比；无 crash、无 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452

### TRN-0176 `dsv4_indexer_aux_loss_path_grad_none` torchtitan DSV4 indexer 辅助 loss 缺失致投影无梯度

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-26 · 旧号 LOSS.12

- **原因对象**：损失计算 / torchtitan / DSV4 indexer 辅助 loss 未接入；模型定义 / torchtitan / Indexer.select 只返回整数索引
- **原因行为**：indexer 辅助 loss 被临时移除（TODO），Indexer.select() 只返回不带梯度的整数 top-k 索引，idx_q/idx_k/idx_w 投影从主 attention loss 拿不到梯度。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：torchtitan main 上训练 DeepSeek V4 时，三个投影 grad 全为 None、整个训练期停在初始化值，稀疏注意力选 token 的质量从不改进；训练曲线正常、无 crash 无 warning，损害不体现在 loss 上。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/issues/4802；https://github.com/pytorch/torchtitan/pull/4835

### TRN-0185 `dpo_len_norm_denominator_unscored_token` trl DPO 长度归一化分母多计一个 token

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-08-24 · 旧号 SFT.08

- **原因对象**：损失计算 / trl / DPO 长度归一化分母掩码
- **原因行为**：_compute_loss 的 ipo/sigmoid_norm 分支中，token logprob 用移位掩码 completion_mask[..., 1:]，序列得分却除以未移位的 completion_mask.sum()。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：序列首位恰为 completion token（keep_end 截掉整个 prompt 或空 prompt）时分母多计 1 个 token，loss 与梯度系统性偏移（复现 ipo loss 0.0278 vs 正确 0）；常规非空 prompt 不受影响，短测全绿。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6879

### TRN-0191 `padding_free_ld_prefix_uses_physical_segment_length` ms-swift padding-free LD-DPO 按物理段长取共享前缀

`故障` · `active` · `sft` · `verified` · `var` · 发现 2026-09-13 · 旧号 SFT.14

- **原因对象**：损失计算 / ms-swift / padding-free LD-DPO 前缀长度
- **原因行为**：padding-free LD-DPO 用 logits_to_keep 产出的物理 packed 段长确定共享 completion 前缀长度，而非有效 completion token 计数，prompt/masked 位可挤进该前缀。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：label-discount 权重落在错误 token 集上：实测 ld_alpha=0 时 chosen 分数计入 3 个而非 2 个 response token（多出的是 prompt 位），训出的偏好边界偏移；有无 logits_to_keep 均错位，无 crash。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/pull/10072
- **关联**：var:TRN-0185

### TRN-0192 `explicit_loss_type_path_drops_token_weights` ms-swift 显式 CE loss_type 丢弃 token 权重

`故障` · `active` · `sft` · `verified` · `var` · 发现 2026-09-13 · 旧号 SFT.15

- **原因对象**：损失计算 / ms-swift / CustomCrossEntropyLoss
- **原因行为**：Seq2SeqTrainer 把 token weights 传给 CustomCrossEntropyLoss，但回调重算 CE 时丢弃 weights，loss_scale 未在 reduce 前作用于 per-token loss。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：显式 --loss_type cross_entropy 时用户配置的 token 权重（如 last_round、工具位降权）不生效，按均匀权重训练，零权重 token 也计入 loss 与梯度；默认 trainer 路径正常。静默、无报错。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/pull/10100
- **关联**：var:loss_scale_reweights_rounds

### TRN-0205 `seq_mean_token_length_bias` 先序列内 token 平均的 loss 归约压小长序列梯度

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-17 · 旧号 RL-ADV.03

- **原因对象**：损失计算 / 通用 / GRPO 策略 loss 的 token 归约
- **原因行为**：每条序列先对 token 取平均再进组聚合，而非按全局 token 数归一
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：长序列中每个 token 的梯度贡献被压小，形成与长度相关的偏置，与 RL-RWD.02 同族但落在 loss 归约而非奖励设计
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：DAPO；
- **关联**：var:TRN-0195

### TRN-0217 `stale_loss_copy_silently_drops_config` trl 变体 trainer 的 loss 副本漂移致配置静默失效

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-20 · 旧号 RL-KL.04

- **原因对象**：损失计算 / trl / _compute_loss 副本与 Liger
- **原因行为**：GSPO-token/GMPO 等复制粘贴的 _compute_loss 与主实现漂移，GRPO 的 Liger 路径又绕过 _compute_loss，新增正则项/开关在这些路径上没有对应代码
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：配置通过校验、resolved config 正确，但 KL 偏置校正、OPSM、entropy bonus、router aux loss 静默 no-op；Liger 路径下改 coef 后 loss bit 级不变，MoE 默认配置即中招
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6807；https://github.com/huggingface/trl/issues/6808；https://github.com/huggingface/trl/issues/7009；https://github.com/huggingface/trl/pull/7038；https://github.com/huggingface/trl/pull/7062；https://github.com/huggingface/trl/issues/7270
- **关联**：var:TRN-0055

### TRN-0307 `mindformers_per_token_loss_degenerate_to_per_microbatch` mindformers per-token loss 等价退化

`故障` · `active` · `pretrain；sft` · `documented` · `var` · 发现 2026-10-17

- **原因对象**：损失计算 / cann / _extract_model_loss 归一
- **原因行为**：崩溃修复把 (numerator, denominator) 当场相除还原标量 loss，数值与开关关闭完全等价：每个 micro-batch 仍按自身 token 数归一，per-token 语义丢失
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：mindformers pynative（!8656 已入 r2.1.0-beta1、!8655 master open）开 calculate_per_token_loss 后 loss 行为与关闭完全等价、随 micro 分组/dp 切法变化，全局 per-token 归一未发生
- **改进措施**：检测 改变 micro-batch 大小/dp 切分对比 loss 是否漂移（等价退化即暴露）；8 卡对拍静态图基线（开关两态各自对基线偏差一致才中性）；修复 修复 MR !8875（open，Fixes #2509）：micro-batch 累加未归一 token-loss 与 token 数、每优化器步全局归约 (numerator, denominator) 后按平均 token 数缩放梯度（对齐 Megatron finalize_model_grads），MoE aux loss 接入配置、indexer loss 保持求和、MTP chunk 分支同语义；8 卡七组并行矩阵与静态图基线对拍中性。https://atomgit.com/mindspore/mindformers/merge_requests/8875
- **来源**：https://atomgit.com/mindspore/mindformers/merge_requests/8875
- **关联**：var:TRN-0175

### TRN-0334 `mindspeed_llm_dsv4_indexer_loss_coeff_microbatch_scale` DSv4 indexer 梯度漏乘 coeff 与 mbs 缩放

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：损失计算 / mindspeed-llm / fused DSv4 indexer 梯度缩放
- **原因行为**：fused indexer loss 路径把 loss_coeff 只用于日志、未作用于反向梯度缩放，且未消费 MCore schedule 的 micro-batch loss scale，默认梯度缩放恒为 1.0。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：indexer-loss-coeff 从 1.0 调到 0.1 时日志 dsa_indexer_loss 降 10 倍而 gnorm 不变，只有设 0.0 才关分支；num_microbatches=8 时 fused indexer 辅助梯度约大 8 倍，主辅 loss 配比失衡。
- **改进措施**：检测 改 indexer-loss-coeff 后同时看 dsa_indexer_loss 与 gnorm：日志 loss 变而 gnorm 不变即为未生效；再把 fused 与非 fused 路径的 indexer 梯度逐元素对比。；修复 修复 PR https://gitcode.com/Ascend/MindSpeed-LLM/pull/4993 ：indexer_scale = grad_scale * loss_coeff / num_seqs，并让 SparseFlashMlaWithIndexerLossFunction 读取与未融合路径一致的 loss_scale/num_microbatches（状态未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1818；https://gitcode.com/Ascend/MindSpeed-LLM/pull/4993
- **关联**：var:TRN-0164

### TRN-0353 `msllm_mtp_loss_num_tokens_zero_nan` MTP num_tokens 为 0 致 mtp_1 loss 成 NaN

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：损失计算 / mindspeed-llm / MTP loss tracker
- **原因行为**：multi_token_prediction.py 用 sum(mtp_loss)/num_tokens 存 loss tracker，num_tokens 为 0 时结果成 NaN 被静默写进 tracker。
- **影响对象**：指标/日志；训练信号（静默错误）
- **影响详情**：glm5.2 SFT 开 --mtp-num-layers 1 后日志只剩 lm loss 与 global_load_balancing_loss，mtp_1 loss 字段整个消失（值为 NaN）；主 loss 看起来正常，MTP 层是否在学无法从日志判断。
- **改进措施**：检测 检查日志是否打印 mtp_1 loss；或直接在 MTPLossLoggingHelper.save_loss_to_tracker 入口断言 num_tokens>0；修复 issue #1841（closed）只指出 num_tokens=0 这一处，正文未附修复 PR，未核实
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1841

### TRN-0451 `verl_logprob_margin_fp32_rounds_to_zero` verl 确信标签 logprob 与梯度 fp32 舍入到 0

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：损失计算 / verl / logprobs_from_logits
- **原因行为**：logp_t=z_t-logsumexp(z) 把标签自身 exp(0)=1 计入和式：margin 超 ~16.6 后 fp32 的 1+exp(-m) 舍入为 1，logprob 与标签梯度变精确 0，其余梯度保留。
- **影响对象**：梯度；训练信号（静默错误）
- **影响详情**：30.0 margin 下 logprob=0、label_grad=0、other_grads_sum=-2.994e-09（fp64 参考 -2.994e-09）；bf16 分支 margin~5.5 即触发；Triton fused linear CE 同病。
- **改进措施**：检测 大 margin 标签（如 30.0）单元对拍 fp64；检查梯度逐元素和是否为零。；修复 待定（issue open，未见修复 PR）。
- **来源**：https://github.com/verl-project/verl/issues/8376

### TRN-0466 `trl_gkd_onpolicy_dataset_token_denom` GKD on-policy 步按数据集 token 数归一化

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：损失计算 / trl / GKD loss 归一化口径
- **原因行为**：Trainer 在用生成 completion 替换 labels 前就从 dataset labels 数出 num_items_in_batch；JSD 和除以数据集 token 数，分母含已丢弃的参考答案 token。
- **影响对象**：训练信号（静默错误）
- **影响详情**：每个 on-policy/seq_kd 步的 loss 尺度取决于被扔掉的参考答案长度（默认 lmbda=0.5 约一半步受影响）；实测 num_items_in_batch=172 而生成 batch label token 远小。同仓 DistillationTrainer 已按生成侧重数。
- **改进措施**：检测 对照 DistillationTrainer 重数逻辑；打印 num_items_in_batch 与生成 batch label token 数；修复 待定（issue open）
- **来源**：https://github.com/huggingface/trl/issues/7924

### TRN-0511 `torchtitan_loss_parallel_confident_target_zero` torchtitan 并行 CE 确信标签 loss 梯度归零

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-29

- **原因对象**：损失计算 / torchtitan / 并行 CE 目标计入归约和
- **原因行为**：log_softmax 构造把目标自身 exp(0)=1 计入 all-reduce 求和：margin 超 ~16.6 后 fp32 和舍入为 1，per-token loss 与目标梯度成精确 0，非目标梯度保留。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：compute_logprobs 以 reduction=none 复用同一 Function，RL 中部分高确信 token 的 logprob 恒 0；TP>1 与 TP=1 的非 TP 路径（F.cross_entropy 未改）均含该舍入。
- **改进措施**：检测 高置信样本（margin>16.6）检查 per-token loss 是否精确 0、梯度是否和为零；修复 修复 PR https://github.com/pytorch/torchtitan/pull/5624 仍 open 未合入（2026-10-30 核对）
- **来源**：https://github.com/pytorch/torchtitan/issues/5623；https://github.com/pytorch/torchtitan/pull/5624
- **关联**：var:TRN-0451

### TRN-0547 `deepspeed_opsd_jsd_lowprec_mask_count_loss_zero` DeepSpeed OPSD JSD 低精 logits 掩码计数错

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：损失计算 / deepspeed / generalized_jsd_loss 掩码计数
- **原因行为**：OPSD JSD loss 把 response mask cast 成 logits dtype 再 sum：bf16 舍入 >256 计数（97992→97792），fp16 溢出 int64 max，loss 归 0
- **影响对象**：训练信号（静默错误）
- **影响详情**：bf16 下有效 token 计数被舍入（97992→97792），loss 归一化分母错；fp16 下计数溢出为 int64 max，JSD loss 归 0，蒸馏信号静默消失而训练照常跑完；新增 bf16/fp16 用例修前失败、修后 22 通过（CPU，未覆盖 GPU/ZeRO）
- **改进措施**：检测 对 bf16/fp16 logits 的 loss 路径断言 mask 计数与 int64 参考一致；监控 loss 是否异常趋 0；修复 修复 PR https://github.com/deepspeedai/DeepSpeed/pull/8947（open，mask 以 int64 计数、逐 token JSD 至少 float32 求和，未合入）
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8947

## MoE路由

### TRN-0017 `bf16_token_count_rounding_flips_bias_sign` BF16 token 计数舍入翻转 MoE 路由 bias 更新方向

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 NUM.08

- **原因对象**：MoE路由 / megatron-lm / router token 计数 buffer
- **原因行为**：aux-loss-free router 的 token 计数注册为浮点 buffer，被 Float16Module 转成 BF16 后累积并跨 rank 归约；计数约 40K 时 spacing=256，专家间小差异被舍入抹掉或翻转。
- **影响对象**：模型权重；训练轨迹（不可复现）
- **影响详情**：无 NaN、无 crash、loss 正常；bias 更新方向 sign(avg−count) 在两次合法运行间相反（W64 实测 −1 vs +1），router bias 沿错误方向更新、训练轨迹分叉，且随归约树/拓扑变化不可复现，eager-vs-eager 也复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7081

### TRN-0150 `router_entropy_collapse` MoE router 熵塌缩：token 涌向少数专家，其余专家饿死

`故障` · `active` · `pretrain` · `verified` · `NEW` · 发现 2026-08-17 · 旧号 MOE.01

- **原因对象**：MoE路由 / 通用 / router 负载均衡 aux loss 配置
- **原因行为**：负载均衡损失被关闭、系数过小或被错误的 aux 系数关掉时，router logits 锐化，token 集中到少数专家，其余专家得不到 token。
- **影响对象**：训练轨迹（质量退化）
- **影响详情**：无 NaN，总 loss 仍可下降（存活专家在过拟合），长跑后能力塌；本实验室 stability_monitor 观察到 per_token_entropy 从 ~4.0（64 专家近均匀）降到 <1.0，且早于 grad 爆炸。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：本实验室 `stability_monitor`：`per_token_entropy` 从 ~4.0（64 专家近均匀）掉到 <1.0，早于 grad 爆炸。

### TRN-0153 `dropless_capacity_silent_drop` 宣称 dropless 的 MoE 实现在容量约束下仍静默丢 token

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 MOE.04

- **原因对象**：MoE路由 / 待定 / dropless 路径的容量/对齐处理
- **原因行为**：宣称 dropless 的实现在容量或对齐约束下仍丢弃 token，或把溢出 token 静默改路由到其他专家，同时统计上报告 dropped=0。
- **影响对象**：隐状态；指标/日志（静默错误）
- **影响详情**：部分 token 的 MoE 输出近零或走错专家，loss 略噪、无报错；dropped 统计仍显示为 0，不可信。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：Megatron / DeepSpeed MoE 容量因子文献；

### TRN-0154 `expert_bias_buffer_dropped_on_replacement` DeepSpeed AutoEP 替换 MoE 模块时静默丢路由偏置

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-08-30 · 旧号 MOE.05

- **原因对象**：MoE路由 / deepspeed / AutoEP 模块替换的路由偏置迁移
- **原因行为**：AutoEP 迁移 e_score_correction_bias 时要求其为 nn.Parameter 且挂在 gate 下，而多数模型族存为 nn.Buffer 或挂在其他位置，两个判定缺陷叠加使偏置未被迁移。
- **影响对象**：模型权重；隐状态（静默错误）
- **影响详情**：无报错、无警告、loss 照降；替换后 top-k 选择偏置归零，专家选择退回未训练的均衡态，表现像换了一批专家。DeepSeek-V3 系 ckpt + ZeRO-3 + AutoEP 即触发，transformers 5.15.1 的 22 个模型族中 20 个中招。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8358

### TRN-0155 `expert_bias_hook_implicit_semantics_shift` torchtitan Qwen3 无条件注册均衡 hook，升级后轨迹分叉

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-02 · 旧号 MOE.06

- **原因对象**：MoE路由 / torchtitan / Qwen3 负载均衡 hook 注册
- **原因行为**：#3666 起 Qwen3 registry 无条件注册 aux-loss-free 负载均衡 hook，每步用累计计数更新持久 buffer expert_bias_E；该变更无独立开关，ckpt/配置也不记录更新模式。
- **影响对象**：训练轨迹；模型权重（静默错误）
- **影响详情**：同 ckpt、数据、seed 与确定性执行下，升级前后从 step 2 起 loss 分叉（235B 1000 步 MAE 0.042、最大差 0.129），grad_norm 首差在 step 19；无 crash、NaN 或日志差异，旧版本 run 无法复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/issues/4394

### TRN-0157 `hash_router_aux_loss_optimizes_undispatched_route` Megatron hash 路由层 aux loss 优化未执行的路由

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-06 · 旧号 MOE.08

- **原因对象**：MoE路由 / megatron-lm / hash MoE 层的 aux loss 路由图
- **原因行为**：hash 路由 MoE 层按 tid2eid 表 dispatch，但开 aux loss 时 router 另从 learned logits 算一份 top-k 路由进 aux loss，优化的路由与执行的路由脱钩。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：无 crash、无 NaN；aux loss 数值正常下降，但 router logits 被训成纸面均衡，实际 token 分布不变，aux 梯度把 router 拉向与真实分配无关的方向。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7079

### TRN-0158 `load_balance_hook_scans_wrong_container` torchtitan 负载均衡 hook 漏掉 MTP MoE 层

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-09-06 · 旧号 MOE.09

- **原因对象**：MoE路由 / torchtitan / 负载均衡 hook 的层容器枚举
- **原因行为**：负载均衡 hook 只遍历 model.layers，而 DeepSeek MTP 块在 FSDP 后位于 model.mtp_layers，其 expert_bias_E/tokens_per_expert_E 从不上报、归约或更新。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：主干训练正常，MTP 专家的 aux-loss-free 偏置停在初值、跨 rank token 计数不归约；两 rank Gloo 复现中修复前 MTP bias 不动、counter 停在 [3,1]，修复后 bias 为 [-0.3,0.3]、counter 归零。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/4494
- **关联**：var:TRN-0155

### TRN-0160 `global_aux_loss_denominator_uses_current_microbatch` Megatron 全局 aux loss 分母误用当前微批 token 数

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-14 · 旧号 MOE.11

- **原因对象**：MoE路由 / megatron-lm / global aux loss 归一化分母
- **原因行为**：--global-aux-loss 下 expert 计数跨 microbatch 累积，但归一化分母取 ga_steps × 当前 microbatch 有效 token 数，累积分子配了瞬时分母。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：各 microbatch 有效 token 数不同时触发，物理等长 padding 会掩盖触发条件；同 12 token 下 balanced [4,4,4] 与 uneven [6,2,4] 的 router 梯度相对 L2 差 0.25（修复后 2.25e-7），无 crash、无 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7213

### TRN-0161 `router_aux_loss_inplace_reduce_overwrites_token_count` Megatron MoE token 计数被就地归约覆写致 aux 梯度 ×TP

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 MOE.12

- **原因对象**：MoE路由 / megatron-lm / moe_utils 有效 token 计数
- **原因行为**：local_tokens_per_expert 被 TP 归约就地覆写为全局和，带 padding_mask 时据此推导的 local_num_tokens 也成全局值，被当作 valid_token_count 算 aux loss。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 crash、无 NaN；MoE aux loss + padding_mask + per-token loss + TP/CP>1 时 router 梯度恒放大 TP 或 CP 倍（TP=2 时 2.226 vs 1.113），负载均衡压力随并行度漂移，不同 TP 的 run 不可比。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7452；https://github.com/NVIDIA/Megatron-LM/pull/7481

### TRN-0162 `overdispersed_routing_importance_signal_collapse` 激进负载均衡致 MoE 路由过度分散，router 重要性信号塌缩

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-19 · 旧号 MOE.13

- **原因对象**：MoE路由 / 通用 / 负载均衡压力下的 router 概率
- **原因行为**：训练期 aux loss 把 token 分布推向近均匀时，router 概率在专家间失去区分度，不再能作为专家重要性信号。
- **影响对象**：训练轨迹；指标/日志（质量退化）
- **影响详情**：训练侧正常、无步级数值症状；gpt-oss-20B 专家剪枝中 perplexity 最低的配置数学推理最差，perplexity 与下游能力的关系反转；标准路由的 Mixtral-8x7B-Instruct 无此现象。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2609.04453

### TRN-0163 `aux_loss_coef_noop_without_router_logit_flag` trl SFTTrainer 靠可选字段判定 MoE，aux loss 静默失效

`故障` · `active` · `sft` · `documented` · `var` · 发现 2026-09-23 · 旧号 MOE.14

- **原因对象**：MoE路由 / trl / SFTTrainer 的 MoE 判定谓词
- **原因行为**：SFTTrainer 以 text_config 是否声明 output_router_logits 判定 MoE 并启用 aux loss，但该字段是可选声明，未声明的 MoE 架构被判为非 MoE，aux 系数不生效。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：无 crash、无警告，loss 曲线正常；transformers main 上 64 个 MoE config 有 30 个未声明（含 DeepSeek-V2/V3、GLM4-MoE、Qwen3-VL-MoE 等），这些架构的 SFT 负载均衡项从未生效，专家利用分布无约束漂移。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7222
- **关联**：var:TRN-0056

### TRN-0170 `router_backbone_update_coupling_spike` MoE 路由与主干同步更新放大 outlier 致 loss 尖峰

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-09-01 · 旧号 LOSS.06

- **原因对象**：MoE路由 / 通用 / router 与 backbone 的同步更新
- **原因行为**：router 与 backbone 同步更新形成正反馈：MoE 层 outlier 放大路由扰动，路由扰动又催生 outlier，恶性循环以 loss spike 爆发；路由功能本身正常。
- **影响对象**：训练轨迹；隐状态（质量退化）
- **影响详情**：反复出现 loss spike，且与 MoE 层 outlier 一致相关，常需 rollback，否则 derail run 或被迫用保守超参；无 crash。见于 DeepSeek-V4 1.6T/284B 预训练。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2606.19348；https://github.com/pytorch/torchtitan/issues/4349；https://github.com/pytorch/torchtitan/pull/4495

### TRN-0285 `moe_fused_topk_mapping_oob_and_overlapping_views` MoeFusedTopk 映射数异常越界读、重叠视图未拦截

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：MoE路由 / cann / moe_fused_topk 映射偏移与输出校验
- **原因行为**：开启专家映射时 kernel 以 mappingNum 原始值（无符号读取）作取模基数算映射表行内偏移，零/负/超表宽时偏移跨出本专家行读到其他专家映射项；host 不检查输出视图步长，内部元素重叠的 y/indices 视图被放行。
- **影响对象**：数值结果（静默错误）
- **影响详情**：映射数异常时 token 被路由到错误专家（读到他人映射项），无报错；重叠输出视图下输出语义不确定。MoE 训练中专家分布与路由结果静默错乱。
- **改进措施**：检测 对 topk 输出 indices 与 expert mapping 做越界/一致性抽检；避免零步长广播视图作输出。；修复 修复已合入：master PR #13819/#13848（mappingNum 按有符号读取、非正按 0、钳位到表宽 tableDim_ 后再取模；host 新增 CheckOutputLayout 按 stride/gcd 拒绝重叠视图返回 161002，合法转置/带间隔布局放行），并回迁 9.2.0 分支 MR !13857（含 UT/ST 回归）。issue #6151 closed。https://gitcode.com/cann/ops-transformer/pull/13819
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6151；https://gitcode.com/cann/ops-transformer/pull/13819；https://gitcode.com/cann/ops-transformer/merge_requests/13857

### TRN-0348 `msllm_capacity_auxloss_drop_denominator_nan` 专家容量 drop 与 aux_loss 并存致负载均衡 loss NaN

`故障` · `active` · `pretrain；sft` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：MoE路由 / mindspeed / capacity drop + aux_loss
- **原因行为**：drop与dropless策略在路由和aux_loss计算路径上互斥：drop下被丢token不计入aux_loss，分母偏小甚至为零；dropless下重路由后aux_loss的路由分布与实际专家计算分布不一致，梯度异常。
- **影响对象**：训练信号；模型权重（数值异常）
- **影响详情**：910C 上训练中途 loss 变 NaN；验证阶段 capacity padding/截断后的 hidden size reshape 也对不齐，报 shape 不匹配。
- **改进措施**：检测 分别只开 capacity 或只开 aux_loss 做 A/B；打印 aux_loss 的分母 token 计数；修复 issue #1399（closed）给出方案：drop 下 aux_loss 只算未 drop 的 token、dropless 下 aux_loss 按 pre-capacity 原始路由分布算；或对参数组合直接报冲突
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1399

### TRN-0362 `msllm_dualpipev_permute_fusion_capacity_conflict` DualPipeV 强绑 permute 融合与专家容量互斥

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：MoE路由 / mindspeed-llm / fused_moe_permute 参数校验
- **原因行为**：DualPipeV 依赖 moe-permute-fusion 而自动开启它，capacity 又要按 token 截断/重路由、改变 permute 语义与输入 shape，参数校验直接把两者判为互斥。
- **影响对象**：可用性/进度（报错）
- **影响详情**：同时开 DualPipeV 与 --moe-expert-capacity-factor，训练在 initialize_megatron 的 validate_args 阶段就 AssertionError 退出，流水 overlap 与容量限制无法共存。
- **改进措施**：检测 启动参数校验里列出 DualPipeV 自动打开的 feature 集，与 capacity/pad 类参数做交叉检查；修复 issue 给两档：短期改报错文案、直接说明 DualPipeV 与 capacity 冲突并建议用 aux_loss；长期解耦调度与 permute 融合，capacity 开启时自动降级为非融合 permute（closed，未附 MR，未核实）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1401

### TRN-0378 `opstransformer_moe_finalize_routing_v3_a2_range_ignored` MoeFinalizeRoutingV3 A2 忽略特殊专家区间静默按普通专家

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：MoE路由 / cann / MoeFinalizeRoutingV2/V3
- **原因行为**：zero/copy/constant 三类特殊专家区间实现只存在于 950 arch35 路径，A2 绑定的 membase tiling 与 kernel 完全不读这三个属性、也不校验，接口已暴露但实现缺失
- **影响对象**：数值结果；隐状态（静默错误）
- **影响详情**：Atlas A2 上无论三类 range 取何值（含非法 end<start、超上限、区间重叠）均 rc=0 且输出与不传完全相同，按普通专家累加；期望 100.0/114.0/120.0 的用例实测全为基线 97.41
- **改进措施**：检测 传任一 range 后断言输出与不传时不同；非法区间（end<start/重叠）应报 161002；修复 待定（issue 建议补 A2 实现或把资料 A2 改不支持二选一，并加 A2 回归用例）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6549

### TRN-0391 `opstransformer_moe_token_unpermute_padded_false_outputs_unwritten` MoeUnpermute paddedMode=false 两输出从不写出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：MoE路由 / cann / MoeTokenUnpermute 写出分支
- **原因行为**：paddedMode=false 时 outIndex 与 permuteTokenId 两个输出从未被写：接口返回 0，buffer 保持调用方预填内容；文档明确两输出在该模式下有定义语义。
- **影响对象**：数值结果（静默错误）
- **影响详情**：非 padded MoE unpermute 路径下 outIndex（槽位索引）与 permuteTokenId 为未初始化显存（canary 全残留）；主输出两种模式都正确，paddedMode=true 对照正确写出。
- **改进措施**：检测 两输出预填哨兵 round-trip；paddedMode=false 下与 numpy.sort/argsort 参考对账。；修复 待定（issue open 2026-10-23，master 23cb0599，未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6607
- **关联**：cross:INF-2174

### TRN-0393 `opstransformer_moe_permute_with_ep_wraparound_tail_unwritten` MoeTokenPermuteWithEp 环绕区间尾部 end 行输出未写

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-24

- **原因对象**：MoE路由 / cann / MoeTokenPermuteWithEp 搬运
- **原因行为**：环绕区间（start>end）时 tiling 按环绕语义算 numOutTokens，但 kernel 过滤条件的索引值域只到数组末尾，尾部 end 行从未写入，两段返回成功。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：EP 环绕窗口下 permuteTokensOut/permuteProbsOut 尾部恒缺 end 行（实测 8 行缺 4），输出为未初始化显存残留，形状正确、前段正确、无报错；76 组 (start,end) 扫描缺口恒等于 end。
- **改进措施**：检测 输出预填哨兵做 round-trip；环绕窗口（start>end）下校验实际写入行数==numOutTokens。；修复 待定（issue open 2026-10-23，根因定位至 moe_index_copy_with_ep.h:158/185 过滤条件，未见修复 MR）
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6622
- **关联**：cross:INF-2173

### TRN-0410 `ops_transformer_moe_init_routing_v2_grad_oob_skip` MoeInitRoutingV2Grad 越界行 idx 静默当 -1 跳过

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-25

- **原因对象**：MoE路由 / cann / aclnnMoeInitRoutingV2Grad
- **原因行为**：kernel 侧对 idx<0 与 idx≥rows 一律按无效行跳过，host 侧未做值域校验；越界（≥行数）与小于 -1 的 expandedRowIdx 被当作 -1，两段返回 0，被跳过行的梯度静默丢失。
- **影响对象**：梯度；数值结果（静默错误）
- **影响详情**：MoE 路由反向展开行索引越界时（Drop/Pad 之外场景值域 [0,B*S*K)），该行梯度被静默丢弃——输出与 skip 语义逐元素一致（CPU 三语义标杆判据），梯度少加一项；接口无报错。
- **改进措施**：检测 含越界 idx 的输入对拍 CPU skip/clamp/mod 三语义标杆；上游路由 idx 生成处加值域断言。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6691；https://gitcode.com/cann/ops-transformer/issues/6710

### TRN-0429 `opstransformer_moe_init_routing_v3_a2_dtype_rank_check_skipped` MoeInitRoutingV3 A2 上 dtype/rank 校验整段跳过

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：MoE路由 / cann / aclnnMoeInitRoutingV3
- **原因行为**：Atlas A2 路径的入参 dtype/rank 校验被整段跳过：资料声明 uint8 应第一段 161002、rank=3 应 561002，实测第一段返回 0、错误延迟到第二段且码不同（561000/561103）。
- **影响对象**：可用性/进度（报错）
- **影响详情**：按资料构造的非法输入在第一段接口被放行，错误延迟到执行段且返回码与资料不一致；错误码契约失效。
- **改进措施**：检测 对拍资料错误码表逐一构造非法 dtype/rank 输入。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6702

### TRN-0435 `opstransformer_moe_init_routing_v4_activenum_ignored` MoeInitRoutingV4 activeNumOptional 完全不生效

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：MoE路由 / cann / aclnnMoeInitRoutingV4
- **原因行为**：activeNumOptional 不参与任何计算：按资料 Active 场景形状构造时第二段 561103；按全量形状传入时 activeNum=0/2/8/100 输出逐字节相同，数值被静默忽略。
- **影响对象**：数值结果；模型权重（静默错误）
- **影响详情**：Active 场景按资料形状调用直接失败（561103）；绕过形状后 activeNum 语义丢失，输出全量行而非激活子集，静默偏离资料语义。
- **改进措施**：检测 activeNum 取 0/2/8/100 对照输出哈希；按资料形状构造首段调用。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6709

### TRN-0437 `opstransformer_moe_init_routing_v3_droppad_scale_unwritten` MoeInitRoutingV3 Drop/Pad 缺 scale 输出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：MoE路由 / cann / aclnnMoeInitRoutingV3
- **原因行为**：Drop/Pad 分支（dropPadMode=1）缺失 scale 写出路径：非量化且传 scaleOptional 时应输出 [expertNum*expertCapacity] 个 FLOAT32，实测两段返回 0 但整块未写。
- **影响对象**：数值结果（静默错误）
- **影响详情**：MoE 路由前向在 Drop/Pad 场景调用后读 expandedScaleOut 得到调用方预填的残留值而非 scale 数据；dropPadMode=0 对照组正常写出，无任何报错。
- **改进措施**：检测 出参预填金丝雀后调用并统计未写字节；对照 dropPadMode=0 分支。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6701

### TRN-0441 `opstransformer_moe_init_routing_v2_grad_oob_dirty_read` MoeInitRoutingV2Grad 越界 idx 读相邻显存当梯度累加

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-10-26

- **原因对象**：MoE路由 / cann / aclnnMoeInitRoutingV2Grad
- **原因行为**：expandedRowIdx 三条 tiling 分支校验均不完整（dropless 无校验、activate 只有上界、drop/pad 只查 -1），kernel 直接按 idx*cols 寻址，越界时把相邻内容当梯度累加。
- **影响对象**：梯度；数值结果（静默错误）
- **影响详情**：expandedRowIdx 越界时不报参数错误：偏移落在相邻已分配显存时把相邻张量内容当梯度累加（静默脏数据）；偏移极大时同步阶段报 507035 AI Core MTE invalid GM address。A2 910B3 / CANN 9.2.0 实测。
- **改进措施**：检测 idx 注入越界值对拍宿主侧区间校验；mssanitizer memcheck。；修复 待定（issue open，未见修复 MR）。
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6710
- **关联**：var:TRN-0410

### TRN-0473 `opstransformer_moe_token_unpermute_negidx_family` CANN MoE token unpermute 族负索引缺下界校验

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：MoE路由 / cann / moe_token_unpermute 族索引。
- **原因行为**：moe_token_unpermute/moe_token_permute_grad/moe_index_copy 对 sortedIndices 只判上界不判下界，负值经 int64_t offset 直读 GM。
- **影响对象**：数值结果（静默错误）
- **影响详情**：sortedIndices 含负值时（上游 -1 padding，vLLM 标准行为）：{-1,1} 输出 [0,0,1.5,2]，无效槽未清零、无报错，两段接口返回 0；大负值（-2^30）sync fail 507035 KERNEL_ERROR。CANN 9.0.0、910_93 实测。
- **改进措施**：检测 训练/路由输入含 -1 padding 时输出对照 CPU 参考实现；大负值直接 KERNEL_ERROR；修复 修复 PR https://gitcode.com/cann/ops-transformer/merge_requests/14742（open，2026-10-27）——按本仓 moe_token_unpermute_with_routing_map_not_pad.h:228-233 的 IsValidInputIndex 范本补 `in_token_index >= 0 && < num_out_tokens` 下界，三文件 4+4+2 处；同仓 commit 0c5c1ed15 为既有范本。用户自编译修复版实测 {-1,1} 用例通过
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6814；https://gitcode.com/cann/ops-transformer/merge_requests/14742
- **关联**：cross:INF-2214

### TRN-0522 `moegating_topk_softmax_310p_tiling_ub_overflow` MoeGatingTopKSoftmax 310P tiling 路由错乱

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：MoE路由 / cann / MoeGating tiling 310P
- **原因行为**：tiling 向上取整越过真实行数使输入塌缩为单尾块，非 8 倍数尾块走单整块 softmax 路径 UB 需求超限，输出被写坏产出垃圾专家索引
- **影响对象**：数值结果；训练样本流（静默错误）
- **影响详情**：col=256 且行数落 (144,159] 非 8 倍数时 router 输出垃圾专家索引；vLLM+MoE GSM8K 动态 batch 约 21% 样本空输出（首 token 即 EOS），空输出样本 input_tokens 全落该区间；EP 机型 blockNum=8 未踩中
- **改进措施**：检测 对 row<16*blockNum 且非 8 倍数输入单算子对拍；监控 MoE 首 token EOS 率；修复 修复 PR https://gitcode.com/cann/ops-transformer/merge_requests/14811（open）：guard 310P 尾块防 softmax UB 溢出
- **来源**：https://gitcode.com/cann/ops-transformer/issues/6910；https://gitcode.com/cann/ops-transformer/merge_requests/14811
- **关联**：cross:INF-2259

### TRN-0527 `meg_sft_moe_aux_loss_mask_normalization_mismatch` SFT MoE aux loss 系数随 mask 漂移

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：MoE路由 / megatron-lm / router aux loss 归一化
- **原因行为**：per_token_loss 模式 router aux loss 乘输入 token 数而 finalize 除以目标 token 数，SFT mask prompt 时 aux 系数随 mask 比例漂移
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：SFT 训练 MoE 模型（mask prompt、calculate_per_token_loss=True）时，目标 token 占比不同的 DP 副本贡献的 aux 梯度没有按预期平均而是相加；路由正则强度随每步 prompt/目标 token 比例漂移，专家负载均衡效果偏离配置，全程无报错
- **改进措施**：检测 对比不同 prompt mask 比例下 aux loss/梯度尺度；检查 router aux 梯度与 moe_grad_scale 的关系；修复 修复/提案 PR https://github.com/NVIDIA/Megatron-LM/pull/8662（open，opt-in flag --moe-aux-loss-input-token-normalization）：缓冲一步 CPU batch 计算全局 scored/input 比，经 moe_grad_scale_func 组合；要求 PP=1、独立 PAD/EOD ID、无序列调度器；内部报告者 aamjad-nvidia
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/8662

## 重计算/卸载

### TRN-0121 `zero2_lowp_master_offload_scratch_stale_poisons_next_step` ZeRO-2 offload 残留 NaN 致后续有限 step 被跳过

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-10-10 · 旧号 OPT.21

- **原因对象**：重计算/卸载 / deepspeed / CPU offload 梯度恢复函数
- **原因行为**：_restore_cpu_offload_grad_to_gpu 只把本 rank 拥有的梯度分片拷进共享 scratch 张量，未清空非拥有区域，而 overflow 检查读整个恢复出的梯度，上一参数组溢出留下的 NaN 驻留其中。
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：一次真实溢出后，之后若干完全有限的 step 仍被判溢出而跳过，训练静默丢更新步、无 crash；ZeRO-2 CPU offload + BF16/FP16 master 权重 + 非托管梯度累积时触发，FP32 master 不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8728

### TRN-0122 `moe_data_dependent_recompute_diverge` MoE 重算时路由/RNG 与前向不一致

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 ACT.01

- **原因对象**：重计算/卸载 / 通用 / MoE 层 activation 重算
- **原因行为**：MoE dispatch 是数据依赖控制流，activation checkpoint 重算时随机数或路由决策与原前向不一致，重算图与保存的激活对不上。
- **影响对象**：梯度（数值异常）
- **影响详情**：反向得到静默 NaN 或错误梯度；若框架校验 checkpoint 一致性则直接硬失败，取决于框架是否校验；MoE 模型开启 activation checkpoint 时触发。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：交叉：推理编目模型图类「数据依赖 expert dispatch 破坏 checkpoint 重算契约」。

### TRN-0123 `selective_recompute_stale_rng` Megatron 选择性重计算漏存 dropout/router RNG

`故障` · `active` · `shared` · `documented` · `var` · 发现 2026-08-17 · 旧号 ACT.02

- **原因对象**：重计算/卸载 / megatron-lm / 选择性重计算 RNG 保存
- **原因行为**：选择性重计算没有保存 dropout 与 router 的 RNG 状态，重算时走了另一条噪声实现。
- **影响对象**：训练轨迹；梯度（质量退化）
- **影响详情**：开启 recompute 后训练曲线与关闭 recompute 的基线分叉，无 shape 错误。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6519
- **关联**：var:TRN-0122

### TRN-0126 `partitioned_activation_recompute_mangles_args` DeepSpeed 分区激活重算时非张量参数错位

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 ACT.05

- **原因对象**：重计算/卸载 / deepspeed / merge_tensors 参数表还原
- **原因行为**：partition_activations 下每个参数保存 (value, size) 成对条目，merge_tensors 的折叠启发式只对张量参数有效，非张量参数后会多插一个 None，其后所有参数右移。
- **影响对象**：梯度；隐状态（静默错误）
- **影响详情**：检查点函数带非张量参数（flag、标量超参、None）且开启 partition_activations 时，重算前向在错位参数表上执行：可能因形状错崩溃，更可能静默产出与原前向不一致的激活和错误梯度；全张量参数不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/pull/8455

### TRN-0127 `sar_recompute_skips_inplace_writes` torchtitan SAR 重算漏放 in-place 写入致梯度静默错误

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-16 · 旧号 ACT.06

- **原因对象**：重计算/卸载 / torchtitan / GraphTrainer SAR 重算 pass
- **原因行为**：SAR pass 只沿 dataflow producer 边选重算点、不建模副作用写入：对 clone 后就地写的 functional 包装算子只重放 clone，不重放 in-place 写。
- **影响对象**：梯度（静默错误）
- **影响详情**：无 crash、无 NaN、graph.lint() 通过，前向 loss 正确，但 backward 拿到变异前的值，梯度静默错误（复现中 6 变 4）；GraphTrainer+SAR 且重算涉及 in-place 包装算子（如 partial-RoPE）即触发。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/issues/4688

### TRN-0128 `offload_reload_missing_stream_ordering_edge` 激活 offload inline reload 缺流排序读到陈旧数据

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-17 · 旧号 ACT.07

- **原因对象**：重计算/卸载 / megatron-lm / tensor_pop inline reload
- **原因行为**：ChunkOffloadHandler.reload() 的 H2D 拷贝与 D2H 的 _offload_event 无排序边；tensor_pop 的 inline reload 未补此边，可在 D2H 写 buffer 时读取。
- **影响对象**：梯度；隐状态（静默错误）
- **影响详情**：无报错、loss 照降，warmup 迭代及 backward 跑赢 prefetch 时重载的激活是新旧内容混合，梯度静默算在陈旧激活上；B300 上 20 次试验 19 次损坏，现有测试丢弃 warmup 迭代而漏检。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/7398；https://github.com/NVIDIA/Megatron-LM/pull/7399

### TRN-0129 `tp_checkpoint_recompute_drops_fp8_autocast` Megatron 重算未重入 fp8_autocast 致梯度分叉

`故障` · `active` · `pretrain` · `documented` · `var` · 发现 2026-09-28 · 旧号 ACT.08

- **原因对象**：重计算/卸载 / megatron-lm / CheckpointFunction 重算上下文
- **原因行为**：tensor_parallel.checkpoint 的 backward 重跑被 checkpoint 的函数时已跳出前向的 fp8_autocast，旧实现只恢复 RNG 状态，区域内 TE 模块以 FP8 关闭状态重算。
- **影响对象**：梯度；隐状态（静默错误）
- **影响详情**：BF16 参数 + FP8 激活时重算静默跑 BF16、前向跑 FP8，梯度自 iteration 2 起与无 recompute 的 run 分叉且无报错；FP8 参数路径则报 AttributeError；--recompute-modules core_attn 或 gdn 触发。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7538
- **关联**：var:TRN-0127

### TRN-0130 `checkpointing_state_flag_not_restored_on_exception_nesting` Megatron IS_CHECKPOINTING 标志在异常与嵌套下未恢复

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-10 · 旧号 ACT.09

- **原因对象**：重计算/卸载 / megatron-lm / IS_CHECKPOINTING 全局标志
- **原因行为**：CheckpointFunction 用进程级全局标志 IS_CHECKPOINTING 控制重算：抛异常时 unset 被跳过、标志残留 True；嵌套 checkpoint 的内层在外层仍运行时就清除标志。
- **影响对象**：梯度（静默错误）
- **影响详情**：训练中捕获异常后继续（如 fault-tolerant 框架 catch-and-retry）时，后续 forward 错误地按 checkpointing 语义执行或反之，RNG/保存策略错位产生错梯度而不 crash；嵌套场景外层语义被内层提前剥夺。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7975

### TRN-0131 `deepep_dispatch_replay_reorders_rows_wrong_grads` FullAC 重放 DeepEP dispatch 致 MoE 梯度错路由

`故障` · `active` · `pretrain` · `verified` · `NEW` · 发现 2026-10-10 · 旧号 ACT.10

- **原因对象**：重计算/卸载 / torchtitan / FullAC 重放 DeepEP dispatch
- **原因行为**：FullAC（及未保存 ep_communication 的 RegionAC）backward 重放前向使 DeepEP dispatch 再跑一次，接收槽由原子操作分配、行序可变，梯度却按首次 handle 路由。
- **影响对象**：梯度（静默错误）
- **影响详情**：routed-expert 与 router 梯度与正确值几乎不相关（cosine 约 0.01–0.03），loss 仅差约 0.0005、曲线照常；使用 FullAC，或 RegionAC 未保存 ep_communication 的 DeepEP MoE 训练时触发。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/5123

### TRN-0138 `activation_offload_bypasses_absorbed_mla` Megatron 激活 offload 静默绕过 absorbed MLA

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-09-06 · 旧号 KER.07

- **原因对象**：重计算/卸载 / megatron-lm / 细粒度 offload 模块选择
- **原因行为**：细粒度 activation offload 的模块选择逻辑不覆盖 absorbed MLA 投影，配置开启 offload 的模块在该路径下被静默绕过，既不报不支持也不下装。
- **影响对象**：性能/资源（性能退化）
- **影响详情**：无 crash、无日志差异，absorbed MLA 模型上 activation offload 的显存收益静默缺失、激活照常驻留显存；同配置在非 MLA 模型上生效，只有 A/B 显存对比能暴露。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/7090

### TRN-0261 `missing_dataloader_silently_disables_resampling` DeepSpeed ZenFlow 未传 dataloader 时列永不重选

`故障` · `active` · `shared` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 OBS.12

- **原因对象**：重计算/卸载 / deepspeed / ZenFlow 列重选间隔解析
- **原因行为**：epoch/auto 策略从 training_dataloader 取 epoch 步数，自管 dataloader 时其为空，设 select_interval=0 即永不重选；告警处误写 raise Warning，实为抛异常。
- **影响对象**：训练轨迹（静默错误）
- **影响详情**：默认配置、自管 dataloader 下无报错无日志，第 0 步选出的列沿用整个 run（40 步对照重选 1 次 vs 4 次），训练动态与配置语义背离；auto+整数 interval 组合在初始化期报错。既有 ZenFlow 测试都跑在这条错路径上，但只断言不 crash。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8456

### TRN-0330 `mindspeed_llm_dsa_shareindex_cache_overwritten_in_recompute` DSA ShareIndex TopK 缓存被后组覆盖，重算错读

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：重计算/卸载 / mindspeed-llm / DSA ShareIndex TopK 缓存
- **原因行为**：ShareIndex 的 TopK 只存在进程级全局变量里、仅保留最近一次写入，未与当前 forward/microbatch 及 source layer 绑定；开启 full recomputation 后多个共享组互相覆盖。
- **影响对象**：数值结果；梯度（静默错误）
- **影响详情**：正向 L3 计算、L4-L6 复用，L7 计算、L8-L10 复用时，反向逆序重算 L4-L6 会误读 L7 的 TopK，attention 结果与梯度错；动态长度场景进一步表现为 shape 不匹配报错，无 NaN。
- **改进措施**：检测 在 Compute 层记录 layer key 与 TopK 的对应关系，重算后校验 Share 层读到的 source layer 是否与正向一致；开 full recompute 后对比关重算的 loss 曲线。；修复 issue 给出实现方案（参考 Megatron-LM 在 forward carrier 上存 dict[source_layer, topk_indices]，holder 绑定 packed_seq_params/attention mask，checkpoint 反向后恢复同一 holder 引用）；issue 已 closed，未在正文给出合入 PR 号（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1701
- **关联**：cross:INF-0648

### TRN-0332 `mindspeed_llm_lora_uniform_recompute_grad_norm_zero` LoRA 开 uniform 重计算后 grad norm 恒为 0

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：重计算/卸载 / mindspeed-llm / LoRA 与 uniform full 重计算
- **原因行为**：LoRA 目标层与 --recompute-method uniform 的整层重计算组合时，重算路径下 LoRA 参数拿不到梯度，wgrad 全零；报告只定位到重计算开关，未给出代码级根因。
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：qwen3-14b-64k LoRA、CP=8、full+uniform 重计算时 grad norm 恒 0.000、loss 停在 12.2 附近 2000 iter；去掉重计算参数即正常，裁到 10 层不加载权重同样复现。
- **改进措施**：检测 LoRA 训练看 grad norm 是否恒 0（而非仅看 loss 曲线）；或对比开/关重计算同名 LoRA 参数的 grad 范数。；修复 待定（issue 已 closed，正文未给出修复 PR；报告给出「关掉 recompute」的规避方式）
- **来源**：https://gitcode.com/Ascend/MindSpeed-LLM/issues/1437

### TRN-0337 `mindspeed_fsdp_adamw_swap_no_stream_sync` AdamWSwap 计算流与 D2H 流无同步致动量错

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：重计算/卸载 / mindspeed / swap_optimizer 流同步
- **原因行为**：swap_optimizer 在用 _fused_adamw_ 更新参数后立刻 swap_tensors_to_host，计算流与 D2H 通信流之间没有同步或 wait，通信流可能在计算完成前就把未更新的一二阶动量搬到 CPU。
- **影响对象**：优化器状态；训练轨迹（不可复现）
- **影响详情**：fsdp 后端用 AdamWSwap、关 shuffle 并开确定性计算时，同一配置多次运行精度结果不一致，且与 adamw 的结果有差；加流同步后多次运行与 adamw 完全一致，无报错。
- **改进措施**：检测 关 shuffle + 确定性计算下同一配置重复运行，比对最终 loss/权重；或把 swap 关掉与 adamw 对照。；修复 报告者验证加 torch.accelerator.synchronize() 或计算流 wait 后精度完全一致；issue 已 closed，正文未给出合入 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed/issues/210

### TRN-0489 `mindformers_pynative_skip_recompute_single_card` MindFormers PyNative 单卡跳过 activation c

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：重计算/卸载 / mindformers / PyNative activation che。
- **原因行为**：PyNative Trainer 单卡（data_parallel=1）时 activation checkpoint / full recompute 配置未生效——配置了重算但实际未启用，配置面与执行面分叉。
- **影响对象**：性能/资源（性能退化）
- **影响详情**：单卡训练开了 activation checkpoint 配置却按未开跑：显存占用高于预期、重算与否与配置不符；无报错，用户按显存预算排布时被误导。
- **改进措施**：检测 单卡下显存占用与开启重算的预期对比；检查重算节点是否生效；修复 修复 PR https://atomgit.com/mindspore/mindformers/merge_requests/8884（open，2026-10-27）——PyNative 单卡正确启用 activation checkpoint
- **来源**：https://atomgit.com/mindspore/mindformers/issues/2615；https://atomgit.com/mindspore/mindformers/merge_requests/8884

### TRN-0497 `megatron_dp_reshardable_resume_adam_step_reset` dp_reshardable 恢复后 Adam step 重置为 1

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：重计算/卸载 / megatron-lm / dp_reshardable 加载器
- **原因行为**：dp_reshardable 加载用 dummy_step 的 step=1 占位张量覆写已恢复的 step，且不同步 HDO 子优化器状态。
- **影响对象**：优化器状态（静默错误）
- **影响详情**：恢复后首个更新用 t=2 而非 trained_steps+1：默认 betas 下偏差校正错，50 步检查点恢复后下一更新约 1.7 倍过大，loss 尖几个步骤后回到原曲线；矩与权重本身恢复正确。GPU 轮审实测 step 63 恢复成 1。
- **改进措施**：检测 恢复后立即打印优化器 step（param_groups 与各 param state）与 trained_steps 对比；修复 待定（issue #8632 已 closed 2026-10-28，未见关联修复 PR；另一报告 #8622 open。建议对齐 fully_reshardable/fully_sharded_model_space 两加载器：丢弃 step 后再 _set_main_param_and_optimizer_states 并同步 HDO 状态）
- **来源**：https://github.com/NVIDIA/Megatron-LM/issues/8632；https://github.com/NVIDIA/Megatron-LM/issues/8622

## RL训练回路

### TRN-0011 `bf16_vs_fp16_rl_engine_mismatch` RL rollout 引擎与 trainer 精度不一致致 logprob 失配

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 NUM.02

- **原因对象**：RL训练回路 / 通用 / rollout 引擎与 trainer 数值精度
- **原因行为**：RL 的 rollout 引擎与 trainer 常一边用 BF16、一边用更激进的核，两侧对同一权重和序列的计算不一致；BF16 的大动态范围不保证两边算得一样。
- **影响对象**：输出分布；训练信号（静默错误）
- **影响详情**：同权重同序列的 token logprob 出现差值 δₜ，极端 token 的 |δₜ| 可达 O(1)，足以掀翻 GRPO 训练。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2510.26788；https://arxiv.org/abs/2605.14220

### TRN-0021 `bf16_reward_rounds_away_group_baseline` BF16 reward 在组统计前被舍入，GRPO 组基线被抹平

`故障` · `active` · `rl` · `verified` · `var` · 发现 2026-09-12 · 旧号 NUM.12

- **原因对象**：RL训练回路 / openrlhf / 组统计 reward dtype 继承
- **原因行为**：组 advantage 统计直接继承 reward dtype，BF16 reward model 输出在组中心化前已被舍入，组内差小于 BF16 ULP 时基线被舍入掉：[1,1,1,1.0078125] 得≈[0,0,0,2]。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：使用 BF16 reward model 时无 crash，组内小幅 reward 差被抹平，GRPO 组相对信号劣化为阶跃（全零或放大），PPO 梯度改变、细粒度偏好学习静默失效；integer reward 在组统计/分数惩罚下失败，FP16 常数组可产生 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/pull/1334
- **关联**：var:TRN-0011

### TRN-0059 `zero3_lazy_teacher_init_reads_partitioned_state` trl SDPO teacher 在 ZeRO-3 分片后初始化读空 shard

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-21 · 旧号 CKPT.10

- **原因对象**：RL训练回路 / trl / PEFTAdapterEMACallback
- **原因行为**：该回调在 on_train_begin() 才创建 SDPO teacher adapter，此时 student 已被 ZeRO-3 分片，get_peft_model_state_dict() 读到未 gather 的空分区。
- **影响对象**：模型权重；训练信号（静默错误）
- **影响详情**：teacher 与 EMA shadow 从空张量初始化（实测 28 个 adapter tensor numel()==0），训练照常、蒸馏目标从错误 anchor 出发；另一面：分片后插入的新参数脱离 ZeRO instrumentation，首个 forward 即崩。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6828

### TRN-0065 `async_rollout_buffer_state_lost_on_resume` 异步 RL resume 丢在途 rollout，prompt 被跳过或重复

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-06 · 旧号 CKPT.16

- **原因对象**：RL训练回路 / openrlhf / 异步 rollout 缓冲与 resume 契约
- **原因行为**：resume 只存 dataloader/模型/优化器、不存在途 rollout：OpenRLHF 的 rollout 缓冲不入 ckpt 且 loader 耗尽后被误清；verl 异步 trainer 恢复时无条件补交 warmup 批。
- **影响对象**：训练样本流；可用性/进度（静默错误）
- **影响详情**：ckpt 与指标正常、run 继续，但已生成未训练的 rollout 永久丢失，prompt 被跳过或重复，生成批边界结束的 episode 整段重放甚至无限循环；verl 相对未抢占 run 静默跳过 prompt 并超填 in-flight 窗口。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/issues/1322；https://github.com/OpenRLHF/OpenRLHF/pull/1323；https://github.com/OpenRLHF/OpenRLHF/issues/1320；https://github.com/OpenRLHF/OpenRLHF/pull/1321；https://github.com/verl-project/verl/issues/7759；https://github.com/verl-project/verl/pull/7762
- **关联**：var:TRN-0057

### TRN-0092 `secondary_eos_mask_misclassifies_terminated` GRPOTrainer 只认主 EOS id，多 EOS 模型边界错判

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-04 · 旧号 DATA.10

- **原因对象**：RL训练回路 / trl / GRPOTrainer EOS 边界判定
- **原因行为**：GRPOTrainer 判定 completion 边界只认 tokenizer.eos_token_id 单值，忽略 generation_config 里的次级 EOS id，EOS mask、截断率指标等四个消费点均错位。
- **影响对象**：训练样本流；训练信号；指标/日志（静默错误）
- **影响详情**：多 EOS 模型（Phi-3.5、Gemma-3、Qwen3）以次级 EOS 结束时：终止后 token 留在 loss；正常终止被记为截断（clipped_ratio≈0.97）；开 mask_truncated_completions 时几乎全部样本被掩掉，RL 零学习信号且无报错。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/7039
- **关联**：var:TRN-0178

### TRN-0093 `minillm_advantage_mask_checks_wrong_tensor` MiniLLM 掩码查错张量，advantage 被 padding 污染

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-06 · 旧号 DATA.11

- **原因对象**：RL训练回路 / trl / MiniLLM advantage 计算
- **原因行为**：completion mask 判 input_ids!=-100，而 -100 写在 labels，mask 恒全 1；长度归一化把掩位填 1e-4 混入分母；gamma 折扣按绝对位置而非 i−t 索引。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：无crash：pad位reward被折进advantage，大小随batch padding量变化（reward=1.0、γ=1.0时单token pad到512得0.9514而非1.0），更新方向随batch组成漂移；gamma缺陷使后段token被指数级压制，或下溢致NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/7044；https://github.com/huggingface/trl/issues/6626；https://github.com/huggingface/trl/issues/7295
- **关联**：var:TRN-0085

### TRN-0152 `train_infer_router_desync` MoE RL 中训练重算与 rollout 的 router 决策不一致

`故障` · `active` · `pretrain；rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 MOE.03

- **原因对象**：RL训练回路 / 通用 / 训练重算与 rollout 的路由决策
- **原因行为**：训练 mini-step 重算时的 router 决策（top-k、jitter）与 rollout 时不一致，同一权重在训练侧与推理侧走不同的专家组合。
- **影响对象**：训练轨迹；输出分布（质量退化）
- **影响详情**：同权重的 MoE 在 RL 中等效于另一张稀疏图，reward 先升后塌。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2510.11370；https://arxiv.org/abs/2610.21682

### TRN-0159 `colocate_reload_swallows_post_load_processing` ms-swift 重载吞掉 vLLM 后处理异常，rollout 用未处理权重

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-13 · 旧号 MOE.10

- **原因对象**：RL训练回路 / ms-swift / vLLM 权重重载的宽 except 处理
- **原因行为**：finish_vllm_weight_reload 用裸 except 包住 vLLM 权重后处理；Megatron colocate 路径传入 int 型 CUDA ordinal 而非 torch.device，后处理抛异常即被吞掉。
- **影响对象**：模型权重；输出分布（静默错误）
- **影响详情**：无 crash、无日志，训练照常推进；Megatron colocate 路径每次 weight reload 后，rollout 引擎在未做 packing、MoE fusion、量化 prep 的权重上采样，生成分布静默偏离训练策略。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10098
- **关联**：var:TRN-0156

### TRN-0177 `bypass_mode_token_mean_divides_by_prerejection_count` verl 拒采 bypass 模式 token-mean 分母用拒采前计数

`故障` · `active` · `rl` · `verified` · `var` · 发现 2026-10-10 · 旧号 LOSS.13

- **原因对象**：RL训练回路 / verl / rollout_rs bypass 分母计数
- **原因行为**：bypass 模式逐 micro-batch mask 被拒 token，但 batch_num_tokens 在拒采前已算好，token-mean 下 loss 为 kept token loss 和除以拒采前 token 数。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：rollout_rs bypass + loss_agg_mode=token-mean 时 loss 与梯度按 kept 比例缩小（各 keep 7/8 时 0.3199 vs 正确 0.3656），有效学习率随拒绝率动态缩水，无任何指标可见；decoupled 模式不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/8176
- **关联**：var:TRN-0173

### TRN-0182 `left_pad_scoring_uses_arange_positions` trl 左 pad 打分不传 position_ids，与采样位置分歧

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-08-20 · 旧号 SFT.05

- **原因对象**：RL训练回路 / trl / 打分路径 position_ids 缺失
- **原因行为**：左 pad batch 打分 logprob 时不传 position_ids，模型回落 torch.arange，pad 行位置整体平移；而 generate() 由 mask 推位置，采样与打分用两套位置。
- **影响对象**：输出分布；训练信号（静默错误）
- **影响详情**：对 RoPE 模型无影响；对 ALiBi、学习式/绝对位置编码模型，左 pad 行 logprob 全错且偏移随 pad 宽度增长（gpt2 实测 max|Δlogp|=11.7）。OnlineDPO/XPO/Nash-MD 受影响、PPO 正确；无 crash、无 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6800

### TRN-0194 `format_reward_hacking` 格式奖励权重过大，策略专刷格式分

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-RWD.01

- **原因对象**：RL训练回路 / 通用 / 格式奖励与正确性奖励权重
- **原因行为**：奖励设计中格式分（XML 标签、think 块）的权重大于正确性分。
- **影响对象**：训练信号；训练轨迹（质量退化）
- **影响详情**：策略专门优化格式：格式分趋于 1、任务分趋于 0，总 reward 看起来在上涨。常见于 RLVR / R1 复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：RLVR / R1 复现中的常规失败；

### TRN-0195 `length_reward_explosion` GRPO序列级平均致更长错误回答惩罚不足、回复冲顶max_tokens

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-RWD.02

- **原因对象**：RL训练回路 / 通用 / GRPO 序列级 loss 归一化
- **原因行为**：GRPO 的序列级平均让更长的错误回答受到的惩罚不足。
- **影响对象**：训练信号；训练轨迹（质量退化）
- **影响详情**：策略把回复拉到 max_tokens 并重复，平均长度冲顶，下游分数掉到 0；无 NaN。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2503.20783

### TRN-0196 `reward_model_overoptimization` 策略过度优化奖励模型的虚假特征

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-RWD.03

- **原因对象**：RL训练回路 / 通用 / 奖励模型 / rubric judge
- **原因行为**：奖励模型（或 rubric judge）含有虚假特征、与真实目标不一致，策略过拟合这些特征。
- **影响对象**：训练信号；训练轨迹（质量退化）
- **影响详情**：代理奖励（RM/训练 judge 分）单调上升，人类/黄金评测变差或先峰后降；Rubric Dropout 实测 GRPO+rubric judge 下 HealthBench-Hard −3、ResearchQA −22。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2608.11669

### TRN-0197 `tool_schema_constraints_silently_weakened` verl 工具 schema 序列化静默丢弃 JSON Schema 约束

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-22 · 旧号 RL-RWD.04

- **原因对象**：RL训练回路 / verl / 工具 schema Pydantic 载体
- **原因行为**：OpenAIFunctionToolSchema 的 Pydantic 载体只声明少数键，model_dump() 把 minimum/maximum/additionalProperties 等未声明键整键丢弃。
- **影响对象**：输入编码（静默错误）
- **影响详情**：工具调用仍正常解析执行、训练无异常，但渲染进 prompt 的工具契约被削弱（如 limit≤128、offset≥0 约束消失）；@function_tool(schema=...) 同样丢失。reward 只认调用成功时越界参数可成得分路径（推断）。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7505；https://github.com/verl-project/verl/pull/7766

### TRN-0198 `prefilled_tag_reward_dead_zone` 模板预填 <think> 使 think_format_reward 恒为 0

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-29 · 旧号 RL-RWD.05

- **原因对象**：RL训练回路 / trl / think_format_reward 锚定正则
- **原因行为**：模板在 generation prompt 末尾预填 <think>，GRPO 送 reward 的 completion 只含生成 token，而 think_format_reward 的锚定正则要求以 <think> 开头。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：使用预填模板（如 DeepSeek-R1-Distill）时该 reward 通道全程为 0.0，无报错无警告；若组内其他 reward 也无区分则 advantage 全 0。reward 恒 0 易被误读为模型没学会格式。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6966

### TRN-0199 `reward_tokenizer_vocab_mismatch_silent_scores` trl XPO/NashMD 把策略 token id 直接喂给 RM 打分

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-30 · 旧号 RL-RWD.06

- **原因对象**：RL训练回路 / trl / XPO/NashMD get_reward 输入
- **原因行为**：XPO/NashMD 的 get_reward() 把策略 token id 直接送入 RM，不做 re-tokenize；XPO 不用 reward_processing_classes，NashMD 硬编码策略 tokenizer。
- **影响对象**：训练信号；输入编码（静默错误）
- **影响详情**：RM 词表更小时则 embedding IndexError；同词表时即落入静默面，RM 对错位 token 打分，reward 量级正常但语义无效，reward 曲线照样能涨。Llama RM + Qwen policy 命中；同 model id 的 CI 测试不可见。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/6952；https://github.com/huggingface/trl/pull/6955；https://github.com/huggingface/trl/issues/6951

### TRN-0200 `verifier_error_group_correlation_sign_flip` GRPO 组内 verifier 误差相关致 advantage 符号翻转

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-10 · 旧号 RL-RWD.07

- **原因对象**：RL训练回路 / 通用 / GRPO 组相对 advantage 估计器
- **原因行为**：组相对 advantage 把同一 verifier 对组内 completion 的打分当独立测量做中心化，而组内 verifier 错误相关（ρ=0.530），8 样本组有效样本量仅 1.70
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：无 crash、无 NaN，reward 与训练指标正常；四种 rule-based verifier 重放下 0.83% 的组至少一条 advantage 符号翻转，策略被推向 verifier 错判方向，多采样去噪效率比名义低约 4.7 倍
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2609.06386

### TRN-0201 `unscored_rollout_defaults_to_zero_reward` trl OpenReward 未打分 rollout 与真实 0 分同值

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-24 · 旧号 RL-RWD.08

- **原因对象**：RL训练回路 / trl / OpenReward env.reward 默认值
- **原因行为**：environment.py 把 self.reward 初始化为 0.0，仅在打分工具返回非 null 时覆写，默认 reward 函数无条件返回 env.reward，未打分哨兵与合法 0 分坍缩成同一值
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：放弃、撞 max_tool_calling_iterations 或工具调用全抛异常的 rollout 被当真实 0 分参与 advantage，unscorable_mask 剔除失效，产生方向性梯度偏置，无 crash；PR #7467 合并后自定义 reward 函数仍受影响
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7364；https://github.com/huggingface/trl/pull/6430；https://github.com/huggingface/trl/pull/7371；https://github.com/huggingface/trl/pull/7467；https://github.com/huggingface/trl/pull/7541

### TRN-0202 `math_verifier_symmetric_unit_erasure` OpenRLHF 数学 grader 对称擦除单位，单位错判为正确

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-25 · 旧号 RL-RWD.09

- **原因对象**：RL训练回路 / openrlhf / grade_answer 的 _normalize
- **原因行为**：_normalize 对 gold 与 prediction 各自独立执行同一单位擦除 re.sub 循环，再比较擦除后的字符串，从不检查两侧单位是否一致（继承自 prm800k grader）
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：无 crash；5 hours 对 5 minutes、10 meters 对 10 miles 等均判 1.0，数值对单位错的样本获得与正样本同量级的正 advantage，单位正确性维度零梯度；shipped 示例 reward 脚本可达
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/issues/1364

### TRN-0203 `grpo_group_std_zero` GRPO 组内奖励全相同致 std 为 0 而除零或零信号

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-ADV.01

- **原因对象**：RL训练回路 / 通用 / GRPO advantage 组内 std 归一
- **原因行为**：一组 rollout 奖励全相同（全对或全错）时组标准差为 0，实现直接相除，或悄悄跳过该组却仍占 batch
- **影响对象**：训练信号；训练轨迹（数值异常）
- **影响详情**：直接相除时出现 Inf/NaN，一步毒化训练；跳过时该 prompt 零学习信号，表现为在训但学不到难题
- **改进措施**：检测 待定；修复 待定
- **来源**：https://huggingface.co/docs/trl/en/grpo_trainer

### TRN-0204 `grpo_std_difficulty_bias` GRPO 用组内 std 归一放大低方差题 advantage

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-ADV.02

- **原因对象**：RL训练回路 / 通用 / GRPO advantage 组内 std 归一
- **原因行为**：用组内标准差除 advantage，低方差题（几乎全对或全错）的 advantage 被放大
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：模型在已经会的题上步子过大，难题信号被压制
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2503.20783

### TRN-0206 `drop_group_ignores_nonbinary_std` OpenRLHF 动态过滤只判全 0/1，近零 std 组漏过

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-17 · 旧号 RL-ADV.04

- **原因对象**：RL训练回路 / openrlhf / dynamic filtering 无对比组判定
- **原因行为**：动态过滤「无对比」组时只检查奖励是否全 0 或全 1，未看标准差，非二值奖励下 std≈0 的组不会被丢弃
- **影响对象**：训练信号（静默错误）
- **影响详情**：软奖励任务里几乎同分的组仍进入更新，带来噪声 advantage
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/issues/1270
- **关联**：var:TRN-0203

### TRN-0207 `flat_group_zero_learning_signal` 零对比组无学习信号，OpenRLHF 过滤可清空整批经验

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-17 · 旧号 RL-ADV.05

- **原因对象**：RL训练回路 / openrlhf / 零对比组及 _generate_vllm 过滤
- **原因行为**：全对/全错组对 GRPO 是零对比；dynamic filtering 在 prompt loader 耗尽后拒绝一组时，_generate_vllm() 返回空列表，丢弃已累积的 accepted_experiences
- **影响对象**：训练样本流；可用性/进度（静默错误）
- **影响详情**：有效 batch 远小于名义 batch、进度虚标；小数据集上开启过滤的 shipped DAPO/REINFORCE recipe 可能清空唯一生成 batch，0 次 optimizer update 而 run 仍正常走完
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/issues/1310
- **关联**：var:TRN-0203

### TRN-0208 `replay_buffer_shape_contract_degenerates` trl GRPO replay buffer 形状契约错配致内容错位

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-23 · 旧号 RL-ADV.06

- **原因对象**：RL训练回路 / trl / GRPOWithReplayBuffer 形状契约
- **原因行为**：调用路径传 1-D (B,) 张量，update_with_replay_buffer 假设 (num_groups, num_generations) 2-D，组筛选与优先级退化成整批标量
- **影响对象**：训练信号；训练样本流（静默错误）
- **影响详情**：每批只有组 0 进 buffer，存单样本 advantage 冒充整组；替换仅在整批零方差时触发，其余行沿用他人 advantage；run 无报错继续训练，单测用手搓 2-D 张量故 CI 全绿
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6804

### TRN-0209 `singleton_group_vectorized_zero_path` verl rloo_vectorized 将单样本组 advantage 清零

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-30 · 旧号 RL-ADV.07

- **原因对象**：RL训练回路 / verl / rloo_vectorized 单样本组掩码
- **原因行为**：向量化版用 loo * (c > 1) 把单样本组行乘成 0，而标量版 if response_num > 1 让其保留原始分数；等价测试断言每组 ≥2 样本，恰好绕开该情形
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：rollout.n=1 时 advantage 全零，RLOO run 无报错、无 NaN、指标齐全但永远不学习；过滤后只剩一条的 ragged 组中，幸存样本同样拿不到梯度
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7581；https://github.com/verl-project/verl/issues/7793
- **关联**：var:TRN-0203

### TRN-0210 `guess_path_spurious_advantage` GRPO 结果 advantage 无法区分猜中与推理而强化猜测

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 RL-ADV.08

- **原因对象**：RL训练回路 / 通用 / GRPO 组内 outcome advantage
- **原因行为**：组内 advantage 只看 outcome reward 统计，靠猜命中与靠推理命中正确答案的 rollout 拿到相同高 advantage，正确信号混入与能力无关的猜测分量
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：reward 曲线上涨、benchmark 分数可能也涨，但策略能力构成漂移、guess-like 行为被强化；见于 bounded-answer 小候选集、open-answer 的 bounded 子题与搜索 agent 多路径撞对
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2609.04063

### TRN-0211 `filter_metric_predicate_mismatch_phantom_advantage` GRPO 动态采样按 shaped 分过滤放行全失败组致伪优势

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-16 · 旧号 RL-ADV.09

- **原因对象**：RL训练回路 / verl / 动态采样 filter metric 谓词
- **原因行为**：动态采样的 filter metric 可配置为 shaped 训练分；复合 shaped reward 下全失败组内仍有非零离差而被判“有对比”放行，std 归一化把 shaping 差异提升为满幅 advantage。
- **影响对象**：训练信号；训练轨迹（质量退化）
- **影响详情**：无 crash、指标看似正常推进，策略在全错解组上学习格式/过程分差异；同预算终值 EM 0.160，而按 accuracy 过滤为 0.763；filter refill 次数（0 vs 29/40 步）是唯一可观测异常。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2609.13866

### TRN-0212 `pfppo_v1_resampled_advantage_trajectory_mispair` verl v1 PF-PPO 重采样后 advantage 写回与轨迹错配

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 RL-ADV.10

- **原因对象**：RL训练回路 / verl / v1 _compute_advantage 写回
- **原因行为**：PF-PPO 有放回重采样整批后，v1 _compute_advantage 从 TransferQueue 取原始行序的 response_mask，再把重采样后的 advantages/returns 按原键写回，原轨迹仍留原位
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：use_pf_ppo=true 且走 GAE 路径时无异常，策略梯度把 credit assignment 赋给错误轨迹；来源仅有 CPU 复现，未提供长程训练回报或任务指标实测
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7956

### TRN-0213 `vectorized_grpo_intermediate_rewards_pollute_group_stats` verl grpo_vectorized 中间输出重复 reward 污染组统计

`故障` · `active` · `rl` · `verified` · `var` · 发现 2026-10-10 · 旧号 RL-ADV.11

- **原因对象**：RL训练回路 / verl / grpo_vectorized 估计器分组
- **原因行为**：grpo_vectorized 跳过 session-aware 路径，多输出 session 的 reward 被复制到每个中间输出后进组统计，同一 session 在均值/标准差中被计 n 次，advantage 按中间输出计算
- **影响对象**：训练信号（静默错误）
- **影响详情**：无 crash；多轮 agent session 中长 session 的 reward 被超权，中间与最终输出的 advantage 错配甚至翻号（实例 −0.104→+0.320）
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/8100
- **关联**：var:TRN-0209

### TRN-0215 `reverse_kl_as_loss_wrong_is_weight` OpenRLHF reverse-KL 损失的梯度与 IS 权重写错

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-KL.02

- **原因对象**：RL训练回路 / openrlhf / reverse-KL 损失及 IS 权重
- **原因行为**：把 reverse-KL 当损失时，梯度形式和 off-policy 重要性权重写错，更新指向错误的散度
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：KL 项在下降但策略并不靠近参照策略，或反过来
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/pull/1309

### TRN-0216 `entropy_collapse_to_repetition` RL 策略熵塌缩致解码陷入重复循环

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-KL.03

- **原因对象**：RL训练回路 / 通用 / RL 训练的策略熵动力学
- **原因行为**：RL 训练中策略熵塌缩（原文未给出具体实现缺陷）
- **影响对象**：输出内容；训练轨迹（质量退化）
- **影响详情**：解码陷入重复循环、文本不可用，而 reward 或格式分仍高；常与长度爆炸一起出现
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：GRPO 失败复盘（Interconnects / R1-zero-like）。

### TRN-0218 `entropy_bonus_unscaled_logits_temperature_split` OpenRLHF entropy bonus 用未除温度的 logits 计算

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-06 · 旧号 RL-KL.05

- **原因对象**：RL训练回路 / openrlhf / Actor.forward 熵计算时序
- **原因行为**：compute_entropy 在 logits 原地除以 rollout.temperature 之前调用，entropy 基于 softmax(logits)，而训练策略与 vLLM 采样器基于 softmax(logits/T)
- **影响对象**：训练信号；指标/日志（静默错误）
- **影响详情**：无 crash；T≠1 时 entropy 项系统性错值（T=0.5 每 token 偏差达 1.03 nats），T<1 高估、T>1 低估，探索/坍缩平衡调不对，entropy_loss 曲线也在报错值
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/pull/1319

### TRN-0219 `kl_estimator_choice_varies_by_trainer` trl RLOOTrainer 仍用高方差 k1 KL 估计器

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-07 · 旧号 RL-KL.06

- **原因对象**：RL训练回路 / trl / RLOOTrainer KL 估计器
- **原因行为**：trl RLOOTrainer 仍用高方差的 k1 式 KL 估计，而 GRPOTrainer 用低方差 k3 近似（PPOTrainer 已在 PR #3240 切换）；同一仓库、同一 KL 语义下估计器选择未对齐。
- **影响对象**：训练信号（静默错误）
- **影响详情**：RLOO 的 KL 信号噪声更大，KL 惩罚实际强度时紧时松；跨 trainer 比较 KL 系数时会把估计器差异误当成算法/任务差异；无 crash，数值有限。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7086
- **关联**：var:TRN-0255

### TRN-0220 `k3_clip_saturates_but_gradient_nans` OpenRLHF k3 KL 先 exp 后 clamp 致反向 NaN 梯度

`故障` · `active` · `rl` · `verified` · `NEW` · 发现 2026-09-12 · 旧号 RL-KL.07

- **原因对象**：RL训练回路 / openrlhf / k3 KL 估计器 clamp 位置
- **原因行为**：k3 KL 估计器在 exp 之后才对输出 clamp：极端 log-prob 差经 exp 变 inf，返回值被拉回有限，但 autograd 图中 exp 留下 0×inf 型 NaN 梯度
- **影响对象**：梯度；模型权重（数值异常）
- **影响详情**：无 crash、KL 指标正常有限，但 grad_norm 突然 NaN，一次 KL 正则更新即污染参数；off-policy 漂移或 rollout-train 失配大、log-prob 差极端时更易触发
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/pull/1335

### TRN-0221 `sequence_mean_is_weight_broadcast_to_token_kl` trl 序列级 IS 权重广播到 token 级 KL 产生伪梯度

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-16 · 旧号 RL-KL.08

- **原因对象**：RL训练回路 / trl / GRPOTrainer KL 偏置校正权重
- **原因行为**：KL 偏置校正用 exp(log_importance_weights) 乘 per-token KL；sequence 级 IS 下该权重是序列均值 (B,1)，广播到 (B,T) 后梯度多出伪项
- **影响对象**：梯度；训练轨迹（静默错误）
- **影响详情**：无 crash、loss 正常下降，但每个 token 的 KL 惩罚梯度带全序列聚合的伪分量，KL 约束方向系统性偏移；该开关默认开启，sequence 级 IS 配置下默认即中招
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/6594；https://github.com/huggingface/trl/issues/6586；https://arxiv.org/abs/2608.02786

### TRN-0222 `fp8_noise_clips_negative_tokens_out_of_trust_region` 全管线 FP8 噪声使负 advantage token 被 clip 屏蔽

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-23 · 旧号 RL-KL.09

- **原因对象**：RL训练回路 / 通用 / 全管线 FP8 下的 ratio clip
- **原因行为**：训练侧与 rollout 侧 FP8 量化噪声逐级复合进 importance ratio，使其系统性偏移，负 advantage token 被不成比例地推出 trust region，梯度被错误归零
- **影响对象**：训练信号；梯度；训练轨迹（质量退化）
- **影响详情**：无 crash、无 NaN；训练中期 entropy 涌现式激增并输出乱码，病态输出得不到惩罚且随训练累积；BF16 rollout + FP8 trainer 无此不稳定
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2609.22870

### TRN-0223 `tim_rollout_trainer_logprob_delta` rollout 与 trainer 对同一序列 logprob 不一致（TIM）

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-RO.01

- **原因对象**：RL训练回路 / 通用 / rollout 与 trainer 概率失配
- **原因行为**：rollout 引擎（vLLM/SGLang）与 trainer（FSDP/Megatron）因核实现不同和非 batch-invariant 归约，对同一权重同一序列给出不同 token 概率
- **影响对象**：输出分布；训练轨迹（质量退化）
- **影响详情**：δ=log π_train−log π_rollout 均值小、极值可达约 1.0，甚至 argmax 翻转；REINFORCE 下仅 TIM 就使 MoE 验证奖励从 0.29 掉到 0.07，零错配的 VeXact 升到 0.53
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2605.14220；https://arxiv.org/abs/2604.07853；https://arxiv.org/abs/2606.29526；https://arxiv.org/abs/2602.01826；https://arxiv.org/abs/2606.09821；https://arxiv.org/abs/2601.18150；https://arxiv.org/abs/2512.23087；https://arxiv.org/abs/2511.17826；https://arxiv.org/abs/2607.15810；https://arxiv.org/abs/2609.22870；https://arxiv.org/abs/2609.20807；https://arxiv.org/abs/2609.32444

### TRN-0224 `recompute_vs_bypass_objective_skew` π_old 取 recompute 或 bypass 都会扭曲优化目标

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-RO.02

- **原因对象**：RL训练回路 / 通用 / π_old 取法 recompute/bypass
- **原因行为**：recompute 以 trainer 重算值作分母，使优势加权的零中心贡献对正负样本不对称扭曲；bypass 以 rollout 作分母，但分子与 ∇logπ 仍在 trainer 数值景观上
- **影响对象**：训练信号；训练轨迹（质量退化）
- **影响详情**：recompute 可把奖励塌到近 0；bypass 奖励掉到约 0.4，且不一定伴随 loss 尖峰，更新到 rollout 侧不兑现；PPO clip 盖不住
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2605.14220

### TRN-0225 `seq_mask_tis_skips_token_clamp` OpenRLHF seq-mask-tis 不 clamp 致梯度溢出

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-RO.03

- **原因对象**：RL训练回路 / openrlhf / seq-mask-tis 系数计算
- **原因行为**：注释称序列几何平均只做过滤、系数仍走 token TIS，实现却对 exp(rollout_log_ratio) 不做 clamp，极端 off-policy 下 exp 溢出
- **影响对象**：梯度（数值异常）
- **影响详情**：中等比值已偏离文档语义；极端时接受序列得 inf 梯度、拒绝序列得 0*inf=NaN，单条陈旧序列毒化整步 PPO；opt-in 但一开就中招
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/issues/1295

### TRN-0226 `gspo_ratio_exponent_overflow` OpenRLHF GSPO 序列级比值指数溢出

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-17 · 旧号 RL-RO.04

- **原因对象**：RL训练回路 / openrlhf / GSPO 序列级重要性比
- **原因行为**：GSPO 序列级重要性比把对数比乘长度再 exp，未对指数设界
- **影响对象**：梯度（数值异常）
- **影响详情**：长回复一步即出现 inf/NaN 非有限梯度；与 #1295 相邻但位于另一条分支
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/OpenRLHF/OpenRLHF/pull/1293
- **关联**：var:TRN-0225

### TRN-0227 `moe_router_not_replayed` MoE RL 未回放 rollout 路由，verl 回放配置键失效

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-17 · 旧号 RL-RO.05

- **原因对象**：RL训练回路 / verl / MoE 路由回放配置
- **原因行为**：训练侧未回放 rollout 的 MoE 路由，top-k 专家集合可与推理侧不一致，IS 校正的是错误计算图；verl 文档所教的 actor.router_replay.mode 为死键，引擎不读。
- **影响对象**：训练信号；训练轨迹（质量退化）
- **影响详情**：MoE RL 比 dense 更早崩塌；按官方 Ascend 文档配置时 routing replay 静默为 disabled，无报错，大 MoE 的 train/infer 路由不一致无人拦截。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2510.11370；https://github.com/verl-project/verl/issues/7463；https://github.com/verl-project/verl/pull/7805
- **关联**：var:TRN-0152

### TRN-0228 `untruncated_is_heavy_tail` 重要性权重未截断，训推错配的重尾变成重尾比率

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-RO.06

- **原因对象**：RL训练回路 / 通用 / 重要性采样权重截断
- **原因行为**：重要性权重未做截断，训推错配（TIM）的重尾 δₜ 直接变成重尾的重要性比率。
- **影响对象**：训练信号；梯度（质量退化）
- **影响详情**：偶发巨大梯度；改用 TIS + 基于 r_corr 的序列拒绝虽可贴近零错配基线，但会有大量样本被拒，有效数据远小于名义 batch。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2605.14220

### TRN-0229 `nucleus_truncation_is_bias` 截断采样 logprob 口径不一致致 IS ratio 偏置

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-19 · 旧号 RL-RO.07

- **原因对象**：RL训练回路 / trl / rollout/trainer logprob
- **原因行为**：top_p/top_k/min_p 截断采样时 vLLM 返回截断后重归一化分布的 logprob，trainer 重算全词表 log-softmax，温度对称处理而截断没有；AsyncGRPO 还直接拿它作 old_log_probs。
- **影响对象**：训练信号（静默错误）
- **影响详情**：无 NaN、无 clip 迹象，IS ratio 带逐 token 恒负偏置，off-policy 校正系统性失真；AsyncGRPO 中策略未动时 coef_1 即等于幸存质量（top_p=0.7→0.7），负优势 token 的 clip 每步误触发。
- **改进措施**：检测 待定；修复 AsyncGRPO 修复方向（PR #7627，open 未 merge）：trainer 侧按与 sampler 相同的 top-k/top-p 候选集重归一化 log-probs（vLLM --return-sampling-mask 返回候选集，keep-sampling-mask 策略，DeepSeek-V3.2/prime-rl 同路线）。https://github.com/huggingface/trl/pull/7627
- **来源**：https://github.com/huggingface/trl/issues/6789；https://github.com/huggingface/trl/issues/6945；https://github.com/huggingface/trl/pull/7627；https://github.com/huggingface/trl/issues/7865

### TRN-0230 `adapter_omitted_from_weight_sync` verl 异步 RL 的 LoRA adapter 从不进入权重同步

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-21 · 旧号 RL-RO.08

- **原因对象**：RL训练回路 / verl / checkpoint_engine 权重同步
- **原因行为**：checkpoint_engine 后端非 naive 且 LoRA merge=False（默认）时，每次权重同步推送的都是冻结的 base model，训练中的 LoRA adapter 从不传输。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：所有 async RL recipe 均受影响：rollout 整个 run 从初始策略采样，RL 循环被静默切断，错配随训练单调增长；loss 降、reward 动、grad_norm/entropy/ESS 看似合理且无警告。colocated（backend: naive）路径正常。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7495
- **关联**：var:TRN-0227

### TRN-0231 `fused_expert_view_frozen_at_capture` Megatron colocated RL 生成引擎使用捕获时冻结的陈旧专家权重

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-30 · 旧号 RL-RO.09

- **原因对象**：RL训练回路 / megatron-lm / colocated RL 专家 fused 张量
- **原因行为**：serving 侧在捕获时另行 fuse 了一份 expert 张量，distributed optimizer 只更新自身参数 buffer，这份独立张量的值冻结在捕获时刻，不随优化器写回刷新。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：colocated RL 的生成引擎一直用陈旧专家权重采样，训练侧却在更新当前策略：rollout 与 train 权重静默脱钩，RL 循环被切断，mismatch 随训练增长，无任何警告。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/NVIDIA/Megatron-LM/pull/6963
- **关联**：var:TRN-0230

### TRN-0232 `zero3_layout_mutation_not_persisted` DeepSpeed Hybrid Engine 的 QKV 布局互转未持久化

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-03 · 旧号 RL-RO.10

- **原因对象**：RL训练回路 / deepspeed / Hybrid Engine QKV 布局互转
- **原因行为**：Hybrid Engine 在 GatheredParameters 内就地改写 QKV 布局却未指定 modifier_rank，ZeRO-3 repartition 时修改不被持久化，交错 QKV 被推理层按连续布局解读。
- **影响对象**：模型权重；输出分布（静默错误）
- **影响详情**：rollout 用布局损坏的权重采样，训练侧重算的 logprob 与真实采样分布脱节，无 crash、无警告，易被误判为 RL 训坏；Pythia-410M + ZeRO-3 复现中 QKV max_abs=20.5625，首个不匹配在 layer-0 attention。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8391；https://github.com/deepspeedai/DeepSpeed/pull/8392；https://github.com/verl-project/verl/pull/7986
- **关联**：var:TRN-0230

### TRN-0233 `decode_reencode_drifts_trajectory` rollout 的 decode/re-encode 使训练序列偏离采样

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-04 · 旧号 RL-RO.11

- **原因对象**：RL训练回路 / ms-swift / rollout decode/re-encode
- **原因行为**：多步 rollout 把引擎采样的 assistant token ids decode 成文本，构造后续历史或训练输入时再 re-encode；tokenization 非双射，round-trip 后的 token 序列不等于采样序列。
- **影响对象**：输入编码；训练信号（静默错误）
- **影响详情**：无 crash、无 NaN；logprob/IS ratio 带结构性偏置，策略按自己未产生过的序列更新，轨迹越长、工具轮次越多偏差越大，off-policy 校正补不齐；漂移点含特殊 token 拼接、空格归并、工具观察插入、多模态 chunk 重建。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/pull/10012
- **关联**：var:TRN-0223

### TRN-0234 `stale_completion_rolls_into_next_weight_version` verl Mooncake 权重同步复用 buffer，接收端读到上一版本张量

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-06 · 旧号 RL-RO.12

- **原因对象**：RL训练回路 / verl / Mooncake 权重同步 slot 回收
- **原因行为**：send_weights() 只消费最后一个 bucket 的 slot，转发 rank 的下游 slot 从不消费、barrier 也不清 marker，跨版本复用 buffer 时旧 marker 在接收者读完前释放它。
- **影响对象**：模型权重；训练信号（静默错误）
- **影响详情**：传输 READ/WRITE 全部返回 success，接收 rank 却读到上一版本张量（复现中应为 2.0、实读 2.125）；rollout 用部分陈旧权重采样，与正在训练的策略静默错位，TIM/IS 校正失准。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/pull/7764
- **关联**：var:TRN-0230

### TRN-0236 `rollout_context_compression_conditions_diverged_history` rollout 中上下文压缩使训练条件历史与生成时不一致

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-07 · 旧号 RL-RO.14

- **原因对象**：RL训练回路 / 通用 / 压缩上下文 rollout 的训练线性化
- **原因行为**：agent harness 在 rollout 中压缩上下文（evict 旧轮次）使训练对象成为树，现有线性化不保真：保留最右路径导致 time-travel leakage，depth-first 重放与生成时条件序不一致。
- **影响对象**：训练样本流；训练轨迹（质量退化）
- **影响详情**：无 crash；agent RL 在训练条件不等于生成条件上更新，策略被优化去利用训练侧虚构的完整历史，部署侧（真实压缩）行为漂移；eviction 密度越高的长程 agent 任务偏差越大，与数值 TIM 叠加后更难归因。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2609.00865
- **关联**：var:TRN-0233

### TRN-0239 `vllm_encoder_cache_survives_weight_sync` trl 权重同步后未清 vLLM 多模态 encoder 缓存

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-14 · 旧号 RL-RO.17

- **原因对象**：RL训练回路 / trl / sync_weights 缓存重置
- **原因行为**：sync_weights 权重同步后只调 reset_prefix_cache() 清 KV 前缀缓存，未清 vLLM 对 vision encoder 输出（image embedding）的 per-image 缓存。
- **影响对象**：输出分布；隐状态（静默错误）
- **影响详情**：训练含 vision encoder 的多模态 RL 中，同一图像复现时命中旧权重算出的视觉 embedding，rollout 分布落后训练策略，IS/KL 在视觉条件上系统性失准，误差随同步周期与图像复现率增长；扰动 encoder 权重后 logprob 不变可复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7198

### TRN-0240 `vllm_sleep_resume_corrupts_rollout_weights` vLLM sleep/resume 周期损坏 verl rollout 权重

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-18 · 旧号 RL-RO.18

- **原因对象**：RL训练回路 / verl / vLLM sleep/resume 周期
- **原因行为**：colocated 模式默认 free_cache_engine=true，每次 weight sync 前后对 vLLM 执行 sleep(level=1)/resume，resume 重建的权重与刚同步的权重不一致；具体根因原文未定位。
- **影响对象**：模型权重；输出内容；训练信号（质量退化）
- **影响详情**：verl 0.8.0/vllm 0.28.0 从第二次 update_weights 起 rollout 输出变成多语言乱码，reward 与 advantage 全零且无报错，外观像 reward collapse；关闭 free_cache_engine 后 0 损坏。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7904

### TRN-0241 `weight_sync_ack_precedes_tp_barrier_buffer_reuse` ms-swift IPC 权重同步过早 ACK，共享 buffer 被提前复用

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-20 · 旧号 RL-RO.19

- **原因对象**：RL训练回路 / ms-swift / Ray Megatron IPC 权重同步 ACK
- **原因行为**：接收侧只做本进程 CUDA 同步，driver rank 在 TP barrier 前即发 ACK，发送端收到 ACK 就复用同一共享 buffer 写下一桶，慢 TP rank 可能仍在读上一桶。
- **影响对象**：模型权重；输出内容（静默错误）
- **影响详情**：若坐实：rollout 引擎收到名形合法但值被部分覆写的权重，静默在新旧混合参数上采样，无同步异常；环境症状为 Ray + Megatron GRPO 首次 rollout 后输出损坏（MI308X/ROCm、TP=4/PP=2）。该 race 是否即根因尚未端到端验证。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/10204

### TRN-0242 `kept_mass_shift_rejects_all_rollout_correction` verl 截断采样的 kept-mass 偏置使校正拒绝全部序列

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-09-26 · 旧号 RL-RO.20

- **原因对象**：RL训练回路 / verl / rollout.logprobs_mode 口径
- **原因行为**：默认向 vLLM 请求 processed_logprobs，截断采样下按保留集归一化，而 trainer 的 old_log_probs 按全词表 log-softmax，两者之差逐 token 带 log(kept mass) 偏置。
- **影响对象**：训练信号；训练轨迹（质量退化）
- **影响详情**：Geo-RS/Seq-MIS 预设拒绝每条序列、actor 梯度恒 0：top_p=0.8 时 100/100 步全拒，reward 停在 0.13–0.14 而对照升至 0.83；只有通用 warning 与 advantages NaN，不点名原因；k3 预设下偏置不可见。
- **改进措施**：检测 待定；修复 修复方向（PR #8207，open 未 merge）：validate_config 在 rollout_is/rollout_rs 校正与截断采样+processed logprobs 组合时直接报错；批内全拒/全零权重时 warning 点名；ESS 除零改报 0.0。https://github.com/verl-project/verl/pull/8207
- **来源**：https://github.com/verl-project/verl/issues/8020；https://github.com/verl-project/verl/pull/8207
- **关联**：var:TRN-0229

### TRN-0243 `group_prefix_dedup_discards_tool_continuations` trl GRPO server 模式组内去重使工具多轮续写共用首个成员历史

`故障` · `active` · `rl` · `verified` · `NEW` · 发现 2026-09-27 · 旧号 RL-RO.21

- **原因对象**：RL训练回路 / trl / VLLMGeneration 组内去重
- **原因行为**：server 模式按 all_prompts[::num_generations] 做组内去重，默认组内前缀相同；工具调用第二轮起各成员历史互不相同，切片只保留首成员历史并以 n=num_generations 为全组采样后回填。
- **影响对象**：跨请求/跨样本数据；训练信号（静默错误）
- **影响详情**：无 crash、无 warning；其他成员续写在首成员的工具结果条件下采样，却按各自历史计 reward 与 logprob，组内方差被压扁、advantage 失真；触发于 server 模式、num_generations>1、多轮工具且首轮分叉，v0.26.0 起各版受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7416；https://github.com/huggingface/trl/pull/7418

### TRN-0245 `fp32_lm_head_not_applied_to_generation_backends` trl cast_lm_head_to_fp32 未作用于生成后端

`故障` · `active` · `rl` · `verified` · `NEW` · 发现 2026-09-29 · 旧号 RL-RO.23

- **原因对象**：RL训练回路 / trl / FP32 lm_head 生成路径
- **原因行为**：cast_lm_head_to_fp32 只接到训练打分路径：替换 head forward 时未禁用 autocast，generate 仍按 BF16 投影；构建 VLLMGeneration 时也不传 head dtype 覆盖。
- **影响对象**：输出分布；训练信号（静默错误）
- **影响详情**：无 crash、无 warning；BF16 训练下 transformers 与 vLLM 生成后端都从 BF16 head 采样，训练侧 logprob 按 FP32 算，IS 权重与 KL 系统偏置；CPU repro 中 logits 误差 3.7e-4。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7430；https://arxiv.org/abs/2510.13786

### TRN-0247 `resume_step_modulo_gating_skips_rollout_weight_sync` trl IWOPDTrainer resume 后取模门控跳过权重同步

`故障` · `active` · `rl` · `verified` · `NEW` · 发现 2026-10-09 · 旧号 RL-RO.25

- **原因对象**：RL训练回路 / trl / IWOPDTrainer vLLM 同步门控
- **原因行为**：同步门控写成 global_step % vllm_sync_frequency == 0 且 _last_vllm_sync_step=-1，构造或 resume 后不强制同步一次，resume 步数非倍数时同步被跳过直到下一个倍数步。
- **影响对象**：模型权重；训练信号（静默错误）
- **影响详情**：无 crash，loss 与指标正常；resume 后到下一个倍数步前 rollout 都用陈旧权重生成，策略梯度对旧策略样本计算；触发于 jsd 目标 + use_vllm + vllm_sync_frequency>1，如 resumed_step=37、freq=5。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7544

### TRN-0249 `dp_vllm_seedless_group_sampling_collapses_diversity` trl AsyncGRPO 采样请求不带 seed，组内样本重复

`故障` · `active` · `rl` · `verified` · `NEW` · 发现 2026-10-10 · 旧号 RL-RO.27

- **原因对象**：RL训练回路 / trl / AsyncGRPO rollout 采样 seed
- **原因行为**：把组内每个 generation 作为独立 n=1 请求发给 data-parallel vLLM server 且不携带 seed，各 engine 分发同源的请求种子序列。
- **影响对象**：输出内容；训练信号（静默错误）
- **影响详情**：无 crash，组内 generations 常逐字相同：8 个 run（DP=8、16 gen/prompt、T=1.0）重复占比 6.1%–70%，短 completion 最重，带 seed 基线 0.00–0.13%；组 std 被压小、advantage 失真、探索受抑。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/7549

### TRN-0289 `verl_prime_reward_dict_keyerror_batch_zero` verl PrimeRewardManager dict 分数整批置 0

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：RL训练回路 / verl / dict 分数分支缺失
- **原因行为**：PrimeRewardManager 缺少 dict 分支：reward 函数返回 dict 时抛 KeyError: 0，被 verify 的 except Exception 吞掉，整批奖励置 0.0。
- **影响对象**：训练信号（静默错误）
- **影响详情**：RL 训练整批 reward 静默变 0.0，仅一行 print；reward 曲线归零、advantage 全 0，训练继续但奖励信号已毁。
- **改进措施**：检测 监控 reward 均值是否异常归零；reward 函数返回 dict 时留意 [Error] Unexpected error during scoring 单行日志。；修复 待定（issue open 无评论；对照修复即比照 NaiveRewardManager/BatchRewardManager/DAPORewardManager 补 dict→score["score"] 分支，未核实上游进展）
- **来源**：https://github.com/verl-project/verl/issues/8216

### TRN-0298 `verl_prime_code_apps_taco_layout_zero_score` verl prime_code 对 APPS/TACO 布局静默 0 分

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-16

- **原因对象**：RL训练回路 / verl / prime_code 测试布局解析
- **原因行为**：default_compute_score 无 sandbox 回落 prime_code，call-based 路径按 JSON 行 .split 解析输入；APPS/TACO 测试是列表布局，.split 抛异常，未跑任何测试即记 0。
- **影响对象**：训练信号（静默错误）
- **影响详情**：apps/taco/codecontests/codeforces 数据源的 call-based 任务：正确解答也得 0 分且无任何日志（30 个种子样本 0/30 满分，重编码为 JSON 行布局后 28/30），RL 训练在这些任务上奖励信号完全失真。
- **改进措施**：检测 抽查各 data_source 的奖励分布是否异常偏低；用数据集自带首解跑 reward 校准（应为满分）。；修复 待定（issue open 无评论；规避=设置 sandbox_fusion_url 或将测试重编码为 JSON 行布局）
- **来源**：https://github.com/verl-project/verl/issues/8174

### TRN-0309 `trl_async_opd_rollout_policy_version_mislabel` trl Async OPD rollout 样本策略版本错标

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-18

- **原因对象**：RL训练回路 / trl / rollout 版本快照
- **原因行为**：rollout worker 任务入口读一次共享 model_version 盖章样本，发给 vLLM 的模型名 dispatch 时二次活读；期间 trainer 发布新 adapter 时样本被盖旧版本号。
- **影响对象**：训练样本流；训练信号（静默错误）
- **影响详情**：无报错。provenance 错标；staleness 门把刚生成的全新 rollout 当陈旧丢弃（max_staleness=0 时必丢），非零门限下 batching 与 staleness 观测失真。
- **改进措施**：检测 对同一 batch 比对样本 model_version 与生成请求 payload 中的模型名版本（两者应恒等）。；修复 报告者已备窄修复 fork（在 HTTP 请求构造边界快照版本、用它选 adapter 并随 token 返回），含确定性 CPU 测试：https://github.com/lindicaphxag-tech/trl/tree/fix/async-opd-pin-rollout-sampling-policy-version-20261017 （未合入上游，状态未核实）。
- **来源**：https://github.com/huggingface/trl/issues/7781；https://github.com/huggingface/trl/issues/7857

### TRN-0310 `trl_merged_weight_sync_publish_after_resume` trl merged 权重同步先 resume 后发布版本号

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-10-18

- **原因对象**：RL训练回路 / trl / merged 同步发布顺序
- **原因行为**：rank0 的 _sync_weight_merged 按 resume()→model_version+=1→update_model_version() 执行，版本发布在 resume 之后。
- **影响对象**：训练样本流；训练信号（静默错误）
- **影响详情**：非 LoRA merged/dense 每次同步的 resume 与版本发布间隙训练照常、无报错；vLLM 已用新权重出 token 但样本标旧版本，新样本可被 max_staleness 门当过期丢弃（门限 0 时尤甚），staleness 观测/批次构成偏离。
- **改进措施**：检测 对版本发布与 resume 的相对顺序做单元断言（issue 提供了六场景生产方法级回归，fork CI PASS）。；修复 报告者修复：把版本发布移到 resume 之前（publish while paused → resume），fork https://github.com/lindicaphxag-tech/trl/tree/fix/async-dense-policy-publish-before-resume-20261017 含两个 trainer 的生产方法级单测与 fork CI PASS（未合入上游，状态未核实）。
- **来源**：https://github.com/huggingface/trl/issues/7782
- **关联**：var:TRN-0309

### TRN-0316 `grpo_resume_inside_generation_block_shifts_schedule` GRPO 块内 resume 使 prompt 训练计划错位

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-19

- **原因对象**：RL训练回路 / trl / _step 与 skip 基准分叉
- **原因行为**：resume 后 self._step 重启为 0 而 Trainer 按 global_step 跳过 dataloader；ckpt 落在 generation 块内时两套计数基准分叉，块边界整体移动。
- **影响对象**：训练样本流（静默错误）
- **影响详情**：resume 后奇数 optimizer step 训练的是上一块的 prompt（prompt 0,1 被第三次训练、最后一块只得一次更新），与不中断 run 的每步 prompt 集合从第 3 步起持续不同；无报错，loss 表面正常
- **改进措施**：检测 固定 shuffle_dataset=False、逐 optimizer step 记录 prompt id 集合，对比中断/连续 run（repro 脚本 exit 1 on mismatch）；resume 于块边界（checkpoint-2 对照）则完全一致可作判别；修复 待定（issue open 2026-10-18，无评论；报告者含 CPU repro：8 prompts、num_iterations=2、steps_per_generation=1、Qwen2 tiny）
- **来源**：https://github.com/huggingface/trl/issues/7787

### TRN-0325 `trl_accuracy_reward_text_unit_false_equation_full_credit` trl accuracy_reward 对否定句与假等式给满分

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：RL训练回路 / trl / accuracy_reward 解析与判定
- **原因行为**：accuracy_reward 把 box 尾部 \text{...} 当单位剥掉，且 math-verify 接受右边等于 gold 的等式，否定句与假等式拿满奖励。
- **影响对象**：训练信号（静默错误）
- **影响详情**：以 accuracy_reward 为 reward 的 RLVR 训练中，模型写「R is wrong」或「W = R」即可拿满分：249 行样本否定句全满分、假等式 190 行满分；奖励与真实正确性脱钩、向 reward hack 漂移，无报错。
- **改进措施**：检测 对 reward=1 的 completion 抽样人工/LLM 复核真实正确率；监控含 \text{} 或等式形态 box 的占比与 reward 曲线的相关性。；修复 待定（issue open 提出两个部分缓解：completion 侧 units=False 或收紧 verify；均引入误杀，见 issue 实测数据；无修复 PR）
- **来源**：https://github.com/huggingface/trl/issues/7794

### TRN-0339 `mindspeed_rl_grpo_reward_norm_no_cross_rank_sync` GRPO reward 归一化未跨 rank 同步致 advantage 不一致

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：RL训练回路 / mindspeed-rl / GRPO reward 归一化的跨 rank 同步
- **原因行为**：GRPO reward 归一化未先 allgather 所有 rank 的 reward，仅用本 rank 局部 reward 计算 mean/std。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：TP=2+DP=4 双机 GRPO 时同一 step 各 rank loss 差距最大 15%；rank 上 prompt 偏难或偏易时本地 mean/std 偏离全局，同一 pair 在不同 rank 上的 loss 不同，方向被拉偏但无报错。
- **改进措施**：检测 同一 step 打印各 rank 的 reward mean/std 与 advantage 均值做跨 rank 比对；或让单 rank 与全局归一化的 advantage 对照。；修复 issue 建议先 all_gather(rewards) 得到 [dp_size*batch] 再算全局 mean/std（veRL/OpenRLHF 参考实现如此）；issue 已 closed，正文未给出合入 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-RL/issues/162

### TRN-0340 `mindspeed_rl_grpo_group_norm_contiguous_assumption` GRPO group_norm 依赖同 prompt 连续排布的隐式假设

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：RL训练回路 / mindspeed-rl / group_norm 组对齐
- **原因行为**：组内归一化直接按行序 reshape(-1, n)，隐含假设连续 n 行同属一个 prompt；调用侧异步取数不保证顺序，也不校验 micro_batch_size 为 n 的整数倍。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：异步 rollout 下样本顺序不保证；micro-batch 横跨 prompt 组或多组交错时，只要总数能被 n 整除，reshape 不报错但归一化不同 prompt 的 reward，组基线失真、静默污染；总数不能被 n 整除则直接抛 shape 错误。
- **改进措施**：检测 给 experience 带 prompt_id，reshape 后校验每组 prompt_id 一致；或在 validate_config 里断言 micro_batch_size % n_samples_per_prompt == 0。；修复 issue 建议两条：compute_advantage 中显式校验组对齐（prompt_id 一致），或把优势计算改为完整 global batch 收齐后做、不再依赖 micro-batch 取数顺序；issue 已 closed，正文未给出合入 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-RL/issues/166

### TRN-0341 `mindspeed_rl_dapo_reward_labels_nested_loop_reversed` DAPO rule_reward labels 两层循环顺序反致奖励错配

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-20

- **原因对象**：RL训练回路 / mindspeed-rl / rule_reward labels 展开
- **原因行为**：rule_reward.py 展开 labels 时把两层循环写反（外层 n_samples_per_prompt、内层 batch_data['labels']），得到的是按样本优先的顺序，而下游按样本内 n 次重复消费。
- **影响对象**：训练信号；训练样本流（静默错误）
- **影响详情**：reward_dispatch_size 与 n_samples_per_prompt 不一致时，labels 顺序与 rollout 样本不匹配，同一 prompt 的多次采样拿到别条样本的 label，reward/advantage 错配；无报错无 NaN。
- **改进措施**：检测 构造 batch 内 label 可区分的小样例跑一遍 rule_reward，检查展开后 labels 与样本的对应关系；或断言 len(labels) 与 reward 数一致且逐项对齐。；修复 issue 给出改法：外层改为 for label in batch_data['labels']、内层 for _ in range(self.n_samples_per_prompt)；issue 已 closed，正文未给出合入 PR（未核实）。
- **来源**：https://gitcode.com/Ascend/MindSpeed-RL/issues/83

### TRN-0345 `mswift_dynamic_num_samples_gdpo_ignored_chunk_rescale` ms-swift 动态 GRPO 丢 gdpo 归一化且分块重缩放 loss

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-21

- **原因对象**：RL训练回路 / ms-swift / 动态 advantage/分块 loss
- **原因行为**：动态路径的 advantage 函数未实现 gdpo 分支而静默退化为无缩放；分块 loss 按样本数加权平均，把已按全局 token 归一的窗口归一化损失再除以块数，梯度被静默缩小。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：dynamic_num_samples=True 时 gdpo advantage 与静态路径不一致（实测 -1.895 vs -2.786）；本地 batch 触发分块时 dapo/cispo/fipo 损失缩为 1/k，等效学习率静默下降，无报错。
- **改进措施**：检测 对同一批数据并行跑 compute_advantages 与 compute_advantages_dynamic 比对（gdpo 分支应一致）；分块前后 loss 数值比对（窗口归一化类应相等而非 /k）。；修复 待定（issue 建议支持 gdpo 或拒绝该组合；分块对窗口归一化类求和、bnpo 按 token 数加权；该路径已计划移除）
- **来源**：https://github.com/modelscope/ms-swift/issues/10405

### TRN-0447 `verl_sglang_rollout_logprobs_mode_ignored` verl SGLang rollout 忽略 logprobs_mode 配置

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：RL训练回路 / verl / SGLang rollout
- **原因行为**：rollout.logprobs_mode 只传给 vLLM，SGLang rollout 不消费：固定返回全词表 log(softmax(logits/T))，raw 模式所需环境变量从不被 verl 设置。
- **影响对象**：训练信号；输出分布（静默错误）
- **影响详情**：同一配置切后端 rollout logprobs 语义不同：top_p=0.8 时 vLLM rollout_corr 0.951/kl 0.053，SGLang 0.9994/0.0010；IS 权重、拒绝掩码、失配指标随后端静默变化。
- **改进措施**：检测 同配置双后端对比 rollout_is_mean/kl/probs_diff 指标（issue 附量化表）。；修复 待定（issue open；issue 提到有 PR 在 SGLang 侧补 raw logprobs 透传，未核实合入状态）。
- **来源**：https://github.com/verl-project/verl/issues/8362

### TRN-0448 `verl_agent_loop_masked_suffix_reward_dropped` verl agent-loop 掩码后缀 reward 被丢弃

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-26

- **原因对象**：RL训练回路 / verl / agent_loop+GAE/RF++
- **原因行为**：agent_loop 把轨迹分数放在最后一个响应 token，而模板后缀（如 '\n'）response_mask=0：GAE/REINFORCE++/ReMax/OTB 忽略 mask=0 上的 reward，outcome 分数丢失。
- **影响对象**：训练信号（静默错误）
- **影响详情**：两轮轨迹末 3 token ['```','<|im_end|>','\n'] mask [1,1,0]：分数落在 mask=0 的 '\n' 上，GAE/RF++ returns 全零；mask 假设被模板后缀打破。
- **改进措施**：检测 检查 reward 张量落点 token 的 response_mask；对照 compute_gae_advantage_return 手工核算。；修复 待定（issue open，未见修复 PR）。
- **来源**：https://github.com/verl-project/verl/issues/8367

### TRN-0449 `msswift_multiturn_nonthinking_prefix_context_mismatch` ms-swift 多轮非思考模板中间轮上下文错位

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-10-26

- **原因对象**：RL训练回路 / ms-swift / multi_turn_scheduler
- **原因行为**：rollout 给每轮 assistant 加非思考前缀采样，训练侧重编码只给最后一轮注入前缀、中间轮原样插入：中间轮训练上下文与采样上下文不同。
- **影响对象**：训练信号（静默错误）
- **影响详情**：中间轮 token 在从未采样过的上下文里计分；两遍 logprob 同用 train 编码，IS ratio 恒 1，无指标暴露该错位。
- **改进措施**：检测 rollout/train 双侧 tokenize 后 diff 中间轮上下文；检查 prefix 前后的 token 序列。；修复 待定（issue open；related #10106/#10107 同类 response_prefix 已修（merged），本条为多轮非思考模板路径）。
- **来源**：https://github.com/modelscope/ms-swift/issues/10429
- **关联**：var:TRN-0238

### TRN-0460 `trl_repetition_penalty_is_ratio_zero` GRPO vLLM 重复惩罚使 IS ratio 归零停滞

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-10-27

- **原因对象**：RL训练回路 / trl / vLLM 采样 logprob 口径
- **原因行为**：repetition_penalty 传入 vLLM 后其返回 logprobs 已含惩罚；trainer 用无惩罚 raw logits 重算取比值，被惩罚 token 给 log-ratio 加偏置并连乘。
- **影响对象**：训练信号；训练轨迹（静默错误）
- **影响详情**：use_vllm=True 且 repetition_penalty≠1.0 时 IS 权重每个 completion 都≈0，grad_norm 无报错跌到 0、训练停滞；presence/frequency penalty 同点位施加应同病。#7866 修复不覆盖。
- **改进措施**：检测 监控 sampling_logp_difference 与 IS ratio 分布；grad_norm→0 告警；修复 待定（同机制 #7865 修复 #7866 不覆盖此触发面，issue open）
- **来源**：https://github.com/huggingface/trl/issues/7914
- **关联**：var:TRN-0229

### TRN-0461 `trl_cispo_epsilon_high_default_clip` TRL cispo 默认 epsilon_high 截死全部权重

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：RL训练回路 / trl / GRPO cispo 默认参数
- **原因行为**：CISPO 用绝对上界 clamp(coef_1, max=epsilon_high)；epsilon_high 未设置时回退 0.2（对绝对界无意义），on-policy coef_1=1 也被截到 0.2；推荐值 5.0 无代码生效。
- **影响对象**：梯度；训练信号（静默错误）
- **影响详情**：loss_type=cispo 未显式设 epsilon_high 时梯度比预期小 5 倍（实测 grad_norm 0.054 vs 0.269），cispo_clip_ratio 把每个正 advantage token 报为 clipped；静默减速无报错。
- **改进措施**：检测 监控 cispo_clip_ratio 是否恒 ≈1；检查 epsilon_high 是否显式设置；修复 待定（作者建议未设置时默认 5.0 或报错，issue open）
- **来源**：https://github.com/huggingface/trl/issues/7916

### TRN-0464 `trl_dpo_stale_ref_scores_collator_limit` DPO 复用陈旧参考分数缓存致梯度错

`故障` · `active` · `sft` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：RL训练回路 / trl / precompute_ref 缓存键
- **原因行为**：precompute_ref_log_probs=True 时参考分缓存以数据集目录为键、不含 collator 截断长度；collator 限制改变后模型分数对新序列计算、参考分数仍来自旧序列，不同序列的分数进入同一 DPO loss。
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：缓存目录存在旧参考分且 collator 截断长度改变时，初始 loss/梯度即错且依赖缓存历史：同配置同数据，仅因是否命中旧缓存目录，初始 loss/梯度不同；静默无告警。
- **改进措施**：检测 清理缓存目录对比初始 loss/梯度是否变化；缓存键纳入 collator 截断参数指纹；修复 待定（issue open）
- **来源**：https://github.com/huggingface/trl/issues/7897

### TRN-0465 `trl_rloo_exp_before_clip_nan_grad` RLOO 先 exp 后 clip 致 NaN 梯度

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-27

- **原因对象**：RL训练回路 / trl / RLOO 序列 ratio 裁剪顺序
- **原因行为**：RLOO 对正 advantage completion 先对序列 log-ratio 求和取 exp 再 clamp：复用旧 completion 时增量和超 FP32 指数域，exp 溢出 inf 后才裁剪，反传 NaN。
- **影响对象**：梯度（数值异常）
- **影响详情**：num_iterations>1 且被复用的正 advantage 长 completion 序列 log-ratio 增量超 FP32 指数域时，loss 数值有限但反传 NaN 梯度；真实 tiny-Llama 复现。默认 num_iterations=1 不触发。
- **改进措施**：检测 clip 前检查序列 log-ratio 上界（>~88 for fp32 exp）；先 clamp log-ratio 再 exp；修复 待定（issue open，建议先裁剪后指数化）
- **来源**：https://github.com/huggingface/trl/issues/7896

### TRN-0469 `trl_vespo_token_mask_sequence_collapse` trl VESPO+token_mask 单 token 出界压零整条序列权

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：RL训练回路 / trl / VESPO get_gamma_weights
- **原因行为**：token_mask 把出界 token 的 IS ratio 置 0 后，VESPO 的 get_gamma_weights 对置零 ratio 取 log 并按序列求和：单个被掩 token 给整条序列加 log(1e-8)≈-18
- **影响对象**：训练信号；梯度（静默错误）
- **影响详情**：含任一出界 token 的整条 completion 的 gamma 权重塌到 ~1e-15/~1e-24 量级，序列级梯度被整体抹掉；无报错、grad_norm 仅显示变小。
- **改进措施**：检测 cispo_clip_ratio/IS 权重直方图：单 token 出界序列整体塌零；γ 权重分布双峰；修复 待定（issue open，2026-10-27；文档口径与实现矛盾待维护者裁决）
- **来源**：https://github.com/huggingface/trl/issues/7952
- **关联**：var:TRN-0229

### TRN-0470 `trl_asyncgrpo_minp_is_bias` trl AsyncGRPO min_p 单独开启时 IS ratio 偏低偏

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：RL训练回路 / trl / AsyncGRPO rollout 候选集请求
- **原因行为**：AsyncGRPOTrainer 的 rollout worker 只为 top_p/top_k 请求候选集；min_p 单独开启时请求不带采样掩码，vLLM 按 min_p 截断后词表归一化 logprob
- **影响对象**：训练信号（静默错误）
- **影响详情**：min_p 采样下 IS 修正权重整体偏低，on-policy 偏置进入每个 completion 的梯度；无报错。
- **改进措施**：检测 min_p>0 时对比 sampling_logp_difference/importance_sampling_ratio 指标是否系统性 <1；修复 待定（#7866 修复不覆盖 min_p；issue open 2026-10-27，由 qgallouedec 在 #7866 review 中报告）
- **来源**：https://github.com/huggingface/trl/issues/7936
- **关联**：var:TRN-0229

### TRN-0471 `trl_gkd_think_format_reward_leak` trl think 格式示例给 think 内 boxed 答案记分

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-28

- **原因对象**：RL训练回路 / trl / rloo/gspo math 示例 rewar。
- **原因行为**：六个官方示例在 prompt 要求 <think></think> 块的同时用 accuracy_reward 计分：reasoning 块内出现的 \boxed{} 答案也被记为正确
- **影响对象**：训练信号（质量退化）
- **影响详情**：把答案写进 <think> 内的 completion 同样拿 accuracy 满分，reward 无法区分「先答后想」的退化行为；策略可能学会把答案前置进推理块。
- **改进措施**：检测 抽查高 reward completion 的 </think> 后内容是否为空/无答案；修复 待定（issue open 2026-10-27，示例代码修复未出）
- **来源**：https://github.com/huggingface/trl/issues/7950

### TRN-0498 `trl_server_peft_last_chunk_unmerged_broadcast` TRL server 模式 LoRA 权重同步尾块未合并

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：RL训练回路 / trl / 权重同步生成器
- **原因行为**：PEFT 权重同步在 yield 完后于生成器内 unmerge_adapter()（就地减 delta）；vLLM 尾块直到迭代器耗尽才 cat 读取视图，unmerge 先执行，尾块 LoRA 目标权重以未合并值发出。
- **影响对象**：模型权重；训练信号（静默错误）
- **影响详情**：vllm_mode=server+PEFT 下每次同步尾块发送未加 LoRA delta 的 base 权重（fp32 默认 dtype 必触发）；rollout 持续用接近原模型的权重生成，与 trainer 脱节，IS ratio/KL 静默失真。
- **改进措施**：检测 server 侧抽样比对收到的权重与 trainer merge 后参数；监控 rollout logprob 与 train logprob 漂移；修复 待定（issue open 2026-10-29，无修复 PR；colocate 模式不受影响；规避：增大 buffer_size_bytes 使尾块非耗尽触发或暂停 unmerge 时序）
- **来源**：https://github.com/huggingface/trl/issues/8003

### TRN-0509 `openrlhf_group_norm_uniform_reward_noise_advantage` OpenRLHF 同酬组 group_norm 噪声 advantage

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：RL训练回路 / openrlhf / group_norm 除以 std+1e-9
- **原因行为**：group_norm 分支除以 std+1e-9：fp32 下相同值组的 std≈3.1e-8 而非 0，epsilon 压不住比值，同酬组每响应得 ±0.9 量级舍入噪声 advantage。
- **影响对象**：训练信号（静默错误）
- **影响详情**：全等酬赏组（部分得分/可验证酬赏常见）advantage 应全零，实测组 8/16/64 下 max|adv| 0.907/0.938/0.960（酬赏 0.3）；噪声信号驱动无效更新，方向由舍入决定。
- **改进措施**：检测 对全等酬赏组断言 advantage 全零；监控同酬组 advantage 分布；修复 修复 PR https://github.com/OpenRLHF/OpenRLHF/pull/1383（open，2026-10-25）——归一化前求组 max/min，max==min 的组事后置零（NaN 组不受影响）；新增 tests/test_group_norm_advantage.py 10 用例修复前全失败
- **来源**：https://github.com/OpenRLHF/OpenRLHF/pull/1383

### TRN-0510 `verl_k3_kl_cancellation_wrong_rejection` verl k3 KL 相减消去致拒绝判定反转

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-10-29

- **原因对象**：RL训练回路 / verl / k3 估计 exp(x)-1-x
- **原因行为**：k3 KL 估计用 exp(x)-1-x：x 接近 0 时对接近 1 的指数减 1 发生灾难性消去，x=-1e-4 时统计量为负（-1.66e-8，应为 +5e-9）。
- **影响对象**：训练信号（静默错误）
- **影响详情**：seq_sum_k3 阈值 1e-4 时本应拒绝的序列被保留、token_k3 阈值 1e-8 时 x=+1e-4 被误拒——KL 惩罚、rollout 拒绝采样与 off-policy 诊断三处 k3 表达式同病；作者明示未确立端到端训练回归。
- **改进措施**：检测 小 log-ratio 输入下与 fp64 基准或 expm1(x)-x 对照 k3 值与符号；修复 修复 PR https://github.com/verl-project/verl/pull/8386（open，2026-10-26）——三处 k3 表达式改用数学等价的 torch.expm1(x)-x；Windows/py3.12/torch2.13 CPU 验证
- **来源**：https://github.com/verl-project/verl/pull/8386
- **关联**：var:TRN-0220

### TRN-0512 `trl_continuous_batching_inplace_bf16_cast` TRL 连续批采样把训练权重就地 cast bf16

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-29

- **原因对象**：RL训练回路 / trl / generate_batch 前就地 cast
- **原因行为**：连续批每次生成前把模型就地 cast bf16 且不 cast 回（FlashAttention 拒 fp32）；nn.Module.to 换掉优化器所持 Parameter 的 .data，第一次生成起纯 bf16 训练。
- **影响对象**：模型权重；训练轨迹（静默错误）
- **影响详情**：策略按 GRPOTrainer 默认 fp32 加载、bf16=True 期望优化器保 fp32 master 权重；实际第一次生成后优化器状态绑定 bf16 参数，更新精度与预期配置静默不符。
- **改进措施**：检测 首步生成后打印 policy 参数 dtype 与优化器 state dtype；对比同配置非连续批路径 loss 曲线；修复 待定（issue open 2026-10-28，1.17.0.dev0；非连续批路径不受影响）
- **来源**：https://github.com/huggingface/trl/issues/7965

### TRN-0516 `swift_grpo_masked_token_log_ratio_overflow_nan` swift GRPO 掩码 token log-ratio 溢出 NaN

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：RL训练回路 / ms-swift / GRPO per-token IS ratio
- **原因行为**：per-token IS ratio 先 exp(Δlogp) 再在 reduce 时乘 completion_mask，被排除 token 的 log-ratio 溢出为 inf 后 inf*0 变 NaN 污染 loss 与梯度
- **影响对象**：训练信号；梯度（数值异常）
- **影响详情**：completion_mask 排除的 token（如 padding/截断段）Δlogp 大于 ~88（fp32 exp 上限）时 loss=NaN 且梯度 NaN；修复把掩码提到 exp 之前
- **改进措施**：检测 监控 loss/梯度 NaN；检查被 mask token 的 Δlogp 分布；修复 修复 PR https://github.com/modelscope/ms-swift/pull/10433（commit 3f6d7cde 已在 main，PR 关闭未标 merged，等价修复已入主干）：exp 之前先把被排除 token 的 log-ratio 置 0
- **来源**：https://github.com/modelscope/ms-swift/issues/10431；https://github.com/modelscope/ms-swift/pull/10433

### TRN-0532 `swift_v5_rl_precision_fp32_override_ignored` swift v5 RL FP32 计算精度被覆盖

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：RL训练回路 / ms-swift / v5 RL 共共 builder 精度解析
- **原因行为**：FP32 参数加载覆盖与计算精度未独立处理，显式 FP32 配置的计算精度被加载覆盖静默降为混精
- **影响对象**：训练轨迹；数值结果（质量退化）
- **影响详情**：显式 FP32 配置的 RL 训练实际按非 FP32 计算精度运行，与用户配置意图不符；修复后 BF16/FP16 保留对应 mixed_precision、显式 FP32 保持 no
- **改进措施**：检测 检查训练日志 mixed_precision 是否与显式 dtype 配置一致；对比半精/全精 loss 曲线；修复 修复 PR https://github.com/modelscope/ms-swift/pull/10451（merged 至 dev-swift-v5 2026-10-29T02:49Z，目标分支 dev-swift-v5 非 main）：FP32 加载覆盖与计算精度独立，覆盖 GRPO/PPO/在线蒸馏公共 builder
- **来源**：https://github.com/modelscope/ms-swift/pull/10451

### TRN-0544 `trl_iwopd_resume_skip_vllm_weight_sync` TRL IW-OPD resume 后跳过 vLLM 同步

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-10-30

- **原因对象**：RL训练回路 / trl / IWOPDTrainer vllm 同步步计数
- **原因行为**：IWOPDTrainer 的 _last_vllm_sync_step 初始 -1 且仅整倍数步同步：resume 到非整倍数步时首步同步被跳过，vLLM 引擎仍用构造时初始权重生成
- **影响对象**：训练信号（静默错误）
- **影响详情**：从 checkpoint resume 到非整倍数步（如 frequency=5 时 resume 到 37，则 37-39 步）时，头几步 rollout 由初始模型权重生成，训练侧却按新权重算损失，重要性偏离静默扩大、日志无异常；需 jsd+use_vllm+frequency>1
- **改进措施**：检测 resume 后首步强制 sync 并断言引擎权重指纹与 trainer 一致；修复 修复 PR https://github.com/huggingface/trl/pull/7994（open，对齐 GOLDTrainer：初始值 -vllm_sync_frequency + >= 判定，未合入）
- **来源**：https://github.com/huggingface/trl/pull/7994

## 观测/评测

### TRN-0096 `metric_flush_key_set_rank_local_contamination` GRPO/RLOO 指标 flush 按本地 key 集合聚合致混列/死锁

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-21 · 旧号 DATA.14

- **原因对象**：观测/评测 / trl / GRPO/RLOO metric flush
- **原因行为**：metric flush 遍历本 rank 本地 pending key 集合并逐 key 调 collective，而 key 集合由条件触发的 reward 函数决定、随 rank 而异；对各 rank 均值再做未加权平均。
- **影响对象**：指标/日志；可用性/进度（静默错误）
- **影响详情**：key 仅单边存在时分布式死锁；各 rank key 集合不同时两条无关指标混进对方聚合；样本数不同时全局指标被触发频次加权。后两者无报错，reward/KL 曲线静默失真，训练 loss 不受影响。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7310；https://github.com/huggingface/trl/pull/7382

### TRN-0168 `long_run_quality_drop_without_nan` loss 正常而下游能力长跑退化：单看标量 loss 会误判健康

`结论` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 LOSS.04

- **原因对象**：观测/评测 / 通用 / 仅依赖标量 loss 的健康判定
- **原因行为**：数据污染、学习率过期、MoE 塌缩或 SDC 累积等导致下游能力下降时，loss 仍缓降或在可接受带内震荡，仅凭标量 loss 判定训练健康会漏检。
- **影响对象**：训练轨迹；指标/日志（质量退化）
- **影响详情**：无显式失败，ckpt 能 resume，评测却一代不如一代；谱/熵/鞅时钟在 loss 之前动。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：本实验室 monitor 的存在理由：谱/熵/鞅时钟在 loss 之前动。

### TRN-0214 `k1_cancels_tim_early_collapse` KL 探针（K1/K3）贴零基线，策略塌缩时仍显示健康

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 RL-KL.01

- **原因对象**：观测/评测 / 通用 / KL 监控探针（K1/K3 估计器）
- **原因行为**：K1=−log r 有符号，batch 内正负抵消；TIM 已在扭曲训练目标时，K1/K3 仍可贴着零基线
- **影响对象**：指标/日志（静默错误）
- **影响详情**：看板显示 KL 健康，而策略已在塌缩；VeXact 文中 recompute 模式前 700 step 奖励已下降，KL 探针几乎不动
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2605.14220

### TRN-0250 `stability_monitor_env_lost_in_torchrun` 稳定性监控开关环境变量经 torchrun 丢失，监控静默未启用

`故障` · `active` · `pretrain` · `verified` · `NEW` · 发现 2026-08-17 · 旧号 OBS.01

- **原因对象**：观测/评测 / megatron-lm / stability monitor 启用开关
- **原因行为**：监控靠 export STABILITY_MONITOR_ENABLED=1 开启，该变量经 torchrun 子进程丢失，_is_enabled() 读到空值即跳过初始化且不报错。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：监控目录里有 JSONL 文件但为 0 字节，排障者以为没有故障；以 export 环境变量经 torchrun 启动即触发。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：`opensource_training_megatron` / megatron-lm-training skill。

### TRN-0251 `empty_metrics_read_as_healthy` 监控文件为空或只有 header 时 dashboard 判为无报警

`故障` · `active` · `shared` · `verified` · `var` · 发现 2026-08-17 · 旧号 OBS.02

- **原因对象**：观测/评测 / 通用 / dashboard 空指标判定
- **原因行为**：监控路径写出的文件为 0 字节或只有 header，dashboard 把无数据当作「无报警」处理。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：KER.01 一类注入可整段跑完无人知道，dashboard 显示健康。
- **改进措施**：检测 待定；修复 待定
- **来源**：引用：同 OBS.01。
- **关联**：var:TRN-0250

### TRN-0252 `job_green_zero_step_progress` 作业显示 Running 但 step 不前进，健康检查看不出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-08-17 · 旧号 OBS.03

- **原因对象**：观测/评测 / 通用 / 作业健康检查（进程存活/GPU util）
- **原因行为**：调度器/健康检查只看进程存活和 GPU util 非零，不看 step 计数是否增长。
- **影响对象**：可用性/进度；指标/日志（挂起）
- **影响详情**：进程 hang 在集体通信或数据加载时，任务仍显示 Running、GPU util 非零，但 step 计数不涨、ckpt 停在旧 iteration，训练正确性监控收不到新样本。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://arxiv.org/abs/2509.16293

### TRN-0253 `zero_signal_run_reports_success` verl 零信号 GRPO run 无护栏、照常报告成功

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-18 · 旧号 OBS.04

- **原因对象**：观测/评测 / verl / fit loop grad_norm 护栏
- **原因行为**：fit loop 对 grad_norm 只记日志不设护栏，全组同分使 advantage 全 0、grad_norm≈0 时不中止也不告警。
- **影响对象**：指标/日志；训练轨迹（静默错误）
- **影响详情**：全组同分时整个 GRPO run 是 no-op，但正常 exit 0、任务显示成功、指标图全平，ckpt 出的模型与初始化相同，烧完整轮 GPU 才从图表发现什么都没学。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7405
- **关联**：var:TRN-0203

### TRN-0255 `rl_diagnostics_unmasked_padding_positions` trl RL 诊断指标未掩 padding，KL/entropy 失真

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-08-23 · 旧号 OBS.06

- **原因对象**：观测/评测 / trl / Online DPO/PPO/XPO 指标计算
- **原因行为**：指标与 loss 掩码不一致：Online DPO 以未掩码张量算 kl/reward/entropy；PPO 的 approxkl/entropy/ratio 含 padding；XPO 报 policy+ref logprob。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：训练 loss 不受影响，但看板上 objective/kl、entropy、rlhf_reward 等曲线被 padding 系统性拉偏（Online DPO 的 pad 位置贡献有限负值、entropy 膨胀），恰是用来发现 KL 塌缩的探针失准。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/6809；https://github.com/huggingface/trl/issues/6803

### TRN-0257 `loss_path_metrics_weighted_by_window_size` trl GRPO 诊断指标按 micro-batch 平摊，尾窗致偏 2 倍

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-05 · 旧号 OBS.08

- **原因对象**：观测/评测 / trl / GRPOTrainer 指标记录与平均
- **原因行为**：指标每个 micro-batch append 一次，log() 对区间内条目扁平平均而非按 optimizer window 平均；policy_loss 记录时点随 loss_type 在 rescale 前后不一。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：transformers 5.11 把 epoch 尾部 accumulation window 截短为余数时，长短窗按条目数 3:1 加权，policy_loss 记录值与窗口均值差 2 倍（−0.000557 vs −0.001114）；跨 run、跨 loss_type 对比失真。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7047；https://github.com/huggingface/trl/issues/7011

### TRN-0258 `gathered_mean_metrics_double_count_padding` trl 指标先本地归约再 gather，尾批 padding 重复计入

`故障` · `active` · `sft；rl` · `documented` · `var` · 发现 2026-09-06 · 旧号 OBS.09

- **原因对象**：观测/评测 / trl / 多个 trainer 的指标 gather 聚合
- **原因行为**：指标先在 rank 本地 reduce 成标量再 gather_for_metrics，其沿 batch 维切片去 padding 对标量失效；PPO micro-batch 指标按槽位取均值，未写入槽位的零值也被计入。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：数据集不整除 rank 数时，每个 epoch 尾批的 accuracy、KL、margins、entropy 等指标系统性偏移，小数据集/大 world_size 偏差最大；涉及六个 trainer 共 11 处，另有全 1 ratio 下 val/ratio_var 记为 0.2667。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/pull/7045
- **关联**：var:TRN-0257

### TRN-0259 `tp_replicated_tokens_summed_in_metrics` trl 在 TP 下对全部进程累加 num_tokens，计数虚高

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-09-08 · 旧号 OBS.10

- **原因对象**：观测/评测 / trl / num_tokens 指标跨进程累加
- **原因行为**：TP 下各 rank 收到同一份 batch，trl 自建的 num_tokens 指标仍对全部进程求和，漏了 Trainer 基类对 num_input_tokens_seen 已做的 TP 除法；EP 同理。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：无 crash、训练本体正确；tp_size=2 时 num_tokens 恰为真实值 2 倍、tp_size=32 时 32 倍，tokens/s、token 预算与成本核算随之按 TP 度虚高。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7100

### TRN-0260 `synthetic_padding_dilutes_rollout_correction_metrics` verl 离策略诊断均值计入合成 padding 行，训推偏移被低估

`故障` · `active` · `rl` · `documented` · `NEW` · 发现 2026-09-09 · 旧号 OBS.11

- **原因对象**：观测/评测 / verl / compute_offpolicy_metrics
- **原因行为**：_balance_batch 补入 response_mask=0 的 padding 行，compute_offpolicy_metrics 对所有行取平均，padding 行以 logprob 均值 0 / PPL 1 计入而未剔除。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：无 crash；padding 行越多，rollout_corr/log_ppl_abs_diff、training_ppl 等训推 gap 指标越小（同批加 0/1/3 行单调漂移），真实 token 的 logprob 不变；下游 is_padding 过滤救不回已算入的均值。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7771

### TRN-0265 `wandb_step_commit_drops_later_logs_same_step` torchtitan W&B 每次 log 即提交 step，验证指标被丢

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-10 · 旧号 OBS.16

- **原因对象**：观测/评测 / torchtitan / WandBLogger.log 的 step 提交
- **原因行为**：WandBLogger.log 以 commit=True 调 wandb.log，每次 log 即提交该 step 行，未把同一 step 的多次 log 累积成一行；验证指标随后才 log 到同一 step。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：无 crash、无 warning，W&B 丢弃已提交 step 的后续 log：默认 log_freq=10 与 validator freq=10 下每次核心验证的指标都缺失，RL post-training 验证同样被吞，validation 面板为空或停在旧值。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/pull/5227

### TRN-0274 `msprof_silent_device_data_loss` msprof 偶发静默丢失 device 侧全部采集数据

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：观测/评测 / cann / msprof device 侧采集通道
- **原因行为**：aclgraph+superkernel负载下，msprof采集疑似因profiling通道初始化与图捕获/静态kernel编译时序竞态导致device侧数据完全丢失。
- **影响对象**：指标/日志（静默错误）
- **影响详情**：msprof采集aclgraph+superkernel时约13%(15轮失败2次)device侧数据完全丢失：三个CSV不生成、trace设备kernel事件为0；host/AICPU正常、退出码0无报错。与迭代次数无关。--delay在图capture后开启则确定性完全无产出或空trace。
- **改进措施**：检测 采集后校验 op_summary/task_time CSV 存在性与 device flips 数（collection_device_0.log 中 0 device flips 与失败 100% 相关）。；修复 待定（issue open，未见修复 MR；#1099 确定性变体同开）
- **来源**：https://gitcode.com/cann/runtime/issues/1098；https://gitcode.com/cann/runtime/issues/1099

### TRN-0304 `torchair_benchmark_check_recompile_false_negative` torchair benchmark --check 校验别的 kernel

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：观测/评测 / cann / benchmark.py --check 精度校验
- **原因行为**：--check 把 eager_fn 片段重交 torch.compile，重编 kernel 与整网 kernel 不同构（kernel 数与 md5 不同），校验通过不代表整网 kernel 正确
- **影响对象**：测试判定（静默错误）
- **影响详情**：结构校验假阴性：整网 kernel 在 CANN 0923 上实测产生 23% NaN 导致训练 grad_norm=nan，同一 kernel 的 benchmark.py --check 却报 Precision check passed（CosineSim=1.0）；校验工具给出错误通过结论
- **改进措施**：检测 对 --check 结果保持怀疑：对比 TORCH_COMPILE_DEBUG=1 下整网与重编产物 kernel 目录数量与 md5（整网 1 个 vs 重编 2 个即暴露）；以固定 commit 源码核对 asc_graph.py 重复链；修复 待定（issue open；已给出直观对比与根因分析（整网 kernel 重复子计算 vs 片段逻辑语义），尚无修复 MR）
- **来源**：https://gitcode.com/Ascend/torchair/issues/870

### TRN-0381 `pytorch_npu_flight_recorder_hccl_matcher_false_matched` Flight Recorder HCCL 匹配器把不匹配集体通信报全匹配

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-23

- **原因对象**：观测/评测 / torch_npu / Flight Recorder matcher
- **原因行为**：匹配器读首个栈帧名当 HCCL 操作而非 profiling_name，比较内置 type 而非 self.type，dtypes 与自身比——不同 size/dtype 的 collective 判 FULLY_MATCHED，端点不解析
- **影响对象**：测试判定；指标/日志（静默错误）
- **影响详情**：构造 input_sizes=(2,) 与 (3,) 的两个 Op 返回 FULLY_MATCHED；Float 与 Half 同样；hccl:send 0->1 事件 src=dst=-1。排障分布式训练挂起的开发者拿到假阴性干净结果
- **改进措施**：检测 用已知 size/dtype 不同的两个 collective 事件构造单测断言必须 mismatch；修复 修复 MR https://gitcode.com/Ascend/pytorch/merge_requests/48400（open，2026-10-22）：用 profiling_name 识别 HCCL 操作、解析 P2P 端点、比较两个操作的 size/dtype，不一致报 mismatch（关联 issue 自带 CPU-only 复现探针）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5616；https://gitcode.com/Ascend/pytorch/merge_requests/48400

## 配置/参数

### TRN-0024 `training_args_env_leak_sticky_bf16_precision` TrainingArguments 环境变量泄漏使 fp32 配置沿用 bf16

`故障` · `active` · `sft；rl` · `documented` · `NEW` · 发现 2026-09-22 · 旧号 NUM.15

- **原因对象**：配置/参数 / transformers / TrainingArguments 混精环境变量
- **原因行为**：transformers<5 的 TrainingArguments 把混精写进进程级环境变量，下次实例化再读回作默认值，bf16=False 与未设置不可区分；旧版 accelerate 未显式传参时也回落读该变量。
- **影响对象**：数值结果；输出分布（静默错误）
- **影响详情**：同进程先建 bf16 配置（TRL 默认 bf16=True）后，bf16=False 的 trainer 或 bare Accelerator 静默继承 bf16 autocast，评测/打分/第二阶段误差约 1e-4、易被当噪声；trl CI 实测 1709/2200 元素 mismatch。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/huggingface/trl/issues/7320；https://github.com/huggingface/trl/pull/7321

### TRN-0056 `dead_or_shadowed_arg_silent_noop` 配置参数声明未消费或被硬编码覆盖而静默无效

`故障` · `active` · `pretrain；rl` · `documented` · `var` · 发现 2026-08-19 · 旧号 CKPT.07

- **原因对象**：配置/参数 / ms-swift / mtp_shared_weights 死参数
- **原因行为**：参数声明后从未被消费（死参数）或被硬编码覆盖：ms-swift --mtp_shared_weights 无 consumer；verl 用硬编码 value_model 覆盖 critic model_type；另有多个同型键。
- **影响对象**：模型权重；性能/资源（静默错误）
- **影响详情**：无报错、无日志差：ms-swift 训出 N 层独立 MTP 权重而非部署用的单层重复 drafter；verl 自定义 critic 引擎静默退回 stock；SP、FSDP2、router replay 等设置静默不生效，曾被误读成显存容量问题。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/modelscope/ms-swift/issues/9936；https://github.com/verl-project/verl/issues/7460；https://github.com/verl-project/verl/issues/7463；https://github.com/verl-project/verl/issues/7462；https://github.com/verl-project/verl/issues/7476；https://github.com/huggingface/trl/issues/6791；https://github.com/verl-project/verl/pull/7597；https://github.com/verl-project/verl/issues/7662
- **关联**：var:TRN-0055

### TRN-0246 `fsdp_engine_dtype_config_ignored_rollout_trainer_split` verl FSDP 引擎不读 dtype 配置，训练侧静默保持 BF16

`故障` · `active` · `rl` · `verified` · `var` · 发现 2026-10-09 · 旧号 RL-RO.24

- **原因对象**：配置/参数 / verl / FSDP 引擎 dtype 配置读取
- **原因行为**：FSDP 引擎从不读取 fsdp_config.dtype，compute dtype 只来自 mixed_precision.param_dtype，mixed_precision 为默认 None 时硬编码为 bfloat16。
- **影响对象**：训练信号（静默错误）
- **影响详情**：无报错；设 rollout.dtype 与 fsdp_config.dtype 为 float16 时 rollout 为 FP16、trainer 仍为 BF16，GradScaler 也被跳过；k3_kl 约为真 FP16 配置的 63 倍。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/8076
- **关联**：var:TRN-0245

### TRN-0308 `mindspeed_msswift_fsdp_decoupled_grad_mapping_missing` ms-swift Megatron-FSDP 精度优化器梯度静默丢失

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-17

- **原因对象**：配置/参数 / ms-swift / DDPConfig 同名拷贝构造
- **原因行为**：swift 同名字段拷贝构造 DDPConfig，漏掉 use_precision_aware_optimizer→megatron_fsdp_use_decoupled_grad 映射，FusedAdam 跳过无梯度参数且不报错
- **影响对象**：梯度；模型权重（静默错误）
- **影响详情**：Megatron-FSDP v1 + use_precision_aware_optimizer=True（MCore 0.19.x）出现零梯度范数、参数不更新；训练继续跑、无报错，官方 Megatron-LM 入口同配置正常，swift 封装下静默失效
- **改进措施**：检测 开启精度优化器时核对 megatron_fsdp_use_decoupled_grad 实际取值；观察 grad_norm 是否恒 0/参数指纹不变；修复 待定（issue open：最小示例已隔离 swift 配置构造缺陷，期望按官方入口把 decoupled-gradient 跟随 use_precision_aware_optimizer；swift 侧修复未提交）
- **来源**：https://github.com/modelscope/ms-swift/issues/10351

## 构建/发布

### TRN-0135 `rocm_wheel_silent_loss_parity_regression` ROCm wheel 7.2→7.14 致梯度 NaN 与 loss 失配

`故障` · `active` · `pretrain` · `documented` · `NEW` · 发现 2026-08-23 · 旧号 KER.04

- **原因对象**：构建/发布 / pytorch / ROCm 7.14 wheel 内 kernel
- **原因行为**：同一训练代码与配置仅把 ROCm 7.2 PyTorch wheel 换成 7.14 wheel，错值来自发行版 kernel/builder 差异，训练框架侧无从断言。
- **影响对象**：梯度；训练信号（数值异常）
- **影响详情**：torchtitan Qwen3 MoE FSDP+TP+EP 配置下部分 run 梯度范数极大或 NaN，另一些仅 loss parity 偏差；不跑 parity golden 只能看到梯度范数异常大，本地极难归因到 wheel；7.2 wheel 对照稳定。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/pytorch/torchtitan/issues/4205

## 待定

### TRN-0136 `framework_version_drift_silent_loss_divergence` verl 版本升级后蒸馏 loss 自第一步静默分叉

`故障` · `active` · `rl` · `documented` · `var` · 发现 2026-08-26 · 旧号 KER.05

- **原因对象**：待定 / verl / 共有 trainer/数据/kernel 路径
- **原因行为**：verl v0.9.0 到 HEAD 之间的未定位变更使同脚本、同数据、同种子的蒸馏数值路径漂移，框架侧无 assert、无警告；根因尚未定位。
- **影响对象**：训练信号（静默错误）
- **影响详情**：多教师 OPD（GRPO+FSDP2+vLLM rollout/teacher）下 distillation/loss、teacher_mass、student_mass 自第一步起与基线版本不一致，全程有限、无 NaN、无 crash；B300 与寒武纪 MLU 均复现。
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/verl-project/verl/issues/7540；https://github.com/verl-project/verl/pull/7597
- **关联**：var:TRN-0135
