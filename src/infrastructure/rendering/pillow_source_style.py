"""Pixel-based SourceStyle analyzer, Qt-free (CORE-SLIM-1).

Behavioural port of :mod:`infrastructure.rendering.pixel_source_style` onto
Pillow, so the packaged Core closure (core_service / acceptance_bridge) ships no
Qt while keeping the frozen D06 §8 heuristic exactly:

- background = median brightness of the border strip; ink = pixels whose
  brightness differs from the background beyond the fixed tolerance;
- detected size ≈ median height of the horizontal ink bands;
- confidence: consistency of the band heights (≥2 bands) via 1 − stdev/mean,
  a single band capped at 0.4, no band at all → 0.0;
- direction hint: horizontal scripts stack several row bands while their
  column projection stays one wide band, and vice versa;
- text color: most frequent quantized color among ink pixels.

Equivalence with the Qt implementation is proven on the frozen evidence crops
(``verification/CORE-SLIM-1/ac1/``: Qt reference vs Pillow results compared
field by field for every fixture region), and covered by
``tests/infrastructure/test_pillow_source_style.py``.

The estimate stays a heuristic by design; callers still fall back to 26 when
the confidence is below the frozen threshold.
"""

from __future__ import annotations

import io
from statistics import median, pstdev

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


class PillowSourceStyleAnalyzer(SourceStyleAnalyzer):
    """Qt-free :class:`SourceStyleAnalyzer` (same heuristic, same outputs)."""

    def analyze(
        self, original_png: bytes, box: tuple[int, int, int, int]
    ) -> SourceStyle:
        from PIL import Image

        try:
            image = Image.open(io.BytesIO(original_png))
            image.load()
            rgb = image.convert("RGB")
        except Exception as error:  # noqa: BLE001 - same refusal the Qt port had
            raise ValueError("original image could not be decoded") from error
        try:
            pixels = rgb.load()
            width, height = rgb.size
            x, y, w, h = box
            x = max(0, min(x, width))
            y = max(0, min(y, height))
            w = max(0, min(w, width - x))
            h = max(0, min(h, height - y))
            if w == 0 or h == 0:
                return SourceStyle(None, 0.0)

            background = self._background_brightness(pixels, x, y, w, h)
            row_profile = [0] * h
            col_profile = [0] * w
            color_votes: dict[tuple[int, int, int], int] = {}
            ink_count = 0

            for row in range(y, y + h):
                for col in range(x, x + w):
                    r, g, b = pixels[col, row]
                    brightness = (r + g + b) / 3
                    if abs(brightness - background) <= _BACKGROUND_TOLERANCE:
                        continue
                    row_profile[row - y] += 1
                    col_profile[col - x] += 1
                    ink_count += 1
                    key = (r // _QUANT, g // _QUANT, b // _QUANT)
                    color_votes[key] = color_votes.get(key, 0) + 1

            border_hex = self._border_median_hex(pixels, x, y, w, h)
            if ink_count == 0:
                return SourceStyle(
                    detected_source_font_size=None,
                    source_font_size_confidence=0.0,
                    background_color=border_hex,
                )

            row_bands = _bands(row_profile)
            col_bands = _bands(col_profile)

            heights = [end - start for start, end in row_bands]
            detected = float(median(heights)) if heights else None
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
                background_color=border_hex,
                direction_hint=direction,
            )
        finally:
            image.close()

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
        self, pixels, x: int, y: int, w: int, h: int
    ) -> float:
        samples: list[float] = []
        for row, col in self._border_pixels(x, y, w, h):
            r, g, b = pixels[col, row]
            samples.append((r + g + b) / 3)
        return median(samples) if samples else 255.0

    def _border_pixels(self, x: int, y: int, w: int, h: int):
        step = max(1, min(w, h) // 8)
        for col in range(x, x + w, step):
            for row in (y, y + h - 1):
                yield row, col
        for row in range(y, y + h, step):
            for col in (x, x + w - 1):
                yield row, col

    def _border_median_hex(self, pixels, x: int, y: int, w: int, h: int) -> str:
        level = int(round(self._background_brightness(pixels, x, y, w, h)))
        return _to_hex(level, level, level)
