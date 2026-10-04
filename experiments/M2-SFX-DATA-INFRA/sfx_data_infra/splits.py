"""AC2：分组隔离拆分器。

规则（冻结于 manifest lock，见 README §组键）：
- 组键 = 来源作品组：densho810/<卷>、manga109/<作品名>、vasyanator2/<作品id>、
  peppercarrot/<E番号>（同 ep 的 ja/kr 语言版共享图像底图，强制同组防泄漏）。
- 挑战集优先：BJ13/14/15（provenance.case_id 命中）无条件单列 challenge。
- 组级哈希分桶：sha256(f"{seed}:{group}") 前 8 字节映射 [0,1)，<0.70 train、
  <0.85 val、否则 test——不依赖随机模块状态，seed 冻结即可复现。
- 派生样本（provenance.type=derived）继承 parent 的 split（fixpoint 传播）。
- TrainingSetBuilder 在构造期把 test/challenge 丢弃且禁止其进入 allowlist：
  API 表面不存在任何取回 test/challenge 的通道。
"""

from __future__ import annotations

import hashlib
import re
from typing import Iterable

from sfx_data_infra.schema import SampleRecord

SEED_DEFAULT = 20261004
CHALLENGE_CASE_IDS = frozenset({"BJ13", "BJ14", "BJ15"})
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
SPLIT_CLASSES = ("train", "val", "test", "challenge")


class SplitAccessError(PermissionError):
    """训练集构建器试图触碰 test/challenge 分组（设计上禁止）。"""


def derive_group_key_from_case(case: dict) -> str:
    """从 cases.json 记录推导来源作品组键。"""
    source = str(case.get("source", ""))
    sid = str(case.get("source_id", ""))
    if "densho810" in source:
        vol = sid.split("_")[0] if sid else "unknown"
        return f"densho810/{vol}"
    if "Manga109" in source or "manga109" in source:
        return f"manga109/{sid or 'unknown'}"
    if "Vasyanator2" in source:
        return f"vasyanator2/{sid.split('_')[0] if sid else 'unknown'}"
    if "peppercarrot" in source:
        m = re.match(r"^E(\d+)", sid)
        if m:
            return f"peppercarrot/E{m.group(1)}"
        m = re.search(r"(ep\d+[^_/]*?)__", source)
        return f"peppercarrot/{m.group(1) if m else 'unknown'}"
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:10]
    return f"other/{digest}"


def _bucket_for_group(group: str, seed: int) -> str:
    digest = hashlib.sha256(f"{seed}:{group}".encode("utf-8")).digest()
    u = int.from_bytes(digest[:8], "big") / float(1 << 64)
    if u < TRAIN_RATIO:
        return "train"
    if u < TRAIN_RATIO + VAL_RATIO:
        return "val"
    return "test"


def assign_splits(samples: Iterable[SampleRecord], seed: int = SEED_DEFAULT, force: bool = False):
    """就地写 sample.split，返回 {group: split}（挑战集组除外）。"""
    samples = list(samples)
    if not force:
        locked = [s for s in samples if s.split != "unassigned"]
        if locked:
            raise ValueError(f"{len(locked)} 个样本已有 split；重划需 force=True")

    # 1) 挑战集单列
    for s in samples:
        cid = s.provenance.get("case_id")
        if cid in CHALLENGE_CASE_IDS or s.provenance.get("challenge") is True:
            s.split = "challenge"

    # 2) 基础样本按组哈希分桶
    group_split: dict[str, str] = {}
    for s in samples:
        if s.split != "unassigned" or s.provenance.get("type") == "derived":
            continue
        if s.group not in group_split:
            group_split[s.group] = _bucket_for_group(s.group, seed)
        s.split = group_split[s.group]

    # 3) 派生继承（fixpoint：链式 derived 逐层传播）
    by_id = {s.sample_id: s for s in samples}
    changed = True
    while changed:
        changed = False
        for s in samples:
            if s.split != "unassigned" or s.provenance.get("type") != "derived":
                continue
            parent = by_id.get(s.provenance.get("parent_sample_id"))
            if parent is not None and parent.split != "unassigned":
                s.split = parent.split
                changed = True

    # 4) 残余（孤儿 derived）：按自身组桶
    for s in samples:
        if s.split == "unassigned":
            if s.group not in group_split:
                group_split[s.group] = _bucket_for_group(s.group, seed)
            s.split = group_split[s.group]
    return group_split


def split_fingerprint(samples: Iterable[SampleRecord], seed: int) -> str:
    """划分冻结指纹：seed + 全部 (sample_id, split) 的 sha256。"""
    items = sorted((s.sample_id, s.split) for s in samples)
    payload = f"{seed}|" + ";".join(f"{sid}={sp}" for sid, sp in items)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class TrainingSetBuilder:
    """训练数据构建器：设计上不可读 test/challenge 分组。

    - allowlist 含 test/challenge 直接抛 SplitAccessError；
    - 构造期过滤后内部仅保留 allowed 样本，原始列表不被持有；
    - 不提供任何全量/按 split 取样通道。
    """

    FORBIDDEN_SPLITS = ("test", "challenge")

    def __init__(self, samples: Iterable[SampleRecord], allowed_splits=("train", "val")):
        bad = [sp for sp in allowed_splits if sp in self.FORBIDDEN_SPLITS]
        if bad:
            raise SplitAccessError(
                f"训练集构建器禁止触碰 test/challenge 分组（请求了 {bad}）；"
                "评估走独立脚本，不与训练数据构建共享读取路径"
            )
        allowed = tuple(allowed_splits)
        self.allowed_splits = allowed
        self._samples = [s for s in samples if s.split in allowed]

    @property
    def samples(self) -> list[SampleRecord]:
        return list(self._samples)

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in self._samples:
            out[s.split] = out.get(s.split, 0) + 1
        return out
