"""T1.1.1 real-manga quality check (read-only over the user's material).

Runs the production adapter over real manga pages and records detection
statistics. The material is NEVER modified; annotated previews are written
outside the repository (default ``--preview-dir`` under task-envs) so no
copyrighted pixels land in git. Only the numeric JSON is committed.

Usage (impl venv):
  PYTHONPATH=src python verification/T1.1.1/scripts/real_material_check.py \
      --material "G:/CODEX/New Manga/material/17" \
      --out verification/T1.1.1/real-material/results.json \
      --device cpu
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def bgra_frame(path: Path) -> tuple[bytes, int, int]:
    """Encode a page exactly like the production ``page_frame`` (rgb32)."""
    with Image.open(path) as page:
        rgb = np.asarray(page.convert("RGB"), dtype=np.uint8)
    height, width = rgb.shape[:2]
    bgra = np.dstack(
        (rgb[:, :, ::-1], np.full((height, width, 1), 255, dtype=np.uint8))
    )
    return bgra.tobytes(), width, height


def draw_preview(source: Path, target: Path, polygons, confidences) -> None:
    with Image.open(source) as page:
        preview = page.convert("RGB").copy()
    draw = ImageDraw.Draw(preview)
    for polygon, confidence in zip(polygons, confidences):
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        draw.rectangle(
            [min(xs), min(ys), max(xs), max(ys)],
            outline=(255, 0, 0),
            width=4,
        )
        draw.text((min(xs) + 4, min(ys) + 4), f"{confidence:.2f}", fill=(255, 0, 0))
    preview.save(target, format="PNG")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=Path("G:/CODEX/New Manga.task-envs/T1.1.1-work/t111-real-material"),
    )
    parser.add_argument(
        "--previews", type=int, default=6, help="annotated previews to write"
    )
    args = parser.parse_args()

    from infrastructure.providers.detection_doctr import DoctrDetectionProvider
    from ports.detection.ports import DetectionRequest

    weights = Path.home() / ".cache" / "doctr" / "models" / "fast_base-688a8b34.pt"
    provider = DoctrDetectionProvider(weights_path=weights, device=args.device)

    pages = sorted(args.material.glob("*.jpg"))
    if not pages:
        print(f"no jpg pages under {args.material}", file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.preview_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for index, page_path in enumerate(pages):
        data, width, height = bgra_frame(page_path)
        started = time.perf_counter()
        result = provider.detect(
            DetectionRequest(
                page_id=page_path.stem, image_bytes=data, width=width, height=height
            )
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        confidences = [c.confidence for c in result.candidates if c.confidence is not None]
        records.append(
            {
                "page": page_path.name,
                "candidates": len(result.candidates),
                "mean_conf": round(sum(confidences) / len(confidences), 4)
                if confidences
                else None,
                "min_conf": round(min(confidences), 4) if confidences else None,
                "elapsed_ms": elapsed_ms,
            }
        )
        print(
            f"[{index + 1}/{len(pages)}] {page_path.name}: "
            f"{len(result.candidates)} blocks, {records[-1]['mean_conf']}, {elapsed_ms}ms",
            flush=True,
        )

    total_candidates = sum(record["candidates"] for record in records)
    summary = {
        "material_root": str(args.material),
        "page_count": len(pages),
        "device": args.device,
        "weights_sha256_probe": "see author-verification.md §1",
        "pages_with_zero_candidates": [
            record["page"] for record in records if record["candidates"] == 0
        ],
        "total_candidates": total_candidates,
        "mean_candidates_per_page": round(total_candidates / len(pages), 2),
        "mean_conf_over_nonempty_pages": round(
            sum(record["mean_conf"] for record in records if record["mean_conf"] is not None)
            / max(1, len([r for r in records if r["mean_conf"] is not None])),
            4,
        ),
        "total_elapsed_ms": sum(record["elapsed_ms"] for record in records),
        "records": records,
    }

    # annotated previews: the emptiest, the busiest, and evenly spaced pages
    preview_sources: list[Path] = []
    if records:
        by_count = sorted(records, key=lambda record: (record["candidates"], record["page"]))
        preview_sources.append(args.material / by_count[0]["page"])
        preview_sources.append(args.material / by_count[-1]["page"])
        step = max(1, len(pages) // args.previews)
        preview_sources.extend(pages[i] for i in range(0, len(pages), step))
    written = 0
    seen: set[Path] = set()
    for source in preview_sources:
        if source in seen or not source.exists():
            continue
        seen.add(source)
        data, width, height = bgra_frame(source)
        result = provider.detect(
            DetectionRequest(
                page_id=source.stem, image_bytes=data, width=width, height=height
            )
        )
        draw_preview(
            source,
            args.preview_dir / f"{source.stem}-preview.png",
            [candidate.polygon for candidate in result.candidates],
            [candidate.confidence or 0.0 for candidate in result.candidates],
        )
        written += 1
    summary["previews_written"] = written
    summary["preview_dir"] = str(args.preview_dir)

    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {args.out} and {written} previews to {args.preview_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
