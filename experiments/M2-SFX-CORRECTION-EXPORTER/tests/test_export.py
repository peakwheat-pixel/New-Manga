"""AC4：双形态导出（T1a manifest + YOLO seg）→ training_data/sfx-corrections/；
AC6：互操作——导出物过 T1a load_manifest + assign_splits + TrainingSetBuilder，
分组隔离规则继承（注册表组继承 + challenge 单列 + 组原子性）。"""

from __future__ import annotations

import json

import pytest

from sfx_correction_exporter import fixture
from sfx_correction_exporter.export import (
    assign_splits_corrections,
    parse_dataset_yaml_names,
    run_export,
)
from sfx_correction_exporter.fixture import make_registry_manifest


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    root = tmp_path_factory.mktemp("export")
    fx = fixture.build_fixture_db(root / "fx")
    out = root / "sfx-corrections"
    summary = run_export(
        db_path=fx["db_path"], out_dir=out, registry_path=None,
        cases_path=fixture.repo_cases_json(), managed_root=None,
        seed=20261004, summary_out=root / "summary.json",
    )
    return fx, out, summary


def test_export_exit_shape(exported):
    fx, out, summary = exported
    assert summary["corrections_empty"] is False
    assert summary["scan"]["events_sfx_directed"] == 6
    assert summary["export"]["main_samples"] == 2      # H, I（complete → 正集）
    assert summary["export"]["auxiliary_samples"] == 4  # A, G, M, N（partial → 辅助集）
    assert summary["db_readonly"] is True


def test_manifest_files_are_t1a_format(exported):
    """AC4+AC6：manifest 可被 T1a load_manifest 直接消费（kind/逐样本校验）。"""
    from sfx_data_infra.atomicio import load_manifest
    _, out, _ = exported
    container, records = load_manifest(out / "manifest.json")
    assert container["kind"] == "sfx-data-infra/manifest@1"
    assert all(r.annotation_status == "complete" for r in records)
    aux_container, aux_records = load_manifest(out / "manifest-auxiliary.json")
    assert all(r.annotation_status == "partial" for r in aux_records)
    # 样本 id 唯一且双册零交集
    ids = [r.sample_id for r in records] + [r.sample_id for r in aux_records]
    assert len(ids) == len(set(ids)) == 6


def test_yolo_seg_labels(exported):
    """YOLO seg：类别 id=sfx（SFX_CLASS_MAP 值反查=2），多边形归一化到 [0,1]。"""
    from infrastructure.providers.detection_sfx import SFX_CLASS_MAP
    _, out, _ = exported
    sfx_id = next(k for k, v in SFX_CLASS_MAP.items() if v == "sfx")
    labels = sorted((out / "labels" / "train").glob("*.txt"))
    assert labels, "train labels 目录非空"
    for lp in labels:
        for line in lp.read_text(encoding="utf-8").strip().splitlines():
            parts = line.split()
            assert int(parts[0]) == sfx_id
            coords = [float(v) for v in parts[1:]]
            assert len(coords) >= 8 and len(coords) % 2 == 0
            assert all(0.0 <= v <= 1.0 for v in coords)
    # challenge 样本（rgM→BJ13）单列 challenge 目录
    challenge_labels = list((out / "labels" / "challenge").glob("*.txt"))
    assert len(challenge_labels) == 1


def test_dataset_yaml_names_order(exported):
    """T0 P3-6 硬约束：dataset.yaml names 顺序逐字 = SFX_CLASS_MAP。"""
    from infrastructure.providers.detection_sfx import SFX_CLASS_MAP
    _, out, _ = exported
    names = parse_dataset_yaml_names(out / "dataset.yaml")
    assert names == [SFX_CLASS_MAP[i] for i in sorted(SFX_CLASS_MAP)]


def test_images_copied_per_split(exported):
    _, out, _ = exported
    assert len(list((out / "images" / "train").glob("*"))) == 5   # A,G,H,I,N
    assert len(list((out / "images" / "challenge").glob("*"))) == 1  # M


