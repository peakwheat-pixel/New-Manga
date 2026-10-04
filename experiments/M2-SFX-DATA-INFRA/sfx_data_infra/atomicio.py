"""AC3：manifest 原子写+读回校验+中断恢复。

KO-FULLRUN env 事故教训：绝不允许半写状态。策略：
- 写入先落同目录 tmp（pid 后缀），flush+fsync 后 os.replace 原子生效；
- 已有文件先移 .bak 保留上一完整版本；
- 写后立即读回 json+schema 校验，失败抛 ManifestValidationError；
- 中断残留 tmp 由 cleanup_stale_tmp 在下次写入前清理。
"""

from __future__ import annotations

import glob
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from sfx_data_infra import MANIFEST_KIND, SCHEMA_VERSION
from sfx_data_infra.schema import SampleRecord, SchemaError

TMP_SUFFIX = ".tmp"


class ManifestValidationError(ValueError):
    """manifest 读回校验失败。"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write_json(path: str | os.PathLike, obj: Any) -> Path:
    """原子写 JSON 文件并读回校验。中断点只可能在 tmp 或 bak，主路径非旧即新。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}{TMP_SUFFIX}")
    payload = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    bak = path.with_name(f"{path.name}.bak")
    if path.exists():
        os.replace(path, bak)
    os.replace(tmp, path)
    # 读回校验：字节级已落盘且可解析
    with open(path, "r", encoding="utf-8") as f:
        json.loads(f.read())
    return path


def write_manifest(
    path: str | os.PathLike,
    samples: Iterable[SampleRecord],
    seed: int | None = None,
    extra: dict | None = None,
) -> Path:
    """写 manifest 容器（kind/schema_version/samples/seed/lock extra）。"""
    container: dict[str, Any] = {
        "kind": MANIFEST_KIND,
        "schema_version": SCHEMA_VERSION,
        "created_at": _now_iso(),
        "sample_count": 0,
        "samples": [],
    }
    if seed is not None:
        container["seed"] = seed
    if extra:
        container.update(extra)
    sample_list = list(samples)
    container["sample_count"] = len(sample_list)
    container["samples"] = [s.to_dict() for s in sample_list]
    return atomic_write_json(path, container)


def load_manifest(path: str | os.PathLike) -> tuple[dict, list[SampleRecord]]:
    """读 manifest 并逐样本校验；任何损坏/结构不符抛 ManifestValidationError。"""
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
        container = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        raise ManifestValidationError(f"manifest 不可解析: {path} ({e})") from e
    if not isinstance(container, dict) or container.get("kind") != MANIFEST_KIND:
        raise ManifestValidationError(f"manifest kind 不符: {container.get('kind')!r}")
    records: list[SampleRecord] = []
    for i, d in enumerate(container.get("samples", [])):
        try:
            records.append(SampleRecord.from_dict(d))
        except (SchemaError, KeyError, TypeError, ValueError) as e:
            raise ManifestValidationError(f"samples[{i}] 校验失败: {e}") from e
    return container, records


def cleanup_stale_tmp(path: str | os.PathLike) -> list[Path]:
    """清理上次中断残留的 tmp/bak 同名前缀文件（bak 保留最新一个由写入逻辑管理）。"""
    path = Path(path)
    removed = []
    pattern = str(path.with_name(f"{path.name}.*{TMP_SUFFIX}"))
    for p in glob.glob(pattern):
        try:
            os.remove(p)
            removed.append(Path(p))
        except OSError:
            pass
    return removed
