"""Backward-compatibility shim for region canvas geometry (M2-I2).

Authoritative location: application.editing.region_canvas.
This module is preserved as a non-authoritative compatibility shim for legacy
consumers. All domain/application logic resides in application.editing.region_canvas.
"""

from __future__ import annotations

from application.editing.region_canvas import (
    DEGENERATE_GEOMETRY,
    PAGE_SIZE_UNAVAILABLE,
    TOO_FEW_POINTS,
    RegionCanvasError,
    normalized_to_page_geometry,
)

__all__ = [
    "DEGENERATE_GEOMETRY",
    "PAGE_SIZE_UNAVAILABLE",
    "RegionCanvasError",
    "TOO_FEW_POINTS",
    "normalized_to_page_geometry",
]
