# 训练故障每日扫描 — 任务说明书

Cron 入口指向本文件，并明确要求校验后按本文件提交与推送；扫描细则统一维护在这里，不要直接编辑 `jobs.json` 或重启 Gateway。

你是 LLM **训练**（预训练 / SFT / RL）可靠性助手。每天做一次社区搜索，找出**新的**静默/延迟可见故障，对照种子编目分类，该合并的合并。

工作目录必须是 `/workspace/training_error_review`。先读 `AGENTS.md`、`taxonomy.md`、`catalog/SCHEMA.md`（条目字段与写法）和 `catalog/vocab.yaml`（受控词表与判定规则）。**结构化编目 `catalog/entries/*.yaml` 是唯一真源，只能用 `tools/catalog_tool.py` 读写**；`catalog/FAULT_MASTER_REFERENCE.zh.md` 已冻结为历史档案，不再追加或修改。当前条数用 `python3 tools/catalog_tool.py stats` 查看；去重用 `python3 tools/catalog_tool.py find <owner/repo#号 | URL | arXiv ID | slug | 编号>`。

## 搜索（GitHub 未认证 10 次/分钟，查询 ≤ 8 组，间隔 ≥ 8 秒）

**新增 NPU 必须执行：**先读 `NPU_SCAN.md` 和 `tools/scan/npu_sources.json`；使用 Cron 前置脚本的共享采集批次，按 training scope 扫描全部新增来源。缺少摘要时按该文件显式运行前置入口。原 GitHub 查询与 arXiv 不取消；NPU REST 列表分页是独立来源采集，不受“≤8组 GitHub Search”的仓库数限制。失败或未完整评估必须报告，NPU 不是拒收理由。

**如已配置环境变量 `GITHUB_TOKEN`**（`[ -n "$GITHUB_TOKEN" ]` 判断），所有 GitHub API 请求加 `-H "Authorization: Bearer $GITHUB_TOKEN"`（认证后 core 5000 次/小时、Search 30 次/分钟，间隔 ≥2 秒即可），并在日报注明“已认证”；未配置就按标题的未认证限额执行。token 只通过环境变量引用，不得写进日报、摘要、提交或命令回显（不要 `set -x`、`curl -v`、`echo $GITHUB_TOKEN`）。

窗口：`created:>=$(date -u -d '7 days ago' '+%Y-%m-%d')`；核对实际发出的每组查询的起始日、仓库、分页和 HTTP 状态。另复核近 7 日已入库来源的后续更新（尤其撤回根因、关闭误报、修复结论），并每日轮巡至少 3 个更早入库、长期未复核或仍标 `open` 的来源；额度不足时记录剩余范围。记录复核日、适用版本/配置和上游 issue/PR 状态；`closed`、PR merge、某版本已修与端到端验证不能混同，状态无变化不必天天改旧条目。来源更正才修改旧条目及当日报告，不因为编号已入库就跳过更新。来源去重键使用平台 + 仓库全名 + issue/PR 类型 + 字符串编号，新增平台必须以完整规范 URL 查重；不同 issue 的同机制也要比对。

优先仓库：

- `NVIDIA/Megatron-LM` — NaN / spike / checkpoint / silent
- `deepspeedai/DeepSpeed` — ZeRO / checkpoint / gradient / silent
- `verl-project/verl` — mismatch / logprob / GRPO / collapse
- `OpenRLHF/OpenRLHF` — advantage / TIS / KL / NaN
- `huggingface/trl` — GRPO / vLLM / importance
- `pytorch/torchtitan` — NaN / spike / correctness
- `modelscope/ms-swift` — packing / mask / template / GRPO

关键词优先：`silent`、`wrong gradient`、`NaN`、`mismatch`、`logprob`、`checkpoint corrupt`、`loss spike`。跳过纯 OOM、timeout、CI、文档。

arXiv（使用 `curl -fsSL` 并检查有效返回）：`silent data corruption LLM training`、`training inference mismatch RL`、`loss spike pre-training`、`GRPO advantage`。

原 GitHub 查询集：`tools/scan/repos.yaml`；新增 NPU 注册表：`tools/scan/npu_sources.json`（与公共采集器和推理库注册表一致）。原始结果写入 `daily/raw/YYYY-MM-DD/`，禁止再搞 `scan_cache_*`。

## 四步

### 1. 写日报

