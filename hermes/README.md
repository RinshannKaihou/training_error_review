# Hermes 定时任务怎么挂到 Gateway

**结论：在本目录写说明书，你在 Gateway / `hermes cron` 里建 job。不要手改 `jobs.json`，也不用重启 Gateway。**

推理扫描已经证明这条路：`secondary` 上的 `bffa0c46a76d`（`0 23 * * *` UTC → 飞书 origin）跑了 21 次，全程没为改 cron 重启过 gateway。

## 谁在跑 cron

每个 profile 自己的 Gateway 进程带一个 ticker，读自己的：

| Profile | 任务文件 | 现在有什么 |
|---|---|---|
| `default` | `~/.hermes/cron/jobs.json` | 空 |
| `secondary` | `~/.hermes/profiles/secondary/cron/jobs.json` | 推理每日扫描（建议训练任务也挂这里） |
| `third` / `fourth` | 各自 `profiles/<name>/cron/jobs.json` | 与故障编目无关 |

挂到 **`secondary`**：和推理扫描同一只飞书机器人、同一套 `glm-5.2`、同一会话可投递。不要挂 `third`（cron 无代理，xAI 会超时）。

## 要不要重启 Gateway？

| 你改的东西 | 要不要重启 |
|---|---|
| `hermes cron create / edit / pause / resume / remove` | **不要**。ticker **每个 tick 重读** `jobs.json` |
| 改本仓库的 `hermes/daily_scan.prompt.md` | **不要**。前提是 cron 的 prompt 是「去读这个文件」，不是把全文嵌进 job |
| 改 `catalog/`、`AGENTS.md`、`taxonomy.md` | **不要**。下次跑会重新读盘 |
| 开/关飞书、改 `.env`、改 `config.yaml` 默认模型、pairing | **要**重启对应 profile 的 gateway |

所以：调度热更新，说明书热更新。重启只留给平台/凭证/默认模型。

推理任务把整份 prompt 嵌进了 `jobs.json`。改规则必须 `hermes cron edit`，否则下次跑的还是旧字。训练任务不要再这么干。

## 推荐挂法（你来建）

1. 确认本文件旁边的 [`daily_scan.prompt.md`](daily_scan.prompt.md) 已经写好。
2. 在 **secondary 的飞书会话**里 `/cron`，或在机器上：

```bash
hermes -p secondary cron create '30 0 * * *' \
  --name 'LLM训练故障模式每日扫描' \
  --workdir /workspace/training_error_review \
  --deliver origin \
  "$(cat <<'EOF'
读 /workspace/training_error_review/hermes/daily_scan.prompt.md，严格按该文件执行今日训练故障扫描。
工作目录必须是 /workspace/training_error_review。
模型必须用当前 profile 默认可达的 zai/glm-5.2（cron 无代理）。
EOF
)"
```

若 CLI 在非飞书上下文里建、`--deliver origin` 没有聊天来源，改成显式投递（与推理任务同一群）：

```bash
--deliver feishu:oc_fd1f5b8215a9c46fdfaa2cf64657090d
```

从飞书 `/cron` 建的好处：`deliver=origin` 和 `origin.chat_id` 会自动填成当前群，和推理扫描一样推摘要回来。

3. 核对（仍不必重启）：

```bash
hermes -p secondary cron list
hermes -p secondary cron status
```

4. 想先试跑一次：`hermes -p secondary cron run <id>`（等下一个 tick 开火，不是立刻同步跑完）。

建议时刻：`30 0 * * *` UTC = 北京 08:30，错开推理的 `0 23 * * *` UTC，避免 GitHub 未认证 10 次/分钟撞车。

## Cron prompt 里必须有、且 CLI 帮不上的

`hermes cron create` **没有** `--model`。模型来自该 profile 的 `config.yaml` 默认值。`secondary` 当前默认已是 `glm-5.2` / `zai`，直接建即可。

若以后有人在 `third`（xAI）上建训练扫描，必须先改那个 profile 的默认模型，或在能设 `model/provider` 的 UI/`cronjob` 工具里显式写成 `zai/glm-5.2`。cron 进程**不读** `.env` 里的代理。

`--workdir /workspace/training_error_review` 会注入本仓库 `AGENTS.md`，终端/文件工具的 cwd 也在这里。推理任务的 `workdir` 是 `null`，所以它只能把路径写死在超长 prompt 里。

## 超时

单次跑没有 3 分钟硬上限。看门狗是**空闲**超时，默认 600s 没有任何 tool/API 活动才杀；一直在搜 GitHub / 改文件可以跑很久。可用 `HERMES_CRON_TIMEOUT` 改，`0` 为不限制。

## 不要做的

- 不要手改 `jobs.json`（有跨进程锁，但和 ticker 抢写容易脏）。
- 不要把说明书全文再嵌进 job（失去文件热更新）。
- 不要在本对话里替你 `cron create`，除非你明确说「现在就挂」。投递会话、时刻、是否和推理扫描挤同一只机器人，应由你确认。
- 种子编目已有 64 条对照，**可以**挂了；没对照之前挂会把一切标成新签名。
