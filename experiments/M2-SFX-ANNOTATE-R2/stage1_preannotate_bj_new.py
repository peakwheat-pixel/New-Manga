"""M2-SFX-ANNOTATE-R2 阶段一（targeted）：BJ 新页 BJ16-25 预标注 + 审核工作表。

R1 同款工具（experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py）的 targeted
变体：只处理 R2 素材采集轮新采的 10 个 BJ 页（BJ16-BJ25），不触碰 R1 已有页。
三步（--step）：

  scan      chiqui7 SFX 密度扫描：BJ16-25 整页 letterbox（R1 BJ 域同口径）。
            需 onnxruntime venv（M2-DOCTR-QUAL-C4-gpu-py312）。
  assemble  页级候选 → preannotate manifest（T1a schema，全标 pseudo）+ BJ16-25
            映射登记（来自素材采集员 material-selection.json bj_selected）。
  worksheet 每候选框裁切预览（20% 边距上下文，R1 同款）+ 页级清单
            （JSON + 人类可读 md，AI 预判列预填、用户裁决列留空）。

与 R1 的差异（targeted 语义，均在产物 JSON 内登记）：
  - 页面选取不重跑：BJ16-25 固定为 material-selection.json 的 bj_selected
    rank 1-10（素材采集员已按密度 seed 冻结选取），本工具不重新选取。
  - cases.json 已含 BJ16-25（R2 AC1 纯追加登记，DSH r1 P3-2 更正本注记）：
    case 元数据与登记条目对齐（source/source_id/local_path 同源）。
  - 候选单源（chiqui7-scan）：R2 新页无 l1/l3/bj06 既有 raw 可复用。

纪律：零 src 修改（生产推理序列经 conf_scan_diag 只读 import 复用）；素材树
只读；T1a 工具链（schema/splits/hash）只读复用不重造。产出数据本体落
training_data/sfx-v1/annotate-r2/（gitignored），Git 只进清单摘要。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "M2-SFX-DATA-INFRA"))

from PIL import Image  # noqa: E402

# 受控本地素材（webtoon 长条最大 ~90.6MP）仅略超 PIL 默认警戒线；显式解除并留痕。
Image.MAX_IMAGE_PIXELS = None

from sfx_data_infra.hash import sha256_file  # noqa: E402
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord  # noqa: E402
from sfx_data_infra.splits import SEED_DEFAULT, derive_group_key_from_case  # noqa: E402
from sfx_data_infra.importers import xyxy_to_polygon  # noqa: E402

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2"
SCAN_JSON = OUT_DIR / "scan" / "density-scan-bj-new.json"
PREANNOTATE_JSON = OUT_DIR / "preannotate" / "manifest-bj-new.json"
SELECTION_JSON = OUT_DIR / "selection" / "selection-bj-new.json"
WORKSHEET_JSON = OUT_DIR / "worksheet" / "worksheet-bj-new.json"
WORKSHEET_MD = OUT_DIR / "worksheet" / "worksheet-bj-new.md"
PREVIEW_DIR = OUT_DIR / "previews"
MATERIAL_SELECTION_JSON = OUT_DIR / "selection" / "material-selection.json"

BJ_ASSET_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"

SEED = SEED_DEFAULT  # 20261004，沿 T1a splits.SEED_DEFAULT（seed 冻结、可复现）
IOU_MERGE = 0.5      # 跨源同框合并阈值（与 R1 同款；本轮单源，防御性保留）
PREVIEW_MAX_EDGE = 640
PREVIEW_MARGIN = 0.20  # 合同：裁切预览含 20% 边距上下文
PREVIEW_MARGIN_MIN_PX = 24


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_bj_new_pages() -> list[dict]:
    """素材采集员 selection → BJ16-25 页表（rank 顺序固定映射，不重新选取）。"""
    sel = json.loads(MATERIAL_SELECTION_JSON.read_text(encoding="utf-8"))
    out = []
    for i, entry in enumerate(sel["bj_selected"], start=1):
        cid = f"BJ{15 + i}"
        sid = entry["source_id"]
        vol, page = sid.split("_")
        path = BJ_ASSET_ROOT / vol / "pages" / f"{sid}.png"
        if not path.is_file():
            raise FileNotFoundError(f"{cid} 页文件不在盘: {path}")
        # cases.json 未含 BJ16-25；case 元数据就地构造，字段与同套件 BJ01 一致。
        case = {
            "case_id": cid,
            "source": "https://densho810.com/free/",
            "source_id": sid,
            "source_type": "official_free_manga_page",
            "layout_type": "paged_manga",
            "reading_direction": "right_to_left",
            "text_type": "in_page_text",
            "orientation": "vertical",
            "difficulty": "unassessed",
            "tags": ["vertical_text", "complex_background"],
            "source_category": "01_black_jack_official",
            "local_path": f"日漫_JA/01_black_jack_official/{vol}/pages",
            "license_class": "commercial_use_permitted_attribution",
            "redistributable": True,
        }
        out.append({
            "case_id": cid,
            "domain": "bj",
            "path": str(path),
            "source_id": sid,
            "density_material_scan": entry["density"],
            "material_rank": entry["rank"],
            "group": derive_group_key_from_case(case),
            "case": case,
        })
    return out


# ---------------------------------------------------------------------------
# scan：chiqui7 密度扫描（onnxruntime venv 运行；R1 同款整页 letterbox）
# ---------------------------------------------------------------------------


def _load_scan_engine():
    """只读 import 复用 conf_scan_diag（其内部复用生产 detection_sfx 序列）。"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "conf_scan_diag",
        REPO_ROOT / "experiments" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "conf_scan_diag.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["conf_scan_diag"] = mod
    spec.loader.exec_module(mod)
    return mod


