"""CORE-SLIM-1: Qt-free SourceStyle analyzer — behavioural parity with Qt.

The packaged Core keeps no Qt, so ``PixelSourceStyleAnalyzer`` (QImage) is
replaced by :class:`PillowSourceStyleAnalyzer`. The frozen D06 §8 heuristic must
not drift: on the same crop both analyzers must return the same
``detected_source_font_size`` / ``source_font_size_confidence`` / colors /
direction hint. The Qt comparison is skipped in a Qt-free environment (that
skip is the point of the replacement); the Pillow behaviour itself is always
asserted.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.rendering.pillow_source_style import (  # noqa: E402
    PillowSourceStyleAnalyzer,
)


def _crop_png() -> bytes:
    """A light page crop with three dark horizontal text-like bars."""
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (120, 80), (250, 245, 240))
    draw = ImageDraw.Draw(image)
    for index in range(3):
        top = 12 + index * 22
        draw.rectangle((10, top, 110, top + 12), fill=(20, 24, 30))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_pillow_analyzer_estimates_bands_confidence_and_colors() -> None:
    style = PillowSourceStyleAnalyzer().analyze(_crop_png(), (0, 0, 120, 80))

    assert style.detected_source_font_size == pytest.approx(13.0)
    assert style.source_font_size_confidence > 0.9  # three equal bands
    assert style.text_color is not None and style.text_color.startswith("#")
    assert style.background_color is not None and style.background_color.startswith("#")


def test_pillow_analyzer_clamps_and_rejects_empty_boxes() -> None:
    analyzer = PillowSourceStyleAnalyzer()
    assert analyzer.analyze(_crop_png(), (500, 500, 10, 10)).detected_source_font_size is None
    assert analyzer.analyze(_crop_png(), (0, 0, 0, 10)).source_font_size_confidence == 0.0


def test_pillow_analyzer_refuses_undecodable_bytes() -> None:
    with pytest.raises(ValueError):
        PillowSourceStyleAnalyzer().analyze(b"not-an-image", (0, 0, 5, 5))


def test_pillow_source_style_module_has_no_qt_import() -> None:
    source = (
        SRC_ROOT / "infrastructure" / "rendering" / "pillow_source_style.py"
    ).read_text(encoding="utf-8")
    for token in ("PySide6", "shiboken6", "QImage"):
        assert token not in source, f"Qt dependency leaked back: {token}"


def test_pillow_and_qt_analyzers_agree_on_the_frozen_heuristic() -> None:
    qt_module = pytest.importorskip("infrastructure.rendering.pixel_source_style")

    payload = _crop_png()
    box = (4, 2, 112, 76)
    pillow_style = PillowSourceStyleAnalyzer().analyze(payload, box)
    qt_style = qt_module.PixelSourceStyleAnalyzer().analyze(payload, box)

    assert pillow_style.detected_source_font_size == qt_style.detected_source_font_size
    assert pillow_style.source_font_size_confidence == pytest.approx(
        qt_style.source_font_size_confidence
    )
    assert pillow_style.text_color == qt_style.text_color
    assert pillow_style.background_color == qt_style.background_color
    assert pillow_style.direction_hint == qt_style.direction_hint
