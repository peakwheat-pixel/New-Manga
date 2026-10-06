"""M2-SFX-BJ13-RECALL-1: v2b-production-chain sfx recall probe for the
BJ-domain blind spot pages (AC1 zero-src evidence experiment).

Question answered (three-state verdict per page, decided in the report —
this script only produces the numbers): has sfx recall RECOVERED on the
current v2b production chain for BJ13/BJ14/BJ15, with BJ06 as the
in-domain positive control?

Production semantics reused verbatim (imported read-only, zero src changes):

  - the v2b production weights (T4 switch @cff4923e): the pinned ONNX whose
    sha256 is enforced by ``_build_engine`` (SFX_WEIGHTS_SHA256 =
    944e8114…d418d) — a substituted/corrupted artifact is a typed failure,
    never a silent run;
  - ``NEWMANGA_SFX_EP`` untouched (default dml, the GPU deployment ruling);
    the effective EP is read back off the session and printed at the TOP of
    the log — a wrapper-level DML->CPU fallback is visible, never silent;
  - the production inference sequence: letterbox -> session.run ->
    conf filter -> all-class NMS (IoU 0.7) -> map back to page pixels,
    exactly the DOMAIN-EXT-DIAG L1 probe form
    (``experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py``);
  - conf rung 0.5 = the frozen production conf threshold (SFX_CONF_THRESHOLD).

Per page the probe records:
  L1-form ladder: every box kept at conf>=0.01 with its FULL 4-class score
    vector, re-filtered per rung (0.01..0.50) — one inference per page, all
    rungs read off the same deterministic output;
  reference verdicts: per visual SFX reference box (the AC2 zoom-confirmed
    inventory, identical to DOMAIN-EXT-DIAG) the best conf>=0.5 sfx-class
    candidate IoU, plus the best sfx-class score among intersecting boxes
    at ANY rung, plus the raw pre-NMS sfx-score peak inside the reference
    (letterbox-space center test — directly comparable to the DOMAIN-EXT-DIAG
    raw peaks 0.0855/0.0043 on BJ13);
  BJ06 control: the 8 production sfx regions (qual-BJ06.json, carried
    verbatim from the prior probe) scored the same way;
  arbitration overlap (AC2 data face): the REAL conf>=0.5 sfx candidates
    crossed with the primary candidates of the M2-REGION-OVERLAP-ARBITRATION
    rerun (read-only from that Task's raw evidence) — per-pair IoU, the
    0.85+ review-line census, containment shapes, and the simulated
    relabel/partial-overlap outcome at the frozen 0.90 threshold.  The
    primary candidates are reusable because the ogkalu snapshot identity is
    RE-VERIFIED HERE against the frozen per-file pins before use; a drift
    is a hard failure, not a footnote.

Fail-fast discipline (M2-SFX-EPFAIL-AUDIT-1 lesson): an engine-init failure
exits non-zero with the reason at the top of the log — a summary file on
disk is NOT evidence by itself; every page carries its inference time so a
degenerate (cached/empty) run is detectable.

Raw outputs land in ``verification/M2-SFX-BJ13-RECALL-1/raw/``.
Read-only over production code and prior evidence; no weights, paths or
pipeline behaviour are modified.

Usage (the venv must expose onnxruntime + numpy + PIL):
  "G:/CODEX/New Manga.task-envs/M2-SFX-T5-TILE-gpu/Scripts/python.exe" \
    experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py \
    [--out-dir verification/M2-SFX-BJ13-RECALL-1/raw]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from infrastructure.providers.detection_manga import (  # noqa: E402
    MANGA_CONFIG_SHA256,
    MANGA_MODEL_SHA256,
    MANGA_PREPROCESSOR_SHA256,
)
from infrastructure.providers.detection_sfx import (  # noqa: E402
    SFX_CLASS_MAP,
    SFX_CONF_THRESHOLD,
    SFX_NMS_IOU,
    _build_engine,
    _letterbox,
    _map_back,
    _nms,
)

import numpy as np  # noqa: E402

CLASS_NAMES = [SFX_CLASS_MAP[i] for i in range(4)]  # bubble, panel, sfx, text
CONF_RUNGS = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]

#: The v2b production weights (T4 switch @cff4923e; local release channel).
#: sha256 is enforced inside ``_build_engine`` against the frozen pin.
DEFAULT_V2B_WEIGHTS = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)

#: The primary detector snapshot used by the M2-REGION-OVERLAP-ARBITRATION
#: rerun — its identity is re-verified below before its candidates are reused.
OGKALU_SNAPSHOT_DIR = Path(
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"
)
ARBITRATION_RAW = (
    REPO_ROOT
    / "verification"
    / "M2-REGION-OVERLAP-ARBITRATION"
    / "raw"
    / "arbitrate-pages.json"
)

#: AC2 zoom-confirmed visual SFX inventory — verbatim from the prior probe
#: (experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py), source
#: pixels, 2946x4167 pages.  Approximate (±10-20px) by construction.
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

#: BJ06 production sfx regions (qual-BJ06.json, bj06 top-left w/h form) —
#: the in-domain positive control, verbatim from the prior probe.
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
        return im.convert("RGB")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_primary_snapshot() -> dict:
    """Re-verify the ogkalu snapshot identity against the frozen pins.

    The arbitration rerun's primary candidates may only be reused if THIS
    exact snapshot produced them; a drift is exit code 3, never a footnote.
    """
    pins = {
        "model.safetensors": MANGA_MODEL_SHA256,
        "config.json": MANGA_CONFIG_SHA256,
        "preprocessor_config.json": MANGA_PREPROCESSOR_SHA256,
    }
    checked = {}
    for filename, pin in pins.items():
        path = OGKALU_SNAPSHOT_DIR / filename
        if not path.is_file():
            print(
                f"FATAL: primary snapshot file missing: {path}",
                flush=True,
            )
            sys.exit(3)
        actual = sha256_file(path)
        checked[filename] = actual
        if actual != pin:
            print(
                f"FATAL: primary snapshot drift: {path} sha256 {actual} "
                f"!= frozen pin {pin} — the arbitration rerun primary "
                "candidates must NOT be reused against a different snapshot",
                flush=True,
            )
            sys.exit(3)
    return {"dir": str(OGKALU_SNAPSHOT_DIR), "files": checked}


def infer_once(session, np_rgb, imgsz: int, page_w: float, page_h: float):
    """One production-sequence inference.  Returns the kept boxes (conf>=0.01,
    all-class NMS, mapped to page pixels, full 4-class vectors) together with
    the raw pre-NMS letterbox-space candidates (xywh centers + class scores)
    so the reference-interior query reads the SAME inference output."""
    inp, scale = _letterbox(np, np_rgb, imgsz)
    t0 = time.perf_counter()
    out = session.run(None, {"images": inp})[0]
    elapsed = round(time.perf_counter() - t0, 3)
    preds = out[0].T
    boxes_xywh = preds[:, :4]
    cls_scores = preds[:, 4:8]
    cls_ids = cls_scores.argmax(axis=1)
    confs = cls_scores.max(axis=1)

    raw = []
    for i in range(preds.shape[0]):
        scores = [float(v) for v in cls_scores[i]]
        if max(scores) < 0.01:
            continue
        raw.append(
            (
                float(boxes_xywh[i][0]),
                float(boxes_xywh[i][1]),
                scores,
            )
        )

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
    keep = _nms([c[0] for c in cand], np.array([c[1] for c in cand]), SFX_NMS_IOU)
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
    return boxes, raw, scale, elapsed


def iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    if inter <= 0.0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def coverage(inner, outer) -> float:
    """Fraction of ``inner``'s area covered by ``outer`` — the containment
    shape detector (1.0 = fully contained; the arbitration report's
    '内含形' notion, cf. BJ06 sfx#7 ⊆ speech#2)."""
    ix = max(0.0, min(inner[2], outer[2]) - max(inner[0], outer[0]))
    iy = max(0.0, min(inner[3], outer[3]) - max(inner[1], outer[1]))
    area_inner = max(0.0, (inner[2] - inner[0]) * (inner[3] - inner[1]))
    if area_inner <= 0.0:
        return 0.0
    return (ix * iy) / area_inner


def raw_peak_in_reference(raw, ref_xyxy, scale: float) -> dict:
    """Pre-NMS query along the DOMAIN-EXT-DIAG L1 form: every raw candidate
    (conf>=0.01) whose LETTERBOX-space center falls inside the scaled
    reference box; the sfx-score peak is directly comparable to the prior
    raw numbers (BJ13: 0.0855 / 0.0043)."""
    rx0, ry0, rx1, ry1 = [v * scale for v in ref_xyxy]
    hits = []
    for cx, cy, scores in raw:
        if not (rx0 <= cx <= rx1 and ry0 <= cy <= ry1):
            continue
        hits.append(
            {
                "letterbox_center": [round(cx, 1), round(cy, 1)],
                "argmax_cls": CLASS_NAMES[int(np.argmax(scores))],
                "scores": {n: round(s, 4) for n, s in zip(CLASS_NAMES, scores)},
            }
        )
    hits.sort(key=lambda hh: hh["scores"]["sfx"], reverse=True)
    return {
        "n_raw_candidates_conf_ge_0.01": len(hits),
        "top_sfx_score": hits[0]["scores"]["sfx"] if hits else 0.0,
        "top20": hits[:20],
    }


def reference_verdicts(boxes, refs) -> list[dict]:
    """Per reference box: production-rung (conf>=0.5) sfx-class IoU best,
    plus every intersecting sfx-class candidate at ANY conf>=0.01 (full box,
    so the report can read sub-threshold recall geometry), plus the best
    sfx-class score among intersecting boxes."""
    verdicts = []
    for ref in refs:
        ref_box = ref["approx_xyxy"]
        hits = [b for b in boxes if iou(ref_box, b["xyxy"]) > 0.0]
        prod_sfx = [b for b in hits if b["cls"] == "sfx" and b["conf"] >= SFX_CONF_THRESHOLD]
        sfx_hits = [b for b in hits if b["cls"] == "sfx"]
        sfx_hits.sort(key=lambda b: b["scores"]["sfx"], reverse=True)
        best_prod_iou = max(
            (iou(ref_box, b["xyxy"]) for b in prod_sfx), default=0.0
        )
        best_sfx_score = max((h["scores"]["sfx"] for h in hits), default=0.0)
        verdicts.append(
            {
                "ref": ref,
                "n_intersecting": len(hits),
                "production_sfx_candidates_conf_ge_0.5": len(prod_sfx),
                "best_prod_sfx_iou": round(best_prod_iou, 4),
                "best_sfx_class_score_among_intersecting": round(best_sfx_score, 4),
                "prod_sfx_boxes": prod_sfx[:8],
                "sfx_class_intersecting_any_conf": sfx_hits[:8],
            }
        )
    return verdicts


def bj06_region_recall(boxes) -> dict:
    """In-domain positive control: how many of the 8 production sfx regions
    are hit by a conf>=0.5 sfx-class candidate (IoU > 0), best IoU each."""
    per_region = []
    hits = 0
    for region in BJ06_SFX_REGIONS:
        x, y, w, h = region["xywh"]
        ref_box = [x, y, x + w, y + h]
        prod_sfx = [
            b
            for b in boxes
            if b["cls"] == "sfx" and b["conf"] >= SFX_CONF_THRESHOLD
        ]
        best = max((iou(ref_box, b["xyxy"]) for b in prod_sfx), default=0.0)
        if best > 0.0:
            hits += 1
        per_region.append(
            {
                "region_id": region["region_id"],
                "xyxy": ref_box,
                "best_prod_sfx_iou": round(best, 4),
            }
        )
    return {"regions_hit": hits, "regions_total": len(BJ06_SFX_REGIONS), "per_region": per_region}


def primary_bbox(candidate: dict) -> list[float]:
    """The arbitration rerun stored each merged candidate with its bbox
    (the same min/max caliber the assembly's ``RegionGeometry`` uses — the
    ``_bbox`` form the arbitration gate itself compares)."""
    return [float(v) for v in candidate["bbox"]]


def arbitration_overlap(sfx_boxes, all_candidates) -> dict:
    """AC2 data face: real conf>=0.5 sfx candidates x PRIMARY candidates
    (M2-REGION-OVERLAP-ARBITRATION rerun), the frozen 0.90 domain, the
    0.85+ review line, containment shapes, and the simulated gate outcome.

    Caliber note: the rerun dump mixes the two channels in one list —
    ``manga-N`` labels are the primary (ogkalu) candidates, ``sfx-N`` labels
    are the CHIQUI7 sfx-channel candidates of that rerun.  The arbitration
    gate is directional sfx x primary, so only ``manga-`` entries qualify
    here (the same filter the arbitration experiment itself applies at
    arbitrate_bj13.py:215); the excluded entries are listed so the caliber
    is auditable."""
    primary_candidates = [
        c for c in all_candidates if c.get("label", "").startswith("manga-")
    ]
    excluded = [
        c.get("label", "?")
        for c in all_candidates
        if not c.get("label", "").startswith("manga-")
    ]
    pairs = []
    for si, sfx in enumerate(sfx_boxes):
        for pi, prim in enumerate(primary_candidates):
            pbox = primary_bbox(prim)
            pair_iou = iou(sfx["xyxy"], pbox)
            if pair_iou <= 0.0:
                continue
            pairs.append(
                {
                    "sfx_idx": si,
                    "sfx_conf": sfx["conf"],
                    "sfx_xyxy": sfx["xyxy"],
                    "primary_idx": pi,
                    "primary_conf": round(prim["confidence"], 4),
                    "primary_bbox": [round(v, 1) for v in pbox],
                    "iou": round(pair_iou, 4),
                    "sfx_covered_by_primary": round(
                        coverage(sfx["xyxy"], pbox), 4
                    ),
                    "primary_covered_by_sfx": round(
                        coverage(pbox, sfx["xyxy"]), 4
                    ),
                }
            )
    pairs.sort(key=lambda p: p["iou"], reverse=True)
    max_iou = pairs[0]["iou"] if pairs else 0.0
    relabels = sum(1 for p in pairs if p["iou"] >= 0.90)
    return {
        "n_sfx_candidates": len(sfx_boxes),
        "n_primary_candidates": len(primary_candidates),
        "excluded_non_primary_labels": excluded,
        "pairs_desc": pairs,
        "max_pair_iou": max_iou,
        "pairs_ge_0.85": sum(1 for p in pairs if p["iou"] >= 0.85),
        "containment_pairs_any_direction_1.0": sum(
            1
            for p in pairs
            if p["sfx_covered_by_primary"] >= 0.999
            or p["primary_covered_by_sfx"] >= 0.999
        ),
        "simulated_gate_at_frozen_0.90": {
            "relabels": relabels,
            "partial_overlap": (
                f"{max(p['iou'] for p in pairs if p['iou'] < 0.90):.4f}"
                if not relabels and pairs
                else None
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(
            REPO_ROOT / "verification" / "M2-SFX-BJ13-RECALL-1" / "raw"
        ),
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- environment fail-fast gates (log-visible, non-zero exits) ---------
    weights = Path(
        os.environ.get("NEWMANGA_SFX_WEIGHTS") or DEFAULT_V2B_WEIGHTS
    )
    if not weights.is_file():
        print(f"FATAL: v2b weights missing: {weights}", flush=True)
        return 2
    weights_sha = sha256_file(weights)
    print(f"weights: {weights}", flush=True)
    print(f"weights sha256: {weights_sha}", flush=True)

    primary_check = verify_primary_snapshot()
    print(f"primary snapshot identity re-verified: {primary_check['dir']}", flush=True)

    arbitration_raw_sha = sha256_file(ARBITRATION_RAW)
    with open(ARBITRATION_RAW, encoding="utf-8") as handle:
        arbitration_pages = json.load(handle)
    print(
        f"primary candidates read from {ARBITRATION_RAW} "
        f"(sha256 {arbitration_raw_sha[:16]}…)",
        flush=True,
    )

    pages = {
        "BJ06": Path(
            r"G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages/vol03_p0056.png"
        ),
        "BJ13": Path(
            r"G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages/vol03_p0048.png"
        ),
        "BJ14": Path(
            r"G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages/vol03_p0060.png"
        ),
        "BJ15": Path(
            r"G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages/vol03_p0159.png"
        ),
    }
    for name, p in pages.items():
        if not p.is_file():
            print(f"FATAL: page missing {name}: {p}", flush=True)
            return 2

    # --- engine build (NEWMANGA_SFX_EP untouched: default dml) -------------
    try:
        session, imgsz, imgsz_source, _raw_text, ep_prov = _build_engine(weights)
    except Exception as error:  # noqa: BLE001 - fail-fast, log-visible
        print(f"FATAL: engine init failed: {error!r}", flush=True)
        traceback.print_exc()
        return 4
    print(
        f"ENGINE OK imgsz={imgsz} ({imgsz_source}) "
        f"ep_requested={ep_prov.requested} ep_effective={ep_prov.effective} "
        f"ep_fallback={ep_prov.fallback_reason!r}",
        flush=True,
    )
    if ep_prov.effective != "dml":
        print(
            "WARNING: effective EP is NOT dml — numbers below carry the "
            f"degradation provenance above (DML<->CPU drift window ≤2e-06 "
            "is the registered bound; 'bit-identical' claims are forbidden "
            "across forms)",
            flush=True,
        )

    # --- per-page probe -----------------------------------------------------
    report = {
        "task": "M2-SFX-BJ13-RECALL-1",
        "generated_at_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "conf_threshold_production": SFX_CONF_THRESHOLD,
        "nms_iou": SFX_NMS_IOU,
        "conf_rungs": CONF_RUNGS,
        "weights": {
            "path": str(weights),
            "sha256": weights_sha,
            "pin_source": "src/infrastructure/providers/detection_sfx.py SFX_WEIGHTS_SHA256 (v2b, T4 @cff4923e)",
        },
        "ep": {
            "requested": ep_prov.requested,
            "effective": ep_prov.effective,
            "fallback_reason": ep_prov.fallback_reason,
        },
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "primary_reuse": {
            "arbitration_raw": str(ARBITRATION_RAW),
            "arbitration_raw_sha256": arbitration_raw_sha,
            "ogkalu_snapshot": primary_check,
            "note": "primary candidates reused read-only; snapshot identity re-verified against frozen pins this run",
        },
        "pages": {},
    }

    for case_id, page_path in pages.items():
        rgb = load_page(page_path)
        page_w, page_h = rgb.size
        np_rgb = np.asarray(rgb)
        boxes, raw, scale, elapsed = infer_once(
            session, np_rgb, imgsz, page_w, page_h
        )
        by_rung = {}
        for rung in CONF_RUNGS:
            kept = [b for b in boxes if b["conf"] >= rung]
            by_rung[str(rung)] = {
                "count_by_class": {
                    c: sum(1 for b in kept if b["cls"] == c)
                    for c in CLASS_NAMES
                },
            }
        refs = REFERENCE_SFX.get(case_id, [])
        ref_verdicts = reference_verdicts(boxes, refs)
        raw_queries = {}
        for idx, ref in enumerate(refs):
            raw_queries[f"ref{idx + 1}"] = raw_peak_in_reference(
                raw, ref["approx_xyxy"], scale
            )
        prod_sfx_boxes = [
            b
            for b in boxes
            if b["cls"] == "sfx" and b["conf"] >= SFX_CONF_THRESHOLD
        ]
        page_entry = {
            "page": str(page_path),
            "page_size": [page_w, page_h],
            "inference_s": elapsed,
            "conf_ge_0.01_count_by_class": {
                c: sum(1 for b in boxes if b["cls"] == c) for c in CLASS_NAMES
            },
            "by_rung": by_rung,
            "production_sfx_candidates_conf_ge_0.5": prod_sfx_boxes,
            "reference_verdicts": ref_verdicts,
            "raw_pre_nms_in_reference": raw_queries,
        }
        if case_id == "BJ06":
            page_entry["bj06_region_recall"] = bj06_region_recall(prod_sfx_boxes)
        # AC2 data face on EVERY page: BJ13/14/15 are the blind-spot pages,
        # BJ06 is the IN-DOMAIN control for the same overlap caliber (the
        # arbitration report's 0.8865 in-domain reading was chiqui7-sfx x
        # primary; the v2b form belongs in the same table).
        page_entry["arbitration_overlap_vs_primary_rerun"] = arbitration_overlap(
            prod_sfx_boxes, arbitration_pages[case_id]["candidates"]
        )
        report["pages"][case_id] = page_entry
        print(
            f"PROBE {case_id}: {page_w}x{page_h} {elapsed}s "
            f"conf0.5_sfx={len(prod_sfx_boxes)} "
            f"all_class={page_entry['conf_ge_0.01_count_by_class']}",
            flush=True,
        )
        for v in ref_verdicts:
            print(
                f"   ref {v['ref']['text']} {v['ref']['approx_xyxy']} -> "
                f"prod_sfx_iou={v['best_prod_sfx_iou']} "
                f"best_sfx_score_any={v['best_sfx_class_score_among_intersecting']}",
                flush=True,
            )
        if "arbitration_overlap_vs_primary_rerun" in page_entry:
            ov = page_entry["arbitration_overlap_vs_primary_rerun"]
            print(
                f"   arbitration: max_pair_iou={ov['max_pair_iou']} "
                f"pairs_ge_0.85={ov['pairs_ge_0.85']} "
                f"containment={ov['containment_pairs_any_direction_1.0']} "
                f"sim_gate={ov['simulated_gate_at_frozen_0.90']}",
                flush=True,
            )
        if case_id == "BJ06":
            print(
                f"   BJ06 control: {page_entry['bj06_region_recall']['regions_hit']}"
                f"/{page_entry['bj06_region_recall']['regions_total']} regions hit",
                flush=True,
            )

    out_path = out_dir / "recall-probe.json"
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"wrote {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
