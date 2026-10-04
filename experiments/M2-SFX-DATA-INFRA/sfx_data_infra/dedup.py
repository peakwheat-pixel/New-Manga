"""AC3：双去重——图级感知哈希（汉明距离）+框级精确哈希。

图 sha256 相同 → exact（最强证据，短路）；同图同框 → box-exact；
dhash 汉明距离 ≤ 阈值 → perceptual。优先级 exact > box-exact > perceptual；
loader 失败（缺图）记入 dhash_errors 不中断。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from sfx_data_infra.hash import box_exact_hash, dhash_image, hamming_distance
from sfx_data_infra.schema import SampleRecord


@dataclass
class DedupReport:
    exact_pairs: list[tuple[str, str]] = field(default_factory=list)
    perceptual_pairs: list[tuple[str, str, int]] = field(default_factory=list)
    box_exact_pairs: list[tuple[str, str]] = field(default_factory=list)
    duplicate_of: dict[str, str] = field(default_factory=dict)
    dhash_errors: list[str] = field(default_factory=list)


def _box_set_key(s: SampleRecord) -> tuple[str, ...]:
    """样本的框集合指纹（排序后的框精确哈希；含图 sha，天然区分不同图）。"""
    return tuple(sorted(box_exact_hash(b.polygon, b.cls, b.text, s.image.sha256) for b in s.boxes))


def find_duplicates(
    samples: Iterable[SampleRecord],
    image_sha_by_sample: Optional[dict[str, str]] = None,
    dhash_threshold: int = 8,
    image_loader: Optional[Callable] = None,
) -> DedupReport:
    """双去重扫描。

    判重语义：**同图+同框集合**才是重复样本（一页多实例=同图不同框=合法多样本）。
      1) exact：图 sha 相同 且 框集合指纹相同；
      2) perceptual：dhash 汉明距离 ≤阈值 且 框集合指纹相同且非空
         （重压缩/缩放的近似重复图+相同标注）。
    image_loader(path)->PIL.Image 提供时启用感知比对；缺图记 dhash_errors 不中断。
    """
    report = DedupReport()
    seen_exact: dict[tuple[str, tuple[str, ...]], str] = {}
    perceptual_seen: list[tuple[str, int, tuple[str, ...]]] = []

    for s in samples:
        if s.sample_id in report.duplicate_of:
            continue
        sha = s.image.sha256
        bkey = _box_set_key(s)
        key = (sha, bkey)

        # 1) 精确：同图+同框集合
        if key in seen_exact:
            first = seen_exact[key]
            report.exact_pairs.append((first, s.sample_id))
            report.box_exact_pairs.append((first, s.sample_id))
            report.duplicate_of[s.sample_id] = first
            continue
        seen_exact[key] = s.sample_id

        # 2) 感知：近似同图+相同非空标注
        if image_loader is not None and bkey:
            try:
                img = image_loader(s.image.path)
                h = dhash_image(img)
            except Exception as e:  # 缺图/解码失败不中断，登记
                report.dhash_errors.append(f"{s.sample_id}: {type(e).__name__}: {e}")
                continue
            for sid2, h2, bk2 in perceptual_seen:
                if bk2 == bkey and hamming_distance(h, h2) <= dhash_threshold:
                    report.perceptual_pairs.append((sid2, s.sample_id, hamming_distance(h, h2)))
                    report.duplicate_of[s.sample_id] = sid2
                    break
            perceptual_seen.append((s.sample_id, h, bkey))
    return report


def drop_duplicates(samples: Iterable[SampleRecord], report: DedupReport) -> list[SampleRecord]:
    """按 duplicate_of 剔除重复，保留首见（保持原顺序）。"""
    dropped = set(report.duplicate_of)
    return [s for s in samples if s.sample_id not in dropped]