def _dedup_boxes(boxes: list[dict], iou_thr: float = 0.5) -> list[dict]:
    """同页 sfx 框去重（贪心 NMS，按 conf 降序；R1 同款）。"""

    def iou(a, b):
        ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = ix * iy
        if inter <= 0.0:
            return 0.0
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        return inter / (area_a + area_b - inter)

    ordered = sorted(boxes, key=lambda b: b["conf"], reverse=True)
    kept: list[dict] = []
    for b in ordered:
        if any(iou(b["xyxy"], k["xyxy"]) >= iou_thr for k in kept):
            continue
        kept.append(b)
    return kept


def cmd_scan() -> int:
    mod = _load_scan_engine()
    run_inference = mod.run_inference
    session, imgsz, imgsz_source, _raw = mod._build_engine(Path(mod.SFX_WEIGHTS_DEFAULT))
    print(f"engine OK imgsz={imgsz} ({imgsz_source})")

    pages = load_bj_new_pages()
    out = {
        "tool": "experiments/M2-SFX-ANNOTATE-R2/stage1_preannotate_bj_new.py --step scan",
        "generated_at_utc": now_iso(),
        "weights": str(mod.SFX_WEIGHTS_DEFAULT),
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "conf_floor": 0.01,
        "note": "R2 targeted BJ 新页密度扫描：BJ16-25 整页 letterbox（R1 BJ 域同口径）；只保留 sfx 类框详情（全类计数保留）；页级与素材采集员 density-scan-material.json 同口径可对照",
        "seed": SEED,
        "pages": {},
    }

    import numpy as np

    t_all = time.perf_counter()
    for info in pages:
        page_path = Path(info["path"])
        with Image.open(page_path) as im:
            rgb = im.convert("RGB")
        page_w, page_h = rgb.size
        t0 = time.perf_counter()
        boxes_raw, _scale, _shape = run_inference(
            session, np.asarray(rgb), imgsz, float(page_w), float(page_h)
        )
        elapsed = round(time.perf_counter() - t0, 1)
        sfx_boxes: list[dict] = []
        count_by_class_total: dict[str, int] = {}
        for b in boxes_raw:
            count_by_class_total[b["cls"]] = count_by_class_total.get(b["cls"], 0) + 1
            if b["cls"] == "sfx":
                sfx_boxes.append({"xyxy": b["xyxy"], "conf": b["conf"], "source": "chiqui7-scan"})
        sfx_kept = _dedup_boxes(sfx_boxes)
        out["pages"][info["case_id"]] = {
            "case_id": info["case_id"],
            "domain": "bj",
            "page": str(page_path),
            "page_size": [page_w, page_h],
            "scan_mode": "fullpage_letterbox",
            "n_tiles": 1,
            "inference_s": elapsed,
            "count_by_class_all": count_by_class_total,
            "sfx_box_count_raw": len(sfx_boxes),
            "sfx_boxes": sfx_kept,
            "material_scan_density_ref": info["density_material_scan"],
        }
        print(
            f"scan {info['case_id']} ({info['source_id']}): {page_w}x{page_h} "
            f"sfx_raw={len(sfx_boxes)} kept={len(sfx_kept)} (material_scan={info['density_material_scan']}) {elapsed}s"
        )
        rgb.close()

    SCAN_JSON.parent.mkdir(parents=True, exist_ok=True)
    SCAN_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {SCAN_JSON} ({round(time.perf_counter() - t_all, 1)}s total)")
    return 0


