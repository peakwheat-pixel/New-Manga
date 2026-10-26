#!/usr/bin/env python
"""Gate-5 fixture builder: compose a real-content 4000x60000 strip and cut it into 4000x2048 tiles.

Source pages are real JPEGs from the repo's read-only `test_assets/comic_golden_suite/日漫_JA`
(Pillow opens them read-only; nothing is written back into the product repo). The composed master,
the tiles and the metadata all live in the task workspace:

    G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/spike/avalonia/fixtures/strip-4000x60000/**

Reproduce:
    python verification/DISPLAY-PERF-DECISION-1/spike/scripts/make_long_strip.py

Outputs:
    fixtures/strip-4000x60000/master_4000x60000.jpg      (composed master)
    fixtures/strip-4000x60000/tiles/tile_000.jpg ...      (4000x2048 tiles)
    fixtures/strip-4000x60000/meta.json                  (tile index consumed by the C# control)
    verification/DISPLAY-PERF-DECISION-1/spike/strip/contact_sheet.png
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[4]
SRC_DIR = REPO / "test_assets" / "comic_golden_suite" / "日漫_JA" / "oc material" / "17"
WORK = Path(
    r"G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/spike/avalonia"
)
OUT = WORK / "fixtures" / "strip-4000x60000"
EVIDENCE = REPO / "verification" / "DISPLAY-PERF-DECISION-1" / "spike" / "strip"

STRIP_W = 4000
STRIP_H = 60000
TILE_W = 4000
TILE_H = 2048
JPEG_QUALITY_MASTER = 88
JPEG_QUALITY_TILE = 92


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    pages = sorted(SRC_DIR.glob("*.jpg"))[:11]
    if not pages:
        print(f"ERROR: no source pages under {SRC_DIR}")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tiles").mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    canvas = Image.new("RGB", (STRIP_W, STRIP_H), (255, 255, 255))
    y = 0
    used = []
    for page in pages:
        with Image.open(page) as im:
            im = im.convert("RGB")
            scale = STRIP_W / im.width
            resized = im.resize((STRIP_W, round(im.height * scale)), Image.LANCZOS)
        if y >= STRIP_H:
            break
        clip = min(resized.height, STRIP_H - y)
        canvas.paste(resized.crop((0, 0, STRIP_W, clip)), (0, y))
        used.append({"page": str(page.relative_to(REPO)).replace("\\", "/"), "y": y, "height": clip})
        y += clip

    master = OUT / "master_4000x60000.jpg"
    canvas.save(master, "JPEG", quality=JPEG_QUALITY_MASTER, optimize=True)

    tiles = []
    index = 0
    for top in range(0, STRIP_H, TILE_H):
        height = min(TILE_H, STRIP_H - top)
        tile = canvas.crop((0, top, TILE_W, top + height))
        name = f"tile_{index:03d}.jpg"
        tile.save(OUT / "tiles" / name, "JPEG", quality=JPEG_QUALITY_TILE, optimize=True)
        tiles.append(
            {
                "index": index,
                "file": name,
                "y": top,
                "height": height,
                "width": TILE_W,
                "bytes": (OUT / "tiles" / name).stat().st_size,
            }
        )
        index += 1

    meta = {
        "image_width": STRIP_W,
        "image_height": STRIP_H,
        "tile_width": TILE_W,
        "tile_height": TILE_H,
        "tile_count": len(tiles),
        "source": "test_assets/comic_golden_suite/日漫_JA/oc material/17 (real JPEG pages, width-scaled to 4000, stacked)",
        "used_pages": used,
        "tiles": tiles,
    }
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # Contact sheet (1/10 scale) so the evidence tree shows real content without shipping 40MB.
    sheet = canvas.resize((STRIP_W // 10, STRIP_H // 10), Image.LANCZOS)
    sheet.save(EVIDENCE / "contact_sheet.png")

    digest = hashlib.sha256(master.read_bytes()).hexdigest()
    summary = {
        "master": str(master).replace("\\", "/"),
        "master_bytes": master.stat().st_size,
        "master_sha256": digest,
        "tiles": len(tiles),
        "tile_total_bytes": sum(t["bytes"] for t in tiles),
        "used_pages": len(used),
        "contact_sheet": str((EVIDENCE / "contact_sheet.png")).replace("\\", "/"),
    }
    (EVIDENCE / "fixture_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
