"""Generate the synthetic M2-S2 fixtures (deterministic, non-user, disposable).

Same method as M2-S1 ``make_fixtures.py``: deterministic RGB-noise PNGs from
fixed seeds, sealed to the lab directory under ``%TEMP%``, regenerated on
demand -- only hashes and dimensions are committed. Nothing here touches a
user library, source file, managed copy or model cache.

Run:
  python verification/M2-S2/probes/make_fixtures.py --lab "%TEMP%\\m2s2-lab"

Emits ``<lab>/fixtures/fixtures.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import m2s2_lab as lab  # noqa: E402

# (name, width, height, seed, zlib level)
SPECS = [
    ("small_page_800x1200", 800, 1200, 2101, 6),
    ("typical_page_1600x2400", 1600, 2400, 2202, 6),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    args = parser.parse_args()

    root = lab.lab_root(args.lab)
    fixture_dir = root / "fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for name, width, height, seed, level in SPECS:
        path = fixture_dir / f"{name}.png"
        info = lab.write_png(path, width, height, seed=seed, level=level)
        info["name"] = name
        info["seed"] = seed
        info["zlib_level"] = level
        info["generator"] = "verification/M2-S2/probes/make_fixtures.py"
        entries.append(info)
        print(
            f"{name}: {width}x{height} png={info['png_bytes']} "
            f"({lab.human_bytes(info['png_bytes'])}) sha256={info['sha256']} level={level}",
            flush=True,
        )

    manifest = {
        "generator": "verification/M2-S2/probes/make_fixtures.py",
        "content": "deterministic RGB noise PNG (incompressible worst case)",
        "lab_root": str(root),
        "media_limit_bytes": lab.MEDIA_LIMIT_BYTES,
        "toctou_limit_bytes": lab.TOCTOU_LIMIT_BYTES,
        "fixtures": entries,
    }
    manifest_path = fixture_dir / "fixtures.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"manifest={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
