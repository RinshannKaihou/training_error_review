# LLM 训练故障模式编目（结构化视图）

> 本文件由 `python3 tools/catalog_tool.py build` 从 `catalog/entries/*.yaml` 生成，**不要手改**。
> 字段说明见 `catalog/SCHEMA.md`，受控词表见 `catalog/vocab.yaml`。

共 282 条；状态：active 282

| 原因子系统 | 条数 |
|---|---|
| 硬件 | 9 |
| 算子/内核 | 15 |
| 编译器 | 6 |
| 运行时/执行 | 6 |
| 集合通信 | 3 |
| 并行切分 | 20 |
| 量化 | 7 |
| 位置编码 | 5 |
| 分词/模板 | 7 |
| 模型定义 | 6 |
| 权重/检查点 | 27 |
| 数据管线 | 27 |
| 优化器 | 28 |
| 损失计算 | 17 |
| MoE路由 | 12 |
| 重计算/卸载 | 11 |
| RL训练回路 | 57 |
| 观测/评测 | 14 |
| 配置/参数 | 3 |
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
- **来源**：https://gitcode.com/cann/ops-math/issues/3553；https://gitcode.com/cann/ops-math/issues/3560；https://gitcode.com/cann/ops-nn/issues/6582；https://gitcode.com/cann/ops-nn/issues/6605

### TRN-0276 `add_rms_norm_gamma_mul_order_overflow` Ascend 950 AddRmsNorm 先乘 gamma 致 FP32 溢出

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / cann / AddRmsNorm trans 模板乘法顺序
- **原因行为**：Ascend 950 regbase 的 AddRmsNorm/InplaceAddRmsNorm trans 模板按 (x1+x2)*gamma*rstd 计算，先乘 gamma 可使 FP32 中间结果提前超范围，输出 Inf。
- **影响对象**：数值结果（数值异常）
- **影响详情**：输入与 gamma 均有限、归一化结果也应有限时输出 Inf：x1=2^32、gamma=2^100 期望 2^100 实得 Inf；24 条 trans 溢出用例修复前全 FAIL、修复后全 PASS。
- **改进措施**：检测 对 AddRmsNorm 输出做有限性抽检；固定输入回归用例（x1=2^32、gamma=2^100）。；修复 修复 MR !11953（open 未合入）：先以 FP32 计算 xSum*rstd 再乘 gamma，两次乘法间不转回低精度；两个算子 arch35 ST CSV 各加一条固定输入回归用例。https://gitcode.com/cann/ops-nn/merge_requests/11953
- **来源**：https://gitcode.com/cann/ops-nn/issues/6679；https://gitcode.com/cann/ops-nn/merge_requests/11953

### TRN-0279 `torch_npu_oob_index_silent_wrong` torch_npu 索引/损失算子越界输入静默错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / torch_npu / gather/scatter/CE 越界校验缺失
- **原因行为**：torch_npu 对 gather/scatter/index_put/cross_entropy/nll_loss 缺 host 越界校验：越界读拿垃圾、越界写被丢弃，无异常；CPU/CUDA 会 raise。
- **影响对象**：数值结果（静默错误）
- **影响详情**：A3 真机确定性复现：cross_entropy 越界 target 返回数值不报错；gather 越界返回垃圾；scatter_ 越界写被静默丢弃。数据侧 bug 被无声吞掉。
- **改进措施**：检测 训练前对 index/target 做范围断言；与 CPU 参考实现对账。；修复 待定（F.embedding、Tensor.select 越界在 NPU 仍会 raise，说明该校验可实现；issue 建议 host 端补齐对齐 CPU/CUDA 语义，未见修复 MR）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5296

### TRN-0282 `add_rms_norm_tiling_mode_bypass_silent` AddRmsNorm tiling 不拦 PRE/POST 模式静默算错越界

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：算子/内核 / cann / AddRmsNorm tiling 分派校验
- **原因行为**：Ascend 950 regbase 仅支持普通模式，aclnn 层已拦截但 tiling 层分派时不校验 norm_key：绕过 aclnn 的路径（GE 直构/TTK 直调）传 PRE/POST 形态不被拒。
- **影响对象**：数值结果（静默错误）
- **影响详情**：regbase tiling 未剥离 PRE/POST 模式 gamma 前导 1，numRow 少算（(B,S,H) 只算 B 行），输出大半为未初始化内存；kernel 无条件写 rstd/xOut 越界写；全程不报错。aclnn 公开接口与 A2/A3 不受影响。
- **改进措施**：检测 TTK/GE 直调路径下对输出与参考对账；PR #11564 反例 UT（pre/post_mode_rejected）可作探针。；修复 已修复：PR #11564（merged）tiling 层拒绝 PRE/POST 模式返回 GRAPH_FAILED，修复后 ophost UT 30/30、opapi UT 18/18、950+910b 定向 CI 全过。https://gitcode.com/cann/ops-nn/pull/11564
- **来源**：https://gitcode.com/cann/ops-nn/issues/6482；https://gitcode.com/cann/ops-nn/pull/11564

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

### TRN-0281 `inductor_mod_eliminate_noncontig_reduction` torch_npu Inductor 取模消除错致非连续归约错值

`故障` · `active` · `shared` · `documented` · `NEW` · 发现 2026-10-15

- **原因对象**：编译器 / torch_npu / eliminate_modular 取模消除
- **原因行为**：eliminate_modular 处理乘积时只用其中一个变量的长度判断取模是否多余：对 (7*r)%7 按 5%7==5 误判可消除，化简为 7*r（实际恒为 0），小归约展开后第一列 load 地址错误。
- **影响对象**：数值结果（静默错误）
- **影响详情**：Inductor default 后端、shape[5,7]/stride[14,1] 非连续输入小归约（unroll_reductions_threshold=8）：amax 期望 62 实得 84、amin 同错；地址错非浮点误差，Triton 源码中地址已错。
- **改进措施**：检测 非连续输入下编译前后 amax/amin 对账；生成 Triton 源码检查首列地址表达式。；修复 待定（issue open，2026-10-08；修复方向：coeff*(numel-1)<divisor*modulus 才消除并返回 FloorDiv，多变量/负系数/未知范围保留原式）
- **来源**：https://gitcode.com/Ascend/pytorch/issues/5295

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
- **改进措施**：检测 待定；修复 待定
- **来源**：https://github.com/deepspeedai/DeepSpeed/issues/8692

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
- **来源**：https://github.com/huggingface/trl/issues/6773

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
- **来源**：https://github.com/huggingface/trl/issues/7274；https://github.com/huggingface/trl/pull/7294
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
- **来源**：https://arxiv.org/abs/2510.11370

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
- **来源**：https://github.com/huggingface/trl/issues/6789；https://github.com/huggingface/trl/issues/6945；https://github.com/huggingface/trl/pull/7627

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

- **原因对象**：观测/评测 / opensource_training_megatron / stability monitor 启用开关
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
