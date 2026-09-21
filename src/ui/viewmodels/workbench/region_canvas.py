"""Normalized (0..1) to page-pixel geometry for the region canvas (T1.1.2).

Qt-free by design. QML owns item->normalized because only it knows the
viewport; this module owns normalized->page pixels because only the model
layer may store integers. Two consequences are pinned here rather than left
to each caller:

- the rounding rule is half-up (``floor(n * size + 0.5)``). Python's builtin
  ``round`` is half-to-even -- round(0.5)==0, round(12.5)==12 -- and the
  pixel values are asserted exactly, so an unstable tie rule would let the
  implementation and its reviewer disagree on half-pixel boundaries;
- every rejection happens before a ``RegionGeometry`` is built, because
  ``BBox``/``RegionGeometry`` raise ``ValueError`` on a non-positive extent
  or a short ring, and that exception must not reach QML.
"""

from __future__ import annotations

import math
from typing import Sequence

from domain.regions.entities import BBox, RegionGeometry

PAGE_SIZE_UNAVAILABLE = "PAGE_SIZE_UNAVAILABLE"
TOO_FEW_POINTS = "TOO_FEW_POINTS"
DEGENERATE_GEOMETRY = "DEGENERATE_GEOMETRY"


class RegionCanvasError(ValueError):
    """Geometry cannot become a valid Region. ``code`` is the typed reason."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _to_pixels(axis: float, size: int) -> int:
    return min(size, max(0, math.floor(axis * size + 0.5)))


def _twice_area(ring: tuple[tuple[int, int], ...]) -> int:
    """Shoelace doubled area, exact because every coordinate is an int.

    This is the one geometry rule that has to hold before a Region is built.
    Every flat selection fails it through the same door -- zero extent, a ring
    that repeats its own corners, and a collinear triple all enclose nothing
    -- and an extent test alone cannot see the last one. ``BBox`` would raise
    ``ValueError`` on the first two, and that must not reach QML.
    """
    total = 0
    for index in range(len(ring)):
        x1, y1 = ring[index]
        x2, y2 = ring[(index + 1) % len(ring)]
        total += x1 * y2 - x2 * y1
    return abs(total)


def _rectangle_ring(xs: Sequence[int], ys: Sequence[int]) -> tuple[tuple[int, int], ...]:
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    return ((left, top), (right, top), (right, bottom), (left, bottom))


def normalized_to_page_geometry(
    points: Sequence[tuple[float, float]], page_w: int, page_h: int
) -> RegionGeometry:
    """Convert normalized points to page-pixel geometry.

    Two points are an axis-aligned rectangle in any corner order; three or
    more are a polygon ring kept as given.
    """

    if page_w <= 0 or page_h <= 0:
        raise RegionCanvasError(
            PAGE_SIZE_UNAVAILABLE,
            f"page {page_w}x{page_h} has no usable pixel extent",
        )
    if len(points) < 2:
        raise RegionCanvasError(
            TOO_FEW_POINTS, f"{len(points)} point(s); need 2 or more"
        )

    xs = [_to_pixels(nx, page_w) for nx, _ in points]
    ys = [_to_pixels(ny, page_h) for _, ny in points]
    polygon = _rectangle_ring(xs, ys) if len(points) == 2 else tuple(zip(xs, ys))

    left, right = min(x for x, _ in polygon), max(x for x, _ in polygon)
    top, bottom = min(y for _, y in polygon), max(y for _, y in polygon)
    width, height = right - left, bottom - top
    if _twice_area(polygon) == 0:
        raise RegionCanvasError(
            DEGENERATE_GEOMETRY,
            f"selection encloses no area (extent {width}x{height} px)",
        )

    return RegionGeometry(bbox=BBox(left, top, width, height), polygon=polygon)
