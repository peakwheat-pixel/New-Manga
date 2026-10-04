"""AC5：存量资产导入器——三份既有资产一键入册。

质量标注判定（写入 provenance.quality_note，口径见 README §口径冻结）：
- l3 七参照框（BJ13/14/15）：人工目检近似框（approx_xyxy，20% inflate crop 探针）
  → `partial`；split 由拆分器单列 `challenge`。
- BJ06 八自证框：检测器 bbox + E2E MATERIAL qual run 人工核验（非像素级精确）
  → `partial`。
- ogkalu 43 region：模型 harvest 灵敏度产出、无人工确认 → `pseudo`（合同明示）。
素材根只读探测：优先本 worktree，缺页则查 E2E-MATERIAL / TA2B worktree。
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable, Optional

from sfx_data_infra.hash import sha256_file
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord
from sfx_data_infra.splits import derive_group_key_from_case

# 素材根候选（只读）：本 worktree → E2E-MATERIAL worktree（BJ13/14/15 页）→ TA2B worktree（BJ06 页）
DEFAULT_ASSET_ROOTS = (
    r"G:\CODEX\New Manga.worktrees\M2-SFX-DATA-INFRA-zcode\test_assets\comic_golden_suite",
    r"G:\CODEX\New Manga.worktrees\M2-SFX-E2E-MATERIAL-zcode\test_assets\comic_golden_suite",
    r"G:\CODEX\New Manga.worktrees\M2-TA2B-OPEN-ASSETS-zcode\test_assets\comic_golden_suite",
)

_PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = _PKG_DIR.parents[2]

_L3_JSON = REPO_ROOT / "verification" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "raw" / "l3-reference-crops.json"
_BJ06_JSON = REPO_ROOT / "verification" / "M2-SFX-E2E-MATERIAL" / "bj06-run" / "summaries" / "qual-BJ06.json"
_OGKALU_JSON = REPO_ROOT / "experiments" / "M2-SFX-DETECT" / "ogkalu-sfx-frames.json"
_CASES_JSON = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"


def load_cases_index() -> dict[str, dict]:
    """cases.json → {case_id: case}。素材 manifest 只读。"""
    data = json.loads(_CASES_JSON.read_text(encoding="utf-8"))
    return {c["case_id"]: c for c in data["cases"]}


def parse_ogkalu_region_key(key: str) -> str:
    """'K01_R035' -> 'K01'。"""
    m = re.match(r"^([A-Za-z]+\d+)_R\d+$", key)
    if not m:
        raise ValueError(f"ogkalu region key 不合法: {key!r}")
    return m.group(1)


def bbox_to_polygon(x, y, w, h) -> list[list[float]]:
    return [[float(x), float(y)], [float(x + w), float(y)], [float(x + w), float(y + h)], [float(x), float(y + h)]]


def xyxy_to_polygon(x0, y0, x1, y1) -> list[list[float]]:
    return [[float(x0), float(y0)], [float(x1), float(y0)], [float(x1), float(y1)], [float(x0), float(y1)]]


def page_filename_for_case(case_id: str, cases_index: dict) -> str:
    """BJ13 -> 'vol03_p0048.png'（cases.json source_id + .png）。"""
    case = cases_index[case_id]
    sid = str(case["source_id"])
    if not re.match(r"^[A-Za-z0-9_\-]+$", sid):
        raise ValueError(f"source_id 含非常规字符: {sid!r}")
    return f"{sid}.png"


def resolve_asset_roots(extra: Iterable = ()) -> list[Path]:
    env = os.environ.get("SFX_DATA_ASSET_ROOTS")
    roots = [Path(p) for p in env.split(os.pathsep)] if env else []
    if extra:
        roots.extend(Path(p) for p in extra)
    roots.extend(Path(p) for p in DEFAULT_ASSET_ROOTS)
    return roots


def find_page_image(case_id: str, cases_index: dict, roots) -> Optional[Path]:
    """在素材根候选里找 case 页图像（相对 local_path）。只读。"""
    case = cases_index[case_id]
    rel = Path(case["local_path"]) / page_filename_for_case(case_id, cases_index)
    for root in roots:
        candidate = root / rel
        if candidate.is_file():
            return candidate
    return None


def _image_ref(path: Path, storage_path: str) -> tuple[ImageRef, str]:
    from PIL import Image

    with Image.open(path) as im:
        w, h = im.size
    return ImageRef(path=storage_path, sha256=sha256_file(path), width=w, height=h), path.name


def import_reference_crops(cases_index: dict, roots, now_iso: str) -> list[SampleRecord]:
    """l3 七参照框（BJ13/14/15）→ partial 样本。"""
    data = json.loads(_L3_JSON.read_text(encoding="utf-8"))
    out: list[SampleRecord] = []
    for cid in sorted(data["crops"].keys()):
        case = cases_index[cid]
        page = find_page_image(cid, cases_index, roots)
        if page is None:
            raise FileNotFoundError(f"{cid} 页图像未在素材根候选中找到（cases.json local_path={case['local_path']}）")
        img_ref, _ = _image_ref(page, str(page))
        group = derive_group_key_from_case(case)
        for i, entry in enumerate(data["crops"][cid]):
            ref = entry["ref"]
            box = BoxAnnotation(
                polygon=xyxy_to_polygon(*ref["approx_xyxy"]),
                cls="sfx",
                text=ref.get("text"),
            )
            out.append(
                SampleRecord(
                    sample_id=f"imp-l3-{cid.lower()}-{i:02d}",
                    image=img_ref,
                    boxes=[box],
                    annotation_status="partial",
                    provenance={
                        "type": "asset_case",
                        "case_id": cid,
                        "source_url": case["source"],
                        "source_id": case["source_id"],
                        "evidence": "verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l3-reference-crops.json",
                        "quality_note": "人工目检近似框（approx_xyxy；20% inflate crop 探针参照），非像素级",
                    },
                    group=group,
                    created_at=now_iso,
                )
            )
    return out


def import_bj06(cases_index: dict, roots, now_iso: str) -> list[SampleRecord]:
    """BJ06 八自证框（qual run sfx region）→ partial 样本。"""
    data = json.loads(_BJ06_JSON.read_text(encoding="utf-8"))
    cid = data["case_id"]
    case = cases_index[cid]
    page = find_page_image(cid, cases_index, roots)
    if page is None:
        raise FileNotFoundError(f"{cid} 页图像未在素材根候选中找到")
    img_ref, _ = _image_ref(page, str(page))
    # 对账：qual 记录的 source_sha256 与当前素材一致（素材未被替换）
    if img_ref.sha256 != data.get("source_sha256"):
        raise ValueError(
            f"BJ06 素材 sha256 对账失败：qual 记录 {data.get('source_sha256')[:12]}… != 现算 {img_ref.sha256[:12]}…"
        )
    group = derive_group_key_from_case(case)
    out = []
    for r in data["regions"]:
        if r.get("region_type") != "sfx":
            continue
        bb = r["bbox"]
        box = BoxAnnotation(polygon=bbox_to_polygon(bb["x"], bb["y"], bb["width"], bb["height"]), cls="sfx")
        out.append(
            SampleRecord(
                sample_id=f"imp-bj06-{r['region_id'][:8]}",
                image=img_ref,
                boxes=[box],
                annotation_status="partial",
                provenance={
                    "type": "asset_case",
                    "case_id": cid,
                    "source_url": case["source"],
                    "source_id": case["source_id"],
                    "region_id": r["region_id"],
                    "evidence": "verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json",
                    "quality_note": "检测器 bbox + E2E MATERIAL qual run 人工核验（自证框），非像素级精确",
                },
                group=group,
                created_at=now_iso,
            )
        )
    return out


def import_ogkalu(cases_index: dict, roots, now_iso: str) -> list[SampleRecord]:
    """ogkalu 43 region（模型 harvest，无人工确认）→ pseudo 样本。

    图引用 = region crop PNG（task-envs 外部工作区，已核在盘）；
    框 = crop 内坐标 detections（与图引用天然同坐标系）。
    """
    data = json.loads(_OGKALU_JSON.read_text(encoding="utf-8"))
    model_info = data.get("candidate_model", {})
    out = []
    for key in sorted(data["regions"].keys()):
        r = data["regions"][key]
        crop_path = Path(r["image"])
        if not crop_path.is_file():
            raise FileNotFoundError(f"ogkalu region crop 不在盘上: {crop_path}")
        case_id = parse_ogkalu_region_key(key)
        case = cases_index.get(case_id)
        group = derive_group_key_from_case(case) if case else f"ogkalu-crop/{case_id}"
        boxes = []
        det_conf_stats = []
        for det in r.get("detections", []):
            boxes.append(
                BoxAnnotation(
                    polygon=xyxy_to_polygon(*det["box_xyxy"]),
                    cls="sfx",
                    text=None,
                )
            )
            # r1 P2-9：harvest(0.25) vs primary(0.5) 的质量分级依据必须留痕
            det_conf_stats.append(
                {"conf": det.get("conf"), "cls": det.get("cls"), "conf_ge_primary": det.get("conf_ge_primary")}
            )
        if not boxes:
            # detections 为空 = 模型在该 crop 无检出（harvest 0.25 灵敏度下）：
            # 以空框 pseudo 负证据样本入册（schema 冻结允许 pseudo 空框），43 region 全量对齐 AC5。
            pass
        img_ref = ImageRef(
            path=str(crop_path),
            sha256=sha256_file(crop_path),
            width=int(r["width"]),
            height=int(r["height"]),
        )
        out.append(
            SampleRecord(
                sample_id=f"imp-ogkalu-{key.lower().replace('_', '-')}",
                image=img_ref,
                boxes=boxes,
                annotation_status="pseudo",
                provenance={
                    "type": "external_model",
                    "case_id": case_id,
                    "region_key": key,
                    "model": model_info.get("arch", "ogkalu-comic-text-and-bubble-detector"),
                    "model_license": model_info.get("license"),
                    "weights_sha256": model_info.get("weights_sha256"),
                    "harvest_threshold": data.get("harvest_threshold"),
                    "evidence": "experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json",
                    "original_classes": sorted({d["cls"] for d in r.get("detections", [])}),
                    "detection_conf_stats": det_conf_stats,
                    "negative": not boxes,
                    "quality_note": "模型 harvest 灵敏度产出（0.25 阈值），无人工确认；仅伪 GT"
                    + ("；该 crop 无检出框（负证据样本）" if not boxes else ""),
                },
                group=group,
                created_at=now_iso,
            )
        )
    return out


def import_all(now_iso: str) -> list[SampleRecord]:
    """一键导入三资产 → 7+8+43=58 样本。"""
    cases_index = load_cases_index()
    roots = resolve_asset_roots()
    samples: list[SampleRecord] = []
    samples += import_reference_crops(cases_index, roots, now_iso)
    samples += import_bj06(cases_index, roots, now_iso)
    samples += import_ogkalu(cases_index, roots, now_iso)
    return samples
