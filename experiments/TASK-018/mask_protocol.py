"""TASK-018 sample + mask protocol (dependency-free core).

This module is an *experiment harness*, not a production contract. It is pure
Python so that mask geometry, parameter records and non-target protection can
be verified even when no inpainting model is installed.

Only the standard library is used here; PNG encoding lives in
``generate_samples.py`` (PySide6 ``QImage``), and the Simple Fill baseline in
``simple_fill.py``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

#: the five fixed sample classes required by TASK-018 AC-2
SAMPLE_KINDS = (
    "white-background",
    "line-art",
    "screentone",
    "gradient",
    "structure-crossing",
)

#: tunable parameters that must be preserved with every mask (AC-3)
DEFAULT_MASK_PARAMS: dict[str, object] = {
    "dilate_radius": 2,
    "feather_radius": 0,
    "min_region_pixels": 1,
    "keep_largest_component": False,
}


def empty_mask(width: int, height: int) -> list[list[bool]]:
    """Return an all-False (keep-everything) mask."""
    if width <= 0 or height <= 0:
        raise ValueError("mask dimensions must be positive")
    return [[False] * width for _ in range(height)]


def rect_mask(
    width: int, height: int, box: Sequence[int], *, value: bool = True
) -> list[list[bool]]:
    """Return a mask with ``box`` = (x0, y0, x1, y1) set (half-open)."""
    if len(box) != 4:
        raise ValueError("box must be (x0, y0, x1, y1)")
    x0, y0, x1, y1 = (int(v) for v in box)
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError(f"box out of bounds for {width}x{height}: {box}")
    mask = empty_mask(width, height)
    for y in range(y0, y1):
        row = mask[y]
        for x in range(x0, x1):
            row[x] = value
    return mask


def mask_area(mask: Sequence[Sequence[bool]]) -> int:
    return sum(1 for row in mask for cell in row if cell)


def dilate(mask: Sequence[Sequence[bool]], radius: int) -> list[list[bool]]:
    """Square-kernel dilation; ``radius=0`` returns an unchanged copy."""
    if radius < 0:
        raise ValueError("dilate radius must be >= 0")
    height = len(mask)
    width = len(mask[0]) if height else 0
    if radius == 0:
        return [list(row) for row in mask]
    out = empty_mask(width, height)
    for y in range(height):
        for x in range(width):
            if not mask[y][x]:
                continue
            for dy in range(-radius, radius + 1):
                ny = y + dy
                if not (0 <= ny < height):
                    continue
                for dx in range(-radius, radius + 1):
                    nx = x + dx
                    if 0 <= nx < width:
                        out[ny][nx] = True
    return out


def erode(mask: Sequence[Sequence[bool]], radius: int) -> list[list[bool]]:
    """Square-kernel erosion; ``radius=0`` returns an unchanged copy."""
    if radius < 0:
        raise ValueError("erode radius must be >= 0")
    height = len(mask)
    width = len(mask[0]) if height else 0
    if radius == 0:
        return [list(row) for row in mask]
    out = empty_mask(width, height)
    for y in range(height):
        for x in range(width):
            keep = True
            for dy in range(-radius, radius + 1):
                ny = y + dy
                if not (0 <= ny < height):
                    keep = False
                    break
                for dx in range(-radius, radius + 1):
                    nx = x + dx
                    if not (0 <= nx < width) or not mask[ny][nx]:
                        keep = False
                        break
                if not keep:
                    break
            out[y][x] = keep
    return out


def refine_mask(
    mask: Sequence[Sequence[bool]], *, dilate_radius: int = 0, erode_radius: int = 0
) -> list[list[bool]]:
    """Apply the mask refinement chain and keep both raw and final masks.

    AC-3 requires the *original* and *final* mask to be preserved, so callers
    must store both; this helper only produces the final one.
    """
    refined = erode(mask, erode_radius)
    refined = dilate(refined, dilate_radius)
    return refined


def bbox(mask: Sequence[Sequence[bool]]) -> tuple[int, int, int, int] | None:
    """Half-open bounding box of the masked pixels, or None when empty."""
    height = len(mask)
    width = len(mask[0]) if height else 0
    xs: list[int] = []
    ys: list[int] = []
    for y in range(height):
        for x in range(width):
            if mask[y][x]:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def protected_pixels(
    before: Sequence[Sequence[object]],
    after: Sequence[Sequence[object]],
    mask: Sequence[Sequence[bool]],
) -> list[tuple[int, int]]:
    """Return pixels that changed **outside** the mask (must be empty).

    This is the non-target protection check required by the test plan: an
    inpainting step is only allowed to rewrite masked pixels.
    """
    height = len(before)
    width = len(before[0]) if height else 0
    violations: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if mask[y][x]:
                continue
            if before[y][x] != after[y][x]:
                violations.append((x, y))
    return violations


def mask_records(
    raw: Sequence[Sequence[bool]],
    final: Sequence[Sequence[bool]],
    params: Mapping[str, object],
) -> dict[str, object]:
    """Build the auditable mask record kept next to every result image."""
    return {
        "mask_params": dict(params),
        "raw_mask_area": mask_area(raw),
        "final_mask_area": mask_area(final),
        "raw_mask_bbox": bbox(raw),
        "final_mask_bbox": bbox(final),
        "final_covers_raw": covers(final, raw),
    }


def covers(outer: Sequence[Sequence[bool]], inner: Sequence[Sequence[bool]]) -> bool:
    """True when every True pixel of ``inner`` is also True in ``outer``."""
    height = len(inner)
    width = len(inner[0]) if height else 0
    for y in range(height):
        for x in range(width):
            if inner[y][x] and not outer[y][x]:
                return False
    return True


def route_available(routes: Mapping[str, Mapping[str, object]], route: str) -> tuple[bool, str]:
    """Return (runnable, reason) for one inpainting route in this environment."""
    info = routes.get(route)
    if info is None:
        return False, f"unknown route: {route}"
    missing = [name for name, ok in info.get("requirements", {}).items() if not ok]
    if missing:
        return False, "missing dependency/weight: " + ", ".join(sorted(missing))
    return True, "ready"


def simple_fill(
    image: Sequence[Sequence[tuple[int, int, int]]],
    mask: Sequence[Sequence[bool]],
    *,
    fill: tuple[int, int, int] = (255, 255, 255),
) -> list[list[tuple[int, int, int]]]:
    """Baseline: paint masked pixels with a constant colour, keep the rest."""
    height = len(image)
    width = len(image[0]) if height else 0
    out = [list(row) for row in image]
    for y in range(height):
        for x in range(width):
            if mask[y][x]:
                out[y][x] = fill
    return out


def edge_bleed_fill(
    image: Sequence[Sequence[tuple[int, int, int]]],
    mask: Sequence[Sequence[bool]],
    *,
    iterations: int = 1,
) -> list[list[tuple[int, int, int]]]:
    """Baseline: iteratively copy the nearest unmasked neighbour into the mask.

    A cheap, dependency-free stand-in used only for *structural* comparison with
    Simple Fill; it is **not** a learned inpainting model and is never reported
    as one.
    """
    if iterations < 0:
        raise ValueError("iterations must be >= 0")
    height = len(image)
    width = len(image[0]) if height else 0
    out = [list(row) for row in image]
    remaining = [list(row) for row in mask]
    for _ in range(iterations):
        if not any(any(row) for row in remaining):
            break
        snapshot = [list(row) for row in out]
        next_remaining = [list(row) for row in remaining]
        for y in range(height):
            for x in range(width):
                if not remaining[y][x]:
                    continue
                neighbours: list[tuple[int, int, int]] = []
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and not remaining[ny][nx]:
                        neighbours.append(snapshot[ny][nx])
                if neighbours:
                    next_remaining[y][x] = False
                    red = sum(c[0] for c in neighbours) // len(neighbours)
                    green = sum(c[1] for c in neighbours) // len(neighbours)
                    blue = sum(c[2] for c in neighbours) // len(neighbours)
                    out[y][x] = (red, green, blue)
        remaining = next_remaining
    return out


def residual_text_pixels(
    before: Sequence[Sequence[tuple[int, int, int]]],
    after: Sequence[Sequence[tuple[int, int, int]]],
    mask: Sequence[Sequence[bool]],
    *,
    dark_threshold: int = 128,
) -> int:
    """Count masked pixels that are still 'ink-dark' after inpainting.

    A crude, model-independent proxy for 残字 (residual glyph). It is reported
    as a *pixel statistic*, never as a visual quality verdict.
    """
    height = len(before)
    width = len(before[0]) if height else 0
    residual = 0
    for y in range(height):
        for x in range(width):
            if not mask[y][x]:
                continue
            red, green, blue = after[y][x]
            luminance = (red * 299 + green * 587 + blue * 114) // 1000
            if luminance < dark_threshold:
                residual += 1
    return residual


def ink_pixels_inside(
    image: Sequence[Sequence[tuple[int, int, int]]],
    mask: Sequence[Sequence[bool]],
    *,
    dark_threshold: int = 128,
) -> int:
    """Count dark (glyph) pixels inside the mask **before** inpainting."""
    return residual_text_pixels(image, image, mask, dark_threshold=dark_threshold)


def summarize(results: Iterable[Mapping[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in results:
        status = str(record.get("status", "UNKNOWN"))
        counts[status] = counts.get(status, 0) + 1
    return counts
