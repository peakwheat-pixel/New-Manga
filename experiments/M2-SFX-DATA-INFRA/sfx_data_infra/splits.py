"""AC2：分组隔离拆分器。

规则（冻结于 manifest lock，见 README §组键）：
- 组键 = 来源作品组：densho810/<卷>、manga109/<作品名>、vasyanator2/<作品id>、
  peppercarrot/<E番号>（同 ep 的 ja/kr 语言版共享图像底图，强制同组防泄漏）。
- 挑战集优先：BJ13/14/15（provenance.case_id 命中）无条件单列 challenge。
  **登记（r1 P2-10 裁定）**：challenge 单列优先于组原子性——同组其余样本仍按组
  分桶（当前 densho810/vol03 余量落 train），challenge 评测分数存在同卷上下文
  泄漏风险，仅用于挑战对照，不得用于泛化声明。
- 组级排序切片分桶（method=group-hash-rank-v2）：组按 sha256(seed:group) 排序后
  按比例切 train/val/test——确定性可复现，组数足够时保证各集合非空（不依赖随机
  模块状态，seed 冻结即可复现）。**注意**：这是排序切片，不是阈值分桶。
- 组级钉扎（pinned）：显式指定 group→split（如合成组钉 train，r1 P1-3）；
  被钉的组不参与比例切片。
- 派生样本（provenance.type=derived）继承 parent 的 split（fixpoint 传播）；
  **登记**：孤儿 derived（parent 不在集内）按自身单组走 `_ranked_group_split`，
  因 n<4 恒返 train——语义即"孤儿派生一律 train"。
- TrainingSetBuilder 在构造期把 test/challenge 丢弃且禁止其进入 allowlist；
  并默认排除 provenance.negative=true 的空框负样本（r1 P1-2：是否使用弱负样本
  由 T1b 显式决策，builder 默认不送训练）。
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


def _ranked_group_split(groups: list[str], seed: int) -> dict[str, str]:
    """组级排序切片分桶（method=group-hash-rank-v2）。

    组按 sha256(seed:group) 排序后按比例切 train/val/test——确定性可复现，
    且组数足够时保证各集合非空（纯阈值哈希在小组数下可能 val 空集）。
    """
    ranked = sorted(groups, key=lambda g: hashlib.sha256(f"{seed}:{g}".encode("utf-8")).digest())
    n = len(ranked)
    if n < 4:
        return {g: "train" for g in ranked}
    n_train = max(1, round(TRAIN_RATIO * n))
    n_val = max(1, round(VAL_RATIO * n))
    out: dict[str, str] = {}
    for i, g in enumerate(ranked):
        if i < n_train:
            out[g] = "train"
        elif i < n_train + n_val:
            out[g] = "val"
        else:
            out[g] = "test"
    return out


def assign_splits(
    samples: Iterable[SampleRecord],
    seed: int = SEED_DEFAULT,
    force: bool = False,
    pinned: dict[str, str] | None = None,
):
    """就地写 sample.split，返回 {group: split}（挑战集与钉扎组除外）。

    force=True：先按挑战集规则重判 challenge，其余样本全部重置为 unassigned
    再重新分配——即真正允许换 seed 重划（r1 P2-4 修复：此前 force 只补划
    unassigned，旧 split 原样保留导致重划失效）。
    pinned：组级钉扎 {group: split}，优先级仅次于 challenge（r1 P1-3：合成组
    钉 train，避免单一大合成组被整组切进 val）。
    """
    samples = list(samples)
    if not force:
        locked = [s for s in samples if s.split != "unassigned"]
        if locked:
            raise ValueError(f"{len(locked)} 个样本已有 split；重划需 force=True")
    pinned = dict(pinned or {})

    # 1) 挑战集单列（优先级最高）
    for s in samples:
        cid = s.provenance.get("case_id")
        if cid in CHALLENGE_CASE_IDS or s.provenance.get("challenge") is True:
            s.split = "challenge"

    # 1b) force：非 challenge 样本全部重置后重划
    if force:
        for s in samples:
            if s.split != "challenge":
                s.split = "unassigned"

    # 2) 钉扎组（不参与比例切片）
    group_split: dict[str, str] = {}
    for g, sp in pinned.items():
        group_split[g] = sp

    # 3) 基础样本按组排序切片分桶（跳过 challenge/已钉组）
    base_groups = sorted({
        s.group for s in samples
        if s.split == "unassigned"
        and s.provenance.get("type") != "derived"
        and s.group not in group_split
    })
    if base_groups:
        group_split.update(_ranked_group_split(base_groups, seed))
    for s in samples:
        if s.split != "unassigned" or s.provenance.get("type") == "derived":
            continue
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
                group_split.update(_ranked_group_split([s.group], seed))
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

    def __init__(
        self,
        samples: Iterable[SampleRecord],
        allowed_splits=("train", "val"),
        exclude_negative: bool = True,
    ):
        bad = [sp for sp in allowed_splits if sp in self.FORBIDDEN_SPLITS]
        if bad:
            raise SplitAccessError(
                f"训练集构建器禁止触碰 test/challenge 分组（请求了 {bad}）；"
                "评估走独立脚本，不与训练数据构建共享读取路径"
            )
        allowed = tuple(allowed_splits)
        self.allowed_splits = allowed
        self.exclude_negative = exclude_negative
        self.excluded_negative_ids: list[str] = []
        picked: list[SampleRecord] = []
        for s in samples:
            if s.split not in allowed:
                continue
            if exclude_negative and s.provenance.get("negative") is True:
                self.excluded_negative_ids.append(s.sample_id)
                continue
            picked.append(s)
        self._samples = picked

    @property
    def samples(self) -> list[SampleRecord]:
        return list(self._samples)

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in self._samples:
            out[s.split] = out.get(s.split, 0) + 1
        return out

    def status_distribution(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in self._samples:
            out[s.annotation_status] = out.get(s.annotation_status, 0) + 1
        return out
