"""Create harmless synthetic page images for the real GUI audit.

The generated fixture contains geometric panels and labels only.  It never reads
user files, manga images, or a project database, and it refuses to write inside
the repository checkout.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _page(number: int) -> Image.Image:
    image = Image.new("RGB", (720, 1080), (248, 247, 244))
    draw = ImageDraw.Draw(image)
    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    font = ImageFont.truetype(str(font_path), 28) if font_path.exists() else ImageFont.load_default()
    small = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default()
    draw.rounded_rectangle((28, 28, 692, 1052), radius=18, outline=(42, 48, 58), width=5)
    draw.text((58, 52), f"SYNTHETIC AUDIT PAGE {number:02d}", fill=(24, 31, 41), font=font)
    draw.text((58, 104), "Geometric fixture only - no manga or user data", fill=(85, 91, 101), font=small)

    if number == 1:
        panels = [
            ((58, 170, 662, 440), (226, 236, 242), "PANEL A"),
            ((58, 466, 350, 800), (242, 226, 205), "PANEL B"),
            ((370, 466, 662, 800), (218, 232, 211), "PANEL C"),
            ((58, 826, 662, 1008), (232, 225, 240), "PANEL D"),
        ]
    else:
        panels = [
            ((58, 170, 350, 470), (225, 232, 246), "PANEL E"),
            ((370, 170, 662, 470), (246, 229, 223), "PANEL F"),
            ((58, 496, 662, 740), (222, 239, 228), "PANEL G"),
            ((58, 766, 350, 1008), (239, 234, 211), "PANEL H"),
            ((370, 766, 662, 1008), (231, 224, 239), "PANEL I"),
        ]
    for box, fill, label in panels:
        draw.rounded_rectangle(box, radius=12, fill=fill, outline=(54, 61, 72), width=3)
        left, top, right, bottom = box
        cx, cy = (left + right) // 2, (top + bottom) // 2
        draw.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=(255, 255, 255), outline=(54, 61, 72), width=3)
        draw.text((left + 18, top + 16), label, fill=(35, 42, 52), font=small)
        draw.text((cx - 22, cy - 12), str(number), fill=(35, 42, 52), font=font)
    return image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    repository = Path(__file__).resolve().parents[3]
    if repository == output or repository in output.parents:
        raise SystemExit("refusing to write synthetic fixture inside repository")
    if "New Manga.workspace" not in str(output):
        raise SystemExit("output directory must be inside the governed New Manga.workspace")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    pages = []
    for number in (1, 2):
        path = output / f"{number:03d}.png"
        _page(number).save(path, format="PNG", optimize=False)
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        pages.append({
            "path": str(path),
            "width": 720,
            "height": 1080,
            "bytes": path.stat().st_size,
            "sha256": digest,
        })
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "synthetic_only": True,
        "description": "Geometric labeled panels; no manga, user content, or external images.",
        "pages": pages,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output), "pages": pages, "manifest": str(manifest_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
