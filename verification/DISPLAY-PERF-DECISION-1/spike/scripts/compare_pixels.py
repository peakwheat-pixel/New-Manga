#!/usr/bin/env python
"""Gate 6 evidence: 1:1 pixel comparison of the Core portrait page rendered in Avalonia.

The C# harness (--mode=bench-pixel) writes:
    pixel/portrait_render_dpr1.png   1350x1920 device pixels (DPR1, no interpolation)
    pixel/portrait_render_dpr2.png   1350x1920 device pixels (675x960 logical @ 192 dpi = DPR2)
    pixel/dpr2_probe.png             100x100 logical red square @ 192 dpi (proves dpi scale is real)

Run:
    python verification/DISPLAY-PERF-DECISION-1/spike/scripts/compare_pixels.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops

REPO = Path(__file__).resolve().parents[4]
SPIKE = REPO / "verification" / "DISPLAY-PERF-DECISION-1" / "spike"
PIXEL = SPIKE / "pixel"
SOURCE = REPO / "verification" / "DISPLAY-PERF-DECISION-1" / "routes" / "sample_current_pillow.png"


def compare(source: Image.Image, rendered: Image.Image) -> dict:
    if source.size != rendered.size:
        return {"same_size": False, "source_size": source.size, "rendered_size": rendered.size}
    diff = ImageChops.difference(source.convert("RGB"), rendered.convert("RGB"))
    bands = diff.split()
    max_delta = bands[0]
    for band in bands[1:]:
        max_delta = ImageChops.lighter(max_delta, band)
    hist = max_delta.histogram()
    total = source.size[0] * source.size[1]
    exact = hist[0]
    return {
        "same_size": True,
        "pixels": total,
        "identical_pixels": exact,
        "identical_ratio": round(exact / total, 6),
        "diff_pixels": total - exact,
        "diff_ratio": round((total - exact) / total, 6),
        "diff_ratio_le2": round((total - hist[0] - hist[1] - hist[2]) / total, 6),
        "max_channel_delta": max(i for i, c in enumerate(hist) if c > 0),
        "mean_abs_delta": round(sum(i * c for i, c in enumerate(hist)) / total, 4),
    }


def probe_analysis(path: Path) -> dict:
    """The probe is a 100x100 logical red square rendered at 192 dpi: 200x200 device px if honoured."""
    image = Image.open(path).convert("RGB")
    width, height = image.size
    red_pixels = 0
    for y in range(height):
        for x in range(0, min(width, 420)):
            r, g, b = image.getpixel((x, y))
            if r > 200 and g < 60 and b < 60:
                red_pixels += 1
    # bounding box of the red region
    bbox = None
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            if r > 200 and g < 60 and b < 60:
                if bbox is None:
                    bbox = [x, y, x, y]
                else:
                    bbox = [min(bbox[0], x), min(bbox[1], y), max(bbox[2], x), max(bbox[3], y)]
    return {
        "png_size": [width, height],
        "red_pixels": red_pixels,
        "red_bbox": bbox,
        "red_bbox_size": None if bbox is None else [bbox[2] - bbox[0] + 1, bbox[3] - bbox[1] + 1],
        "dpi_scale_honoured_2x": bbox is not None and (bbox[2] - bbox[0] + 1) >= 190,
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    PIXEL.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as src:
        source = src.convert("RGB")

    result = {
        "gate": "6-portrait-1to1",
        "source": {"path": str(SOURCE.relative_to(REPO)).replace("\\", "/"), "size": list(source.size)},
    }

    dpr1_path = PIXEL / "portrait_render_dpr1.png"
    if dpr1_path.exists():
        with Image.open(dpr1_path) as rendered:
            result["dpr1"] = compare(source, rendered)
    else:
        result["dpr1"] = {"error": "missing portrait_render_dpr1.png"}

    dpr2_path = PIXEL / "portrait_render_dpr2.png"
    if dpr2_path.exists():
        with Image.open(dpr2_path) as rendered:
            rgb = rendered.convert("RGB")
            result["dpr2"] = compare(source, rgb)
            # Every source pixel must map to a uniform 2x2 device block (no resampling).
            uniform_blocks = 0
            checked_blocks = 0
            for y in range(0, min(rgb.size[1] - 1, source.size[1] * 2 - 2), 2):
                for x in range(0, min(rgb.size[0] - 1, source.size[0] * 2 - 2), 2):
                    checked_blocks += 1
                    block = {rgb.getpixel((x + dx, y + dy)) for dy in (0, 1) for dx in (0, 1)}
                    if len(block) == 1:
                        uniform_blocks += 1
            result["dpr2"]["uniform_2x2_blocks"] = uniform_blocks
            result["dpr2"]["checked_2x2_blocks"] = checked_blocks
            result["dpr2"]["uniform_ratio"] = round(uniform_blocks / checked_blocks, 6) if checked_blocks else None
    else:
        result["dpr2"] = {"error": "missing portrait_render_dpr2.png"}

    probe_path = PIXEL / "dpr2_probe.png"
    result["dpr2_probe"] = probe_analysis(probe_path) if probe_path.exists() else {"error": "missing dpr2_probe.png"}

    dpr1_exact = result.get("dpr1", {}).get("identical_ratio") == 1.0
    dpr2_exact = result.get("dpr2", {}).get("identical_ratio") == 1.0
    result["pass_dpr1_exact"] = dpr1_exact
    result["pass_dpr2_exact"] = dpr2_exact
    (PIXEL / "pixel_compare.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
