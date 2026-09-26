"""Generate the synthetic M2-S3 fixtures (deterministic, non-user, disposable).

Same method as M2-S1/M2-S2 (deterministic RGB-noise PNGs from fixed seeds,
stdlib only). Everything is sealed to the lab directory under ``%TEMP%``;
scope-internal assets are independent *copies* (never hardlinks -- a lesson
recorded in M2-S2: content-write attacks can traverse hardlinks).

Also creates the adversary junction (``scope/derived/linkj`` ->
``outside/dir``) used by the negative matrix, and the minimal Tauri icon.

Run:
  python experiments/M2-S3/fixtures/gen_fixtures.py
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
import zlib
from pathlib import Path

LAB = Path(os.environ.get("TEMP", ".")) / "m2s3-lab"

SPECS = [
    ("small_page_800x1200", 800, 1200, 3101, 6),
    ("typical_page_1600x2400", 1600, 2400, 3202, 6),
    ("outside_secret", 800, 1200, 3401, 6),
    ("outside_nested", 800, 1200, 3501, 6),
    ("user_source_private", 800, 1200, 3601, 6),
]


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, *, seed: int, level: int = 6) -> dict:
    import random

    rng = random.Random(seed)
    stride = width * 3
    compressor = zlib.compressobj(level)
    parts = []
    for _ in range(height):
        parts.append(compressor.compress(b"\x00" + rng.randbytes(stride)))
    parts.append(compressor.flush())
    idat = b"".join(parts)
    payload = b"".join(
        (
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            _png_chunk(b"IDAT", idat),
            _png_chunk(b"IEND", b""),
        )
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return {
        "path": str(path),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def make_icon(path: Path, size: int = 32) -> None:
    """Minimal valid 32bpp BMP-in-ICO so tauri-build has an icon (probe-only)."""

    width = height = size
    pixel_rows = b""
    for y in range(height):
        row = b"\x00" * 1  # row padding placeholder replaced below
        row = b""
        for x in range(width):
            # simple two-tone diagonal pattern, opaque blue
            shade = 0x40 if (x + y) % 8 < 4 else 0xA0
            row += bytes((0xFF, shade, 0x20, 0xFF))  # BGRA
        pixel_rows += row
    and_mask = b"\x00" * (((width + 31) // 32) * 4 * height)
    bmp_height = height * 2
    dib = struct.pack(
        "<IiiHHIIiiII", 40, width, bmp_height, 1, 32, 0, len(pixel_rows) + len(and_mask), 0, 0, 0, 0
    )
    image = dib + pixel_rows + and_mask
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", width % 256, height % 256, 0, 0, 1, 32, len(image), 22)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + entry + image)


def main() -> int:
    scope_derived = LAB / "scope" / "derived"
    outside = LAB / "outside"

    manifest = {"lab": str(LAB), "generator": "experiments/M2-S3/fixtures/gen_fixtures.py", "fixtures": {}}

    copies = {
        "asset": (SPECS[0], scope_derived / "asset.png"),
        "typical": (SPECS[1], scope_derived / "typical.png"),
    }
    outsides = {
        "outside_secret": (SPECS[2], outside / "outside_secret.png"),
        "outside_nested": (SPECS[3], outside / "dir" / "nested.png"),
        "user_source_private": (SPECS[4], outside / "user_source_private.png"),
    }
    for group, items in (("scope", copies), ("outside", outsides)):
        for name, (spec, target) in items.items():
            name_, width, height, seed, level = spec
            info = write_png(target, width, height, seed=seed, level=level)
            info["role"] = group
            manifest["fixtures"][name] = info
            print(f"{name}: {info['bytes']} B sha256={info['sha256']}")

    # adversary junction inside the scope: scope/derived/linkj -> outside/dir
    link = scope_derived / "linkj"
    if link.exists() or link.is_symlink():
        os.rmdir(link)
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(outside / "dir")],
        capture_output=True,
        timeout=30,
    )
    manifest["junction"] = {
        "link": str(link),
        "target": str(outside / "dir"),
        "created": created.returncode == 0 and link.exists(),
    }
    print(f"junction created={manifest['junction']['created']}")

    make_icon(Path(__file__).resolve().parents[1] / "probe" / "icons" / "icon.ico")
    print("icon written")

    out = LAB / "fixtures.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"manifest={out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
