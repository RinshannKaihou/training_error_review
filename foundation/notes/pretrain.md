# 笔记：预训练

- loss spike 的机制文献是 Spike No More（小子层 + 大捷径），不是「把 LR 改小」。
- 本实验室已有两条独立早警：QK 谱 climb→collapse、`realized_var`；MoE 再加 `per_token_entropy`。
- 长跑静默退化（LOSS.04）是监控产品要打的象限：loss 绿、能力掉。
