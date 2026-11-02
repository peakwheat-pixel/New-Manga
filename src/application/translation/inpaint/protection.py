"""Non-target pixel protection rule (TASK-018 hard rule, D06 §19~22).

An inpaint may rewrite **masked pixels only**. This check compares the bytes
outside the final mask and is the rule the Inpaint Step enforces before it
lets a result be committed; the adapter-side enforcement helper
(``require_non_target_protection``) lives with the raster implementations in
``infrastructure/providers/inpaint_routes.py`` and consumes this rule.

It sits in the application layer so the Inpaint Step needs no infrastructure
import (``doc/02_TECHNICAL_ARCHITECTURE_.md`` §架构方向; Standards finding
S-1 of the TASK-019 review).
"""

from __future__ import annotations

from ports.inpaint.ports import MODE_BYTES_PER_PIXEL, BooleanMask, ImageFrame
from ports.providers.errors import ProviderInputError


def protected_pixel_violations(
    before: ImageFrame, after: ImageFrame, mask: BooleanMask
) -> tuple[tuple[int, int], ...]:
    """Pixels that changed **outside** the mask; must be empty before commit."""
    if (before.width, before.height) != (after.width, after.height):
        raise ProviderInputError("image size changed during inpaint", stage="inpaint")
    bpp = MODE_BYTES_PER_PIXEL[before.mode]
    violations: list[tuple[int, int]] = []
    for y, row in enumerate(mask.rows):
        base = y * before.width * bpp
        for x, cell in enumerate(row):
            if cell:
                continue
            offset = base + x * bpp
            if before.data[offset : offset + bpp] != after.data[offset : offset + bpp]:
                violations.append((x, y))
    return tuple(violations)
