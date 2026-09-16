"""Provider-neutral experiment protocol helpers.

These functions intentionally live under experiments and are not production
contracts. They make coordinate and RegionID mistakes observable before any
optional OCR model is available.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def tile_polygon_to_global(polygon: list[list[float]], origin: list[float]) -> list[list[float]]:
    """Translate a Tile-local polygon into page-global coordinates."""
    if len(origin) != 2:
        raise ValueError("tile origin must be [x, y]")
    if not polygon:
        raise ValueError("polygon must not be empty")
    return [[point[0] + origin[0], point[1] + origin[1]] for point in polygon]


def map_region_result(
    *,
    region_id: str,
    text: str,
    polygon: list[list[float]],
    reading_order: int,
    coordinate_space: str = "page-global",
    tile_origin: list[float] | None = None,
) -> dict:
    """Build one normalized result and preserve the caller's RegionID."""
    if not region_id:
        raise ValueError("region_id is required")
    if coordinate_space == "tile-local":
        if tile_origin is None:
            raise ValueError("tile-local output requires tile_origin")
        polygon = tile_polygon_to_global(polygon, tile_origin)
        coordinate_space = "page-global"
    if coordinate_space != "page-global":
        raise ValueError(f"unsupported coordinate space: {coordinate_space}")
    return {
        "region_id": region_id,
        "text": text,
        "polygon": polygon,
        "reading_order": reading_order,
        "coordinate_space": coordinate_space,
    }


def order_results(results: Iterable[Mapping]) -> list[dict]:
    """Return stable reading order without changing RegionIDs."""
    return [dict(result) for result in sorted(results, key=lambda item: (item["reading_order"], item["region_id"]))]


def fallback_status(provider_status: str, configured_routes: set[str]) -> str:
    """Allow fallback only to an explicitly configured route."""
    if provider_status == "PASS":
        return "PASS"
    if not configured_routes:
        return "BLOCKED"
    return "FALLBACK_CONFIGURED"
