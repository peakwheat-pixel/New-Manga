"""AC1：纠错事件识别器——fixture 混合 revision 链逐条断言（先红后绿）。

fixture 链矩阵（fixture.build_fixture_db，schema=生产 v1+v2 冻结 DDL）：
  A  corr-basic        m(speech) → u(sfx)                     → 事件@r2 存活（partial 路线）
  B  undone            m(speech) → u(sfx) → restored(r1)      → 事件@r2 被撤销(a) 不入册
  C  geom-only         m(speech) → u(仅几何, speech)           → 非事件
  D  text-only         m(speech) → u(仅文本, needs_review)     → 非事件
  E  machine-retype    m(speech) → m(sfx)                     → 非事件（origin=machine 排除）
  F  superseded        m(speech) → u(sfx) → u(title)          → r2 被改判(b)；r3 sfx→title 存活（非 sfx 向）
  G  undo-recorrect    m(speech) → u(sfx) → restored → u(sfx) → r2 撤销(a)；r4 存活
  H  user-created      u(speech) → u(sfx)                     → 事件@r2 存活（complete 路线：首笔 user）
  I  corr-geom-restore m(speech) → u(sfx) → u(几何) → restored(r2) → r2 存活（restore 未回退类型）；complete（用户几何编辑）
  J  reorder-only      m(speech) → u(仅 reading_order)         → 非事件
  K  non-sfx           m(sfx) → u(speech)                     → 事件存活但非 sfx 向（资格层排除）
  L  deleted           m(speech) → u(sfx)，region 软删除        → 跳过并计数
  M  challenge-corr    p2(BJ13 映射): m(speech) → u(sfx)       → 事件存活（partial；challenge 路线）
  N  bbox-fallback     m(speech, 空 polygon) → u(sfx)          → 事件存活；多边形回退 bbox 四角
                       （生产 xywh bbox 语义，DSH r1 P1-1）
  O2 undo-then-restore m(speech) → u(sfx) → restored(r1,speech) → restored(r2,sfx)
                       撤销后 restore 复活已改标 revision → 判据 (a) 保守误杀：
                       事件 undone 不存活（DSH r1 P3-1 显式钉住保守读法，
                       非契约 §5.4 唯一读法；登记 CONSTANTS.SURVIVAL_UNDONE_RULE）

判据引用：doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md rev1.4 §5.4（改标=新 revision
origin 恒 user；撤销=RestoreRegionRevision 产生 origin=restored；机器改标 origin=machine
不是纠错；改标 revision review_state=UNREVIEWED）。
"""

from __future__ import annotations

import sqlite3

import pytest

from sfx_correction_exporter import fixture
from sfx_correction_exporter.db import open_readonly
from sfx_correction_exporter.scanner import scan_corrections


@pytest.fixture(scope="module")
def fx(tmp_path_factory):
    return fixture.build_fixture_db(tmp_path_factory.mktemp("fx"))


@pytest.fixture(scope="module")
def scan(fx):
    conn = open_readonly(fx["db_path"])
    try:
        return scan_corrections(conn)
    finally:
        conn.close()


def events_of(scan, region_id):
    return [e for e in scan.events if e.region_id == region_id]


def test_region_A_single_correction_survives(scan):
    evs = events_of(scan, "rgA")
    assert len(evs) == 1
    e = evs[0]
    assert (e.revision_no, e.type_before, e.type_after) == (2, "speech", "sfx")
    assert e.origin == "user"
    assert e.review_state == "unreviewed"  # 契约 §5.4 r1 P3-1
    assert e.survives and not e.undone and not e.superseded


def test_region_B_undo_reverts_correction(scan):
    evs = events_of(scan, "rgB")
    assert len(evs) == 1
    e = evs[0]
    assert (e.revision_no, e.type_before, e.type_after) == (2, "speech", "sfx")
    assert e.undone is True and e.survives is False  # 撤销链解析：被撤销纠错不入册


def test_region_C_geometry_only_not_event(scan):
    assert events_of(scan, "rgC") == []


def test_region_D_text_only_not_event(scan):
    assert events_of(scan, "rgD") == []


def test_region_E_machine_retype_not_event(scan):
    assert events_of(scan, "rgE") == []
    assert scan.machine_type_changes_excluded == 1


