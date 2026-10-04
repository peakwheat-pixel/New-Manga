"""AC3：图感知哈希（dhash 自实现）+框级精确哈希。零新依赖：PIL+numpy+stdlib。"""

from __future__ import annotations

import hashlib
import json


def dhash_image(img, hash_size: int = 8) -> int:
    """图感知哈希：灰度缩到 (hash_size+1)x hash_size，横向梯度 64bit。"""
    from PIL import Image

    gray = img.convert("L").resize((hash_size + 1, hash_size), Image.LANCZOS)
    import numpy as np

    arr = np.asarray(gray, dtype=np.int16)
    diff = (arr[:, 1:] > arr[:, :-1]).flatten()
    value = 0
    for bit in diff:
        value = (value << 1) | int(bit)
    return value


def hamming_distance(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def box_exact_hash(polygon, cls: str, text, image_sha256: str) -> str:
    """框级精确哈希：坐标规范化到 0.1px + 类 + 文本 + 图 sha256 → sha256 hex。"""
    norm = [[round(float(x), 1), round(float(y), 1)] for x, y in polygon]
    payload = json.dumps(
        {"polygon": norm, "cls": cls, "text": text, "image": image_sha256},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_file(path, chunk_size: int = 1 << 20) -> str:
    """文件 sha256（流式，大图安全）。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
