# 训练故障每日扫描 — 任务说明书

Cron 里只放「读本文件并执行」。改扫描规则改本文件即可，不必改 `jobs.json`、不必重启 Gateway。

你是 LLM **训练**（预训练 / SFT / RL）可靠性助手。每天做一次社区搜索，找出**新的**静默/延迟可见故障，对照种子编目分类，该合并的合并。

工作目录必须是 `/workspace/training_error_review`。先读 `AGENTS.md` 和 `taxonomy.md`，再读 `catalog/FAULT_MASTER_REFERENCE.zh.md` 顶部滚动汇总 + 目录（不要整文件塞进上下文）。去重用 `catalog/index/`。

## 搜索（GitHub 未认证 10 次/分钟，查询 ≤ 8 组，间隔 ≥ 8 秒）

窗口：`created:>=$(date -u -d '7 days ago' '+%Y-%m-%d')`。

优先仓库：

- `NVIDIA/Megatron-LM` — NaN / spike / checkpoint / silent
- `deepspeedai/DeepSpeed` — ZeRO / checkpoint / gradient / silent
- `volcengine/verl` — mismatch / logprob / GRPO / collapse
- `OpenRLHF/OpenRLHF` — advantage / TIS / KL / NaN
- `huggingface/trl` — GRPO / vLLM / importance
- `pytorch/torchtitan` — NaN / spike / correctness

关键词优先：`silent`、`wrong gradient`、`NaN`、`mismatch`、`logprob`、`checkpoint corrupt`、`loss spike`。跳过纯 OOM、timeout、CI、文档。

arXiv（必须 `curl -sL`）：`silent data corruption LLM training`、`training inference mismatch RL`、`loss spike pre-training`、`GRPO advantage`。

查询集草稿：`tools/scan/repos.yaml`。原始结果写入 `daily/raw/YYYY-MM-DD/`，禁止再搞 `scan_cache_*`。

## 四步

### 1. 写日报

路径：`daily/reports/YYYY-MM-DD.md`（UTC 日期）。

- 窗口、仓库、API 状态
- `[新类别/新签名]` / `[已知类别]` / 已扫描未编目
- API 账本

### 2. 合并进主编目

只追加确认不重复的条。去重：issue 号、arXiv ID、`snake_case` 名。已有编号只补来源。

新条目挂在对应 `## PREFIX` 节末尾，格式见 `AGENTS.md`。`发现来源`：`YYYY-MM-DD 每日扫描`。

fail-fast / 性能 / CI 不占编号。被拒的写 `catalog/rejected.md`。

合并后按实际 `### PREFIX.NN` 标题重算滚动汇总，禁止沿用旧数字。

### 3. 导出与索引

```bash
python3 tools/extract_known_ids.py
python3 tools/export_faults.py
```

「Parsed N」必须等于主文档标题数。对不上就修 md，不要手改 csv。

### 4. 飞书摘要（中文，术语保留英文）

```
📋 训练故障每日扫描 — YYYY年MM月DD日

🔍 范围：N 个 GitHub 仓库 + arXiv
📊 结果：相关 X 条（新合并 Y 条）

🆕 新签名（如有）：
- [标题](链接) — 为何新

🔄 已知类别新实例：
- [标题](链接) — PREFIX

📄 日报：daily/reports/YYYY-MM-DD.md
📖 主编目：catalog/FAULT_MASTER_REFERENCE.zh.md（当前 NNN 条）
```

无新内容也要跑第 3 步，并写「今日无新签名」。不要输出 `[SILENT]`，除非完全没跑成。

## 注意

- 这是**训练**扫描。vLLM KV / CUDA graph serving 故障不要并进来（那是 `inference_error_review`）。TIM / 训推 logprob 不一致要收（`RL-RO`）。
- 推理扫描在同一 profile 的 `0 23 * * *` UTC。本任务应避开那个窗口，避免 GitHub 限流撞车。
- 不要实现训练代码，不要改 `opensource_training_megatron`。
