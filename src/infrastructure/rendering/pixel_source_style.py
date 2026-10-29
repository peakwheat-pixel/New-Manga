"""Pixel-based SourceStyle analyzer (D06 §8).

Estimates the source text style from the region crop of the original
image using projection profiles:

- background = median brightness of the border strip; ink = pixels whose
  brightness differs from the background beyond a fixed tolerance.
- detected size ≈ median height of the horizontal ink bands (one band
  per text line for horizontal scripts).
- confidence: consistency of the band heights (≥2 bands) via
  1 − stdev/mean; a single band is capped at 0.4; no band at all → 0.0.
- direction hint: horizontal scripts stack several row bands while
  their column projection stays one wide band, and vice versa.
- text color: most frequent quantized color among ink pixels.

This is a heuristic estimate by design (D06 §8); callers fall back to
26 when the confidence is below the frozen threshold.
"""

from __future__ import annotations

from statistics import median, pstdev

from PySide6.QtGui import QImage

from ports.rendering.ports import SourceStyle, SourceStyleAnalyzer
from ports.rendering.direction import TextDirection

_BACKGROUND_TOLERANCE = 60  # brightness distance to count as ink
_QUANT = 32  # color quantization step for dominant-color voting
_SINGLE_BAND_CONFIDENCE = 0.4


def _to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _bands(profile: list[int]) -> list[tuple[int, int]]:
    """Contiguous non-zero runs of a projection profile as (start, end)."""
    bands: list[tuple[int, int]] = []
    start = None
    for index, value in enumerate(profile + [0]):
        if value > 0 and start is None:
            start = index
        elif value == 0 and start is not None:
            bands.append((start, index))
            start = None
    return bands


class PixelSourceStyleAnalyzer(SourceStyleAnalyzer):
    def analyze(
        self, original_png: bytes, box: tuple[int, int, int, int]
    ) -> SourceStyle:
        image = QImage.fromData(original_png)
        if image.isNull():
            raise ValueError("original image could not be decoded")
        x, y, w, h = box
        x = max(0, min(x, image.width()))
        y = max(0, min(y, image.height()))
        w = max(0, min(w, image.width() - x))
        h = max(0, min(h, image.height() - y))
        if w == 0 or h == 0:
            return SourceStyle(None, 0.0)

        background = self._background_brightness(image, x, y, w, h)
        row_profile = [0] * h
        col_profile = [0] * w
        color_votes: dict[tuple[int, int, int], int] = {}
        ink_count = 0

        for row in range(y, y + h):
            for col in range(x, x + w):
                color = image.pixelColor(col, row)
                brightness = (color.red() + color.green() + color.blue()) / 3
                if abs(brightness - background) <= _BACKGROUND_TOLERANCE:
                    continue
                row_profile[row - y] += 1
                col_profile[col - x] += 1
                ink_count += 1
                key = (
                    color.red() // _QUANT,
                    color.green() // _QUANT,
                    color.blue() // _QUANT,
                )
                color_votes[key] = color_votes.get(key, 0) + 1

        if ink_count == 0:
            return SourceStyle(
                detected_source_font_size=None,
                source_font_size_confidence=0.0,
                background_color=_border_median_hex(image, x, y, w, h),
            )

        row_bands = _bands(row_profile)
        col_bands = _bands(col_profile)

        heights = [end - start for start, end in row_bands]
        if heights:
            detected = float(median(heights))
        else:
            detected = None
        confidence = self._confidence(heights)

        direction = self._direction_hint(row_bands, col_bands)

        dominant_key = max(color_votes, key=color_votes.__getitem__)
        text_color = _to_hex(
            min(255, dominant_key[0] * _QUANT + _QUANT // 2),
            min(255, dominant_key[1] * _QUANT + _QUANT // 2),
            min(255, dominant_key[2] * _QUANT + _QUANT // 2),
        )
        return SourceStyle(
            detected_source_font_size=detected,
            source_font_size_confidence=confidence,
            text_color=text_color,
            background_color=_border_median_hex(image, x, y, w, h),
            direction_hint=direction,
        )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _confidence(self, band_heights: list[int]) -> float:
        if not band_heights:
            return 0.0
        if len(band_heights) == 1:
            return _SINGLE_BAND_CONFIDENCE
        mean = sum(band_heights) / len(band_heights)
        if mean == 0:
            return 0.0
        spread = pstdev(band_heights) / mean
        return max(0.0, min(1.0, 1.0 - spread))

    def _direction_hint(
        self, row_bands: list[tuple[int, int]], col_bands: list[tuple[int, int]]
    ) -> TextDirection | None:
        rows = len(row_bands)
        cols = len(col_bands)
        if rows >= 2 and rows >= cols:
            return TextDirection.HORIZONTAL
        if cols >= 2 and cols > rows:
            return TextDirection.VERTICAL
        return None

    def _background_brightness(
        self, image: QImage, x: int, y: int, w: int, h: int
    ) -> float:
        samples: list[float] = []
        for row, col in self._border_pixels(image, x, y, w, h):
            color = image.pixelColor(col, row)
            samples.append((color.red() + color.green() + color.blue()) / 3)
        return median(samples) if samples else 255.0

    def _border_pixels(
        self, image: QImage, x: int, y: int, w: int, h: int
    ):
        step = max(1, min(w, h) // 8)
        for col in range(x, x + w, step):
            for row in (y, y + h - 1):
                yield row, col
        for row in range(y, y + h, step):
            for col in (x, x + w - 1):
                yield row, col


def _border_median_hex(image: QImage, x: int, y: int, w: int, h: int) -> str:
    analyzer = PixelSourceStyleAnalyzer()
    brightness = analyzer._background_brightness(image, x, y, w, h)
    level = int(round(brightness))
    return _to_hex(level, level, level)