def test_ac6_training_set_builder_consumes(exported):
    """AC6：正集+辅助集记录直接进 T1a TrainingSetBuilder；challenge 被设计性隔离。"""
    from sfx_data_infra.atomicio import load_manifest
    from sfx_data_infra.splits import TrainingSetBuilder
    _, out, _ = exported
    _, main_records = load_manifest(out / "manifest.json")
    _, aux_records = load_manifest(out / "manifest-auxiliary.json")
    builder = TrainingSetBuilder(main_records + aux_records)
    counts = builder.counts()
    assert counts.get("train", 0) + counts.get("val", 0) == 5  # challenge(rgM) 被隔离
    assert builder.status_distribution() == {"complete": 2, "partial": 3}
    # 组原子性：同组样本 split 一致
    by_group = {}
    for s in builder.samples:
        by_group.setdefault(s.group, set()).add(s.split)
    assert all(len(v) == 1 for v in by_group.values())


def test_ac6_builder_refuses_forbidden_splits(exported):
    from sfx_data_infra.atomicio import load_manifest
    from sfx_data_infra.splits import SplitAccessError, TrainingSetBuilder
    _, out, _ = exported
    _, records = load_manifest(out / "manifest.json")
    with pytest.raises(SplitAccessError):
        TrainingSetBuilder(records, allowed_splits=("train", "test"))


def test_split_inheritance_from_registry(tmp_path_factory):
    """分组隔离继承：注册表内已有的组 → 直接继承该组 split（挑战集规则优先）。"""
    root = tmp_path_factory.mktemp("inherit")
    fx = fixture.build_fixture_db(root / "fx")
    registry = make_registry_manifest(root / "registry", group="user-library/bk-fixture", split="val")
    out = root / "sfx-corrections"
    summary = run_export(
        db_path=fx["db_path"], out_dir=out, registry_path=str(registry),
        cases_path=fixture.repo_cases_json(), managed_root=None,
        seed=20261004, summary_out=root / "summary.json",
    )
    assert summary["eligibility"]["registry_status"] == "loaded"
    assert summary["export"]["split_inheritance"]["inherited_groups"] == ["user-library/bk-fixture"]
    assert summary["export"]["by_split"].get("val", 0) == 5      # B1 组继承 val
    assert summary["export"]["by_split"].get("challenge", 0) == 1  # rgM case 触发，优先于组继承


def test_dedup_registry_drops_duplicate_in_export(tmp_path_factory):
    """注册表含同图同框样本 → 导出时该纠错被去重剔除并在 summary 登记。"""
    from sfx_data_infra.atomicio import load_manifest
    root = tmp_path_factory.mktemp("dedup")
    fx = fixture.build_fixture_db(root / "fx")
    registry = make_registry_manifest(
        root / "registry", group="user-library/bk-fixture", split="train",
        duplicate_of_fixture=fx,
    )
    out = root / "sfx-corrections"
    summary = run_export(
        db_path=fx["db_path"], out_dir=out, registry_path=str(registry),
        cases_path=fixture.repo_cases_json(), managed_root=None,
        seed=20261004, summary_out=root / "summary.json",
    )
    assert summary["eligibility"]["duplicates_dropped"] == 1
    assert summary["eligibility"]["duplicates"][0]["duplicate_of"] == "reg-dup-000"
    _, aux = load_manifest(out / "manifest-auxiliary.json")
    assert all(s.sample_id != summary["eligibility"]["duplicates"][0]["sample_id"] for s in aux)


def test_export_deterministic(exported, tmp_path_factory):
    """同 fixture 同 seed 重跑：split 指纹一致（确定性可复现）。"""
    _, _, summary = exported
    root = tmp_path_factory.mktemp("rerun")
    fx = fixture.build_fixture_db(root / "fx")
    out = root / "sfx-corrections"
    summary2 = run_export(
        db_path=fx["db_path"], out_dir=out, registry_path=None,
        cases_path=fixture.repo_cases_json(), managed_root=None,
        seed=20261004, summary_out=root / "summary.json",
    )
    assert summary2["export"]["fingerprint"] == summary["export"]["fingerprint"]
