# 每日扫描日报目录

`daily/reports/YYYY-MM-DD.md` 存放 Hermes 每日扫描（UTC 00:30）产出的日报。

- 编目唯一真源为 `catalog/entries/*.yaml`，通过 `tools/catalog_tool.py` 读写与查重，不再对照冻结档案 `catalog/FAULT_MASTER_REFERENCE.zh.md` 或 `catalog/index/`。
- 被拒候选追加写入 `catalog/rejected.md`（带完整规范 URL），观测/检测工具盲区写入 `catalog/blindspots.md`。
- `daily/raw/` 仅用于本地未追踪原始响应缓存（由 `.gitignore` 忽略），禁止提交进 Git。