def test_region_F_second_retype_supersedes_first(scan):
    evs = sorted(events_of(scan, "rgF"), key=lambda e: e.revision_no)
    assert len(evs) == 2
    r2, r3 = evs
    assert (r2.revision_no, r2.type_before, r2.type_after) == (2, "speech", "sfx")
    assert r2.superseded is True and r2.survives is False  # 终态 title ≠ sfx：被后续改标取代
    assert (r3.revision_no, r3.type_before, r3.type_after) == (3, "sfx", "title")
    assert r3.survives is True and r3.sfx_directed is False  # 非事件排除——资格层不产样本


def test_region_G_undo_then_recorrect(scan):
    evs = sorted(events_of(scan, "rgG"), key=lambda e: e.revision_no)
    assert len(evs) == 2
    r2, r4 = evs
    assert r2.revision_no == 2 and r2.undone is True and r2.survives is False
    assert r4.revision_no == 4 and r4.survives is True
    assert (r4.type_before, r4.type_after) == ("speech", "sfx")


def test_region_H_user_created_correction(scan):
    evs = events_of(scan, "rgH")
    assert len(evs) == 1
    e = evs[0]
    assert (e.revision_no, e.type_after) == (2, "sfx")
    assert e.survives is True


def test_region_I_restore_keeps_geometry_not_type_undo(scan):
    evs = events_of(scan, "rgI")
    assert len(evs) == 1
    e = evs[0]
    # r4 是 restore 回 r2（类型 sfx）：不构成对 r2 纠错（speech→sfx）的撤销
    assert (e.revision_no, e.type_after) == (2, "sfx")
    assert e.undone is False and e.superseded is False and e.survives is True


def test_region_J_reorder_only_not_event(scan):
    assert events_of(scan, "rgJ") == []


def test_region_K_non_sfx_correction_identified(scan):
    evs = events_of(scan, "rgK")
    assert len(evs) == 1
    e = evs[0]
    assert (e.type_before, e.type_after) == ("sfx", "speech")
    assert e.survives is True and e.sfx_directed is False  # 识别层照实报告；资格层排除


def test_region_L_soft_deleted_skipped(scan, fx):
    assert events_of(scan, "rgL") == []
    assert scan.regions_skipped_deleted == 1


def test_region_M_challenge_page_correction(scan):
    evs = events_of(scan, "rgM")
    assert len(evs) == 1
    e = evs[0]
    assert e.page_id == "pgBJ13"
    assert (e.type_before, e.type_after) == ("speech", "sfx")
    assert e.survives is True


def test_region_N_bbox_only_correction(scan):
    evs = events_of(scan, "rgN")
    assert len(evs) == 1 and evs[0].survives is True


def test_region_O2_restore_rehide_after_undo_conservative_misdrop(scan):
    """P3-1 保守读法显式钉住（DSH r1）：撤销后经 restore 复活已改标 revision 的终态纠错。

    链 = m(speech) → u(sfx) → restored(r1, speech) → restored(r2, sfx)。判据 (a) 按
    「其后任一 restored 回退 type_before 即撤销」判 undone——尽管链末笔又 restore 回
    已改标 revision（纠错态复活）。保守不采（survives=False），此为保守误杀、非契约
    §5.4 唯一读法；登记见 eligibility.CONSTANTS["SURVIVAL_UNDONE_RULE"]，重裁定留 T2。
    """
    evs = events_of(scan, "rgO2")
    assert len(evs) == 1
    e = evs[0]
    assert (e.revision_no, e.type_before, e.type_after) == (2, "speech", "sfx")
    assert e.undone is True and e.superseded is False and e.survives is False


def test_totals(scan):
    assert scan.regions_scanned == 14  # 15 - 1 软删除
    surviving = [e for e in scan.events if e.survives]
    # 存活 8：A、F-r3、G-r4、H、I、K、M、N
    assert sorted(
        (e.region_id, e.revision_no) for e in surviving
    ) == [
        ("rgA", 2), ("rgF", 3), ("rgG", 4), ("rgH", 2),
        ("rgI", 2), ("rgK", 2), ("rgM", 2), ("rgN", 2),
    ]
    sfx_directed = [e for e in surviving if e.sfx_directed]
    assert sorted(e.region_id for e in sfx_directed) == [
        "rgA", "rgG", "rgH", "rgI", "rgM", "rgN",
    ]


def test_scanner_never_writes(fx):
    """只读铁律：扫描用的连接必须是 mode=ro + query_only（AC5 语义在 AC1 路径复验）。"""
    conn = open_readonly(fx["db_path"])
    try:
        assert conn.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.Error):
            conn.execute(
                "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
                " text_json, style_json, created_at, updated_at)"
                " VALUES ('x','pg1','sfx','{}','{}','{}','t','t')"
            )
    finally:
        conn.close()
