# 笔记：硬件 / 训练期 SDC

- 生产证据已经够用：Llama 3 1.4% 意外中断、Ma 等人的不健康节点对照、Gemini「一两周一次」。
- 关键形状不是 NaN，是**有限值坏更新**进 Adam，再进 ckpt。
- 检测尺度：fleet / 设备 / DP 副本对照（SCOUT），不是 per-step 语义探针。
- ABFT 对 GEMM 在 Ma 的生产故障上大多没用——故障经常不在 matmul。
- 与本地注入的关系：KER.01 是软件可控阳性，用来校准 monitor；不能代替真实 SDC 器件。
