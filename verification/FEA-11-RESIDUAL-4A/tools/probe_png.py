"""FEA-11-RESIDUAL-4A (AC-R3-2) evidence probe: describe one served PNG.

The production ``ReadPageImageAsync`` returns a decoded/re-encoded rendition
(never raw user-source bytes, C-15 §4.2), so the test compares the DECODED
pixels and the served digest — not the container member's byte hash.

Usage:
  python probe_png.py --path P
Output (one line JSON): {"sha256", "format", "width", "height", "pixel"}
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()

    data = args.path.read_bytes()
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        image.load()
        rgb = image.convert("RGB")
        payload = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "format": image.format,
            "width": int(image.size[0]),
            "height": int(image.size[1]),
            "pixel": list(rgb.getpixel((0, 0))),
        }
    print("FEA11_R4A_PNG_OK " + json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
