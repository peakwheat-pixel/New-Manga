#!/usr/bin/env python3
"""S4 reader fixtures.

Reuses the S0 long-strip method/output (real manga JPEG pages stacked to 4000x60000 and cut into
4000x2048 device rasters) and adds two typography samples that stand in for Core-rendered vertical /
horizontal text pages, so the 1:1 pixel test never depends on Core being available.

Outputs (workspace task-env, never the product repo):
    fixtures/typography/vertical-1200x1800.png
    fixtures/typography/horizontal-1800x1200.png
    fixtures/meta.json                         (strip dims/tiles + typography samples + sha256)
    <evidence>/performance/fixtures.json       (machine-checkable summary)
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
TASK_ENV = Path(r"G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1")
S0_STRIP = Path(
    r"G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/spike/avalonia/fixtures/strip-4000x60000"
)
SRC_PAGES = REPO / "test_assets" / "comic_golden_suite" / "日漫_JA" / "oc material" / "17"
EVIDENCE = REPO / "verification" / "UI-WORKBENCH-READER-1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_strip() -> Path:
    if (S0_STRIP / "meta.json").exists() and (S0_STRIP / "tiles").exists():
        return S0_STRIP
    raise SystemExit(
        f"S0 long-strip fixture missing at {S0_STRIP}; rerun DISPLAY-PERF-DECISION-1 "
        "make_long_strip.py first (S4 reuses that method/output by design)."
    )


def make_typography(vertical: bool, width: int, height: int, out: Path) -> None:
    pages = sorted(SRC_PAGES.glob("*.jpg"))[:1]
    if pages:
        source = Image.open(pages[0]).convert("RGB")
        scale = width / source.width
        resized = source.resize((width, max(1, int(source.height * scale))), Image.LANCZOS)
        canvas = Image.new("RGB", (width, height), (250, 248, 244))
        canvas.paste(resized.crop((0, 0, width, min(height, resized.height))), (0, 0))
    else:
        canvas = Image.new("RGB", (width, height), (250, 248, 244))
    if not vertical:
        canvas = canvas.rotate(90, expand=True).resize((width, height), Image.LANCZOS)
    draw = ImageDraw.Draw(canvas)
    # Deterministic flat probes used by the 1:1 pixel-rendering test (no interpolation allowed).
    probes = [(0, 0, (255, 0, 0)), (width - 64, 0, (0, 128, 255)), (0, height - 64, (0, 200, 0)), (width - 64, height - 64, (255, 0, 255))]
    for x, y, color in probes:
        draw.rectangle([x, y, x + 63, y + 63], fill=color)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, "PNG")


def main() -> int:
    strip = find_strip()
    strip_meta = json.loads((strip / "meta.json").read_text(encoding="utf-8"))
    tiles = sorted((strip / "tiles").glob("tile_*.jpg"))
    if len(tiles) != 30:
        raise SystemExit(f"expected 30 tiles, got {len(tiles)}")

    fixtures = TASK_ENV / "fixtures"
    typography = fixtures / "typography"
    typography.mkdir(parents=True, exist_ok=True)
    vertical = typography / "vertical-1200x1800.png"
    horizontal = typography / "horizontal-1800x1200.png"
    if not vertical.exists():
        make_typography(True, 1200, 1800, vertical)
    if not horizontal.exists():
        make_typography(False, 1800, 1200, horizontal)

    meta = {
        "schema": "nm.reader-fixtures/1",
        "strip": {
            "dir": str(strip),
            "tile_dir": str(strip / "tiles"),
            "tile_count": len(tiles),
            "image_width": strip_meta["image_width"],
            "image_height": strip_meta["image_height"],
            "tile_width": strip_meta["tile_width"],
            "tile_height": strip_meta["tile_height"],
            "source": strip_meta["source"],
            "sha256_sample": sha256(tiles[0]),
        },
        "typography": {
            "vertical": {"path": str(vertical), "width": 1200, "height": 1800, "sha256": sha256(vertical)},
            "horizontal": {"path": str(horizontal), "width": 1800, "height": 1200, "sha256": sha256(horizontal)},
        },
    }
    (fixtures / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "performance").mkdir(parents=True, exist_ok=True)
    summary = {
        "ac": "AC3/AC4",
        "strip_image": f'{meta["strip"]["image_width"]}x{meta["strip"]["image_height"]}',
        "tile": f'{meta["strip"]["tile_width"]}x{meta["strip"]["tile_height"]}',
        "tile_count": meta["strip"]["tile_count"],
        "device_raster_claim": "4000x2048 device rasters",
        "typography_vertical": meta["typography"]["vertical"]["sha256"],
        "typography_horizontal": meta["typography"]["horizontal"]["sha256"],
        "fixtures_meta": str(fixtures / "meta.json"),
        "reuses_s0_method": True,
    }
    (EVIDENCE / "performance" / "fixtures.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
