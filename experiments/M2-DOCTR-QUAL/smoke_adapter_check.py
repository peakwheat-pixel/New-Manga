"""Spot-check: production DoctrDetectionProvider vs the eval harness path.

Runs the production adapter end-to-end (rgb32 page frame -> DetectionResult
blocks) over a few manifest regions AND the harness path (docTR predictor
forward + frozen ``cluster_words_into_blocks``) on the same pixels, then
compares both block count and per-block coordinates (max absolute corner
delta). Same model, same forward, same merge policy: blocks must match to
floating-point tolerance. Evidence for AC4 adapter consistency.

  PYTHONPATH=src python experiments/M2-DOCTR-QUAL/smoke_adapter_check.py \
      --manifest "…/eval-manifest.smoke.json" \
      --weights "…/fast_base-688a8b34.pt" --device cuda
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def harness_blocks(image_path: Path, arch_predictor, cluster_fn):
    with Image.open(image_path).convert("RGB") as page:
        rgb = np.asarray(page, dtype=np.uint8)
    words = arch_predictor([rgb])[0]["words"]
    arr = np.asarray(words, dtype=float).reshape(-1, 5)
    h, w = rgb.shape[:2]
    rects = [
        (
            min(max(r[0] * w, 0.0), w),
            min(max(r[1] * h, 0.0), h),
            min(max(r[2] * w, 0.0), w),
            min(max(r[3] * h, 0.0), h),
        )
        for r in arr
    ]
    confs = [float(r[4]) for r in arr]
    blocks = cluster_fn(rects, confs, page_size=(float(w), float(h)))
    out = []
    for polygon, _conf in blocks:
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        out.append([min(xs), min(ys), max(xs), max(ys)])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    from infrastructure.providers.detection_doctr import DoctrDetectionProvider
    from ports.detection.ports import DetectionRequest
    from eval_detection import build_engine

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    regions = manifest["regions"][: args.limit]

    provider = DoctrDetectionProvider(weights_path=args.weights, device=args.device)
    cluster_fn = __import__("infrastructure.providers.detection_doctr", fromlist=["x"]).cluster_words_into_blocks
    predictor = build_engine(args.weights, "fast_base", args.device)

    records = []
    n_match = 0
    max_delta_overall = 0.0
    for entry in regions:
        with Image.open(entry["image"]).convert("RGB") as page:
            rgb = np.asarray(page, dtype=np.uint8)
        height, width = rgb.shape[:2]
        bgra = np.dstack(
            (rgb[:, :, ::-1], np.full((height, width, 1), 255, dtype=np.uint8))
        )
        request = DetectionRequest(
            page_id=f"{entry['case_id']}-R{entry['region_index']}",
            image_bytes=bgra.tobytes(),
            width=width,
            height=height,
        )
        result = provider.detect(request)

        adapter_rects = [
            [
                min(p[0] for p in c.polygon),
                min(p[1] for p in c.polygon),
                max(p[0] for p in c.polygon),
                max(p[1] for p in c.polygon),
            ]
            for c in result.candidates
        ]
        harness_rects = harness_blocks(entry["image"], predictor, cluster_fn)

        count_match = len(adapter_rects) == len(harness_rects)
        max_delta = None
        coords_match = False
        if count_match and adapter_rects:
            deltas = [
                max(abs(float(a) - float(b)) for a, b in zip(ra, rb))
                for ra, rb in zip(adapter_rects, harness_rects)
            ]
            max_delta = float(max(deltas))
            coords_match = bool(max_delta <= 1e-3)
        record_match = bool(count_match and coords_match)
        n_match += int(record_match)
        if max_delta is not None:
            max_delta_overall = max(max_delta_overall, float(max_delta))
        records.append(
            {
                "case_id": entry["case_id"],
                "region_index": entry["region_index"],
                "adapter_blocks": len(adapter_rects),
                "harness_blocks": len(harness_rects),
                "count_match": count_match,
                "coords_max_abs_delta_px": max_delta,
                "coords_match": coords_match,
                "match": record_match,
                "adapter_rects": adapter_rects,
                "elapsed_ms": result.elapsed_ms,
            }
        )
        print(
            f"{entry['case_id']} R{entry['region_index']}: "
            f"adapter={len(adapter_rects)} harness={len(harness_rects)} "
            f"maxΔ={max_delta if max_delta is not None else 'n/a'} "
            f"match={record_match} ({result.elapsed_ms} ms)"
        )

    out = {
        "task": "M2-DOCTR-QUAL-PREFLIGHT",
        "purpose": "AC4 production-adapter end-to-end spot check (count + coordinates)",
        "device": args.device,
        "weights": str(args.weights),
        "n_regions": len(records),
        "n_match": n_match,
        "coords_max_abs_delta_px_overall": max_delta_overall if records else None,
        "all_match": n_match == len(records),
        "regions": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(
        f"adapter consistency: {n_match}/{len(records)} regions match "
        f"(maxΔ={max_delta_overall}) -> {args.out}"
    )
    return 0 if out["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
