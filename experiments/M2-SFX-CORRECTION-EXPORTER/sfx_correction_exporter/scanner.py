"""AC1：纠错事件识别器——扫描 regions+region_revisions revision 链（只读）。

语义判据（doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md rev 1.4 §5.4；行号为该文件 grep 定位）：
- 改标 = 经既有 commit seam 产生一笔新 revision，origin 恒 `user`；snapshot 相对
  改标前仅 region_type 与 sfx_policy 两字段变化（§5.4「改标=新 revision」；
  写路径 src/application/editing/service.py:222-241 `_commit_user_or_raise`）。
- 撤销 = 既有 RestoreRegionRevision：产生 origin=`restored` 新 revision，
  restored_from_revision_id 溯源，历史不重写（§5.4「撤销」；service.py:550-572）。
- 机器改标 origin=`machine`（检测/仲裁产出）不是纠错事件（§5.4 来源字段语义）。
- 改标 revision review_state=`UNREVIEWED`（§5.4 r1 P3-1）。

事件定义：链上第 j>=2 笔 origin=`user` revision，其 snapshot.region_type !=
前笔 snapshot.region_type（首笔是创建不是纠错；revision_no 由
service.py:130-134 max+1 单调分配，链为线性全快照序列）。

存活判定（撤销链解析，冻结于 fixture 断言）：
  (a) 未被撤销：链上其后不存在 origin=`restored` 且 snapshot.region_type ==
      type_before 的 revision（显式回退到改标前类型即撤销；RESTORED 本身不是事件）；
  (b) 未被改判：链末笔 snapshot.region_type == type_after（用户 settled 终判与
      该事件一致；否则该中间判断已被后续改标取代，不得作为 GT 入册）。
排除项：origin=machine/imported 的类型变化（计数上报）；纯几何/文本/reading_order
用户编辑（类型未变，天然非事件）；软删除 region 整链跳过（计数上报）。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

USER_ORIGIN = "user"
RESTORED_ORIGIN = "restored"


@dataclass(frozen=True)
class RevisionRow:
    """region_revisions 单行（snapshot_json 已解析）。"""

    region_id: str
    page_id: str
    revision_no: int
    revision_id: str
    snapshot: dict[str, Any]
    origin: str
    review_state: str
    created_at: str
    restored_from_revision_id: str | None = None

    @property
    def region_type(self) -> str:
        return str(self.snapshot["region_type"])


@dataclass(frozen=True)
class CorrectionEvent:
    """一笔类型纠错事件（含存活判定结果；非存活事件保留用于报告）。"""

    region_id: str
    page_id: str
    revision_no: int
    revision_id: str
    type_before: str
    type_after: str
    sfx_policy_after: str
    origin: str
    review_state: str
    created_at: str
    undone: bool          # (a) 其后存在 RESTORED 回退到 type_before
    superseded: bool      # (b) 链末笔类型 != type_after

    @property
    def survives(self) -> bool:
        return not (self.undone or self.superseded)

    @property
    def sfx_directed(self) -> bool:
        """改标后类型是否 sfx（T1a schema 框类恒 sfx，非 sfx 向由资格层排除）。"""
        return self.type_after == "sfx"


@dataclass
class ScanResult:
    events: list[CorrectionEvent] = field(default_factory=list)
    chains: dict[str, list[RevisionRow]] = field(default_factory=dict)
    regions_scanned: int = 0
    regions_skipped_deleted: int = 0
    revisions_scanned: int = 0
    machine_type_changes_excluded: int = 0


def scan_corrections(conn) -> ScanResult:
    """只读扫描全库 region revision 链，产出类型纠错事件清单。"""
    rows = conn.execute(
        """
        SELECT r.region_id AS region_id, r.page_id AS page_id, r.deleted_at AS deleted_at,
               rv.region_revision_id AS region_revision_id, rv.revision_no AS revision_no,
               rv.snapshot_json AS snapshot_json, rv.origin AS origin,
               rv.review_state AS review_state, rv.created_at AS created_at,
               rv.restored_from_revision_id AS restored_from_revision_id
        FROM regions r
        JOIN region_revisions rv ON rv.region_id = r.region_id
        ORDER BY r.region_id, rv.revision_no
        """
    ).fetchall()

    chains: dict[str, list[RevisionRow]] = {}
    page_of: dict[str, str] = {}
    deleted: set[str] = set()
    for row in rows:
        rid = row["region_id"]
        page_of[rid] = row["page_id"]
        if row["deleted_at"] is not None:
            deleted.add(rid)
        chains.setdefault(rid, []).append(
            RevisionRow(
                region_id=rid,
                page_id=row["page_id"],
                revision_no=int(row["revision_no"]),
                revision_id=row["region_revision_id"],
                snapshot=json.loads(row["snapshot_json"]),
                origin=row["origin"],
                review_state=row["review_state"],
                created_at=row["created_at"],
                restored_from_revision_id=row["restored_from_revision_id"],
            )
        )

    result = ScanResult(chains=chains)
    for rid, chain in chains.items():
        if rid in deleted:
            result.regions_skipped_deleted += 1
            continue
        result.regions_scanned += 1
        result.revisions_scanned += len(chain)
        result.events.extend(_events_for_chain(rid, page_of[rid], chain, result))
    return result


def _events_for_chain(
    region_id: str, page_id: str, chain: list[RevisionRow], result: ScanResult
) -> list[CorrectionEvent]:
    events: list[CorrectionEvent] = []
    final_type = chain[-1].region_type
    for j in range(1, len(chain)):
        prev, cur = chain[j - 1], chain[j]
        if cur.region_type == prev.region_type:
            continue  # 类型未变：几何/文本/顺序编辑天然不产生事件
        if cur.origin != USER_ORIGIN:
            # 机器改标（检测/仲裁）与 imported 类型变化不是纠错事件，计数上报；
            # RESTORED 类型回退是撤销动作本身，不构成事件也不计入机器改标。
            if cur.origin in ("machine", "imported"):
                result.machine_type_changes_excluded += 1
            continue
        type_before, type_after = prev.region_type, cur.region_type
        undone = any(
            later.origin == RESTORED_ORIGIN and later.region_type == type_before
            for later in chain[j + 1:]
        )
        superseded = final_type != type_after
        events.append(
            CorrectionEvent(
                region_id=region_id,
                page_id=page_id,
                revision_no=cur.revision_no,
                revision_id=cur.revision_id,
                type_before=type_before,
                type_after=type_after,
                sfx_policy_after=str(cur.snapshot.get("sfx_policy", "skip")),
                origin=cur.origin,
                review_state=cur.review_state,
                created_at=cur.created_at,
                undone=undone,
                superseded=superseded,
            )
        )
    return events
