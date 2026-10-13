# 训练故障编目（pretrain / SFT / RL）

对照仓库：[`../inference_error_review`](../inference_error_review)（推理静默故障，572 条滚动编目）。

本仓库收集 **预训练 / SFT / RL** 里「进程绿、结果已坏」的故障模式。当前阶段是一次性摸清历史，写出基础报告和种子编目。每日洞察（Hermes cron）等种子编目可对照之后再挂。

## 先读

| 文件 | 用途 |
|---|---|
| [`AGENTS.md`](AGENTS.md) | 任意 CLI agent 的操作入口 |
| [`taxonomy.md`](taxonomy.md) | 类目、stage 轴、收录边界 |
| [`catalog/entries/`](catalog/entries) | **唯一编目真源**：每条一个 YAML，只能用 `tools/catalog_tool.py` 写入；字段见 [`catalog/SCHEMA.md`](catalog/SCHEMA.md) |
| [`views/CATALOG.zh.md`](views/CATALOG.zh.md) | 由条目生成的浏览视图（另有 `views/fault_catalog.csv`） |
| [`catalog/FAULT_MASTER_REFERENCE.zh.md`](catalog/FAULT_MASTER_REFERENCE.zh.md) | 2026-10-13 起冻结的历史档案 |
| [`foundation/REPORT.md`](foundation/REPORT.md) | 基础报告（历史摸底） |

## 目录

```
catalog/          编目 SoT（entries/）+ 词表/规范 + 负结果；FAULT_MASTER 与 index/ 为冻结档案
foundation/       当前主战场：基础报告、矿源、工作笔记
daily/            后期每日洞察（现在只有约定，不开 cron）
views/            由 catalog/entries 生成的 Markdown/CSV 视图
exports/          旧 md → csv 导出（冻结档案）
tools/            catalog_tool.py（写入/查询/生成/校验）、catalog_audit.py + daily_audit.sh（每日审计）；旧导出脚本为档案
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
