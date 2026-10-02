"""M2-SFX-E2E-MATERIAL: why did the new pages yield (almost) no sfx regions?

Diagnostic-only replay of the PRODUCTION chiqui7 inference sequence
(``src/infrastructure/providers/detection_sfx.py`` internals, imported
read-only — zero src changes) with ONE difference: after the identical
conf-filter + all-class NMS, this keeps ALL FOUR classes (bubble/panel/sfx/
text) at conf>=0.25 instead of filtering to the sfx class, so the detection
behaviour AT THE VISUAL SFX LOCATIONS can be classified:

  - no box at all            -> detector blind spot (recall gap);
  - boxes of text/bubble cls -> class confusion (the DETECT-EVAL §3.3 form);
  - sfx box below 0.5        -> sub-threshold hit (frozen-threshold effect).

Reference locations are the AC2 visual SFX inventory (zoom-confirmed);
per-page crops with the drawn boxes are written to the git-external tree
for eyeball verification.  Read-only over production code; no weights,
paths or pipeline behaviour are modified.

Usage:
  python experiments/M2-SFX-E2E-MATERIAL/diagnose_sfx_detect.py \
    [--conf 0.25] [--preview-dir G:/.../detect-diag-previews]
"""

from __future__ import annotations

import argparse
import json
import sys
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

SFX_CLASS_ID = next(int(k) for k, v in SFX_CLASS_MAP.items() if v == "sfx")
NMS_IOU = 0.7

#: AC2 zoom-confirmed visual SFX inventory (text + approx bbox in source
#: pixels at 2946x4167, from the 100dpi inspection crops, scale 2946/1964).
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


def all_class_boxes(session, inp, scale, conf_threshold, page_w, page_h):
    """The production _sfx_boxes sequence, keeping every class after NMS."""
    out = session.run(None, {"images": inp})[0]
    preds = out[0].T
    boxes_xywh = preds[:, :4]
    cls_scores = preds[:, 4:8]
    import numpy

    cls_ids = cls_scores.argmax(axis=1)
    confs = cls_scores.max(axis=1)
    cand = []
    for i in numpy.where(confs >= conf_threshold)[0]:
        x, y, w, h = boxes_xywh[i]
        cand.append(
            ([x - w / 2, y - h / 2, x + w / 2, y + h / 2], float(confs[i]), int(cls_ids[i]))
        )
    keep = _nms([c[0] for c in cand], numpy.array([c[1] for c in cand]), NMS_IOU)
    result = []
    for i in keep:
        box, confidence, cls_id = cand[i]
        x0, y0, x1, y1 = _map_back(box, scale, page_w=page_w, page_h=page_h)
        if x1 <= x0 or y1 <= y0:
            continue
        result.append(
            {
                "cls": SFX_CLASS_MAP[cls_id],
                "conf": round(confidence, 4),
                "xyxy": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
            }
        )
    return result


def coverage(box_a, box_b) -> float:
    """intersection area / area of box_a (single-side, DETECT-EVAL caliber)."""
    ax0, ay0, ax1, ay1 = box_a
    bx0, by0, bx1, by1 = box_b
    ix = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    iy = max(0.0, min(ay1, by1) - max(ay0, by0))
    area = max(0.0, (ax1 - ax0) * (ay1 - ay0))
    return (ix * iy / area) if area > 0 else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument(
        "--preview-dir",
        default=r"G:/CODEX/New Manga.task-envs/M2-SFX-E2E-MATERIAL/detect-diag-previews",
    )
    parser.add_argument(
        "--out",
        default=str(REPO_ROOT / "verification" / "M2-SFX-E2E-MATERIAL" / "sfx-detect-diagnosis.json"),
    )
    args = parser.parse_args()

    from PIL import Image, ImageDraw

    pages_root = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official" / "vol03" / "pages"
    pages = {
        "BJ13": pages_root / "vol03_p0048.png",
        "BJ14": pages_root / "vol03_p0060.png",
        "BJ15": pages_root / "vol03_p0159.png",
    }
    session, imgsz, imgsz_source, _raw = _build_engine(Path(SFX_WEIGHTS_DEFAULT))
    print(f"engine OK imgsz={imgsz} ({imgsz_source}) conf>={args.conf}")

    preview_dir = Path(args.preview_dir)
    preview_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "tool": "experiments/M2-SFX-E2E-MATERIAL/diagnose_sfx_detect.py",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "weights": SFX_WEIGHTS_DEFAULT,
        "conf_threshold_diagnostic": args.conf,
        "production_threshold": 0.5,
        "nms_iou": NMS_IOU,
        "note": (
            "diagnostic replay of the production inference sequence with all "
            "classes kept after NMS; production keeps only cls=sfx at conf>=0.5"
        ),
        "pages": {},
    }
    for case_id, page_path in pages.items():
        with Image.open(page_path) as im:
            rgb = im.convert("RGB")
            page_w, page_h = rgb.size
            import numpy
            array = numpy.asarray(rgb)
            mod = numpy
        inp, scale = _letterbox(mod, array, imgsz)
        boxes = all_class_boxes(session, inp, scale, args.conf, page_w, page_h)

        # classify each reference SFX location against the detected boxes
        refs = []
        for ref in REFERENCE_SFX[case_id]:
            scored = sorted(
                ((b, coverage(ref["approx_xyxy"], [b["xyxy"][0], b["xyxy"][1], b["xyxy"][2], b["xyxy"][3]])) for b in boxes),
                key=lambda t: t[1],
                reverse=True,
            )
            best, best_cov = (scored[0] if scored else (None, 0.0))
            if best is None or best_cov <= 0.0:
                verdict = "no_box_at_all (detector blind spot)"
            else:
                cov_txt = f"best_cov={best_cov:.2f} cls={best['cls']} conf={best['conf']}"
                if best["cls"] == "sfx":
                    verdict = (
                        f"sfx-class box {'ABOVE' if best['conf'] >= 0.5 else 'BELOW production 0.5 threshold'}"
                        f" ({cov_txt})"
                    )
                else:
                    verdict = f"class confusion: picked up as {cov_txt}"
            refs.append({"ref": ref, "verdict": verdict})

        draw_target = rgb.copy()
        draw = ImageDraw.Draw(draw_target)
        for b in boxes:
            is_sfx = b["cls"] == "sfx"
            color = "red" if is_sfx else ("orange" if b["cls"] == "text" else "lime")
            draw.rectangle(b["xyxy"], outline=color, width=6 if is_sfx else 3)
            draw.text((b["xyxy"][0] + 4, b["xyxy"][1] + 4), f"{b['cls']} {b['conf']:.2f}", fill=color)
        for ref in REFERENCE_SFX[case_id]:
            draw.rectangle(ref["approx_xyxy"], outline="blue", width=4)
        preview = draw_target.resize((page_w // 3, page_h // 3))
        preview_path = preview_dir / f"{case_id}-detect-diag.jpg"
        preview.convert("RGB").save(preview_path, format="JPEG", quality=80)

        report["pages"][case_id] = {
            "page": str(page_path),
            "page_size": [page_w, page_h],
            "boxes_all_classes": boxes,
            "box_count_by_class": {
                cls: sum(1 for b in boxes if b["cls"] == cls) for cls in ("bubble", "panel", "sfx", "text")
            },
            "reference_sfx_verdicts": refs,
            "preview": str(preview_path),
        }
        print(f"{case_id}: {len(boxes)} boxes", report["pages"][case_id]["box_count_by_class"])
        for r in refs:
            print("   ", r["ref"]["text"], "->", r["verdict"])

    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"report -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
