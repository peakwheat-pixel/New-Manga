"""AC3：去重（桩——红绿纪律先红后绿）。"""

from __future__ import annotations


def find_duplicates(samples, image_sha_by_sample=None, dhash_threshold: int = 8, image_loader=None):
    """双去重：图级感知哈希（汉明距离≤阈值）+框级精确哈希。

    返回 DedupReport(exact_pairs, perceptual_pairs, duplicate_of)。
    """
    raise NotImplementedError


def drop_duplicates(samples, report):
    """按 duplicate_of 映射剔除重复，保留首见。"""
    raise NotImplementedError
