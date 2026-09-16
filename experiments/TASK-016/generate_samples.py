"""Generate self-authored OCR samples for TASK-016.

The images contain no third-party artwork.  The manifest is the only ground
truth used by the experiment harness; it is not a product fixture or a quality
threshold.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter, QPen


ROOT = Path(__file__).resolve().parent


def _font(family: str, size: int, *, bold: bool = False) -> QFont:
    font = QFont(family, size)
    font.setBold(bold)
    return font


def _canvas(width: int, height: int) -> QImage:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor("#fffdf7"))
    return image


def _draw_label(painter: QPainter, text: str, x: int, y: int, font: QFont) -> QRectF:
    painter.setFont(font)
    painter.setPen(QPen(QColor("#1f2937"), 1))
    rect = painter.boundingRect(QRectF(x, y, 720, 100), 0, text)
    painter.drawText(QPointF(x, y + rect.height()), text)
    return QRectF(x, y, rect.width(), rect.height())


def _jp_horizontal() -> tuple[QImage, list[dict]]:
    image = _canvas(800, 260)
    painter = QPainter(image)
    rect = _draw_label(painter, "東京の朝です。", 70, 75, _font("Meiryo", 42))
    painter.end()
    return image, [{"region_id": "jp-h-01", "text": "東京の朝です。", "polygon": _rect_polygon(rect), "reading_order": 0}]


def _jp_vertical() -> tuple[QImage, list[dict]]:
    image = _canvas(420, 620)
    painter = QPainter(image)
    painter.setFont(_font("Yu Mincho", 38))
    painter.setPen(QPen(QColor("#1f2937"), 1))
    text = "静かな夜。"
    x, top, advance = 150, 55, 70
    for index, char in enumerate(text):
        painter.drawText(QPointF(x, top + index * advance), char)
    painter.end()
    return image, [{"region_id": "jp-v-01", "text": text, "polygon": [[130, 20], [205, 20], [205, 500], [130, 500]], "reading_order": 0}]


def _korean() -> tuple[QImage, list[dict]]:
    image = _canvas(800, 260)
    painter = QPainter(image)
    rect = _draw_label(painter, "오늘도 좋은 하루!", 65, 75, _font("Malgun Gothic", 42, bold=True))
    painter.end()
    return image, [{"region_id": "ko-h-01", "text": "오늘도 좋은 하루!", "polygon": _rect_polygon(rect), "reading_order": 0}]


def _art_text() -> tuple[QImage, list[dict]]:
    image = _canvas(900, 420)
    painter = QPainter(image)
    painter.translate(450, 210)
    painter.rotate(-11)
    painter.setFont(_font("Yu Mincho", 56, bold=True))
    painter.setPen(QPen(QColor("#b91c1c"), 4))
    painter.drawText(QPointF(-285, 20), "冒険はここから")
    painter.setPen(QPen(QColor("#fef3c7"), 1))
    painter.drawText(QPointF(-285, 20), "冒険はここから")
    painter.end()
    return image, [{"region_id": "art-01", "text": "冒険はここから", "polygon": [[125, 115], [780, 20], [800, 205], [145, 315]], "reading_order": 0}]


def _long_tile() -> tuple[QImage, list[dict], list[dict]]:
    image = _canvas(900, 1900)
    painter = QPainter(image)
    entries = [
        ("long-01", "第一場面です。", 80, 170, "Meiryo", 42),
        ("long-02", "두 번째 장면입니다.", 80, 760, "Malgun Gothic", 42),
        ("long-03", "第三場面、つづく。", 80, 1330, "Yu Mincho", 42),
        ("long-04", "最後のコマ。", 80, 1750, "Meiryo", 42),
    ]
    regions: list[dict] = []
    for order, (region_id, text, x, y, family, size) in enumerate(entries):
        rect = _draw_label(painter, text, x, y, _font(family, size))
        regions.append({"region_id": region_id, "text": text, "polygon": _rect_polygon(rect), "reading_order": order})
    painter.end()
    tiles = [
        {"tile_id": "tile-00", "origin": [0, 0], "size": [900, 700]},
        {"tile_id": "tile-01", "origin": [0, 600], "size": [900, 700]},
        {"tile_id": "tile-02", "origin": [0, 1200], "size": [900, 700]},
        {"tile_id": "tile-03", "origin": [0, 1800], "size": [900, 100]},
    ]
    return image, regions, tiles


def _rect_polygon(rect: QRectF) -> list[list[int]]:
    return [
        [round(rect.left()), round(rect.top())],
        [round(rect.right()), round(rect.top())],
        [round(rect.right()), round(rect.bottom())],
        [round(rect.left()), round(rect.bottom())],
    ]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = [
        ("jp-horizontal", "jp_horizontal.png", _jp_horizontal, "japanese-horizontal"),
        ("jp-vertical", "jp_vertical.png", _jp_vertical, "japanese-vertical"),
        ("ko-horizontal", "ko_horizontal.png", _korean, "korean-horizontal"),
        ("art-text", "art_text.png", _art_text, "rotated-art-text"),
    ]
    samples: list[dict] = []
    for sample_id, filename, builder, kind in cases:
        image, regions = builder()
        path = output_dir / filename
        if not image.save(str(path), "PNG"):
            raise OSError(f"failed to save sample: {path}")
        samples.append({
            "sample_id": sample_id,
            "kind": kind,
            "path": filename,
            "width": image.width(),
            "height": image.height(),
            "regions": regions,
            "tiles": [],
            "sha256": _sha256(path),
        })

    image, regions, tiles = _long_tile()
    path = output_dir / "long_tile.png"
    if not image.save(str(path), "PNG"):
        raise OSError(f"failed to save sample: {path}")
    samples.append({
        "sample_id": "long-tile",
        "kind": "long-image-tile-global-coordinate",
        "path": path.name,
        "width": image.width(),
        "height": image.height(),
        "regions": regions,
        "tiles": tiles,
        "sha256": _sha256(path),
    })

    manifest = {
        "schema": "task016-sample-manifest-v1",
        "provenance": "self-authored raster samples; no third-party artwork",
        "generator": "experiments/TASK-016/generate_samples.py",
        "samples": samples,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "samples")
    args = parser.parse_args()
    app = QGuiApplication(["task016-sample-generator"])
    manifest = generate(args.output_dir)
    print(manifest)
    app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
