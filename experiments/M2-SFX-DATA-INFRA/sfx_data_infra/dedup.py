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


def find_duplicates(
    samples: Iterable[SampleRecord],
    image_sha_by_sample: Optional[dict[str, str]] = None,
    dhash_threshold: int = 8,
    image_loader: Optional[Callable] = None,
) -> DedupReport:
    """双去重扫描。image_loader(path)->PIL.Image 提供时启用感知比对。"""
    report = DedupReport()
    seen_by_sha: dict[str, str] = {}
    dhash_seen: list[tuple[str, int]] = []
    box_first: dict[tuple[str, str], str] = {}

    for s in samples:
        if s.sample_id in report.duplicate_of:
            continue
        sha = s.image.sha256

        # 1) 图级精确：同图 sha
        if sha in seen_by_sha:
            report.exact_pairs.append((seen_by_sha[sha], s.sample_id))
            report.duplicate_of[s.sample_id] = seen_by_sha[sha]
            continue
        seen_by_sha[sha] = s.sample_id

        # 2) 框级精确：同图+同框（同图多框样本逐框比对）
        for box in s.boxes:
            bh = box_exact_hash(box.polygon, box.cls, box.text, sha)
            key = (sha, bh)
            if key in box_first:
                report.box_exact_pairs.append((box_first[key], s.sample_id))
                report.duplicate_of[s.sample_id] = box_first[key]
                break
            box_first[key] = s.sample_id
        if s.sample_id in report.duplicate_of:
            continue

        # 3) 图级感知：dhash
        if image_loader is not None:
            try:
                img = image_loader(s.image.path)
                h = dhash_image(img)
            except Exception as e:  # 缺图/解码失败不中断，登记
                report.dhash_errors.append(f"{s.sample_id}: {type(e).__name__}: {e}")
                continue
            for sid2, h2 in dhash_seen:
                dist = hamming_distance(h, h2)
                if dist <= dhash_threshold:
                    report.perceptual_pairs.append((sid2, s.sample_id, dist))
                    report.duplicate_of[s.sample_id] = sid2
                    break
            dhash_seen.append((s.sample_id, h))
    return report


def drop_duplicates(samples: Iterable[SampleRecord], report: DedupReport) -> list[SampleRecord]:
    """按 duplicate_of 剔除重复，保留首见（保持原顺序）。"""
    dropped = set(report.duplicate_of)
    return [s for s in samples if s.sample_id not in dropped]
