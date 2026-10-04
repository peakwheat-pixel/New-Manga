"""AC2：分组隔离拆分器（桩——红绿纪律先红后绿）。"""

from __future__ import annotations

SEED_DEFAULT = 20261004
CHALLENGE_CASE_IDS = frozenset({"BJ13", "BJ14", "BJ15"})
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15


class SplitAccessError(PermissionError):
    """训练集构建器试图触碰 test/challenge 分组（设计上禁止）。"""


def derive_group_key_from_case(case: dict) -> str:
    """从 cases.json 记录推导来源作品组键（规则见 README §组键）。"""
    raise NotImplementedError


def assign_splits(samples, seed: int = SEED_DEFAULT, force: bool = False):
    """按组哈希分桶 train/val/test；挑战集单列；派生样本继承父 split。

    返回 {group: split} 映射，并就地写 sample.split。
    """
    raise NotImplementedError


def split_fingerprint(samples, seed: int) -> str:
    """划分冻结指纹：seed+全部 (sample_id, split) 的 sha256，用于复现校验。"""
    raise NotImplementedError


class TrainingSetBuilder:
    """训练数据构建器：设计上不可读 test/challenge 分组。"""

    def __init__(self, samples, allowed_splits=("train", "val")):
        raise NotImplementedError
