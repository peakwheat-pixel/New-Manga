#!/usr/bin/env python
"""Gate 4 evidence: per-switch screenshot diff against the cold reference capture.

The C# harness (--mode=bench-theme) writes:
    theme/ref_light.png, ref_dark.png, ref_saber-purple.png   (cold correct rendering per skin)
    theme/switch_NN_<theme>.png                               (live screenshot right after switch)

A switch is "clean" when the live screenshot matches that skin's reference almost exactly: any pixel
that still shows the previous palette (or a half-applied resource) shows up as a difference. We also
prove the three references really are visually distinct (otherwise the diff would be meaningless).

Run:
    python verification/DISPLAY-PERF-DECISION-1/spike/scripts/theme_diff.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops

REPO = Path(__file__).resolve().parents[4]
SPIKE = REPO / "verification" / "DISPLAY-PERF-DECISION-1" / "spike"
THEME = SPIKE / "theme"


def diff_stats(a: Image.Image, b: Image.Image) -> dict:
    if a.size != b.size:
        return {"same_size": False, "a_size": a.size, "b_size": b.size}
    rgb_a = a.convert("RGB")
    rgb_b = b.convert("RGB")
    diff = ImageChops.difference(rgb_a, rgb_b)
    # Per-pixel maximum channel delta, then threshold at 0 (exact) and 1 (AA/rounding noise).
    bands = diff.split()
    max_delta = bands[0].point(lambda v: v)
    for band in bands[1:]:
        max_delta = ImageChops.lighter(max_delta, band)
    hist = max_delta.histogram()
    total = a.size[0] * a.size[1]
    exact = hist[0]
    le1 = hist[0] + hist[1]
    nonzero = total - exact
    return {
        "same_size": True,
        "pixels": total,
        "identical_pixels": exact,
        "identical_ratio": round(exact / total, 6),
        "diff_ratio": round(nonzero / total, 6),
        "diff_ratio_le1": round((total - le1) / total, 6),
        "mean_abs_delta": round(sum(i * c for i, c in enumerate(hist)) / total, 4),
        "max_channel_delta": max(i for i, c in enumerate(hist) if c > 0),
        "hist_nonzero_buckets": {str(i): c for i, c in enumerate(hist) if c > 0},
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    THEME.mkdir(parents=True, exist_ok=True)
    refs = {p.stem.replace("ref_", ""): p for p in THEME.glob("ref_*.png")}
    if len(refs) < 3:
        print(f"ERROR: expected 3 reference skins, found {sorted(refs)}")
        return 1

    ref_images = {key: Image.open(path) for key, path in refs.items()}
    distinct = {}
    keys = sorted(ref_images)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            distinct[f"{keys[i]}__vs__{keys[j]}"] = diff_stats(ref_images[keys[i]], ref_images[keys[j]])
    if all(v["diff_ratio"] < 0.01 for v in distinct.values()):
        print("WARNING: reference skins are nearly identical; palette diff would be meaningless")

    switches = []
    for path in sorted(THEME.glob("switch_*.png")):
        match = re.match(r"switch_(\d+)_(.+)\.png$", path.name)
        if not match:
            continue
        index = int(match.group(1))
        theme = match.group(2)
        if theme not in ref_images:
            continue
        stats = diff_stats(Image.open(path), ref_images[theme])
        stats.update({"index": index, "theme": theme, "png": path.name})
        switches.append(stats)

    worst = max((s["diff_ratio"] for s in switches), default=None)
    worst_le1 = max((s["diff_ratio_le1"] for s in switches), default=None)
    payload = {
        "gate": "4-runtime-skinning",
        "reference_diff": distinct,
        "reference_skins_distinct": all(v["diff_ratio"] > 0.05 for v in distinct.values()),
        "switches_checked": len(switches),
        "worst_diff_ratio": worst,
        "worst_diff_ratio_le1": worst_le1,
        "threshold_diff_ratio": 0.001,
        "all_switches_clean": all(s["diff_ratio"] <= 0.001 for s in switches),
        "switches": switches,
    }
    (THEME / "theme_diff.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in (
        "switches_checked", "worst_diff_ratio", "worst_diff_ratio_le1",
        "all_switches_clean", "reference_skins_distinct")}, ensure_ascii=False, indent=2))
    print(f"wrote {THEME / 'theme_diff.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
