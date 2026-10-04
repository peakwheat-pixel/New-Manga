"""AC2：底图库缺口检测与自动触发（独立于浏览器层，纯文件系统逻辑）。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# r2 P2-4：读侧魔数校验兜底（写侧原子写已保证不落半写文件）
PNG_MAGIC_HEX = "89 50 4e 47 0d 0a 1a 0a"


@dataclass
class GapReport:
    current: int
    required: int
    missing: int

    @property
    def has_gap(self) -> bool:
        return self.missing > 0


def count_backgrounds(bg_dir: Path) -> int:
    """底图库余量：bg_*.png 计数（目录不存在=0）。

    r2 P2-4：只数 PNG 魔数完整的文件——半写/坏文件不计入余量。
    """
    if not bg_dir.is_dir():
        return 0
    magic = bytes.fromhex(PNG_MAGIC_HEX)
    n = 0
    for p in bg_dir.glob("bg_*.png"):
        try:
            with open(p, "rb") as f:
                if f.read(8) == magic:
                    n += 1
        except OSError:
            continue
    return n


def check_gap(bg_dir: Path, min_backgrounds: int) -> GapReport:
    current = count_backgrounds(bg_dir)
    return GapReport(current=current, required=min_backgrounds,
                     missing=max(0, min_backgrounds - current))


def trigger_if_gap(
    bg_dir: Path,
    min_backgrounds: int,
    generate_fn: Callable[[int], None],
    dry_run: bool = False,
) -> tuple[GapReport, bool]:
    """缺口检查→触发生成。返回 (报告, 是否触发生成)。

    dry_run=True 只报告缺口，不调 generate_fn（AC2 --dry-run）。
    """
    report = check_gap(bg_dir, min_backgrounds)
    if not report.has_gap:
        return report, False
    if dry_run:
        return report, False
    generate_fn(report.missing)
    return report, True


def append_manifest(bg_dir: Path, entry: dict) -> Path:
    """底图索引追加（临时文件+replace 原子语义）。

    r2 P2-5：文件名 bg_index.json——旁路索引（非 T1a manifest container 口径），
    消费方为 gap 检查与人工审阅；T1a manifest 口径对接属 T1b。
    """
    manifest_path = bg_dir / "bg_index.json"
    entries: list[dict] = []
    if manifest_path.exists():
        entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries.append(entry)
    tmp = manifest_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(manifest_path)
    return manifest_path
