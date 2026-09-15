"""SourceStyle extraction (D06 §8): pixel analysis + application service.

Test images are synthesized with the real Qt engine at a known pixel
size; assertions stay in honest ranges because D06 §8 promises an
estimate with confidence, not typographic exactness.
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection)

import pytest

from application.rendering.style import RELIABLE_SOURCE_SIZE_CONFIDENCE
from application.translation.color.service import SourceStyleService
from ports.rendering.ports import SourceStyle, TextDirection


def make_text_image(
    lines: list[str],
    *,
    pixel_size: int = 30,
    line_gap: int = 22,
    vertical: bool = False,
    width: int = 260,
    height: int = 200,
    text_color: str = "#000000",
    background: str = "#FFFFFF",
) -> bytes:
    """Render synthetic manga-style text onto a PNG (real QPainter)."""
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QFont, QGuiApplication, QImage, QPainter

    assert QGuiApplication.instance() is not None, "qapp fixture required"
    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(background)
    painter = QPainter(image)
    font = QFont("Microsoft YaHei")
    font.setPixelSize(pixel_size)
    painter.setFont(font)
    painter.setPen(text_color)
    if vertical:
        step = pixel_size + 6
        for column_index, column in enumerate(lines):
            x = width - 20 - column_index * (pixel_size + line_gap)
            for row_index, ch in enumerate(column):
                painter.drawText(x - pixel_size, 20 + row_index * step, ch)
    else:
        y = pixel_size + 8
        for line in lines:
            painter.drawText(12, y, line)
            y += pixel_size + line_gap
    painter.end()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


@pytest.fixture()
def analyzer(qapp):
    from infrastructure.rendering.pixel_source_style import PixelSourceStyleAnalyzer

    return PixelSourceStyleAnalyzer()


@pytest.fixture()
def service(analyzer) -> SourceStyleService:
    return SourceStyleService(analyzer)


BOX = (0, 0, 260, 200)


class TestPixelAnalyzer:
    def test_two_horizontal_lines_estimate_size_and_direction(
        self, analyzer
    ) -> None:
        png = make_text_image(["字体估算", "第二行字"], pixel_size=30)
        style = analyzer.analyze(png, BOX)
        assert style.detected_source_font_size is not None
        # ink band height is a rough proxy: 0.6..1.3 × pixel size
        assert 0.6 * 30 <= style.detected_source_font_size <= 1.3 * 30
        assert style.source_font_size_confidence >= 0.5
        assert style.direction_hint is TextDirection.HORIZONTAL

    def test_vertical_columns_hint_vertical(self, analyzer) -> None:
        png = make_text_image(
            ["纵向", "排列", "文本"], vertical=True, pixel_size=28, width=200, height=220
        )
        style = analyzer.analyze(png, (0, 0, 200, 220))
        assert style.direction_hint is TextDirection.VERTICAL

    def test_black_text_on_white_reports_colors(self, analyzer) -> None:
        png = make_text_image(["黑色文字"], pixel_size=30)
        style = analyzer.analyze(png, BOX)
        assert style.text_color is not None
        assert style.text_color.lower().startswith("#00") or style.text_color.lower() < "#404040"
        assert style.background_color is not None
        assert style.background_color.lower() >= "#f0f0f0"

    def test_blank_image_gives_no_detection(self, analyzer) -> None:
        from PySide6.QtCore import QBuffer, QIODevice
        from PySide6.QtGui import QImage

        image = QImage(200, 100, QImage.Format_ARGB32)
        image.fill("#FFFFFF")
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        style = analyzer.analyze(bytes(buffer.data()), (0, 0, 200, 100))
        assert style.detected_source_font_size is None
        assert style.source_font_size_confidence == 0.0

    def test_box_is_clamped_to_image_bounds(self, analyzer) -> None:
        png = make_text_image(["越界裁剪", "第二行字"], pixel_size=30)
        # the oversized box must be clamped to the image, not rejected
        style = analyzer.analyze(png, (0, 0, 5000, 5000))
        assert style.detected_source_font_size is not None


class TestSourceStyleService:
    def test_reliable_result_is_passed_through(self, service) -> None:
        png = make_text_image(["可靠估算", "两行文字"], pixel_size=30)
        result = service.extract(png, BOX)
        assert result.style.detected_source_font_size is not None
        assert not result.needs_fallback

    def test_unreliable_result_flags_fallback(self, service) -> None:
        png = make_text_image(["低置信"], pixel_size=30)
        result = service.extract(png, BOX)
        if result.style.source_font_size_confidence < RELIABLE_SOURCE_SIZE_CONFIDENCE:
            assert result.needs_fallback
        else:
            pytest.skip("synthetic single line was still confident")
