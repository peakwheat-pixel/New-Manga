"""AC2：纠错事件 → T1a schema 样本（sfx-data-infra/sample@1）。

- 图引用：页面真实图像文件 sha256+尺寸（T1a importers._image_ref 同构，
  importers.py:91-97；sha256 复用 sfx_data_infra.hash.sha256_file）。
- 框/多边形：链末笔 settled 几何（存活事件 type_after == 终态类型，标签与
  settled 状态一致）；polygon>=4 点直用，不足（含空/三点）回退 bbox 四角并
  在 quality_note 登记。生产 bbox 语义 = BBox.as_tuple()=(x, y, width, height)
  （entities.py:72-73），回退四角复用 T1a importers.bbox_to_polygon（xywh 语义，
  importers.py:54-55）。cls 恒 "sfx"（T1a schema.py:15 BOX_CLASSES）。
- 标注状态：complete（用户自建 region 或链上有用户几何编辑）/
  partial（几何为机器检出且未被用户触碰）——AC3 几何确认度门的落地值。
- provenance：type=asset_case（PROVENANCE_TYPES 四值内；user library 页即素材
  案例，derived 会触发 split 继承语义故不用）+ source=revision_chain_correction
  + correction.chain 全链 trace（revision_no/origin/region_type 序列，可溯源可回放）
  + geometry_from_revision_no（settled 几何来源 revision）。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sfx_data_infra.hash import sha256_file
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord

from sfx_correction_exporter import __version__
from sfx_correction_exporter.scanner import CorrectionEvent, RevisionRow


@dataclass(frozen=True)
class PageRef:
    """pages 行投影（含 book 归属）。"""

    page_id: str
    book_id: str
    source_filename: str | None
    managed_original_ref: str | None
    deleted_at: str | None


def load_pages(conn) -> dict[str, PageRef]:
    rows = conn.execute(
        """
        SELECT p.page_id AS page_id, p.source_filename AS source_filename,
               p.managed_original_ref AS managed_original_ref, p.deleted_at AS deleted_at,
               c.book_id AS book_id
        FROM pages p
        JOIN chapters c ON c.chapter_id = p.chapter_id
        ORDER BY p.page_id
        """
    ).fetchall()
    return {
        row["page_id"]: PageRef(
            page_id=row["page_id"],
            book_id=row["book_id"],
            source_filename=row["source_filename"],
            managed_original_ref=row["managed_original_ref"],
            deleted_at=row["deleted_at"],
        )
        for row in rows
    }


def geometry_confidence(chain: list[RevisionRow]) -> tuple[str, str]:
    """AC3 几何确认度门（阈值冻结 CONSTANTS["GEOMETRY_CONFIRM_RULE"]=v1）。

    返回 (annotation_status, geometry_provenance)：
    - complete / user_created：链首笔 origin=user（用户自建 region，几何为用户所画）；
    - complete / user_edited：链上存在 user revision 且几何相对前笔变化（用户几何编辑；
      改标 revision 几何与前笔一致——契约 §5.4——不会误计）；
    - partial / machine_only：几何为机器检出且从未被用户触碰。
    """
    if chain and chain[0].origin == "user":
        return "complete", "user_created"
    for i in range(1, len(chain)):
        cur = chain[i]
        if cur.origin == "user" and cur.snapshot.get("geometry") != chain[i - 1].snapshot.get("geometry"):
            return "complete", "user_edited"
    return "partial", "machine_only"


def _page_field(page: Any, name: str) -> Any:
    if isinstance(page, dict):
        return page.get(name)
    return getattr(page, name, None)


def _polygon_from_geometry(geo: dict) -> tuple[list[list[float]], str]:
    """settled 几何 → T1a 多边形；不足 4 点回退 bbox 四角（返回值含登记注记）。

    bbox 生产语义 = BBox.as_tuple()=(x, y, width, height)（entities.py:72-73），
    回退四角用 T1a 现成 helper importers.bbox_to_polygon(x, y, w, h)
    （importers.py:54-55）——DSH r1 P1-1：不得把 xywh 当 xyxy 读。
    """
    polygon = geo.get("polygon") or []
    if len(polygon) >= 4:
        return [[float(x), float(y)] for x, y in polygon], ""
    bbox = geo.get("bbox")
    if not bbox or len(bbox) != 4:
        raise ValueError(f"settled 几何既无 >=4 点 polygon 也无合法 bbox: {geo!r}")
    from sfx_data_infra.importers import bbox_to_polygon

    x, y, w, h = (float(v) for v in bbox)
    if w <= 0 or h <= 0:
        raise ValueError(f"bbox 须为生产 xywh 语义且 width/height 为正: {geo!r}")
    return bbox_to_polygon(x, y, w, h), "polygon<4 点（空/三点），按生产 xywh bbox 回退四角包络"


def _image_ref(image_path: Path) -> ImageRef:
    from PIL import Image  # 既有依赖（T1a 同用法），延迟导入保 --help 轻启动

    with Image.open(image_path) as im:
        width, height = im.size
    return ImageRef(path=image_path.as_posix(), sha256=sha256_file(image_path), width=width, height=height)


def build_sample(
    event: CorrectionEvent,
    chain: list[RevisionRow],
    page: Any,
    *,
    image_path: Path,
    group: str,
    case: dict | None,
    license_info: dict,
    now_iso: str,
) -> SampleRecord:
    """sfx 向存活纠错事件 → T1a SampleRecord（逐条过 SampleRecord.validate）。"""
    final = chain[-1]
    polygon, note = _polygon_from_geometry(final.snapshot["geometry"])
    status, geom_prov = geometry_confidence(chain)
    page_id = _page_field(page, "page_id")
    book_id = _page_field(page, "book_id")

    provenance: dict[str, Any] = {
        "type": "asset_case",
        "source": "revision_chain_correction",
        "exporter": f"{__version__}",
        "page_id": page_id,
        "region_id": event.region_id,
        "book_id": book_id,
        "correction": {
            "revision_no": event.revision_no,
            "revision_id": event.revision_id,
            "type_before": event.type_before,
            "type_after": event.type_after,
            "origin": event.origin,
            "review_state": event.review_state,
            "sfx_policy_after": event.sfx_policy_after,
            "chain": [
                {
                    "revision_no": rev.revision_no,
                    "origin": rev.origin,
                    "region_type": rev.region_type,
                    "review_state": rev.review_state,
                    **(
                        {"restored_from": rev.restored_from_revision_id}
                        if rev.restored_from_revision_id
                        else {}
                    ),
                }
                for rev in chain
            ],
        },
        "geometry_provenance": geom_prov,
        "geometry_from_revision_no": final.revision_no,  # P4-5：settled 几何来源链末笔
        "license": dict(license_info),
    }
    quality_note = "revision 链类型纠错（改标后类型框；几何为链末笔 settled 状态）"
    if note:
        quality_note += f"；{note}"
    if case:
        provenance["case_id"] = case.get("case_id")
        provenance["source_url"] = case.get("source")
        provenance["source_id"] = case.get("source_id")
    provenance["quality_note"] = quality_note

    sample_id = f"corr-{str(page_id)[:8]}-{event.region_id[:8]}-r{event.revision_no:03d}"
    record = SampleRecord(
        sample_id=sample_id,
        image=_image_ref(image_path),
        boxes=[BoxAnnotation(polygon=polygon, cls="sfx")],
        annotation_status=status,
        provenance=provenance,
        group=group,
        created_at=now_iso,
        notes="",
    )
    errors = record.validate()
    if errors:
        raise ValueError(f"样本校验失败 {sample_id}: {errors}")
    return record
