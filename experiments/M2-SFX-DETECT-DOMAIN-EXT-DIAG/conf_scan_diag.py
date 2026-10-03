"""M2-SFX-DETECT-DOMAIN-EXT-DIAG: low-conf scan + resolution probe for the
BJ-domain chiqui7 sfx-class blind spot (AC4 zero-src evidence experiment).

Three evidence layers, all reusing the PRODUCTION inference sequence
(``src/infrastructure/providers/detection_sfx.py`` internals, imported
read-only; zero src changes):

  L1  full-page letterbox (the production form) at a conf LADDER
      0.01..0.50 — separates "threshold split" from "no sfx signal at all";
  L2  60% tiles (4 per page, ~1.67x effective resolution) at conf 0.01 —
      the WEBTOON-DIAG probe form (pixel-budget restoration), adapted to
      YOLO-seg letterbox semantics (aspect-preserving, so NO anisotropy
      here — this probes resolution/scale only, NOT the WEBTOON-DIAG
      anisotropic-rescale mechanism);
  L3  per-reference-SFX crops (box inflated 20%) — the strongest form of
      "given enough pixels, does the model recognize THIS shape as sfx".

Unlike the production provider, EVERY box kept after the identical
conf-filter + all-class NMS is dumped with its FULL 4-class score vector
(bubble/panel/sfx/text) — the class-mapping-ambiguity hypothesis (sfx
signal present but argmax-lost to text) is only decidable with the full
vector, not the argmax class alone.  Additionally, for L1 the RAW
pre-NMS candidates whose letterbox-space center falls inside each
reference box are listed (NMS drops boxes; the raw query cannot).

References: the AC2 zoom-confirmed visual SFX inventory (identical to
``experiments/M2-SFX-E2E-MATERIAL/diagnose_sfx_detect.py``), plus BJ06 as
the IN-DOMAIN control page (8 production sfx regions at conf>=0.5).

Raw outputs land in ``verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/``.
Read-only over production code; no weights, paths or pipeline behaviour
are modified.

Usage:
  python experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py \
    [--out-dir verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "experiments" / "M2-TA3-B"))

from infrastructure.providers.detection_sfx import (  # noqa: E402
    SFX_CLASS_MAP,
    _build_engine,
    _letterbox,
    _map_back,
    _nms,
)
from run_qualification import SFX_WEIGHTS_DEFAULT  # noqa: E402

import numpy as np  # noqa: E402

CONF_LADDER = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
NMS_IOU = 0.7
CLASS_NAMES = [SFX_CLASS_MAP[i] for i in range(4)]  # bubble, panel, sfx, text

# AC2 zoom-confirmed visual SFX inventory (source pixels, 2946x4167) —
# identical to the prior diagnosis script; BJ06 has no reference list here
# (its 8 production sfx regions ARE the in-domain control, see CONTROL).
REFERENCE_SFX = {
    "BJ13": [
        {"text": "ピ一一ーン！", "approx_xyxy": [2210, 240, 2560, 1000]},
        {"text": "ピ一一ーン！", "approx_xyxy": [420, 2560, 760, 3400]},
    ],
    "BJ14": [
        {"text": "オギャァ", "approx_xyxy": [1230, 300, 1520, 950]},
        {"text": "オギャァ", "approx_xyxy": [400, 1900, 700, 2560]},
        {"text": "オギャァ", "approx_xyxy": [1900, 2260, 2200, 2900]},
    ],
    "BJ15": [
        {"text": "オギャァ", "approx_xyxy": [1600, 200, 1900, 800]},
        {"text": "オギャァ", "approx_xyxy": [900, 1650, 1150, 2200]},
    ],
}

# BJ06 production sfx regions (qual-BJ06.json, bj06 top-left w/h form) — the
# in-domain positive control: same page size, same letterbox, chiqui7 FOUND
# these at conf>=0.5.  Used to compare the scale distribution of in-domain
# sfx boxes vs the blind-spot references.
BJ06_SFX_REGIONS = [
    {"region_id": "3ca2446544644ceeb2768bebf61789bf", "xywh": [2145, 3084, 161, 309]},
    {"region_id": "dab09d6b4e24438cb2dc6b2ea4d18af3", "xywh": [2495, 2907, 157, 409]},
    {"region_id": "2eeaa2c4d2a747f59bd7cf52b8d12e30", "xywh": [1534, 3517, 223, 395]},
    {"region_id": "ab8974e10c0b476ab26366798668de53", "xywh": [926, 2818, 170, 294]},
    {"region_id": "eac72dfd7b834871a1cec081153b560e", "xywh": [388, 3402, 340, 534]},
    {"region_id": "ea4cbed9134c428ab3804944055449ce", "xywh": [1830, 2969, 162, 297]},
    {"region_id": "c3781c28a8e14d648560dcf03418b44b", "xywh": [408, 468, 217, 492]},
    {"region_id": "b5b747d0919542a4adf781a9f3eaa841", "xywh": [2494, 1895, 87, 103]},
]


def load_page(path: Path):
    from PIL import Image

    with Image.open(path) as im:
        rgb = im.convert("RGB")
    return rgb


def run_inference(session, np_rgb, letterbox_size: int, page_w: float, page_h: float):
    """One production-sequence inference; returns mapped-back boxes with
    full class-score vectors (conf filter at 0.01 + all-class NMS)."""
    inp, scale = _letterbox(np, np_rgb, letterbox_size)
    out = session.run(None, {"images": inp})[0]
    preds = out[0].T
    boxes_xywh = preds[:, :4]
    cls_scores = preds[:, 4:8]
    cls_ids = cls_scores.argmax(axis=1)
    confs = cls_scores.max(axis=1)
    cand = []
    for i in np.where(confs >= 0.01)[0]:
        x, y, w, h = boxes_xywh[i]
        cand.append(
            (
                [x - w / 2, y - h / 2, x + w / 2, y + h / 2],
                float(confs[i]),
                int(cls_ids[i]),
                [float(v) for v in cls_scores[i]],
            )
        )
    keep = _nms([c[0] for c in cand], np.array([c[1] for c in cand]), NMS_IOU)
    boxes = []
    for i in keep:
        box, confidence, cls_id, scores = cand[i]
        x0, y0, x1, y1 = _map_back(box, scale, page_w=page_w, page_h=page_h)
        if x1 <= x0 or y1 <= y0:
            continue
        boxes.append(
            {
                "cls": CLASS_NAMES[cls_id],
                "conf": round(confidence, 4),
                "xyxy": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
                "scores": {n: round(s, 4) for n, s in zip(CLASS_NAMES, scores)},
            }
        )
    return boxes, scale, inp.shape


def raw_candidates_in_ref(session, np_rgb, letterbox_size, ref_xyxy, page_w, page_h):
    """Pre-NMS raw query: every candidate (conf>=0.01) whose LETTERBOX-space
    center falls inside the (mapped) reference box — NMS cannot have dropped
    these, so this is the cleanest 'was there ANY sfx signal here' probe."""
    inp, scale = _letterbox(np, np_rgb, letterbox_size)
    out = session.run(None, {"images": inp})[0]
    preds = out[0].T
    boxes_xywh = preds[:, :4]
    cls_scores = preds[:, 4:8]
    rx0, ry0, rx1, ry1 = [v * scale for v in ref_xyxy]
    hits = []
    for i in range(preds.shape[0]):
        x, y, w, h = boxes_xywh[i]
        cx, cy = x, y  # xywh form: x,y IS the center in Ultralytics exports
        if not (rx0 <= cx <= rx1 and ry0 <= cy <= ry1):
            continue
        scores = [float(v) for v in cls_scores[i]]
        if max(scores) < 0.01:
            continue
        hits.append(
            {
                "letterbox_center": [round(float(cx), 1), round(float(cy), 1)],
                "argmax_cls": CLASS_NAMES[int(np.argmax(scores))],
                "scores": {n: round(s, 4) for n, s in zip(CLASS_NAMES, scores)},
            }
        )
    hits.sort(key=lambda hh: hh["scores"]["sfx"], reverse=True)
    return hits[:20]


def iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    if inter <= 0.0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def ref_verdicts(boxes, refs):
    """Per-reference: enumerate intersecting boxes with full score vectors."""
    verdicts = []
    for ref in refs:
        ref_box = ref["approx_xyxy"]
        hits = [b for b in boxes if iou(ref_box, b["xyxy"]) > 0.0]
        hits.sort(key=lambda b: (b["scores"]["sfx"], b["conf"]), reverse=True)
        sfx_hits = [h for h in hits if h["cls"] == "sfx"]
        best_sfx_score = max((h["scores"]["sfx"] for h in hits), default=0.0)
        verdicts.append(
            {
                "ref": ref,
                "n_intersecting": len(hits),
                "best_sfx_class_score_among_intersecting": round(best_sfx_score, 4),
                "sfx_class_box": bool(sfx_hits),
                "intersecting_boxes": hits[:8],
            }
        )
    return verdicts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(
            REPO_ROOT / "verification" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "raw"
        ),
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    session, imgsz, imgsz_source, _raw = _build_engine(Path(SFX_WEIGHTS_DEFAULT))
    print(f"engine OK imgsz={imgsz} ({imgsz_source})")

    pages_root_ta2b = Path(
        r"G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages"
    )
    pages_root_e2e = Path(
        r"G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages"
    )
    pages = {
        "BJ06": pages_root_ta2b / "vol03_p0056.png",
        "BJ13": pages_root_e2e / "vol03_p0048.png",
        "BJ14": pages_root_e2e / "vol03_p0060.png",
        "BJ15": pages_root_e2e / "vol03_p0159.png",
    }
    for name, p in pages.items():
        if not p.is_file():
            print(f"FATAL: page missing {name}: {p}")
            return 2

    # --- L1: full-page conf ladder ----------------------------------------
    l1 = {
        "layer": "L1_fullpage_conf_ladder",
        "letterbox": imgsz,
        "conf_ladder": CONF_LADDER,
        "note": "production inference sequence per conf rung (conf filter -> all-class NMS IoU 0.7); every kept box carries its full 4-class score vector",
        "pages": {},
    }
    for case_id, page_path in pages.items():
        rgb = load_page(page_path)
        page_w, page_h = rgb.size
        np_rgb = np.asarray(rgb)
        t0 = time.perf_counter()
        boxes, scale, inp_shape = run_inference(session, np_rgb, imgsz, page_w, page_h)
        elapsed = round(time.perf_counter() - t0, 1)
        by_rung = {}
        for rung in CONF_LADDER:
            kept = [b for b in boxes if b["conf"] >= rung]
            by_rung[str(rung)] = {
                "count_by_class": {
                    c: sum(1 for b in kept if b["cls"] == c) for c in CLASS_NAMES
                },
                "boxes": kept,
            }
        refs = ref_verdicts(boxes, REFERENCE_SFX.get(case_id, []))
        raw_ref_query = {}
        if case_id in REFERENCE_SFX:
            for idx, ref in enumerate(REFERENCE_SFX[case_id]):
                raw_ref_query[f"ref{idx + 1}"] = raw_candidates_in_ref(
                    session, np_rgb, imgsz, ref["approx_xyxy"], page_w, page_h
                )
        l1["pages"][case_id] = {
            "page": str(page_path),
            "page_size": [page_w, page_h],
            "inference_s": elapsed,
            "conf_ge_0.01_count_by_class": {
                c: sum(1 for b in boxes if b["cls"] == c) for c in CLASS_NAMES
            },
            "by_rung": by_rung,
            "reference_verdicts": refs,
            "raw_pre_nms_candidates_in_reference": raw_ref_query,
        }
        print(
            f"L1 {case_id}: {len(boxes)} boxes @0.01",
            l1["pages"][case_id]["conf_ge_0.01_count_by_class"],
            f"{elapsed}s",
        )
        for v in refs:
            print(
                f"   ref {v['ref']['text']} -> sfx_box={v['sfx_class_box']} "
                f"best_sfx_score={v['best_sfx_class_score_among_intersecting']}"
            )
    (out_dir / "l1-fullpage-conf-scan.json").write_text(
        json.dumps(l1, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("wrote", out_dir / "l1-fullpage-conf-scan.json")

    # --- L2: 60% tiles (effective resolution ~1.67x) -----------------------
    l2 = {
        "layer": "L2_tiles_60pct",
        "tile_frac": 0.60,
        "note": "four 60%-size tiles per page (TL/TR/BL/BR, 40% overlap between neighbours), each letterboxed to the same imgsz — effective full-page resolution ~1.67x the L1 form; WEBTOON-DIAG probe form adapted to aspect-preserving letterbox (resolution probe ONLY, no anisotropy involved); conf 0.01",
        "pages": {},
    }
    for case_id in ("BJ13", "BJ14", "BJ15"):
        rgb = load_page(pages[case_id])
        page_w, page_h = rgb.size
        np_rgb = np.asarray(rgb)
        tw, th = int(page_w * 0.60), int(page_h * 0.60)
        anchors = [
            ("TL", 0, 0),
            ("TR", page_w - tw, 0),
            ("BL", 0, page_h - th),
            ("BR", page_w - tw, page_h - th),
        ]
        tile_reports = []
        page_boxes = []
        for tname, ax, ay in anchors:
            tile = rgb.crop((ax, ay, ax + tw, ay + th))
            np_tile = np.asarray(tile)
            t0 = time.perf_counter()
            boxes, _scale, _shape = run_inference(
                session, np_tile, imgsz, float(tw), float(th)
            )
            elapsed = round(time.perf_counter() - t0, 1)
            mapped = []
            for b in boxes:
                x0, y0, x1, y1 = b["xyxy"]
                mapped.append(
                    {
                        **b,
                        "xyxy": [round(x0 + ax, 1), round(y0 + ay, 1), round(x1 + ax, 1), round(y1 + ay, 1)],
                    }
                )
            page_boxes.extend(mapped)
            tile_reports.append(
                {
                    "tile": tname,
                    "anchor_xy": [ax, ay],
                    "tile_size": [tw, th],
                    "inference_s": elapsed,
                    "count_by_class": {
                        c: sum(1 for b in boxes if b["cls"] == c) for c in CLASS_NAMES
                    },
                }
            )
            print(f"L2 {case_id}/{tname}: {len(boxes)} boxes", tile_reports[-1]["count_by_class"], f"{elapsed}s")
        refs = ref_verdicts(page_boxes, REFERENCE_SFX[case_id])
        l2["pages"][case_id] = {
            "tiles": tile_reports,
            "reference_verdicts": refs,
        }
        for v in refs:
            print(
                f"   ref {v['ref']['text']} -> sfx_box={v['sfx_class_box']} "
                f"best_sfx_score={v['best_sfx_class_score_among_intersecting']}"
            )
    (out_dir / "l2-tiles-resolution-probe.json").write_text(
        json.dumps(l2, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("wrote", out_dir / "l2-tiles-resolution-probe.json")

    # --- L3: per-reference crops (box inflated 20%) ------------------------
    l3 = {
        "layer": "L3_reference_crops",
        "inflate": 0.20,
        "note": "each reference SFX box inflated 20% on all sides, cropped and letterboxed to the same imgsz — the strongest 'given enough pixels, is THIS shape recognized as sfx' probe; conf 0.01; full score vectors",
        "crops": {},
    }
    for case_id, refs in REFERENCE_SFX.items():
        rgb = load_page(pages[case_id])
        page_w, page_h = rgb.size
        crop_reports = []
        for idx, ref in enumerate(refs):
            x0, y0, x1, y1 = ref["approx_xyxy"]
            bw, bh = x1 - x0, y1 - y0
            cx0 = max(0, int(x0 - bw * 0.20))
            cy0 = max(0, int(y0 - bh * 0.20))
            cx1 = min(page_w, int(x1 + bw * 0.20))
            cy1 = min(page_h, int(y1 + bh * 0.20))
            crop = rgb.crop((cx0, cy0, cx1, cy1))
            np_crop = np.asarray(crop)
            t0 = time.perf_counter()
            boxes, _scale, _shape = run_inference(
                session,
                np_crop,
                imgsz,
                float(cx1 - cx0),
                float(cy1 - cy0),
            )
            elapsed = round(time.perf_counter() - t0, 1)
            # map crop-local boxes back to page coordinates for reporting
            page_boxes = []
            for b in boxes:
                bx0, by0, bx1, by1 = b["xyxy"]
                page_boxes.append(
                    {
                        **b,
                        "xyxy": [
                            round(bx0 + cx0, 1),
                            round(by0 + cy0, 1),
                            round(bx1 + cx0, 1),
                            round(by1 + cy0, 1),
                        ],
                    }
                )
            best_sfx = max((b["scores"]["sfx"] for b in boxes), default=0.0)
            crop_reports.append(
                {
                    "ref": ref,
                    "crop_xyxy_page": [cx0, cy0, cx1, cy1],
                    "crop_size": [cx1 - cx0, cy1 - cy0],
                    "effective_scale_vs_fullpage": round(
                        (cy1 - cy0) / page_h, 3
                    ),
                    "inference_s": elapsed,
                    "count_by_class": {
                        c: sum(1 for b in boxes if b["cls"] == c) for c in CLASS_NAMES
                    },
                    "best_sfx_class_score_any_box": round(best_sfx, 4),
                    "boxes_top": sorted(
                        boxes, key=lambda b: b["conf"], reverse=True
                    )[:12],
                }
            )
            print(
                f"L3 {case_id}/ref{idx + 1}: {len(boxes)} boxes",
                crop_reports[-1]["count_by_class"],
                f"best_sfx={best_sfx:.4f}",
                f"{elapsed}s",
            )
        l3["crops"][case_id] = crop_reports
    (out_dir / "l3-reference-crops.json").write_text(
        json.dumps(l3, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("wrote", out_dir / "l3-reference-crops.json")

    manifest = {
        "tool": "experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "weights": SFX_WEIGHTS_DEFAULT,
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "nms_iou": NMS_IOU,
        "conf_ladder": CONF_LADDER,
        "bj06_control_regions": BJ06_SFX_REGIONS,
        "outputs": [
            "l1-fullpage-conf-scan.json",
            "l2-tiles-resolution-probe.json",
            "l3-reference-crops.json",
        ],
    }
    (out_dir / "scan-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("wrote", out_dir / "scan-manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
