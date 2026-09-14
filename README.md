# 训练故障编目（pretrain / SFT / RL）

对照仓库：[`../inference_error_review`](../inference_error_review)（推理静默故障，572 条滚动编目）。

本仓库收集 **预训练 / SFT / RL** 里「进程绿、结果已坏」的故障模式。当前阶段是一次性摸清历史，写出基础报告和种子编目。每日洞察（Hermes cron）等种子编目可对照之后再挂。

## 先读

| 文件 | 用途 |
|---|---|
| [`AGENTS.md`](AGENTS.md) | 任意 CLI agent 的操作入口 |
| [`taxonomy.md`](taxonomy.md) | 类目、stage 轴、收录边界 |
| [`catalog/FAULT_MASTER_REFERENCE.zh.md`](catalog/FAULT_MASTER_REFERENCE.zh.md) | **唯一编目真源** |
| [`foundation/REPORT.md`](foundation/REPORT.md) | 基础报告（历史摸底） |

## 目录

```
catalog/          编目 SoT + 负结果 + 去重索引
foundation/       当前主战场：基础报告、矿源、工作笔记
daily/            后期每日洞察（现在只有约定，不开 cron）
exports/          md → csv/xlsx 单向导出
tools/            导出、去重、稳定查询集
hermes/           cron prompt 版本化（后置）
docs/             分析短文，不是编目
```

根目录只留 `README.md` / `AGENTS.md` / `taxonomy.md`。日报、raw、xlsx、bak 不准堆在根上。

## 和推理目录的关系

- 训练期机制写在这里；serving 期机制留在 `inference_error_review`。
- 交叉条目（例如带毒 ckpt 被推理加载）写双向指针，不复制正文。
- 不把推理 572 条搬过来。

## 本仓库不做什么

- 不实现训练注入或监控（继续住在 `../opensource_training_megatron`）。
- 不把 OOM / NCCL timeout / 启动 assert 目录化，除非它们骗过健康检查。
- Phase 1 完成前不启用 Hermes 每日任务。
