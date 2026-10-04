"""AC3 红绿测试：manifest 原子写+中断恢复。

合同测试表场景「AC3 中断恢复」：kill 后重跑 manifest 完整（KO-FULLRUN env
事故教训：不产生半写状态）。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from sfx_data_infra.atomicio import (
    ManifestValidationError,
    cleanup_stale_tmp,
    load_manifest,
    write_manifest,
)
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord

REPOTests = Path(__file__).resolve().parents[1]  # experiments/M2-SFX-DATA-INFRA


def make_samples(n: int) -> list[SampleRecord]:
    out = []
    for i in range(n):
        out.append(
            SampleRecord(
                sample_id=f"s-{i:03d}",
                image=ImageRef(path=f"img/{i}.png", sha256=f"{i:064x}", width=64, height=64),
                boxes=[BoxAnnotation(polygon=[[1, 1], [9, 1], [9, 9], [1, 9]])],
                annotation_status="synthetic",
                provenance={"type": "synthetic_render", "render_seed": 20261004},
                group="synthetic/poc",
                created_at="2026-10-04T00:00:00+00:00",
            )
        )
    return out


def test_write_then_load_roundtrip(tmp_path):
    path = tmp_path / "manifest.json"
    samples = make_samples(10)
    write_manifest(path, samples, seed=20261004)
    container, loaded = load_manifest(path)
    assert container["kind"] == "sfx-data-infra/manifest@1"
    assert len(loaded) == 10
    assert [s.sample_id for s in loaded] == [s.sample_id for s in samples]


def test_corrupt_file_rejected(tmp_path):
    path = tmp_path / "manifest.json"
    write_manifest(path, make_samples(3))
    raw = path.read_bytes()
    path.write_bytes(raw[: len(raw) // 2])  # 模拟半写/损坏
    with pytest.raises(ManifestValidationError):
        load_manifest(path)


def test_crash_before_replace_leaves_old_manifest_intact(tmp_path):
    """写 v2 中途崩溃（os.replace 前 os._exit）→ 磁盘上仍是完整 v1。"""
    path = tmp_path / "manifest.json"
    write_manifest(path, make_samples(3), seed=1)
    old_raw = path.read_bytes()

    crash_script = """
import os, sys, json
sys.path.insert(0, r'{pkgparent}')
def crash_replace(src, dst):
    os._exit(1)
os.replace = crash_replace
from sfx_data_infra.atomicio import write_manifest
from sfx_data_infra.schema import SampleRecord
sample = json.loads(open(r'{onesample}', encoding='utf-8').read())
write_manifest(r'{mpath}', [SampleRecord.from_dict(sample)], seed=2)
""".format(
        pkgparent=str(REPOTests),
        onesample=str(_one_sample_json(tmp_path)),
        mpath=str(path),
    )
    proc = subprocess.run([sys.executable, "-c", crash_script], capture_output=True)
    assert proc.returncode != 0, "子进程应模拟崩溃退出"
    # 主文件完好 = v1 原样；tmp 残留存在
    assert path.read_bytes() == old_raw
    stale = list(tmp_path.glob("manifest.json*tmp*"))
    assert stale, "崩溃点在 replace 前，应存在 tmp 残留"

    # 重跑：先清残留再写 → 完整 v2，无半写
    cleanup_stale_tmp(path)
    write_manifest(path, make_samples(3) + make_samples(1)[:1], seed=2)
    container, loaded = load_manifest(path)
    assert len(loaded) == 4
    assert not list(tmp_path.glob("manifest.json*tmp*"))


def _one_sample_json(tmp_path: Path) -> Path:
    p = tmp_path / "_one_sample.json"
    if not p.exists():
        from sfx_data_infra.schema import SampleRecord

        s = make_samples(1)[0]
        d = s.to_dict()
        d["sample_id"] = "crash-sample"
        p.write_text(json.dumps(d), encoding="utf-8")
    return p


def test_load_rejects_wrong_kind(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"kind": "something/else", "samples": []}), encoding="utf-8")
    with pytest.raises(ManifestValidationError):
        load_manifest(path)


def test_load_manifest_falls_back_to_bak_when_main_missing(tmp_path):
    """r1 P2-6 回归：主路径缺失（写入中途崩溃第三态）时自动回退 .bak 上一完整版本。"""
    path = tmp_path / "manifest.json"
    write_manifest(path, make_samples(1), seed=6)  # 首写无旧版，不产 bak
    write_manifest(path, make_samples(2), seed=7)  # 二写保留首版为 .bak
    bak = path.with_name("manifest.json.bak")
    assert bak.exists(), "前置：重写已保留上一版 .bak"
    # 模拟 os.replace(path→bak) 完成、os.replace(tmp→path) 未执行的崩溃现场
    path.unlink()
    container, records = load_manifest(path)
    # 回退读的是"上一完整版本"（首版），非最后一次写入——崩溃现场的正确恢复语义
    assert len(records) == 1
    assert container["seed"] == 6
