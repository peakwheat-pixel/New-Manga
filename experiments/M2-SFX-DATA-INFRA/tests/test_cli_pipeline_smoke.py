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

    # r2 新-1 回归：summary 重生成不得降级——dedup/train_builder/import 统计仍在
    assert summary["dedup"]["exact_pairs"] == 0 and "perceptual_pairs" in summary["dedup"]
    assert summary["train_builder"]["excluded_negative_ids"] is not None
    assert summary["import_assets"]["imported"] == 58
    # r3 C1 回归：import_assets 的 boxes/assets_copied 必须重算而非丢失
    assert summary["import_assets"]["boxes"] == sum(
        len(s.boxes) for s in records if s.provenance.get("type") != "synthetic_render")
    assert summary["import_assets"]["assets_copied"] >= 1
    assert "not_recomputable_by_summary" in str(
        summary["synthetic_poc"]["gt_roundtrip_max_err_px"])
    # r2 新-2 回归：摘要内字体只记基名，无本机绝对路径
    for f in summary["synthetic_poc"]["fonts"]:
        assert "\\" not in f and "/" not in f, f"字体应为基名: {f}"
    # r2 新-6 回归：lock 形状不随写者漂移（pipeline 与 split/dedup 同键集）
    assert container["lock"].get("challenge_single_bucket") == ["BJ13", "BJ14", "BJ15"]
    # r2 新-6：dedup 子命令后 lock.fingerprint 仍与盘上 kept 集一致
    rc3 = cli.main(["--data-root", str(data_root), "dedup"])
    assert rc3 == 0
    container2, records2 = load_manifest(data_root / "manifest.full.json")
    from sfx_data_infra.splits import split_fingerprint as _sf
    assert container2["lock"]["fingerprint"] == _sf(records2, int(container2["seed"]))


def test_cmd_dedup_recomputes_fingerprint_on_real_drop(tmp_path):
    """r2 新-6 回归：真丢弃样本时 cmd_dedup 必须重算 lock.fingerprint（非透传旧值）。"""
    from sfx_data_infra.atomicio import load_manifest, write_manifest
    from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord
    from sfx_data_infra.splits import split_fingerprint

    data_root = tmp_path / "data"
    data_root.mkdir()
    def mk(sid, sha):
        return SampleRecord(
            sample_id=sid,
            image=ImageRef(path=f"{sid}.png", sha256=sha, width=64, height=64),
            boxes=[BoxAnnotation(polygon=[[0, 0], [8, 0], [8, 8], [0, 8]])],
            annotation_status="synthetic",
            provenance={"type": "synthetic_render", "render_seed": 1},
            group="synthetic/poc",
            split="train",
            created_at="2026-10-04T00:00:00+00:00",
        )
    samples = [mk("dup-a", "a" * 64), mk("dup-b", "a" * 64), mk("keep", "b" * 64)]
    write_manifest(data_root / "manifest.full.json", samples, seed=7,
                   extra={"lock": {"seed": 7, "method": "group-hash-rank-v2",
                                   "fingerprint": "stale-value", "frozen_at": "2026-10-04T00:00:00Z"}})
    rc = cli.main(["--data-root", str(data_root), "dedup"])
    assert rc == 0
    container, records = load_manifest(data_root / "manifest.full.json")
    assert len(records) == 2, "同图同框副本应被剔除"
    assert container["lock"]["fingerprint"] != "stale-value"
    assert container["lock"]["fingerprint"] == split_fingerprint(records, 7)
