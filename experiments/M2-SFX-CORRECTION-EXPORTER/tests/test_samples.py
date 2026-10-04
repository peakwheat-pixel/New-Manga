"""AC2：纠错事件 → T1a schema 样本（图引用+改标后类型框/多边形+状态+溯源 provenance）。

关键断言：
- sfx 向存活事件才建样本；非 sfx 向（rgK/rgF-r3）不进样本构建；
- 图引用 = 页面真实图像文件 sha256+尺寸（与 T1a ImageRef 同构）；
- 框/多边形 = 链末笔 settled 几何（标签=存活事件 type_after，与终态类型一致）；
  空 polygon 回退 bbox 四角并登记 quality_note；
- annotation_status：complete（用户自建/用户几何编辑）vs partial（纯机器几何）；
- provenance.type=asset_case + source=revision_chain_correction + correction.chain
  全链 trace（region_id/revision_no/event 序列可溯源可回放）。
"""

from __future__ import annotations

import pytest

from sfx_correction_exporter import fixture
from sfx_correction_exporter.db import open_readonly
from sfx_correction_exporter.samples import (
    build_sample,
    geometry_confidence,
    load_pages,
)
from sfx_correction_exporter.scanner import scan_corrections


@pytest.fixture(scope="module")
def fx(tmp_path_factory):
    return fixture.build_fixture_db(tmp_path_factory.mktemp("fx2"))


@pytest.fixture(scope="module")
def ctx(fx):
    conn = open_readonly(fx["db_path"])
    try:
        scan = scan_corrections(conn)
        pages = load_pages(conn)
    finally:
        conn.close()
    return fx, scan, pages


def _event(ctx, region_id):
    _, scan, _ = ctx
    return [e for e in scan.events if e.region_id == region_id and e.survives][0]


def _chain(ctx, region_id):
    _, scan, _ = ctx
    return [r for r in scan.chains[region_id]]


def test_geometry_confidence_gate(ctx):
    """AC3 几何确认度门（阈值冻结 GEOMETRY_CONFIRM_RULE=v1）：complete vs partial。"""
    _, _, _ = ctx
    assert geometry_confidence(_chain(ctx, "rgH"))[0] == "complete"  # 首笔 origin=user（用户自建）
    assert geometry_confidence(_chain(ctx, "rgI"))[0] == "complete"  # 用户几何编辑（r3）
    assert geometry_confidence(_chain(ctx, "rgA"))[0] == "partial"   # 纯机器几何，改标不动几何
    assert geometry_confidence(_chain(ctx, "rgB"))[0] == "partial"


def test_build_sample_A_partial_with_full_provenance(ctx):
    fx, _, pages = ctx
    e = _event(ctx, "rgA")
    page = pages[e.page_id]
    sample = build_sample(
        e, _chain(ctx, "rgA"), page,
        image_path=fx["page_images"][e.page_id],
        group="user-library/book-fixture",
        case=None, license_info=fixture.USER_LIBRARY_LICENSE,
        now_iso="2026-10-04T00:00:00Z",
    )
    assert sample is not None
    # 图引用：sha256 与尺寸来自真实文件
    import hashlib
    raw = fx["page_images"][e.page_id].read_bytes()
    assert sample.image.sha256 == hashlib.sha256(raw).hexdigest()
    assert (sample.image.width, sample.image.height) == (64, 48)
    # 框：cls 恒 sfx（T1a schema.py:15 BOX_CLASSES）；多边形=链末笔 settled 几何
    assert len(sample.boxes) == 1
    assert sample.boxes[0].cls == "sfx"
    assert sample.boxes[0].polygon == [[10.0, 10.0], [60.0, 10.0], [60.0, 50.0], [10.0, 50.0]]
    assert sample.annotation_status == "partial"
    # 样本自身逐条校验通过（T1a 冻结字段集）
    assert sample.validate() == []
    # provenance 可溯源可回放：revision 链全 trace
    prov = sample.provenance
    assert prov["type"] == "asset_case"
    assert prov["source"] == "revision_chain_correction"
    assert prov["region_id"] == "rgA" and prov["page_id"] == e.page_id
    chain = prov["correction"]["chain"]
    assert [(c["revision_no"], c["origin"], c["region_type"]) for c in chain] == [
        (1, "machine", "speech"), (2, "user", "sfx"),
    ]
    assert prov["correction"]["revision_no"] == 2
    assert prov["correction"]["type_before"] == "speech"
    assert prov["correction"]["type_after"] == "sfx"
    assert prov["geometry_provenance"] == "machine_only"
    assert prov["license"]["blocking"] is False  # 二次裁决：全备案不阻断
    assert sample.sample_id.startswith("corr-") and sample.sample_id.endswith("-r002")


def test_build_sample_N_bbox_fallback(ctx):
    """空 polygon（纯 bbox region）→ 回退 bbox 四角，quality_note 登记。"""
    fx, _, pages = ctx
    e = _event(ctx, "rgN")
    sample = build_sample(
        e, _chain(ctx, "rgN"), pages[e.page_id],
        image_path=fx["page_images"][e.page_id],
        group="user-library/book-fixture",
        case=None, license_info=fixture.USER_LIBRARY_LICENSE,
        now_iso="2026-10-04T00:00:00Z",
    )
    assert sample.boxes[0].polygon == [[20.0, 20.0], [50.0, 20.0], [50.0, 40.0], [20.0, 40.0]]
    assert "bbox" in sample.provenance["quality_note"]


def test_build_sample_M_case_mapped_group(ctx):
    """BJ13 映射页的样本：组键继承 T1a 组键、case_id 进 provenance（challenge 触发器）。"""
    fx, _, pages = ctx
    e = _event(ctx, "rgM")
    case = {"case_id": "BJ13", "source": "https://densho810.com/free/",
            "source_id": "vol03_p0048", "local_path": "日漫_JA/01_black_jack_official/vol03/pages",
            "license_class": "commercial_use_permitted_attribution", "redistributable": True}
    sample = build_sample(
        e, _chain(ctx, "rgM"), pages[e.page_id],
        image_path=fx["page_images"][e.page_id],
        group="densho810/vol03", case=case,
        license_info={"license_class": "commercial_use_permitted_attribution",
                      "redistributable": True, "source_url": "https://densho810.com/free/",
                      "registered": False, "blocking": False},
        now_iso="2026-10-04T00:00:00Z",
    )
    assert sample.group == "densho810/vol03"
    assert sample.provenance["case_id"] == "BJ13"
    assert sample.provenance["license"]["license_class"] == "commercial_use_permitted_attribution"


def test_non_sfx_events_never_built(ctx):
    """非 sfx 向事件（rgK sfx→speech / rgF-r3 sfx→title）不产样本——T1a BOX_CLASSES 恒 sfx。"""
    _, scan, _ = ctx
    non_sfx = [e for e in scan.events if e.survives and not e.sfx_directed]
    assert sorted((e.region_id, e.revision_no) for e in non_sfx) == [("rgF", 3), ("rgK", 2)]
