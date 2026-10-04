"""AC2 红绿测试：分组隔离拆分器。

合同测试表场景「AC2 派生同集合」：构造同底图派生样本断言 split 键一致。
另覆盖：挑战集单列、seed 冻结可复现、训练集构建器不可读 test。
"""

from __future__ import annotations

import pytest

from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord
from sfx_data_infra.splits import (
    CHALLENGE_CASE_IDS,
    SEED_DEFAULT,
    SplitAccessError,
    TrainingSetBuilder,
    assign_splits,
    derive_group_key_from_case,
    split_fingerprint,
)


def make_sample(sample_id: str, group: str, provenance: dict) -> SampleRecord:
    return SampleRecord(
        sample_id=sample_id,
        image=ImageRef(path=f"{sample_id}.png", sha256="a" * 64, width=100, height=100),
        boxes=[BoxAnnotation(polygon=[[0, 0], [10, 0], [10, 10], [0, 10]])],
        annotation_status="synthetic",
        provenance=provenance,
        group=group,
        created_at="2026-10-04T00:00:00+00:00",
    )


def base_samples() -> list[SampleRecord]:
    """3 组普通样本 + 1 组父派生对 + BJ13/14/15 挑战样本。"""
    samples = [
        make_sample("g1-a", "peppercarrot/E04", {"type": "asset_case", "case_id": "K11"}),
        make_sample("g1-b", "peppercarrot/E04", {"type": "asset_case", "case_id": "K12"}),
        make_sample("g2-a", "manga109/AisazuNihaIrarenai", {"type": "asset_case", "case_id": "J01"}),
        make_sample("g3-a", "vasyanator2/724815", {"type": "asset_case", "case_id": "K01"}),
        # 派生对：parent g3-a 的同底图派生（裁切/增强/合成）
        make_sample(
            "g3-a-deriv",
            "vasyanator2/724815",
            {"type": "derived", "parent_sample_id": "g3-a", "op": "crop"},
        ),
    ]
    for cid in sorted(CHALLENGE_CASE_IDS):
        samples.append(
            make_sample(f"chal-{cid}", f"densho810/vol03", {"type": "asset_case", "case_id": cid})
        )
    return samples


def test_groups_are_atomic_no_split_within_group():
    samples = base_samples()
    assign_splits(samples, seed=SEED_DEFAULT)
    by_group: dict[str, set] = {}
    for s in samples:
        if s.split == "challenge":
            continue
        by_group.setdefault(s.group, set()).add(s.split)
    for group, splits in by_group.items():
        assert len(splits) == 1, f"组 {group} 被拆散: {splits}"


def test_derived_inherits_parent_split():
    samples = base_samples()
    assign_splits(samples, seed=SEED_DEFAULT)
    parent = next(s for s in samples if s.sample_id == "g3-a")
    deriv = next(s for s in samples if s.sample_id == "g3-a-deriv")
    assert deriv.split == parent.split, "同底图派生样本必须继承父 split"
    assert deriv.split in ("train", "val", "test")


def test_challenge_cases_single_bucket():
    samples = base_samples()
    assign_splits(samples, seed=SEED_DEFAULT)
    chal = [s for s in samples if s.provenance.get("case_id") in CHALLENGE_CASE_IDS]
    assert len(chal) == 3
    assert all(s.split == "challenge" for s in chal), "BJ13/14/15 必须单列 challenge"
    rest = [s for s in samples if s.provenance.get("case_id") not in CHALLENGE_CASE_IDS]
    assert all(s.split != "challenge" for s in rest)


def test_seed_frozen_reproducible():
    s1 = base_samples()
    s2 = base_samples()
    m1 = assign_splits(s1, seed=SEED_DEFAULT)
    m2 = assign_splits(s2, seed=SEED_DEFAULT)
    assert m1 == m2
    assert split_fingerprint(s1, SEED_DEFAULT) == split_fingerprint(s2, SEED_DEFAULT)
    assert all(s.split != "unassigned" for s in s1)


def test_all_three_splits_reachable_or_documented():
    """分桶覆盖性冒烟：多组输入下 train 必然非空（比例 70%）。"""
    samples = [make_sample(f"g{i}", f"grp/{i:03d}", {"type": "asset_case", "case_id": f"X{i}"}) for i in range(30)]
    assign_splits(samples, seed=SEED_DEFAULT)
    splits = {s.split for s in samples}
    assert "train" in splits


def test_training_builder_cannot_read_test_or_challenge():
    samples = base_samples()
    assign_splits(samples, seed=SEED_DEFAULT)
    builder = TrainingSetBuilder(samples)
    got_splits = {s.split for s in builder.samples}
    assert got_splits <= {"train", "val"}
    assert "test" not in got_splits
    assert "challenge" not in got_splits
    # API 表面不存在任何取回 test/challenge 的通道
    assert not hasattr(builder, "all_samples")
    assert not hasattr(builder, "get_by_split")


def test_training_builder_rejects_test_in_allowlist():
    samples = base_samples()
    with pytest.raises(SplitAccessError):
        TrainingSetBuilder(samples, allowed_splits=("train", "test"))
    with pytest.raises(SplitAccessError):
        TrainingSetBuilder(samples, allowed_splits=("challenge",))


def test_group_key_rules():
    # peppercarrot：同 ep 的 ja/kr 共享图像底图 → 同组（防泄漏关键）
    ja = {"case_id": "K11", "language": "ja", "source": "https://www.peppercarrot.com/ja/webcomic/ep04_Stroke-of-genius__sources.html", "source_id": "E04P02"}
    kr = {"case_id": "O09", "language": "kr", "source": "https://www.peppercarrot.com/kr/webcomic/ep04_Stroke-of-genius__sources.html", "source_id": "E04P05"}
    assert derive_group_key_from_case(ja) == derive_group_key_from_case(kr)
    # densho810：同卷同作品组
    bj06 = {"case_id": "BJ06", "source": "https://densho810.com/free/", "source_id": "vol03_p0056"}
    bj13 = {"case_id": "BJ13", "source": "https://densho810.com/free/", "source_id": "vol03_p0048"}
    assert derive_group_key_from_case(bj06) == derive_group_key_from_case(bj13)
    assert derive_group_key_from_case(bj06).startswith("densho810/")
    # manga109：按作品名分组
    j1 = {"case_id": "J01", "source": "https://huggingface.co/datasets/hal-utokyo/Manga109", "source_id": "AisazuNihaIrarenai"}
    j2 = {"case_id": "J02", "source": "https://huggingface.co/datasets/hal-utokyo/Manga109", "source_id": "AosugiruHaru"}
    assert derive_group_key_from_case(j1) != derive_group_key_from_case(j2)
    # vasyanator2：按数据集作品 id 前缀分组
    k1 = {"case_id": "K01", "source": "https://huggingface.co/datasets/Vasyanator2/cleaned_webtoon_dataset", "source_id": "724815_1"}
    assert derive_group_key_from_case(k1) == "vasyanator2/724815"