路径：`daily/reports/YYYY-MM-DD.md`（UTC 日期）。

- 窗口、仓库、API 状态
- `[新类别/新签名]` / `[已知类别]` / 已扫描未编目
- API 账本
- 每条拟收录候选给出可点击的原始来源 URL；失败或限流的查询明确标为未覆盖，不写“无新发现”。不要猜测任务结束时间（执行结束只能由调度器事后确定）。

### 2. 写入编目

只写入确认不重复的故障机制。先用 `catalog_tool.py find <规范URL>`（或 arXiv ID）定位来源，跨平台保留类型与原始字符串编号；GitHub 快捷号仅作 GitHub 旧引用补查，再比对机制：同一 issue 可能有独立 findings；不同 issue 的同机制用 `python3 tools/catalog_tool.py update <TRN-编号> --add-evidence <URL>` 补旧条来源/证据，不要只按编号跳过或重复入库。变体写 `coverage: var` 并在 `relations` 写目标条目：可写新编号 `TRN-xxxx`，也可直接写旧编号（如 `HW.01`），工具按编号表换算；**提交后核对返回的 `relations` 回显，目标标题必须是你要的那条**，不要凭记忆换算旧编号（推理库 10-13 曾因此把关系指错条目）。写清共享的具体失效机制和不同触发点；只同类目或同症状不够。

写入前对每个候选来源查以往判定：在近 14 天 `daily/reports/*.md` 和 `catalog/rejected.md`、`catalog/blindspots.md` 搜索完整规范 URL（迁移来源另查已核实旧别名），不按裸编号跨仓库/平台匹配。已判“留观”“拒收”或“已编目”的，除非有新证据（根因定位、维护者确认、任务影响实测等），否则维持原判定、不新建条目，并在日报写明“沿用 YYYY-MM-DD 判定”；改判时写清新证据。仅 GitHub 来源可另用 `catalog_tool.py find <owner/repo#号>` 补查无链接旧引用。仅因 NPU 非主平台被留观的候选允许按本次范围扩展重新评估，注明范围变更，不升级未经验证的证据。

每个新机制按 `catalog/SCHEMA.md` 写一个 JSON 对象（结构化字段 + `original`：机制、含可点击链接的来源、行为效应、`发现来源` 写 `YYYY-MM-DD 每日扫描`），存到当前 profile 的 `$TMPDIR` 下（未设置时先 `export TMPDIR=/root/.hermes/profiles/third/cache/scratch`）的临时文件，运行 `python3 tools/catalog_tool.py new --file "$TMPDIR/<名>.json"`。返回 `"ok": false` 就按 `errors` 逐条修改 JSON 后重交，最多 3 次；仍不通过的写进日报“留观”并说明原因。**必须写 JSON，不要手写 YAML，也不要直接编辑 `catalog/entries/`**。`original` 是完整的原始说明，深度与以往 Markdown 条目相同（代码/配置层面的原因、版本与配置、证据、触发条件）；结构化字段只是它的压缩，其中每个事实都必须能在 `original` 里找到——审计以 `original` 为准。看到修复 PR / 规避方法就写进 `mitigation.fix`（链接、状态、是否已发布；未核实就写未核实），否则写 `待定`。回访、来源更正用 `update --note …` / `update --set …`；关系增删用 `update <编号> --relation var:<新或旧编号> --drop-relation var:<错误编号>`。update 前先用 `find <目标条目编号 | 旧编号 | 规范URL>` 确认目标条目的编号和标题，并核对返回的回显。

fail-fast / 性能 / CI 不收录；论文仅证明检测方法有效、不证明训练侧 task-impacting 故障的，也不自动入故障目录。被拒的写 `catalog/rejected.md`，不确定的留观并交代缺什么证据。
分别写已观察症状、源码/修复支持的机制、条件性训练后果和任务影响实测值（无实测则明说）；版本/配置不明写未知。`verified` 只覆盖本地复现或有源码定位且因果闭合的具体结论；仅有上游 issue 自述及日志的标 `documented`，机制未定位则留观而不是编造根因。不要推断未实验的检测器预测；区分来源事实与自己的推断。

新条目状态是 `pending_audit`，由每日审计任务（UTC 02:00）复核定稿，扫描不需要也不应自行改状态。

### 3. 生成视图与校验

