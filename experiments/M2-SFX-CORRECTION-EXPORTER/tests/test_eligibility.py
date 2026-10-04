"""AC3：资格判定——许可继承（全备案不阻断）/ 几何确认度门 / 与 T1a 已册样本去重。"""

from __future__ import annotations

import pytest

from sfx_correction_exporter import fixture
from sfx_correction_exporter.db import open_readonly
from sfx_correction_exporter.eligibility import (
    CONSTANTS,
    filter_sfx_directed,
    match_case,
    resolve_license,
)
from sfx_correction_exporter.scanner import scan_corrections
from sfx_correction_exporter.samples import load_pages


@pytest.fixture(scope="module")
def fx(tmp_path_factory):
    return fixture.build_fixture_db(tmp_path_factory.mktemp("fx3"))


@pytest.fixture(scope="module")
def ctx(fx):
    conn = open_readonly(fx["db_path"])
    try:
        scan = scan_corrections(conn)
        pages = load_pages(conn)
    finally:
        conn.close()
    cases_index = fixture.load_cases_index()
    return fx, scan, pages, cases_index


def test_frozen_constants_registered():
    """阈值冻结登记：四条规则常量必须存在且不可空（AC3「阈值冻结并登记」）。"""
    assert CONSTANTS["GEOMETRY_CONFIRM_RULE"].startswith("v1:")
    assert CONSTANTS["PARTIAL_ROUTING"] == "auxiliary manifest（不入正集，可选入辅助集）"
    assert CONSTANTS["DEDUP_LEVEL"].startswith("exact+box-exact")
    assert CONSTANTS["LICENSE_RULE"] == "user_ruling_2026-10-04_训练质量效率优先_许可降权备案: 全备案不阻断"
    assert CONSTANTS["EXPORTABLE_TARGET"] == "sfx"


def test_filter_sfx_directed(ctx):
    _, scan, _, _ = ctx
    keep, dropped = filter_sfx_directed(scan.events)
    assert sorted((e.region_id, e.revision_no) for e in keep) == [
        ("rgA", 2), ("rgG", 4), ("rgH", 2), ("rgI", 2), ("rgM", 2), ("rgN", 2),
    ]
    assert sorted((e.region_id, e.revision_no) for e, _ in dropped) == [("rgF", 3), ("rgK", 2)]
    assert all("non-sfx" in reason for _, reason in dropped)


def test_match_case_by_page_filename(ctx):
    """页映射判据：source_filename 茎 == cases.json 页文件茎（page_filename_for_case 语义）。"""
    _, _, pages, cases_index = ctx
    case, basis = match_case(pages["pgBJ13"], cases_index)
    assert case is not None and case["case_id"] == "BJ13"
    assert basis == "page_filename"
    case2, basis2 = match_case(pages["pg1"], cases_index)
    assert case2 is None and basis2 == "unmatched"


def test_resolve_license_inherited_and_blocking_false(ctx):
    _, _, pages, cases_index = ctx
    case, _ = match_case(pages["pgBJ13"], cases_index)
    lic = resolve_license(case, pages["pgBJ13"])
    assert lic["license_class"] == "commercial_use_permitted_attribution"
    assert lic["redistributable"] is True
    assert lic["blocking"] is False  # 二次裁决：全备案不阻断


def test_resolve_license_user_library_fallback(ctx):
    _, _, pages, cases_index = ctx
    case, _ = match_case(pages["pg1"], cases_index)
    assert case is None
    lic = resolve_license(case, pages["pg1"])
    assert lic["license_class"] == "user_library_source"
    assert lic["blocking"] is False


def test_geometry_gate_routing_via_status(ctx):
    """complete → 正集；partial → 辅助集（AC3「不入正集可选入辅助集」）。"""
    _, scan, _, _ = ctx
    from sfx_correction_exporter.samples import geometry_confidence
    complete_ids = {
        e.region_id for e in scan.events
        if e.survives and e.sfx_directed
        and geometry_confidence(scan.chains[e.region_id])[0] == "complete"
    }
    partial_ids = {
        e.region_id for e in scan.events
        if e.survives and e.sfx_directed
        and geometry_confidence(scan.chains[e.region_id])[0] == "partial"
    }
    assert complete_ids == {"rgH", "rgI"}
    assert partial_ids == {"rgA", "rgG", "rgM", "rgN"}


def _mk_record(sid, sha, polygon, group="user-library/book-fixture"):
    from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord
    return SampleRecord(
        sample_id=sid,
        image=ImageRef(path="x.png", sha256=sha, width=64, height=48),
        boxes=[BoxAnnotation(polygon=polygon, cls="sfx")],
        annotation_status="partial",
        provenance={"type": "asset_case", "source": "revision_chain_correction"},
        group=group,
        created_at="2026-10-04T00:00:00Z",
    )


def test_dedup_against_registry_drops_exact(fx, ctx):
    """与 T1a 已册样本查重：同图 sha+同框集合 → 精确重复，册内优先保留。"""
    from sfx_correction_exporter.eligibility import dedup_against_registry
    _, scan, _, _ = ctx
    from sfx_correction_exporter.samples import build_sample
    e = [e for e in scan.events if e.region_id == "rgA" and e.survives][0]
    sample = build_sample(
        e, scan.chains["rgA"], {"page_id": e.page_id, "book_id": "bk1"},
        image_path=fx["page_images"][e.page_id],
        group="user-library/book-fixture", case=None,
        license_info=fixture.USER_LIBRARY_LICENSE, now_iso="2026-10-04T00:00:00Z",
    )
    registry = [_mk_record("reg-001", sample.image.sha256, sample.boxes[0].polygon)]
    kept, dropped = dedup_against_registry([sample], registry)
    assert kept == []
    assert len(dropped) == 1
    assert dropped[0]["sample_id"] == sample.sample_id
    assert dropped[0]["duplicate_of"] == "reg-001"


def test_dedup_keeps_distinct_box_same_image(fx, ctx):
    """同图不同框 = 合法新样本（T1a dedup 判重语义：同图+同框集合才是重复）。"""
    from sfx_correction_exporter.eligibility import dedup_against_registry
    _, scan, _, _ = ctx
    from sfx_correction_exporter.samples import build_sample
    e = [e for e in scan.events if e.region_id == "rgA" and e.survives][0]
    sample = build_sample(
        e, scan.chains["rgA"], {"page_id": e.page_id, "book_id": "bk1"},
        image_path=fx["page_images"][e.page_id],
        group="user-library/book-fixture", case=None,
        license_info=fixture.USER_LIBRARY_LICENSE, now_iso="2026-10-04T00:00:00Z",
    )
    registry = [_mk_record("reg-001", sample.image.sha256, [[1.0, 1.0], [9.0, 1.0], [9.0, 9.0], [1.0, 9.0]])]
    kept, dropped = dedup_against_registry([sample], registry)
    assert kept == [sample] and dropped == []


def test_dedup_registry_missing_is_not_error(fx):
    from sfx_correction_exporter.eligibility import load_registry
    status, records = load_registry(None)
    assert status == "not_provided" and records == []
    status2, records2 = load_registry(fx["db_path"])  # 非 manifest 文件 → 不可读登记
    assert status2 == "load_error" and records2 == []
