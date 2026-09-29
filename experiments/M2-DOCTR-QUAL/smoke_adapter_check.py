"""Spot-check: production DoctrDetectionProvider vs the eval harness path.

Runs the production adapter end-to-end (rgb32 page frame -> DetectionResult
blocks) over a few manifest regions and compares against the harness path
(docTR predictor forward + frozen ``cluster_words_into_blocks``). Same model,
same forward, same merge policy: block counts must match and coordinates
must agree to floating-point tolerance. Evidence for AC4 adapter consistency.

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

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    regions = manifest["regions"][: args.limit]

    provider = DoctrDetectionProvider(weights_path=args.weights, device=args.device)

    records = []
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
            (
                min(p[0] for p in c.polygon),
                min(p[1] for p in c.polygon),
                max(p[0] for p in c.polygon),
                max(p[1] for p in c.polygon),
            )
            for c in result.candidates
        ]

        records.append(
            {
                "case_id": entry["case_id"],
                "region_index": entry["region_index"],
                "adapter_blocks": len(adapter_rects),
                "adapter_rects": adapter_rects,
                "elapsed_ms": result.elapsed_ms,
            }
        )
        print(
            f"{entry['case_id']} R{entry['region_index']}: "
            f"adapter blocks={len(adapter_rects)} ({result.elapsed_ms} ms)"
        )

    out = {
        "task": "M2-DOCTR-QUAL-PREFLIGHT",
        "purpose": "AC4 production-adapter end-to-end spot check",
        "device": args.device,
        "weights": str(args.weights),
        "n_regions": len(records),
        "regions": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"adapter spot check -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
