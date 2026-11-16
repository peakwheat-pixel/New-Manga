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


def test_manifest_is_structurally_identical_to_the_shared_writer(exported):
    """AC4「与 T1b 产物同构、训练侧零适配」—— **构造性证明**，不依赖 training_data/。

    AC4 的判定要求导出物与 T1b（批量数据生产）产物同构。`training_data/` 被 `.gitignore:13`
    排除，**不能**作为可复现依赖（新克隆里不存在）。所以这里证明的是更强的性质：

      T1b 产物与本导出物都由 `sfx_data_infra.atomicio.write_manifest` + 同一个
      `SampleRecord.to_dict()` 产出 ⇒ 容器形状与样本键集合**同源**，不是「碰巧像」。

    并且训练侧读取走同一个 `load_manifest`（见 test_manifest_files_are_t1a_format），
    因此「训练侧零适配」不是叙述，而是同一套 IO 模块的直接后果。

    若本机恰好存在 T1b 产物（开发者机器上会有），额外做一次**跨产物对账**；
    缺失时**跳过而不是失败** —— 否则这个测试在干净克隆里必然红。
    """
    from pathlib import Path

    from sfx_data_infra import MANIFEST_KIND, SCHEMA_VERSION
    from sfx_data_infra.atomicio import load_manifest
    from sfx_data_infra.schema import SampleRecord

    _, out, _ = exported
    container, records = load_manifest(out / "manifest.json")

    # 1) 容器形状 == 共享写入器的承诺
    assert container["kind"] == MANIFEST_KIND
    assert container["schema_version"] == SCHEMA_VERSION
    assert container["sample_count"] == len(records)
    assert {"kind", "schema_version", "created_at", "sample_count", "samples"} <= set(container)

    # 2) 样本键集合 == 共享记录类的键集合（不是手搓 dict）
    canonical_sample_keys = set(records[0].to_dict())
    for emitted in container["samples"]:
        assert set(emitted) == canonical_sample_keys

    # 3) 辅助册同源同构（双册本来就都走 write_manifest）
    aux_container, aux_records = load_manifest(out / "manifest-auxiliary.json")
    assert aux_container["kind"] == MANIFEST_KIND
    assert aux_container["sample_count"] == len(aux_records)
    for emitted in aux_container["samples"]:
        assert set(emitted) == canonical_sample_keys

    # 4) 跨产物对账（本地存在 T1b 产物时才做；.gitignore 排除，干净克隆里没有）
    t1b_path = Path(__file__).resolve().parents[3] / "training_data" / "sfx-v1" / "manifest.train.json"
    if not t1b_path.exists():
        pytest.skip(f"T1b 产物不在本地（{t1b_path} 被 .gitignore 排除）：跳过跨产物对账，"
                    "构造性同构证明（1)–3)）已成立")

    t1b_container = json.loads(t1b_path.read_text(encoding="utf-8"))
    assert t1b_container["kind"] == container["kind"], "T1b 与导出物的 manifest kind 必须相同"
    assert t1b_container["schema_version"] == container["schema_version"]
    assert {"kind", "schema_version", "sample_count", "samples"} <= set(t1b_container)
    t1b_sample_keys = set(t1b_container["samples"][0])
    assert t1b_sample_keys == canonical_sample_keys, (
        "T1b 样本键集合与导出物不相同 ⇒ 训练侧需要适配（AC4 不成立）："
        f"T1b-only={sorted(t1b_sample_keys - canonical_sample_keys)} "
        f"exporter-only={sorted(canonical_sample_keys - t1b_sample_keys)}"
    )

def test_yolo_seg_labels(exported):
    """YOLO seg（默认 --yolo-scope main，DSH r1 P2-1）：仅正集入树。

    类别 id=sfx（SFX_CLASS_MAP 值反查=2），多边形归一化到 [0,1]；
    辅助集（partial）样本不出现在 YOLO 树（显式 all 才混入）。
    """
    from infrastructure.providers.detection_sfx import SFX_CLASS_MAP
    _, out, summary = exported
    assert summary["export"]["yolo_scope"] == "main"
    sfx_id = next(k for k, v in SFX_CLASS_MAP.items() if v == "sfx")
    labels = sorted((out / "labels" / "train").glob("*.txt"))
    # 正集 complete 仅 rgH/rgI（split=train）→ train 恰 2 个标签
    assert len(labels) == 2
    for lp in labels:
        for line in lp.read_text(encoding="utf-8").strip().splitlines():
            parts = line.split()
            assert int(parts[0]) == sfx_id
            coords = [float(v) for v in parts[1:]]
            assert len(coords) >= 8 and len(coords) % 2 == 0
            assert all(0.0 <= v <= 1.0 for v in coords)
    # 辅助集样本不入 YOLO 树：无 challenge 标签（rgM=partial）、无 partial train 标签
    assert list((out / "labels" / "challenge").glob("*.txt")) == []
    all_label_ids = {lp.stem for lp in (out / "labels").rglob("*.txt")}
    assert all(sid.startswith("corr-") for sid in all_label_ids)
    assert len(all_label_ids) == 2


def test_yolo_scope_all_includes_auxiliary(tmp_path_factory):
    """--yolo-scope all（DSH r1 P2-1）：显式把辅助集混入 YOLO seg 树并登记 scope。"""
    root = tmp_path_factory.mktemp("scope-all")
    fx = fixture.build_fixture_db(root / "fx")
    out = root / "sfx-corrections"
    summary = run_export(
        db_path=fx["db_path"], out_dir=out, registry_path=None,
        cases_path=fixture.repo_cases_json(), managed_root=None,
        seed=20261004, yolo_scope="all", summary_out=root / "summary.json",
    )
    assert summary["export"]["yolo_scope"] == "all"
    assert summary["export"]["yolo_labels"] == 6  # main 2 + auxiliary 4（含 challenge rgM）
    train_ids = {lp.stem for lp in (out / "labels" / "train").glob("*.txt")}
    challenge_ids = {lp.stem for lp in (out / "labels" / "challenge").glob("*.txt")}
    assert len(train_ids) == 5 and len(challenge_ids) == 1  # 旧默认行为的全量形态


def test_dataset_yaml_names_order(exported):
    """T0 P3-6 硬约束：dataset.yaml names 顺序逐字 = SFX_CLASS_MAP。"""
    from infrastructure.providers.detection_sfx import SFX_CLASS_MAP
    _, out, _ = exported
    names = parse_dataset_yaml_names(out / "dataset.yaml")
    assert names == [SFX_CLASS_MAP[i] for i in sorted(SFX_CLASS_MAP)]


def test_images_copied_per_split(exported):
    """图像副本随 YOLO 树走（scope=main 默认 → 仅正集 2 张，辅助集不复制）。"""
    _, out, _ = exported
    assert len(list((out / "images" / "train").glob("*"))) == 2   # H,I（complete→正集）
    assert len(list((out / "images" / "challenge").glob("*"))) == 0  # M=partial，scope=main 不入树


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
