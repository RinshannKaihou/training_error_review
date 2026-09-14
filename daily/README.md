# 每日洞察约定

**现在不要往这里写日报，也不要挂 cron。** 等 `catalog/` 种子编目可对照之后，再启用 Hermes 任务。

## 以后的落点

| 路径 | 用途 |
|---|---|
| `daily/reports/YYYY-MM-DD.md` | 人读日报 |
| `daily/raw/YYYY-MM-DD/` | 当天 API 原始结果（只此一种缓存名） |

禁止再出现推理侧的 `scan_cache_*` / `scan_raw_*` / 根目录 `daily_scan_*.md`。

## 日报结构（预留）

1. 扫描窗口、仓库、API 状态
2. 重点新签名
3. 已知类别的新实例
4. 已扫描未编目（fail-fast / 性能 / CI）
5. API 调用账本

分类只有两档：`[已知类别]` / `[新类别/新签名]`。对照物是 `catalog/FAULT_MASTER_REFERENCE.zh.md` 和 `catalog/index/`。

## 查询集

稳定查询写在 `tools/scan/repos.yaml`，不要按日复制 shell。

建议与推理 cron 错开：推理 `0 23 * * *` UTC，训练 `30 0 * * *` UTC，避免 GitHub 未认证 10 次/分钟撞车。