# ---------------------------------------------------------------------------
# assemble：页级候选 → T1a schema（全 pseudo）+ BJ16-25 映射登记
# ---------------------------------------------------------------------------


def cmd_assemble() -> int:
    pages = load_bj_new_pages()
    scan = json.loads(SCAN_JSON.read_text(encoding="utf-8"))
    stamp = now_iso()

    records: list[SampleRecord] = []
    density: dict[str, int] = {}
    for info in pages:
        cid = info["case_id"]
        sd = scan["pages"][cid]
        # scan 框形态 {xyxy,conf,source} → merge 形态 {xyxy,conf,sources}（单源，R1 merge 语义的恒等形态）
        merged = sorted(
            ({"xyxy": b["xyxy"], "conf": b["conf"], "sources": [b["source"]]} for b in sd["sfx_boxes"]),
            key=lambda m: (-(m["conf"]), m["xyxy"]),
        )
        density[cid] = len(merged)
        page_path = Path(info["path"])
        with Image.open(page_path) as im:
            w, h = im.size
        case = info["case"]
        rec = SampleRecord(
            sample_id=f"pre-{cid.lower()}",
            image=ImageRef(path=str(page_path), sha256=sha256_file(page_path), width=w, height=h),
            boxes=[
                BoxAnnotation(
                    polygon=xyxy_to_polygon(*m["xyxy"]),
                    cls="sfx",
                    text=None,
                )
                for m in merged
            ],
            annotation_status="pseudo",
            provenance={
                "type": "asset_case",
                "case_id": cid,
                "source_url": case["source"],
                "source_id": case["source_id"],
                "stage": "annotate-r2-stage1-bj-new",
                "review_domain": "bj",
                "boxes_meta": [
                    {"conf": m["conf"], "sources": m["sources"], "texts": []} for m in merged
                ],
                "quality_note": "AI 预标注草稿（chiqui7-scan 单源，全 pseudo）；R2 用户逐条裁决",
                "evidence": "density-scan-bj-new.json；页选取来自素材采集员 material-selection.json bj_selected",
                "cases_json_note": "BJ16-25 已由 R2 AC1 登记（cases.json 纯追加 commit 9b9916af，page_sha256/volume/pdf_page_number 见该文件）；本工具 case 元数据与登记条目对齐",
            },
            group=info["group"],
            created_at=stamp,
        )
        records.append(rec)

    selection = {
        "tool": "experiments/M2-SFX-ANNOTATE-R2/stage1_preannotate_bj_new.py --step assemble",
        "generated_at_utc": stamp,
        "seed": SEED,
        "targeted": True,
        "targeted_note": "R2 targeted：BJ16-25 固定 = material-selection.json bj_selected rank1-10（素材采集员已按密度 seed 冻结选取），本工具不重新选取",
        "pages": [
            {
                "case_id": info["case_id"],
                "source_id": info["source_id"],
                "material_rank": info["material_rank"],
                "density_material_scan": info["density_material_scan"],
                "density_this_scan": density[info["case_id"]],
                "page": info["path"],
                "group": info["group"],
            }
            for info in pages
        ],
        "density": density,
    }

    PREANNOTATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    PREANNOTATE_JSON.write_text(
        json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=1), encoding="utf-8"
    )
    SELECTION_JSON.parent.mkdir(parents=True, exist_ok=True)
    SELECTION_JSON.write_text(json.dumps(selection, ensure_ascii=False, indent=1), encoding="utf-8")
    n_boxes = sum(len(r.boxes) for r in records)
    print(f"page samples: {len(records)} | page boxes: {n_boxes}")
    print(f"wrote {PREANNOTATE_JSON}")
    print(f"wrote {SELECTION_JSON}")
    return 0


