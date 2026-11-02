"""Mask geometry and refinement (D06 §19/§20, TASK-018 mask protocol).

Pure geometry, no dependencies: the Segment Step produces the raw text mask
from Region geometry, the Mask Refinement Step applies the declared parameter
chain, and both the raw and the final mask are kept so the record can be
persisted (AC-INPAINT-001) and the "final covers raw" invariant is provable.

The parameter set mirrors the TASK-018 experiment record: ``dilate_radius``,
``erode_radius``, ``min_region_pixels``, ``keep_largest_component``. Only the
first two are applied by this dependency-free refinement; the remaining two are
kept in the record verbatim so a later learned segmenter can honour them
without changing the persisted shape.
"""

from __future__ import annotations

from collections.abc import Sequence

from ports.inpaint.ports import BooleanMask, MaskRecord
from ports.providers.errors import ProviderInputError

DEFAULT_MASK_PARAMS: tuple[tuple[str, str], ...] = (
    ("dilate_radius", "2"),
    ("feather_radius", "0"),
    ("min_region_pixels", "1"),
    ("keep_largest_component", "false"),
)

MASK_SOURCE_REGION_GEOMETRY = "region-geometry"
MASK_SOURCE_REFINED = "mask-refine"


def empty_mask(width: int, height: int) -> BooleanMask:
    return BooleanMask(
        width, height, tuple(tuple(False for _ in range(width)) for _ in range(height))
    )


def from_boxes(
    width: int, height: int, boxes: Sequence[Sequence[int]]
) -> BooleanMask:
    """Mask from half-open ``(x0, y0, x1, y1)`` boxes; out-of-range fails."""
    if width <= 0 or height <= 0:
        raise ProviderInputError("mask dimensions must be positive", stage="segment")
    rows = [[False] * width for _ in range(height)]
    for box in boxes:
        if len(box) != 4:
            raise ProviderInputError(
                f"box must be (x0, y0, x1, y1): {box!r}", stage="segment"
            )
        x0, y0, x1, y1 = (int(value) for value in box)
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ProviderInputError(
                f"box {tuple(box)} is out of bounds for {width}x{height}",
                stage="segment",
            )
        for y in range(y0, y1):
            row = rows[y]
            for x in range(x0, x1):
                row[x] = True
    return BooleanMask(width, height, tuple(tuple(row) for row in rows))


def from_polygons(
    width: int, height: int, polygons: Sequence[Sequence[Sequence[float]]]
) -> BooleanMask:
    """Mask from page-global polygons (even-odd rule, bbox-clipped)."""
    if width <= 0 or height <= 0:
        raise ProviderInputError("mask dimensions must be positive", stage="segment")
    rows = [[False] * width for _ in range(height)]
    for polygon in polygons:
        points = [(float(x), float(y)) for x, y in polygon]
        if len(points) < 3:
            raise ProviderInputError(
                "a polygon needs at least three points", stage="segment"
            )
        ys = [point[1] for point in points]
        y_start = max(0, int(min(ys)))
        y_end = min(height, int(max(ys)) + 1)
        for y in range(y_start, y_end):
            scan = y + 0.5
            crossings: list[float] = []
            for index, (x1, y1) in enumerate(points):
                x2, y2 = points[(index + 1) % len(points)]
                if (y1 > scan) == (y2 > scan):
                    continue
                crossings.append(x1 + (scan - y1) * (x2 - x1) / (y2 - y1))
            crossings.sort()
            row = rows[y]
            for index in range(0, len(crossings) - 1, 2):
                left = max(0, int(crossings[index] + 0.5))
                right = min(width, int(crossings[index + 1] + 0.5))
                for x in range(left, right):
                    row[x] = True
    return BooleanMask(width, height, tuple(tuple(row) for row in rows))


def dilate(mask: BooleanMask, radius: int) -> BooleanMask:
    """Square-kernel dilation; ``radius=0`` returns an unchanged mask."""
    if radius < 0:
        raise ProviderInputError("dilate radius must be >= 0", stage="mask_refine")
    if radius == 0:
        return mask
    width, height = mask.width, mask.height
    rows = [[False] * width for _ in range(height)]
    for y in range(height):
        source = mask.rows[y]
        for x in range(width):
            if not source[x]:
                continue
            for ny in range(max(0, y - radius), min(height, y + radius + 1)):
                target = rows[ny]
                for nx in range(max(0, x - radius), min(width, x + radius + 1)):
                    target[nx] = True
    return BooleanMask(width, height, tuple(tuple(row) for row in rows))


def erode(mask: BooleanMask, radius: int) -> BooleanMask:
    """Square-kernel erosion; ``radius=0`` returns an unchanged mask."""
    if radius < 0:
        raise ProviderInputError("erode radius must be >= 0", stage="mask_refine")
    if radius == 0:
        return mask
    width, height = mask.width, mask.height
    rows = [[False] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if not mask.rows[y][x]:
                continue
            keep = True
            for ny in range(y - radius, y + radius + 1):
                if not 0 <= ny < height:
                    keep = False
                    break
                for nx in range(x - radius, x + radius + 1):
                    if not 0 <= nx < width or not mask.rows[ny][nx]:
                        keep = False
                        break
                if not keep:
                    break
            rows[y][x] = keep
    return BooleanMask(width, height, tuple(tuple(row) for row in rows))


def refine(
    mask: BooleanMask,
    *,
    dilate_radius: int = 0,
    erode_radius: int = 0,
) -> BooleanMask:
    """Apply the refinement chain: erode first, then dilate (TASK-018)."""
    refined = erode(mask, erode_radius)
    refined = dilate(refined, dilate_radius)
    if not refined.covers(mask):
        # Boundary protection must never shrink the text area away.
        refined = dilate(refined, max(dilate_radius, 1))
    return refined


def mask_record(
    raw: BooleanMask,
    final: BooleanMask,
    *,
    parameters: Sequence[tuple[str, str]] = DEFAULT_MASK_PARAMS,
    source: str = MASK_SOURCE_REFINED,
) -> MaskRecord:
    """Build the auditable record kept next to every mask revision."""
    return MaskRecord(
        parameters=tuple(parameters),
        raw_area=raw.area,
        final_area=final.area,
        raw_bbox=raw.bbox(),
        final_bbox=final.bbox(),
        final_covers_raw=final.covers(raw),
        source=source,
    )


def area_ratio(mask: BooleanMask) -> float:
    return mask.area / float(mask.width * mask.height)
