"""Test helpers for the rendering suite.

Injects ``src`` into sys.path (same convention as tests/editing) and
provides deterministic fakes for the layout engine so font-size resolution
tests can predict fits exactly, plus PNG building blocks for the Qt
compositor tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class FixedMetricsProbe:
    """Deterministic fit probe: CJK-square glyphs, width = size per char.

    Horizontal model used by tests:
    - chars per line = floor(box_width / size)
    - lines = ceil(len(text) / chars_per_line) (>= 1)
    - total height = lines * size * line_spacing
    - fits iff chars_per_line >= 1 and total height <= box_height
    """

    def __init__(self, text: str, *, box_w: int, box_h: int, line_spacing: float = 1.0):
        self._text = text
        self._box_w = box_w
        self._box_h = box_h
        self._line_spacing = line_spacing
        self.probe_sizes: list[float] = []

    def __call__(self, font_size: float) -> bool:
        self.probe_sizes.append(font_size)
        chars_per_line = int(self._box_w // font_size) if font_size > 0 else 0
        if chars_per_line < 1:
            return False
        lines = max(1, -(-len(self._text) // chars_per_line))
        total_height = lines * font_size * self._line_spacing
        return total_height <= self._box_h


def make_probe(text: str, *, box_w: int, box_h: int, line_spacing: float = 1.0):
    return FixedMetricsProbe(text, box_w=box_w, box_h=box_h, line_spacing=line_spacing)
