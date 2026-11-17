# 训练故障编目（pretrain / SFT / RL）

对照仓库：[`../inference_error_review`](../inference_error_review)（推理期静默故障编目）。检索工具：`/workspace/RAG/fault_review`（读本仓库与推理库的只读快照）。

本仓库收集 **预训练 / SFT / RL** 期「进程正常、结果已坏」的静默或延迟可见故障模式。每日 UTC 00:30 由 Hermes cron 执行增量扫描（状态 `pending_audit`），UTC 02:00 由每日审计复核定稿。

## 先读

| 文件 | 用途 |
|---|---|
| [`AGENTS.md`](AGENTS.md) | 任意 CLI agent 的操作入口 |
| [`taxonomy.md`](taxonomy.md) | 类目、stage 轴、收录边界 |
| [`catalog/entries/`](catalog/entries) | **唯一编目真源**：每条一个 YAML，只能用 `tools/catalog_tool.py` 读写；字段见 [`catalog/SCHEMA.md`](catalog/SCHEMA.md)，词表见 [`catalog/vocab.yaml`](catalog/vocab.yaml) |
| [`catalog/patterns/`](catalog/patterns) | 故障模式层，由条目的 `var` 关系派生（`catalog_tool.py pattern-sync`） |
| [`catalog/rejected.md`](catalog/rejected.md) / [`catalog/blindspots.md`](catalog/blindspots.md) | 已拒收候选与观测/框架外盲区记录 |
| [`views/`](views) | 由条目生成的浏览视图：`CATALOG.zh.md`、`fault_catalog.csv`、`fault_catalog.xlsx`（`catalog_tool.py build`，不要手改） |
| [`hermes/daily_scan.prompt.md`](hermes/daily_scan.prompt.md) | 每日扫描执行规范 |
| [`NPU_SCAN.md`](NPU_SCAN.md) | NPU 跨平台来源扫描规范 |
| [`catalog/FAULT_MASTER_REFERENCE.zh.md`](catalog/FAULT_MASTER_REFERENCE.zh.md) | 2026-10-13 起冻结的历史档案 |

## 目录

```
catalog/          编目真源（entries/、patterns/）、SCHEMA.md、vocab.yaml、id_registry.tsv、rejected.md、blindspots.md、audit/
tools/            catalog_tool.py（读写/查询/生成/校验）、catalog_audit.py + daily_audit.sh（每日审计）、scan/
views/            由 catalog/entries 生成的 Markdown/CSV/XLSX 视图
daily/reports/    每日扫描日报 YYYY-MM-DD.md
hermes/           每日扫描提示词与运行说明
foundation/       种子期基础调研与笔记档案
exports/          2026-10-13 切换前的历史导出档案
docs/             分析短文，不是编目
```

## 自动化依赖与约定

- 每晚扫描和审计开始前均要求 `main` 分支、`git status --porcelain -uall` 为空、fetch 后 `HEAD == origin/main`；手工改动必须通过 `validate` 并提交推送。
- 训练期机制（含反向算子、优化器、检查点以及 RL 训推 logprob 一致性 TIM）写在这里；纯 serving 期机制留在 `inference_error_review`。训推共有底层故障在两侧证实各自影响后通过 `relations: [{kind: cross}]` 双向关联。
- 不收纯 OOM、NCCL timeout、启动期 fail-fast 报错、纯性能回退、单测比对脚本自身缺陷或 C++ `aclnn` 契约外非法入参（GIGO）。