# ---------------------------------------------------------------------------
# worksheet：预览裁切 + 页级清单（JSON+md）（R1 同款）
# ---------------------------------------------------------------------------


def _crop_with_margin(im: Image.Image, xyxy: list[float]) -> Image.Image:
    x0, y0, x1, y1 = xyxy
    bw, bh = x1 - x0, y1 - y0
    dx = max(bw * PREVIEW_MARGIN, PREVIEW_MARGIN_MIN_PX)
    dy = max(bh * PREVIEW_MARGIN, PREVIEW_MARGIN_MIN_PX)
    W, H = im.size
    box = (max(0, int(x0 - dx)), max(0, int(y0 - dy)), min(W, int(x1 + dx)), min(H, int(y1 + dy)))
    return im.crop(box)


def _annotate_preview(img: Image.Image, unit_id: str, conf, sources: list[str]) -> Image.Image:
    """预览下采样 + AI 框描边 + unit_id/conf 标注（R1 同款）。"""
    from PIL import ImageDraw

    if max(img.size) > PREVIEW_MAX_EDGE:
        s = PREVIEW_MAX_EDGE / max(img.size)
        img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, img.width - 1, img.height - 1], outline=(200, 30, 30), width=2)
    conf_s = f"conf={conf:.2f}" if isinstance(conf, (int, float)) else "conf=ref"
    label = f"{unit_id} {conf_s} [{'/'.join(sources)}]"
    draw.rectangle([0, 0, img.width - 1, 14], fill=(0, 0, 0))
    draw.text((3, 2), label, fill=(255, 255, 255))
    return img


