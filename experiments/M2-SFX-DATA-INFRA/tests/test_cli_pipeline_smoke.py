"""r1 返修回归：CLI 管线级冒烟（真实素材+渲染，覆 P1-2/P1-3/P1-4/P2-2/P2-5）。

跑真实 step_import（读盘上存量资产）+ step_synth（真实渲染）+ split/dedup/
build-train/summary 全链，断言 r1 四项 P1 的修复在产物层成立。
"""

from __future__ import annotations

import json
from pathlib import Path

from sfx_data_infra import cli
from sfx_data_infra.atomicio import load_manifest


def test_step_synth_marks_occluded(tmp_path):
    """r1 P1-4：含遮挡贴片的合成样本 box.occluded 必须为 True（口径落地非仅 README）。"""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    samples, _info = cli.step_synth(tmp_path, now, count=6)
    by_occ = {(s.boxes[0].occluded, s.provenance.get("occlusion") is not None) for s in samples}
    assert (True, True) in by_occ, "应有 occluded=True 且带遮挡参数的样本"
    assert (False, False) in by_occ, "应有无遮挡样本 occluded=False"
    for s in samples:
        assert s.boxes[0].occluded == (s.provenance.get("occlusion") is not None)


def test_pipeline_end_to_end_r1_fixes(tmp_path):
    """r1 四项 P1 在产物层的端到端验证 + summary 子命令可跑（P2-2）。"""
    data_root = tmp_path / "data"
    summary_out = tmp_path / "manifest_summary.json"
    rc = cli.main([
        "--data-root", str(data_root),
        "pipeline", "--synth-count", "6", "--summary-out", str(summary_out),
    ])
    assert rc == 0

    container, records = load_manifest(data_root / "manifest.full.json")
    # P1-3：合成样本必须全部落 train（pinned）
    syn = [s for s in records if s.annotation_status == "synthetic"]
    assert syn, "管线应产出合成样本"
    assert {s.split for s in syn} == {"train"}, f"合成组应整组钉 train，实际 { {s.split for s in syn} }"
    # P1-4：遮挡标记落地
    occ_samples = [s for s in syn if s.provenance.get("occlusion") is not None]
    assert occ_samples and all(s.boxes[0].occluded for s in occ_samples)
    # P2-5：lock.fingerprint 与落盘产物一致
    from sfx_data_infra.splits import split_fingerprint
    lock = container["lock"]
    assert lock["fingerprint"] == split_fingerprint(records, int(container["seed"]))
    assert lock["pinned_groups"] == cli.PINNED_GROUPS

    # P1-2：负样本不进 manifest.train.json
    _, train_records = load_manifest(data_root / "manifest.train.json")
    assert not any(s.provenance.get("negative") is True for s in train_records), \
        "空框负样本不得进入训练 manifest"

    # P2-2：summary 子命令不再 KeyError
    rc2 = cli.main(["--data-root", str(data_root), "summary", "--summary-out", str(summary_out)])
    assert rc2 == 0
    summary = json.loads(summary_out.read_text(encoding="utf-8"))
    assert summary["synthetic_poc"]["by_split"] == {"train": len(syn)}
    assert "absolute" not in summary["data_root_gitignored"]
