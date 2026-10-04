"""AC3：资格判定（导出阶段）——许可备案 / 几何确认度门 / 与 T1a 已册样本去重。

四条规则常量冻结登记（CONSTANTS；任务合同 AC3「阈值冻结并登记」）：
- 许可：二次裁决「全备案不阻断」（user_ruling_2026-10-04_训练质量效率优先_许可降权备案）
  ——每个样本携带 license 备案块，永不因许可丢样本；
- 几何：GEOMETRY_CONFIRM_RULE v1（见 samples.geometry_confidence），partial 不入
  正集、可选入辅助集（PARTIAL_ROUTING）；
- 去重：复用 T1a find_duplicates 精确+框精确层级（image_loader=None——修正感知
  比对需要外部素材树，纠错样本位于用户库页，跨集感知比对不在本工具范围），
  册内样本优先保留；
- 导出目标：仅 sfx 向纠错（T1a BOX_CLASSES 恒 sfx），非 sfx 向事件识别层照实
  报告、资格层排除计数。
"""

from __future__ import annotations

from pathlib import Path

from sfx_data_infra.dedup import find_duplicates
from sfx_data_infra.schema import SampleRecord

CONSTANTS: dict[str, str] = {
    "GEOMETRY_CONFIRM_RULE": (
        "v1: complete iff 链首笔 origin=user（用户自建）或链上存在用户几何编辑；"
        "否则 partial（机器检出几何未被用户触碰）"
    ),
    "PARTIAL_ROUTING": "auxiliary manifest（不入正集，可选入辅助集）",
    "DEDUP_LEVEL": "exact+box-exact（T1a find_duplicates, image_loader=None；感知层级不启用）",
    "LICENSE_RULE": "user_ruling_2026-10-04_训练质量效率优先_许可降权备案: 全备案不阻断",
    "EXPORTABLE_TARGET": "sfx",
}

CASES_MATCH_BASIS_PAGE_FILENAME = "page_filename"
CASES_MATCH_BASIS_UNMATCHED = "unmatched"


def filter_sfx_directed(events):
    """存活事件分流：[(sfx 向事件)] 与 [(非 sfx 向事件, 排除理由)]。"""
    keep = [e for e in events if e.survives and e.sfx_directed]
    dropped = [
        (e, f"non-sfx 纠错（{e.type_before}->{e.type_after}）：T1a 框类恒 sfx，不入样本册")
        for e in events
        if e.survives and not e.sfx_directed
    ]
    return keep, dropped


def match_case(page, cases_index: dict[str, dict]) -> tuple[dict | None, str]:
    """页 → cases.json case 映射：source_filename 茎 == 页文件茎。

    判据复刻 T1a importers.page_filename_for_case（importers.py:62-70）：
    页文件名 = f"{source_id}.png"，即 stem == source_id。仅精确茎匹配，不做模糊。
    """
    source_filename = getattr(page, "source_filename", None)
    if not source_filename:
        return None, CASES_MATCH_BASIS_UNMATCHED
    stem = Path(str(source_filename)).stem
    for case_id, case in cases_index.items():
        page_file = Path(f"{case.get('source_id', '')}.png").stem
        if stem == page_file:
            return case, CASES_MATCH_BASIS_PAGE_FILENAME
    return None, CASES_MATCH_BASIS_UNMATCHED


def resolve_license(case: dict | None, page) -> dict:
    """许可备案块（永不阻断）：case 映射继承，否则 user_library_source 备案。"""
    if case:
        return {
            "license_class": case.get("license_class", "unknown"),
            "redistributable": bool(case.get("redistributable", False)),
            "source_url": case.get("source", ""),
            "registered": False,
            "blocking": False,
        }
    return {
        "license_class": "user_library_source",
        "redistributable": False,
        "source_url": "",
        "registered": True,
        "registered_per": CONSTANTS["LICENSE_RULE"],
        "blocking": False,
    }


def load_registry(registry_path: str | Path | None) -> tuple[str, list[SampleRecord]]:
    """载入 T1a 已册 manifest（--registry）。四态：not_provided/missing/loaded/load_error。"""
    from sfx_data_infra.atomicio import load_manifest

    if registry_path is None:
        return "not_provided", []
    path = Path(registry_path)
    if not path.exists():
        return "missing", []
    try:
        _, records = load_manifest(path)
    except Exception:  # 结构不符/不可解析 → 登记为 load_error，不阻断空册去重
        return "load_error", []
    return "loaded", records


def dedup_against_registry(
    corrections: list[SampleRecord], registry: list[SampleRecord]
) -> tuple[list[SampleRecord], list[dict]]:
    """与 T1a 已册样本查重（册内优先保留）。返回 (保留, 剔除登记)。"""
    if not corrections:
        return [], []
    combined = list(registry) + list(corrections)
    report = find_duplicates(combined, image_loader=None)
    dropped = [
        {"sample_id": s.sample_id, "duplicate_of": report.duplicate_of[s.sample_id]}
        for s in corrections
        if s.sample_id in report.duplicate_of
    ]
    dropped_ids = {d["sample_id"] for d in dropped}
    kept = [s for s in corrections if s.sample_id not in dropped_ids]
    return kept, dropped