def cmd_worksheet() -> int:
    manifest = json.loads(PREANNOTATE_JSON.read_text(encoding="utf-8"))
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    WORKSHEET_JSON.parent.mkdir(parents=True, exist_ok=True)
    stamp = now_iso()

    units: list[dict] = []
    zero_box_pages: list[dict] = []  # 零 AI 检出的入选页（负证据页，用户直接补画）
    page_cache: dict[str, Image.Image] = {}

    def get_image(path_str: str) -> Image.Image:
        if path_str not in page_cache:
            page_cache.clear()
            page_cache[path_str] = Image.open(Path(path_str)).convert("RGB")
        return page_cache[path_str]

    for m in manifest:
        prov = m["provenance"]
        cid = prov["case_id"]
        meta = prov.get("boxes_meta", [{}] * len(m["boxes"]))
        if not m["boxes"]:
            zero_box_pages.append({"case_id": cid, "domain": prov["review_domain"],
                                   "page_file": Path(m["image"]["path"]).name})
            continue
        im = get_image(m["image"]["path"])
        for i, (b, bm) in enumerate(zip(m["boxes"], meta)):
            unit_id = f"R2-{cid}-B{i:02d}"
            xyxy = [b["polygon"][0][0], b["polygon"][0][1], b["polygon"][2][0], b["polygon"][2][1]]
            preview_name = f"{unit_id}__{cid}.png"
            pv = _annotate_preview(_crop_with_margin(im, xyxy), unit_id, bm.get("conf"), bm.get("sources", []))
            pv.save(PREVIEW_DIR / preview_name)
            units.append(
                {
                    "unit_id": unit_id,
                    "kind": "page_box",
                    "domain": prov["review_domain"],
                    "case_id": cid,
                    "page_file": Path(m["image"]["path"]).name,
                    "page_path": m["image"]["path"],
                    "box_index": i,
                    "xyxy": [round(v, 1) for v in xyxy],
                    "box_size": [round(xyxy[2] - xyxy[0], 1), round(xyxy[3] - xyxy[1], 1)],
                    "ai_cls": b["cls"],
                    "ai_conf": bm.get("conf"),
                    "sources": bm.get("sources", []),
                    "ai_text": b.get("text"),
                    "preview_file": f"previews/{preview_name}",
                    "verdict": "",
                    "user_rationale": "",
                }
            )
    page_cache.clear()

    lines = [
        "# M2-SFX-ANNOTATE-R2 阶段一（targeted BJ 新页 BJ16-25）· 用户审核工作表",
        "",
        f"- 生成：{stamp} | seed={SEED}（冻结）",
        "- 裁决枚举（verdict 列）：`confirm`（确认是 SFX，框可接受）/ `correct`（是 SFX 但框需修）/ `delete`（非 SFX）/ `miss`（页级漏标，在页小节末尾补记框坐标）",
        "- 每行附预览裁切图（20% 边距上下文，红框=AI 候选框，顶部条=unit_id/conf/来源）",
        "- `user_rationale` 列：填写裁决依据（可空）；R1 同款，AI 预判已预填，采纳即确认",
        "",
    ]
    by_page: dict[str, list[dict]] = {}
    for u in units:
        by_page.setdefault(u["case_id"], []).append(u)
    for cid in sorted(set(by_page) | {z["case_id"] for z in zero_box_pages}):
        us = by_page.get(cid, [])
        if not us:
            lines += [
                f"### {cid}（0 AI 候选框——负证据页：模型在该页无 SFX 检出，chiqui7 对 BJ 域存在已知盲区）",
                "",
                f"→ 请用户直接补画漏标 SFX 框（`miss` + 框坐标，页文件：{next(z['page_file'] for z in zero_box_pages if z['case_id'] == cid)}）",
                "",
            ]
            continue
        lines += [f"### {cid}（{len(us)} 候选框；页级漏标补记：`miss` + 框坐标）", "",
                  "| unit_id | conf | 来源 | xyxy | 预览 | 用户裁决 | user_rationale |", "|---|---|---|---|---|---|---|"]
        for u in us:
            conf_s = f"{u['ai_conf']:.2f}" if isinstance(u["ai_conf"], (int, float)) else "ref"
            lines.append(
                f"| {u['unit_id']} | {conf_s} | {'/'.join(u['sources'])} | {u['xyxy']} | {Path(u['preview_file']).name} |  |  |"
            )
        lines.append("")

    WORKSHEET_JSON.write_text(
        json.dumps({"generated_at_utc": stamp, "seed": SEED, "n_units": len(units), "units": units},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    WORKSHEET_MD.write_text("\n".join(lines), encoding="utf-8")

    conf_tiers = {"conf_ge_0.5": 0, "conf_0.2_to_0.5": 0, "conf_lt_0.2": 0, "ref_no_conf": 0}
    for u in units:
        c = u.get("ai_conf")
        if not isinstance(c, (int, float)):
            conf_tiers["ref_no_conf"] += 1
        elif c >= 0.5:
            conf_tiers["conf_ge_0.5"] += 1
        elif c >= 0.2:
            conf_tiers["conf_0.2_to_0.5"] += 1
        else:
            conf_tiers["conf_lt_0.2"] += 1
    print(f"units: {len(units)} | conf tiers: {conf_tiers} | zero_box_pages: {zero_box_pages}")
    print(f"wrote {WORKSHEET_JSON}")
    print(f"wrote {WORKSHEET_MD}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True, choices=["scan", "assemble", "worksheet", "all"])
    args = parser.parse_args()
    steps = [args.step] if args.step != "all" else ["scan", "assemble", "worksheet"]
    for s in steps:
        rc = {"scan": cmd_scan, "assemble": cmd_assemble, "worksheet": cmd_worksheet}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
