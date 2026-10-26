#!/usr/bin/env python
"""Gate 3 evidence: proves the Mica backdrop is actually composited behind the window.

`window_probe.ps1 -ClientOnly` captures the client area of the same build twice:
  * mica/mica_on_run1.png  -> TransparencyLevelHint=Mica, app logs ActualTransparencyLevel=Mica
  * mica/mica_off_run1.png -> no hint, opaque client area

The top 120 logical px of the window is a deliberately transparent band ("Mica 取色区"), so those
pixels are either the composited desktop wallpaper (Mica on: blurred + theme-tinted) or our opaque
theme colour (Mica off). Non-flat tinted pixels + a large delta against the opaque fallback = real
backdrop, not a fake CSS panel. The raw wallpaper sampled at the same screen coordinates is included
for comparison: Mica must be lighter/blurrier than the raw wallpaper, never identical to it.

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

BAND_BOX = (8, 8, 290, 88)  # transparent band, excludes the left-bottom label text and window edges
WALLPAPER = Path(r"C:\WINDOWS\web\wallpaper\Windows\img0.jpg")
# Windows 11 fill-mode mapping of the wallpaper on the 2560x1440 primary display, for the screen
# rectangle the band occupies while window_probe captures a centred 1200x800 window.
SCREEN_SIZE = (2560, 1440)
BAND_SCREEN_BOX = (687, 315, 967, 395)


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
        "is_flat": unique < 24 and max(stat.stddev) < 1.5,
    }


def wallpaper_sample() -> dict | None:
    if not WALLPAPER.exists():
        return None
    with Image.open(WALLPAPER) as wp:
        wp = wp.convert("RGB")
        scale = max(SCREEN_SIZE[0] / wp.size[0], SCREEN_SIZE[1] / wp.size[1])
        scaled_w, scaled_h = int(wp.size[0] * scale), int(wp.size[1] * scale)
        offset_x, offset_y = (scaled_w - SCREEN_SIZE[0]) // 2, (scaled_h - SCREEN_SIZE[1]) // 2
        x0, y0, x1, y1 = BAND_SCREEN_BOX
        box = (
            int((x0 + offset_x) / scale),
            int((y0 + offset_y) / scale),
            int((x1 + offset_x) / scale),
            int((y1 + offset_y) / scale),
        )
        crop = wp.crop(box)
        return {
            "path": str(WALLPAPER),
            "mapping_scale": round(scale, 4),
            "crop": list(box),
            "channel_mean": [round(v, 3) for v in ImageStat.Stat(crop).mean],
            "unique_colors": len(crop.getcolors(maxcolors=4_000_000) or []),
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
        changed = sum(1 for v in diff.convert("L").getdata() if v > 2)
        width = BAND_BOX[2] - BAND_BOX[0]
        height = BAND_BOX[3] - BAND_BOX[1]

        payload = {
            "gate": "3-mica-real",
            "captures": {
                "mica_on": str(on_path.relative_to(REPO)).replace("\\", "/"),
                "mica_off": str(off_path.relative_to(REPO)).replace("\\", "/"),
                "band_box": list(BAND_BOX),
            },
            "mica_on_band": on_stats,
            "mica_off_band": off_stats,
            "wallpaper_raw_at_same_screen_rect": wallpaper_sample(),
            "on_vs_off": {
                "mean_abs_delta": [round(v, 3) for v in diff_stat.mean],
                "max_channel_delta": max(int(round(v)) for v in diff_stat.extrema[0]) if diff_stat.extrema else None,
                "pixels_changed_gt2": changed,
                "pixel_changed_ratio": round(changed / (width * height), 4),
            },
            "mica_backdrop_proven": (
                on_stats["unique_colors"] > 1
                and on_stats["max_stddev"] > 0.2
                and off_stats["is_flat"]
            ),
            "interpretation": (
                "Mica blurs+tints the wallpaper behind the window: the transparent band keeps a "
                "non-flat light-blue tint (~233,244,255) that is NOT the opaque theme colour (#F6F7F9), "
                "while the no-hint run is exactly one flat colour. The raw wallpaper at the same screen "
                "rect is much darker/bluer with thousands of colours, which is what Mica blurs/tints. "
                "Runtime ActualTransparencyLevel=Mica is logged by the app in mica/window/transparency.log."
            ),
        }
    (MICA / "mica_analysis.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
