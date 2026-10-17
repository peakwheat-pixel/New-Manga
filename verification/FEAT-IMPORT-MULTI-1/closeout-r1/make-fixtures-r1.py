from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import zlib
from pathlib import Path

isolation = Path(sys.argv[1]).resolve()
approved = (Path(os.environ["TEMP"]) / "feat-import-multi-r1").resolve()
if isolation != approved:
    raise SystemExit("refusing fixture creation outside the approved TEMP isolation root")
root = isolation / "fixtures"
targets = [(root / "multi-select" / "001.png", 17), (root / "multi-select" / "002.png", 43)]
targets += [(root / "folder-direct" / f"{index:03}.png", seed) for index, seed in enumerate((71, 113, 157), start=1)]


def chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def write_png(path: Path, seed: int) -> None:
    width, height = 256, 320
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            tile = (x // 19 + y // 23 + seed // 7) % 2
            red = (x * 3 + y * 7 + seed * 13) % 256
            green = (x * 11 + y * 5 + seed * 29) % 256
            blue = (x * 5 + y * 13 + seed * 47) % 256
            if tile:
                red, green, blue = 255 - red, 255 - green, 255 - blue
            rows.extend((red, green, blue))
    header = struct.pack(">2I5B", width, height, 8, 2, 0, 0, 0)
    payload = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")
    if path.exists():
        raise SystemExit(f"refusing to overwrite fixture: {path.name}")
    path.write_bytes(payload)


manifest = []
for path, seed in targets:
    write_png(path, seed)
    content = path.read_bytes()
    manifest.append({"path": path.relative_to(root).as_posix(), "seed": seed, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
if len({item["sha256"] for item in manifest}) != len(targets):
    raise SystemExit("fixture PNG contents were not unique")
out = Path(__file__).with_name("gui-run-r1") / "fixture-hashes.json"
if out.exists():
    raise SystemExit("refusing to overwrite fixture hash evidence")
out.write_text(json.dumps({"format": "PNG", "image_count": len(manifest), "unique_sha256": True, "images": manifest}, indent=2) + "\n", encoding="utf-8")
print("fixtures=PASS files=5 content_hashes_unique=true names_ascii=true")
