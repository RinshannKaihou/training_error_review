# 训练故障基础报告（2026-08-17）

对照：`../inference_error_review` 用 21 天每日扫描堆出 572 条推理静默故障。训练侧从零开始。本报告是 Phase 1 的人读总览；可检索条目在 `catalog/FAULT_MASTER_REFERENCE.zh.md`。

## 1. 范围

收预训练 / SFT / RL 里**进程绿、结果已坏**的模式。

- 要：有限值坏梯度、带毒 ckpt、packing 串文档、GRPO 统计偏置、训推 logprob 不一致、监控空文件。
- 不要：纯 OOM、NCCL timeout、启动 assert、把 572 条推理故障搬过来。

栈：Megatron（实验室主栈）+ DeepSpeed / TRL / OpenRLHF / veRL 文献。NeMo / ColossalAI 种子期只留查询槽。

## 2. 推理侧抄什么、改什么

抄：单一 md 真源、机制/来源/行为三件套、`NEW` vs `var:`、负结果另册、计数以标题为准、cron 后置。

改：

| 推理侧的债 | 这里怎么避 |
|---|---|
| A / 1–15 / K 三套编号 | 第一天就用 `HW.01` 这种前缀 |
| 日报堆在根目录 | `daily/reports/` + `daily/raw/YYYY-MM-DD/` |
| 6700 行单文件当唯一索引 | `catalog/index/` 给去重 |
| cron prompt 只活在 jobs.json | `hermes/` 后置，先不挂 |
| 新条目写没测过的隐藏态预测 | 种子条目不写检测器脑补 |

训练和推理的主轴也不同。推理问「这次前向的 hidden/logits 还能信吗」。训练问「这条更新该不该进权重 / 这个 advantage 是不是在优化另一张概率表」。

## 3. 历史故障图（按机制，不按仓库）

### 3.1 硬件把一次错更新烤进模型

Ma et al.（2502.12340）第一次把生产「不健康节点」和健康节点对照着训：扰动经常不大，但足以换一个局部最优，有时打出 spike。Llama 3 54 天快照里 GPU SDC 占意外中断 1.4%。有限值占 SDC 的约 99%（2605.04213），所以 NaN 守卫几乎没用。发布之后这就是推理目录里的 `1.6`：serving 前向干净，权重已经错了。

### 3.2 软件归约可以做到和 SDC 一样静默

DeepSpeed #8224：ZeRO-2 + bf16，子模块一步用两次，跨 rank 归约在梯度攒完前开火。单卡 bitwise 对，多卡主损失约翻倍。LR=0 的 warmup 会把它完全藏住。这是种子编目里最干净的「框架正确性」样本。

### 3.3 预训练不稳是有机制的，不是玄学

Spike No More：梯度上界由子层谱范数和残差捷径决定，需要对 embedding 做 scale/LN。QK-norm / softcap 压的是另一条尖峰（logits 增长）。本实验室用 FA backward 尾数截断当阳性：谱和鞅时钟先动，loss 后动。

### 3.4 SFT 的静默面几乎全是数据契约

模板、packing 边界、loss mask、tokenizer 行对齐。优化器很少是根因。偏好对调会让 DPO 稳定地学反的。

### 3.5 RL 的第一故障是 TIM，第二故障是 GRPO 会计

VeXact（2605.14220）：只关掉训推错配，MoE REINFORCE 就能从塌缩变成继续涨分。recompute 和 bypass 改的是不同的目标，PPO clip 盖不住。OpenRLHF #1295 证明「TIS」开关可以没做 clamp，一条序列就能写出 inf/NaN。

GRPO 会计是另一条线：组 std=0、低方差题被放大、序列平均制造长度偏置。DrGRPO / DAPO 改的是公式，不是硬件。

### 3.6 观测性可以先于模型骗人

本实验室：`STABILITY_MONITOR_ENABLED` 被 torchrun 吞掉，留下 0 字节 JSONL。ByteDance 2509.16293 把 hang、轨迹偏离、无明确报错列为 implicit failure。没有 step 的监控不是漏检，是没输入。

## 4. 种子编目怎么读

十六个前缀，`stage` 是字段。本地已跑过的标 `verified`（KER、部分 DATA/OBS/MOE）。其余多数是 `documented`。

交叉条目（SDC 继承、from_pretrained 随机初始化、内核同步语义）在本目录写训练视角，推理 ID 只做指针。见 `docs/overlap_with_inference.md`。

## 5. 已知缺口（故意留给以后）

1. veRL / NeMo 的 GitHub 查询本轮被 API 422，历史 issue 还没系统挖。
2. 没有逐条 Megatron 长尾（576 个含 NaN 的命中里大多是功能 PR）。
3. 没有把本地注入剂量曲线写进编目——那是实验仓库的事。
4. 没有启用每日 cron。没有对照基准的扫描会把一切标成新签名。

## 6. 下一步

1. 需要人工翻的时候，用 `catalog/index/` 去重后再加条。
2. 导出脚本已能过「标题数 = 行数」门闩。改主文档后跑 `python3 tools/export_faults.py` 和 `python3 tools/extract_known_ids.py`。
3. Phase 3：写 `hermes/daily_scan.prompt.md`，挂 `secondary`，`30 0 * * *` UTC，模型 `glm-5.2`。
