"""Color / Source Style use case (D06 §8).

Wraps the pixel analyzer with the frozen reliability rule: when the
detected source font size is missing or below the confidence threshold,
consumers must fall back to the default (26) instead of trusting a bad
estimate. Pure application logic — no Qt/sqlite imports.
"""

from __future__ import annotations

from dataclasses import dataclass

from application.rendering.style import RELIABLE_SOURCE_SIZE_CONFIDENCE
from ports.rendering.ports import SourceStyle, SourceStyleAnalyzer


@dataclass(frozen=True)
class SourceStyleResult:
    style: SourceStyle
    needs_fallback: bool


class SourceStyleService:
    def __init__(self, analyzer: SourceStyleAnalyzer) -> None:
        self._analyzer = analyzer

    def extract(
        self, original_png: bytes, box: tuple[int, int, int, int]
    ) -> SourceStyleResult:
        style = self._analyzer.analyze(original_png, box)
        needs_fallback = (
            style.detected_source_font_size is None
            or style.source_font_size_confidence < RELIABLE_SOURCE_SIZE_CONFIDENCE
        )
        return SourceStyleResult(style=style, needs_fallback=needs_fallback)
