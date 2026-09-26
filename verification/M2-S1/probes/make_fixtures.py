"""Generate the synthetic M2-S1 fixtures (deterministic, non-user, disposable).

Nothing here reads a user library, a source file, a managed copy or a model
cache. Everything is sealed to the lab directory under ``%TEMP%`` and is
regenerated on demand from the seeds below, so the fixtures themselves are
never committed -- only their hashes and dimensions are.

Run:
  python verification/M2-S1/probes/make_fixtures.py --lab "%TEMP%\\m2s1-lab"

Emits ``<lab>/fixtures/fixtures.json``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import m2s1_lab as lab  # noqa: E402

#: (name, width, height, seed, zlib level)
#:
#: The two long fixtures use zlib level 1: noise is incompressible, so the
#: level barely moves the byte count while it moves generation time a lot.
SPECS = [
    ("small_page_800x1200", 800, 1200, 101, 6),
    ("typical_page_1600x2400", 1600, 2400, 202, 6),
    ("webtoon_long_800x24000", 800, 24000, 303, 1),
    ("oversize_2000x12000", 2000, 12000, 404, 1),
]
TILE_SPECS = [(f"webtoon_tile_{index:02d}_800x4000", 800, 4000, 900 + index, 1) for index in range(6)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--skip-tiles", action="store_true")
    args = parser.parse_args()

    root = lab.lab_root(args.lab)
    fixture_dir = root / "fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    specs = list(SPECS) + ([] if args.skip_tiles else TILE_SPECS)
    for name, width, height, seed, level in specs:
        path = fixture_dir / f"{name}.png"
        info = lab.write_png(path, width, height, seed=seed, level=level)
        info["name"] = name
        info["seed"] = seed
        info["zlib_level"] = level
        info["generator"] = "verification/M2-S1/probes/make_fixtures.py"
        entries.append(info)
        print(
            f"{name}: {width}x{height} png={info['png_bytes']} "
            f"({lab.human_bytes(info['png_bytes'])}) sha256={info['sha256']} level={level}",
            flush=True,
        )

    manifest = {
        "generator": "verification/M2-S1/probes/make_fixtures.py",
        "content": "deterministic RGB noise PNG (incompressible worst case)",
        "lab_root": str(root),
        "media_limit_bytes": lab.MEDIA_LIMIT_BYTES,
        "fixtures": entries,
    }
    manifest_path = fixture_dir / "fixtures.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"manifest={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
