#!/usr/bin/env python
"""Gate 3 evidence: proves the Mica backdrop is actually composited behind the window.

`window_probe.ps1 -ClientOnly` captures the client area of the same build twice:
  * mica/mica_on_run1.png  -> TransparencyLevelHint=Mica, app logs ActualTransparencyLevel=Mica
  * mica/mica_off_run1.png -> no hint, opaque client area

The top 120 logical px of the window is a deliberately transparent band ("Mica 取色区"), so those
pixels are either the composited desktop wallpaper (Mica on) or our opaque theme colour (Mica off).
Non-uniform colour + a big delta against the opaque fallback = real backdrop, not a fake.

Run:
    python verification/DISPLAY-PERF-DECISION-1/spike/scripts/mica_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

REPO = Path(__file__).resolve().parents[4]
SPIKE = REPO / "verification" / "DISPLAY-PERF-DECISION-1" / "spike"
MICA = SPIKE / "mica"

BAND_BOX = (40, 8, 1160, 112)  # inside the 120px transparent band, away from window edges


def stats(image: Image.Image) -> dict:
    rgb = image.convert("RGB")
    stat = ImageStat.Stat(rgb)
    colors = rgb.getcolors(maxcolors=4_000_000) or []
    unique = len(colors)
    colors.sort(reverse=True)
    return {
        "size": list(rgb.size),
        "unique_colors": unique,
        "channel_stddev": [round(v, 3) for v in stat.stddev],
        "channel_mean": [round(v, 3) for v in stat.mean],
        "max_stddev": round(max(stat.stddev), 3),
        "top_colors": [{"count": c, "rgb": list(v)} for c, v in colors[:5]],
        "is_flat": unique < 8 and max(stat.stddev) < 1.0,
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    on_path = MICA / "mica_on_run1.png"
    off_path = MICA / "mica_off_run1.png"
    if not on_path.exists() or not off_path.exists():
        print(f"ERROR: missing captures: {on_path.exists()=} {off_path.exists()=}")
        return 1

    with Image.open(on_path) as on_img, Image.open(off_path) as off_img:
        on = on_img.crop(BAND_BOX)
        off = off_img.crop(BAND_BOX)
        on.save(MICA / "band_mica_on.png")
        off.save(MICA / "band_mica_off.png")

        on_stats = stats(on)
        off_stats = stats(off)

        diff = ImageChops.difference(on.convert("RGB"), off.convert("RGB"))
        diff_stat = ImageStat.Stat(diff)
        total = BAND_BOX[2] * BAND_BOX[3] * 3
        changed = sum(1 for v in diff.convert("L").getdata() if v > 2)

        payload = {
            "gate": "3-mica-real",
            "captures": {
                "mica_on": str(on_path.relative_to(REPO)).replace("\\", "/"),
                "mica_off": str(off_path.relative_to(REPO)).replace("\\", "/"),
                "band_box": list(BAND_BOX),
            },
            "mica_on_band": on_stats,
            "mica_off_band": off_stats,
            "on_vs_off": {
                "mean_abs_delta": [round(v, 3) for v in diff_stat.mean],
                "max_channel_delta": max(int(round(v)) for v in diff_stat.extrema[0]) if diff_stat.extrema else None,
                "pixels_changed_gt2": changed,
                "pixel_changed_ratio": round(changed / (BAND_BOX[2] * BAND_BOX[3]), 4),
            },
            "mica_backdrop_proven": (
                on_stats["unique_colors"] > 100
                and on_stats["max_stddev"] > 3.0
                and off_stats["is_flat"]
            ),
        }
    (MICA / "mica_analysis.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
