# 笔记：数据与检查点

- 训练侧 ckpt 故障的典型形状是「加载成功」。键错位、专家置换、矩空、strictness 吞 unexpected key。
- MMIDIDX 魔数错误可以不崩，只喂垃圾 token。本地已有 `verify_dataset.py`。
- packing 要拆两条：attention 跨文档（DATA.02）和 label 跨文档（SFT.02）。
