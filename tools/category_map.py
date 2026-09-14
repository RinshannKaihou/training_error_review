"""Prefix → domain category. ID scheme is PREFIX.NN from day one."""

CATEGORY_ORDER = [
    "硬件/训练SDC",
    "数值/混精",
    "并行/通信",
    "检查点",
    "数据管线",
    "优化器",
    "重计算/卸载",
    "训练kernel",
    "MoE",
    "loss发散",
    "SFT",
    "RL-reward",
    "RL-advantage",
    "RL-KL",
    "RL-rollout",
    "观测性",
]

PREFIX_CATEGORY = {
    "HW": "硬件/训练SDC",
    "NUM": "数值/混精",
    "PAR": "并行/通信",
    "CKPT": "检查点",
    "DATA": "数据管线",
    "OPT": "优化器",
    "ACT": "重计算/卸载",
    "KER": "训练kernel",
    "MOE": "MoE",
    "LOSS": "loss发散",
    "SFT": "SFT",
    "RL-RWD": "RL-reward",
    "RL-ADV": "RL-advantage",
    "RL-KL": "RL-KL",
    "RL-RO": "RL-rollout",
    "OBS": "观测性",
}


def prefix_of(fault_id: str) -> str:
    if "." not in fault_id:
        return ""
    return fault_id.rsplit(".", 1)[0]


def resolve_category(fault_id: str) -> str:
    return PREFIX_CATEGORY.get(prefix_of(fault_id), "未分类")
