"""Run the ogkalu production detector over the SFX candidate sample (AC2).

Status-quo baseline for M2-SFX-DETECT-EVAL: the pinned ogkalu
``comic-text-and-bubble-detector`` (RT-DETR-v2, classes 0=bubble / 1=
text_bubble / 2=text_free, NO SFX class) runs over every candidate region
from ``build_sfx_sample.py`` and ALL text-class detections are recorded at
a harvest threshold of 0.25 (the C1/C4 formal threshold 0.5 stays the
primary reporting cut; 0.25-0.5 boxes are sensitivity evidence only).

The inference path is REUSED BY IMPORT from the frozen C4 eval base
``experiments/M2-DOCTR-QUAL/eval_detection_manga.py`` (detect_text_boxes +
CANDIDATE + sha256_file) — zero bytes of it are changed. No merge, no GT
matching, no judging happens here: this is a raw-detection harvest for the
agent's visual SFX pass (directional evidence; previews carry a 100 px
coordinate grid so visually estimated SFX boxes are anchored).

Previews are written OUTSIDE the repo (task-env tree, never committed).
The JSON payload (detections per candidate region) is committed.

Usage (from the worktree root):

  "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
      experiments/M2-SFX-DETECT/eval_sfx_ogkalu.py \
      --candidates experiments/M2-SFX-DETECT/sfx-sample-candidates.json \
      --weights-dir "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector" \
      --device cuda --harvest-threshold 0.25 \
      --preview-dir "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/previews" \
      --out experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

# Frozen C4 eval base, reused strictly by import (zero-change rule).
_HARNESS = importlib.util.spec_from_file_location(
    "eval_detection_manga",
    Path(__file__).resolve().parents[1] / "M2-DOCTR-QUAL" / "eval_detection_manga.py",
)
_eval_manga = importlib.util.module_from_spec(_HARNESS)
import sys

sys.modules["eval_detection_manga"] = _eval_manga
_HARNESS.loader.exec_module(_eval_manga)

detect_text_boxes = _eval_manga.detect_text_boxes
CANDIDATE = _eval_manga.CANDIDATE
sha256_file = _eval_manga.sha256_file

PRIMARY_THRESHOLD = 0.5  # C1/C4 formal cut; reporting primary
GRID_PX = 100


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--weights-dir", type=Path, required=True)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    parser.add_argument("--harvest-threshold", type=float, default=0.25)
    parser.add_argument("--preview-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    import numpy as np
    from PIL import Image, ImageDraw

    cand_payload = json.loads(args.candidates.read_text(encoding="utf-8"))
    candidates = cand_payload["candidates"]
    regions = sorted({(c["case_id"], c["region_index"], c["image"]) for c in candidates})

    model, processor, weights_sha256 = _eval_manga.load_model(args.weights_dir, args.device)
    args.preview_dir.mkdir(parents=True, exist_ok=True)

    detections_by_region: dict[str, dict] = {}
    for case_id, region_index, image_path in regions:
        img = Image.open(image_path).convert("RGB")
        rgb = np.asarray(img, dtype=np.uint8)
        w, h = float(img.width), float(img.height)
        classes: list[int] = []
        boxes, n_bubble = detect_text_boxes(
            model, processor, rgb, w, h, args.harvest_threshold, class_sink=classes
        )
        dets = [
            {
                "box_xyxy": [round(float(v), 1) for v in box],
                "conf": round(float(conf), 4),
                "cls": CANDIDATE["classes"][str(cls)],
                "conf_ge_primary": float(conf) >= PRIMARY_THRESHOLD,
            }
            for (box, conf), cls in zip(boxes, classes)
        ]
        detections_by_region[f"{case_id}_R{region_index:03d}"] = {
            "case_id": case_id,
            "region_index": region_index,
            "image": image_path,
            "width": int(w),
            "height": int(h),
            "n_text_dets_harvest": len(dets),
            "n_bubble_dropped": n_bubble,
            "detections": dets,
        }

        # preview: 100 px grid + prior box (green) + detections (red, conf)
        canvas = img.copy()
        draw = ImageDraw.Draw(canvas)
        for x in range(0, img.width, GRID_PX):
            draw.line([(x, 0), (x, img.height)], fill=(160, 160, 160), width=1)
            draw.text((x + 2, 2), str(x), fill=(60, 60, 60))
        for y in range(0, img.height, GRID_PX):
            draw.line([(0, y), (img.width, y)], fill=(160, 160, 160), width=1)
            draw.text((2, y + 2), str(y), fill=(60, 60, 60))
        for c in candidates:
            if (c["case_id"], c["region_index"]) != (case_id, region_index):
                continue
            if c.get("sfx_prior_box_xyxy"):
                x0, y0, x1, y1 = c["sfx_prior_box_xyxy"]
                draw.rectangle([x0, y0, x1, y1], outline=(0, 160, 0), width=2)
        for d in dets:
            x0, y0, x1, y1 = d["box_xyxy"]
            draw.rectangle([x0, y0, x1, y1], outline=(220, 30, 30), width=2)
            draw.text(
                (x0 + 2, max(0, y0 - 12)),
                f"{d['conf']:.2f} {d['cls'][:9]}",
                fill=(220, 30, 30),
            )
        preview_name = f"ogkalu__{case_id}_R{region_index:03d}.png"
        canvas.save(args.preview_dir / preview_name, format="PNG")

    payload = {
        "schema": "m2-sfx-detect/ogkalu-sfx-frames@1",
        "task": "M2-SFX-DETECT-EVAL",
        "candidate_model": {**CANDIDATE, "weights_sha256": weights_sha256},
        "weights_dir": str(args.weights_dir),
        "device": args.device,
        "harvest_threshold": args.harvest_threshold,
        "primary_threshold": PRIMARY_THRESHOLD,
        "threshold_note": (
            "harvest=0.25 records 0.25-0.5 boxes as sensitivity evidence; "
            "conf_ge_primary marks the C1/C4-formal 0.5 cut; visual verdicts "
            "report both (directional evidence, no formal SFX GT)"
        ),
        "preview_note": (
            "previews carry a 100 px coordinate grid; green=sample prior box "
            "(C1 evidence or ogkalu FP), red=ogkalu detection with conf+class"
        ),
        "candidates_source": str(args.candidates),
        "n_regions": len(detections_by_region),
        "regions": detections_by_region,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    n_dets = sum(r["n_text_dets_harvest"] for r in detections_by_region.values())
    print(
        f"ogkalu harvest done: regions={len(detections_by_region)} "
        f"text_dets(>= {args.harvest_threshold})={n_dets} -> {args.out}"
    )
    print(f"previews -> {args.preview_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
