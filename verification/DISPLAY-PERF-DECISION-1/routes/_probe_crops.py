"""Throwaway probe: crop candidate bubble regions for the typesetting sample.

Not part of the deliverable; kept only to make bbox selection auditable.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "_probe"
PAGES = ["010.jpg", "050.jpg"]

CANDIDATES = {
    # (page, name, box) in page pixels (1350x1920)
    ("010.jpg", "p010_bottomright", (1060, 1080, 1320, 1560)),
    ("010.jpg", "p010_left_mid", (330, 620, 560, 1010)),
    ("050.jpg", "p050_topright", (940, 40, 1330, 380)),
    ("050.jpg", "p050_bottomright", (980, 800, 1330, 1560)),
}


def main() -> int:
    page_dir = ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "oc material" / "17"
    OUT.mkdir(parents=True, exist_ok=True)
    for page_name in PAGES:
        image = Image.open(page_dir / page_name).convert("RGB")
        print(page_name, image.size)
    for page_name, name, box in CANDIDATES:
        image = Image.open(page_dir / page_name).convert("RGB")
        crop = image.crop(box)
        crop.save(OUT / f"{name}.png")
        print(name, box, crop.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