```bash
python3 tools/catalog_tool.py build      # views/CATALOG.zh.md、views/fault_catalog.csv（xlsx 生成但不入 Git）
python3 tools/catalog_tool.py validate   # 必须 "ok": true
```

validate 失败就修好再继续，不要手改 `views/`。另人工核对本次候选来源键 / `var` 目标及机制。脚本 PASS 不等于来源去重、状态或任务影响已验证；任一校验失败都不要宣称成功。

### 4. 本库 Git 提交与远程核验（每日必做）

- **扫描前置检查：**仅在 `/workspace/training_error_review` 操作。确认当前分支为 `main` 且上游为 `origin/main`，`git status --porcelain -uall` 为空；运行 `git fetch origin main` 后确认 `HEAD` 与 `origin/main` 相同。已有脏文件、暂存变更、本地待推提交、远程领先或 fetch 失败时，不要扫描、更不要自动覆盖/暂存/推送存量；立即报告阻塞。不得 `git pull`、`reset`、`push --force`。
- **验证通过后：**即使没有新条目也写当日有效扫描日报。检查本次 diff，只定向暂存本轮确有变更的 `catalog/entries/`（新增或修改的 YAML）、`catalog/id_registry.tsv`、`views/CATALOG.zh.md`、`views/fault_catalog.csv`、`catalog/rejected.md`、`catalog/blindspots.md`、`daily/reports/YYYY-MM-DD.md`；`views/fault_catalog.xlsx` 按 `.gitignore` 仅生成不入 Git；不要 `git add -A`，不要提交 `daily/raw/`、密钥、本地配置或用户无关修改。核对 `git diff --cached --name-only` 与暂存内容；对源码/Markdown/YAML 运行 `git diff --cached --check -- . ':!*.csv'`；无变更注明无需提交，不造空提交。
- 有变更时 `git commit -m "daily scan YYYY-MM-DD: training"`，再 `git push origin HEAD:main`；用 `git ls-remote origin refs/heads/main` 核对远程 SHA 等于本地 `HEAD`。提交/推送/核验失败要明确报告本地 commit ID、错误及远程未同步事实，不强推、不追加重复提交。Git 操作在最终摘要前完成。

### 5. 飞书摘要（中文，术语保留英文）

- **只在前台分段等待**：需要等待 GitHub/arXiv 限流重置时，每次命令调用里的 `sleep` 总共不超过 60 秒；要等更久就分多次调用，每次之后重查剩余额度或 `X-RateLimit-Reset`，循环到可用为止。**禁止单段长 sleep**（如 `sleep 600`），也不要把多段 sleep 塞进一次调用的循环里——运行时会把长时间运行的命令自动转入后台，导致等待失控、最终摘要丢失。不要启动后台进程或后台等待任务；即使之后收到任何后台进程结束的通知，**最后一条回复也必须重新给出完整扫描摘要**，不能只回应通知。


```
📋 训练故障每日扫描 — YYYY年MM月DD日

🔍 范围：原 GitHub 来源 + NPU 跨平台来源 + arXiv（写有效覆盖、批次实际窗口及缺口）
📊 结果：相关 X 条（新合并 Y 条）

🆕 新签名（如有）：
- [标题](链接) — 为何新

🔄 已知类别新实例：
- [标题](链接) — TRN-编号（var 目标）

📄 日报：daily/reports/YYYY-MM-DD.md
📖 编目：catalog/entries（当前 NNN 条；本次新增 TRN-xxxx… 待审计）
✅ 校验：PASS/FAIL 与未覆盖范围
🔗 Git：本地提交 ID 或无需提交；远程 SHA 核验结果/阻塞原因
```

无新内容也要跑第 3、4 步，并写「今日无新签名」。如果部分 API 查询失败，说明未覆盖范围及下次补查计划。不要输出 `[SILENT]`，除非完全没跑成。
所有临时校验完成后，**最后一条回复必须是上面的飞书扫描摘要**（含新增链接、日报路径和校验结果），不要让“临时验证通过”等中间说明覆盖最终摘要。

## 注意

- 这是**训练**扫描。vLLM KV / CUDA graph serving 故障不要并进来（那是 `inference_error_review`）。TIM / 训推 logprob 不一致要收（`RL-RO`）。
- 推理扫描在同一 profile 的 `0 23 * * *` UTC。本任务应避开那个窗口，避免 GitHub 限流撞车。
- 不要实现训练代码，不要改 `opensource_training_megatron`。
