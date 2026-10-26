"""Probe: locate the white speech bubble on page 050 and synthesize a clean plate.

Throwaway probe (kept for bbox audit); the chosen box is hardcoded in the final
sample generator.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[3]
PAGE = ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "oc material" / "17" / "050.jpg"
OUT = Path(__file__).resolve().parent / "_probe"


def main() -> int:
    page = Image.open(PAGE).convert("RGB")
    arr = np.asarray(page)
    # Search window: bottom-right bubble only (avoids other bubbles/margins).
    x0, y0, x1, y1 = 950, 780, 1340, 1560
    win = arr[y0:y1, x0:x1]
    white = (win[..., 0] >= 235) & (win[..., 1] >= 235) & (win[..., 2] >= 235)
    labels, count = ndimage.label(white)
    sizes = ndimage.sum(white, labels, range(1, count + 1))
    best = int(np.argmax(sizes)) + 1
    comp = labels == best
    filled = ndimage.binary_fill_holes(comp)
    print("components:", count, "best size:", int(sizes[best - 1]))
    ys, xs = np.nonzero(filled)
    bbox = (x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()) + 1, y0 + int(ys.max()) + 1)
    print("bubble bbox:", bbox, "w/h:", bbox[2] - bbox[0], bbox[3] - bbox[1])
    fill_ratio = filled.sum() / ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
    print("fill ratio:", round(float(fill_ratio), 4))

    # Clean plate: white-fill the filled bubble interior (+2px AA dilation).
    mask = np.zeros(arr.shape[:2], dtype=bool)
    local = ndimage.binary_dilation(filled, iterations=2)
    mask[y0:y1, x0:x1] = local
    clean = arr.copy()
    clean[mask] = 255
    Image.fromarray(clean).save(OUT / "clean_plate_full.png")
    Image.fromarray(clean[bbox[1] - 20 : bbox[3] + 20, bbox[0] - 20 : bbox[2] + 20]).save(
        OUT / "clean_plate_crop.png"
    )
    # sample dark pixels inside the filled area to see residual text speckles
    region = arr[mask]
    dark = int((region.min(axis=1) < 128).sum())
    print("dark pixels inside mask before fill:", dark)

    # Inner text box suggestion: inset the ellipse bbox.
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    box = (bbox[0] + round(w * 0.16), bbox[1] + round(h * 0.07), round(w * 0.68), round(h * 0.86))
    print("suggested text box (x,y,w,h):", box)
    # crop of the clean bubble for visual check
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
