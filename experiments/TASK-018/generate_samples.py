"""Generate the five fixed TASK-018 samples as PNG + manifest.

Dependency note: this environment has **no PIL/numpy**. PySide6 is available,
and ``QImage`` can be constructed and saved without a QGuiApplication, so the
samples are rendered with QPainter onto ``QImage`` buffers.

The five classes are fixed by TASK-018 AC-2: white background, line art,
screentone, gradient, and structure crossing. Every sample carries an explicit
**target box** (what the mask must cover) and **protected boxes** (pixels an
inpaint step must never touch).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter, QPen

SIZE = 320
ROOT = Path(__file__).resolve().parent


def _ensure_app() -> QGuiApplication:
    """``QPainter`` needs a live ``QGuiApplication``.

    Creating a ``QPainter`` without one aborts the process on Windows
    (observed: exit code ``0xC0000409``), so the app object is created once and
    reused. ``QImage`` alone would not require it.
    """
    return QGuiApplication.instance() or QGuiApplication(sys.argv[:1])

#: sample_id -> (kind, human description, target box, protected boxes)
SAMPLE_SPECS: tuple[dict[str, object], ...] = (
    {
        "sample_id": "s1-white-background",
        "kind": "white-background",
        "description": "白底黑字对白：纯白背景 + 粗体文字，最简单的填充场景",
        "target_box": (96, 128, 224, 176),
        "protected_boxes": [(0, 0, 320, 96), (0, 208, 320, 320)],
    },
    {
        "sample_id": "s2-line-art",
        "kind": "line-art",
        "description": "线稿：密集细线构成的图案，文字压在线的上方",
        "target_box": (104, 136, 216, 168),
        "protected_boxes": [(0, 0, 320, 100), (0, 200, 320, 320)],
    },
    {
        "sample_id": "s3-screentone",
        "kind": "screentone",
        "description": "网点：规则点阵半调背景，文字位于网点之上",
        "target_box": (96, 128, 224, 176),
        "protected_boxes": [(0, 0, 320, 110), (0, 196, 320, 320)],
    },
    {
        "sample_id": "s4-gradient",
        "kind": "gradient",
        "description": "渐变：水平灰阶渐变，文字位于渐变中部",
        "target_box": (96, 128, 224, 176),
        "protected_boxes": [(0, 0, 320, 100), (0, 200, 320, 320)],
    },
    {
        "sample_id": "s5-structure-crossing",
        "kind": "structure-crossing",
        "description": "结构穿越：面板边框与速度线穿过文字区，修复必须延续结构而不是抹平",
        "target_box": (92, 124, 228, 180),
        "protected_boxes": [(0, 0, 320, 92), (0, 212, 320, 320)],
    },
)


def _new_canvas() -> tuple[QImage, QPainter]:
    image = QImage(SIZE, SIZE, QImage.Format_RGB32)
    image.fill(QColor(255, 255, 255))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, False)
    return image, painter


def _draw_text(painter: QPainter, box: tuple[int, int, int, int], text: str) -> None:
    x0, y0, x1, y1 = box
    painter.setPen(QColor(0, 0, 0))
    font = QFont("Yu Gothic", 20, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRectF(x0, y0, x1 - x0, y1 - y0), Qt.AlignCenter | Qt.TextWordWrap, text)


def _render(spec: dict[str, object]) -> QImage:
    image, painter = _new_canvas()
    kind = spec["kind"]
    if kind == "white-background":
        painter.setPen(QPen(QColor(0, 0, 0), 4))
        painter.drawRect(QRectF(60, 60, 200, 200))
    elif kind == "line-art":
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        for offset in range(-200, 220, 12):
            painter.drawLine(QPointF(40 + offset, 40), QPointF(40 + offset + 160, 280))
            painter.drawLine(QPointF(40 + offset, 280), QPointF(40 + offset + 160, 40))
    elif kind == "screentone":
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        for y in range(40, 280, 8):
            for x in range(40, 280, 8):
                painter.drawEllipse(QPointF(x + (4 if (y // 8) % 2 else 0), y), 2.0, 2.0)
    elif kind == "gradient":
        for y in range(SIZE):
            level = int(235 - (y / SIZE) * 150)
            painter.setPen(QColor(level, level, level))
            painter.drawLine(0, y, SIZE, y)
    elif kind == "structure-crossing":
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawRect(QRectF(48, 48, 224, 224))
        for offset in range(0, 240, 18):
            painter.drawLine(QPointF(48 + offset, 48), QPointF(48, 48 + offset))
        painter.drawRect(QRectF(92, 124, 136, 56))
    _draw_text(painter, spec["target_box"], "TEXT")
    painter.end()
    return image


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def build_manifest(out_dir: Path) -> dict[str, object]:
    _ensure_app()
    out_dir.mkdir(parents=True, exist_ok=True)
    samples = []
    for spec in SAMPLE_SPECS:
        image = _render(spec)
        path = out_dir / f"{spec['sample_id']}.png"
        if not image.save(str(path), "PNG"):
            raise RuntimeError(f"failed to write {path}")
        samples.append({
            "sample_id": spec["sample_id"],
            "kind": spec["kind"],
            "description": spec["description"],
            "size": [SIZE, SIZE],
            "path": path.name,
            "sha256": sha256_of(path),
            "target_box": list(spec["target_box"]),
            "protected_boxes": [list(box) for box in spec["protected_boxes"]],
            "reference_text": "TEXT",
        })
    manifest = {
        "schema": "task018-samples-v1",
        "generator": "experiments/TASK-018/generate_samples.py",
        "renderer": "PySide6 QImage/QPainter (no PIL/numpy in this environment)",
        "size": [SIZE, SIZE],
        "sample_count": len(samples),
        "samples": samples,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "samples")
    args = parser.parse_args()
    manifest = build_manifest(args.output_dir)
    print(json.dumps({
        "output_dir": str(args.output_dir),
        "samples": manifest["sample_count"],
        "kinds": [s["kind"] for s in manifest["samples"]],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
