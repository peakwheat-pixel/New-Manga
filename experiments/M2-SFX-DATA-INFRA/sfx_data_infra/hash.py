"""AC3：图感知哈希 dhash+框级精确哈希（桩——红绿纪律先红后绿）。"""

from __future__ import annotations


def dhash_image(img, hash_size: int = 8) -> int:
    """图感知哈希（dhash 横向梯度，64bit），自实现避免新依赖。"""
    raise NotImplementedError


def hamming_distance(a: int, b: int) -> int:
    raise NotImplementedError


def box_exact_hash(polygon, cls: str, text, image_sha256: str) -> str:
    """框级精确哈希：规范化多边形+类+文本+图 sha256 → sha256 hex。"""
    raise NotImplementedError
