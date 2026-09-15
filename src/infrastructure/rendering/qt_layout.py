"""Qt-based text layout engine (D06 §23, D03 §11).

Horizontal: greedy word wrap (Latin words stay whole, CJK breaks per
glyph), row pitch = fontMetrics.height() * line_spacing.
Vertical: upright glyphs stacked top-to-bottom in columns that proceed
right-to-left (manga vertical); line_spacing acts as the column pitch
multiplier. Stroke allowance shrinks the usable box on every side so
shrink-to-fit decisions include the stroke (D03 §11.3).
"""

from __future__ import annotations

import re

from PySide6.QtGui import QFont, QFontMetrics

from application.rendering.style import TextDirection
from ports.rendering.ports import (
    DrawItem,
    FontCatalog,
    LayoutRequest,
    LayoutResult,
)

_WORD_RE = re.compile(r"\S+|\s")


def _tokenize(text: str) -> list[tuple[str, bool]]:
    """Tokens as ``(text, space_before)``. ASCII word runs stay whole and
    are separated by spaces; every other character is its own token and
    joins without any separator (CJK wraps per glyph, no inserted gap)."""
    tokens: list[tuple[str, bool]] = []
    for chunk in _WORD_RE.findall(text):
        if chunk.strip() and chunk.isascii():
            tokens.append((chunk, bool(tokens)))
        elif not chunk.strip() and chunk.isascii():
            continue  # the separator is modeled by space_before above
        else:
            tokens.extend((ch, False) for ch in chunk)
    return tokens


class QtTextLayoutEngine:
    def __init__(self, catalog: FontCatalog) -> None:
        self._catalog = catalog

    def layout(self, request: LayoutRequest) -> LayoutResult:
        resolved = self._catalog.resolve(request.font_family)
        font = QFont(resolved.resolved_family)
        font.setPixelSize(max(1, round(request.font_size)))
        metrics = QFontMetrics(font)
        spacing = max(0.1, float(request.line_spacing))

        pad = max(0.0, request.stroke_width)
        usable_w = request.box_width - 2 * pad
        usable_h = request.box_height - 2 * pad
        if usable_w <= 0 or usable_h <= 0:
            return LayoutResult(
                (), 0.0, 0.0, False, resolved.available, resolved.resolved_family
            )

        if request.direction is TextDirection.VERTICAL:
            items, width, height = self._layout_vertical(
                request.text, metrics, usable_w, usable_h, spacing
            )
        else:
            items, width, height = self._layout_horizontal(
                request.text, metrics, usable_w, spacing
            )

        fits = width <= usable_w and height <= usable_h
        return LayoutResult(
            items, width, height, fits, resolved.available, resolved.resolved_family
        )

    # ------------------------------------------------------------------
    # horizontal
    # ------------------------------------------------------------------

    def _layout_horizontal(
        self,
        text: str,
        metrics: QFontMetrics,
        usable_w: float,
        spacing: float,
    ) -> tuple[tuple[DrawItem, ...], float, float]:
        tokens = [t for t in _tokenize(text) if t[0].strip()] or [("", False)]
        space_w = metrics.horizontalAdvance(" ")

        lines: list[list[tuple[str, bool]]] = []
        current: list[tuple[str, bool]] = []
        current_w = 0.0
        for token, space_before in tokens:
            advance = metrics.horizontalAdvance(token)
            separator = space_w if (space_before and current) else 0.0
            would_be = current_w + separator + advance
            if current and would_be > usable_w:
                lines.append(current)
                current, current_w = [(token, False)], advance
            else:
                current.append((token, space_before and bool(current)))
                current_w = would_be
        if current:
            lines.append(current)

        ascent = metrics.ascent()
        items: list[DrawItem] = []
        max_width = 0.0
        for index, words in enumerate(lines):
            line_text = "".join(
                (" " if space_before else "") + word for word, space_before in words
            )
            max_width = max(max_width, metrics.horizontalAdvance(line_text))
            baseline = ascent + index * metrics.height() * spacing
            items.append(DrawItem(line_text, 0.0, baseline, per_char=False))
        height = len(lines) * metrics.height() * spacing
        return tuple(items), max_width, height

    # ------------------------------------------------------------------
    # vertical
    # ------------------------------------------------------------------

    def _layout_vertical(
        self,
        text: str,
        metrics: QFontMetrics,
        usable_w: float,
        usable_h: float,
        spacing: float,
    ) -> tuple[tuple[DrawItem, ...], float, float]:
        char_step = metrics.height()  # upright glyph cell (CJK square)
        chars = [ch for ch in text if not ch.isspace()] or [""]
        column_width = max(
            (metrics.horizontalAdvance(ch) for ch in chars), default=char_step
        )
        column_pitch = column_width * spacing
        chars_per_column = max(1, int(usable_h // char_step))

        columns: list[list[str]] = [
            chars[i : i + chars_per_column]
            for i in range(0, len(chars), chars_per_column)
        ]

        items: list[DrawItem] = []
        # columns proceed right-to-left: column 0 gets the largest x
        for column_index, column in enumerate(columns):
            x = (len(columns) - 1 - column_index) * column_pitch
            for row_index, ch in enumerate(column):
                baseline = metrics.ascent() + row_index * char_step
                items.append(DrawItem(ch, x, baseline, per_char=True))
        width = len(columns) * column_pitch
        height = min(len(chars), chars_per_column) * char_step
        return tuple(items), width, height
