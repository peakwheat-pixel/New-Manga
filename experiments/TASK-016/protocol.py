"""Provider-neutral experiment protocol helpers.

These functions intentionally live under experiments and are not production
contracts. They make coordinate and RegionID mistakes observable before any
optional OCR model is available.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Set


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


def fallback_status(
    provider_status: str,
    configured_routes: Set[str],
    *,
    requested_route: str | None = None,
) -> str:
    """Allow fallback only to a route the caller names **and** that is configured.

    R-002 review finding: the earlier form returned ``FALLBACK_CONFIGURED`` as
    soon as *any* route was configured, so "some fallback exists" could be read
    as "any fallback is acceptable". The rule is now narrowed: the caller must
    name the route it intends to use, and that exact name must be present in
    ``configured_routes``. An empty configuration, an unnamed request, or a name
    outside the configuration is ``BLOCKED`` — never silently substituted.
    """

    if provider_status == "PASS":
        return "PASS"
    if not configured_routes:
        return "BLOCKED"
    if requested_route is None or requested_route not in configured_routes:
        return "BLOCKED"
    return "FALLBACK_CONFIGURED"


def validate_route_configuration(configured_routes: Iterable[str]) -> dict:
    """Report invalid fallback configuration without inventing a route.

    Returns a record intended for the experiment log: ``valid`` is False when no
    route is configured or when a blank/non-string entry is present.
    """

    routes = list(configured_routes)
    problems: list[str] = []
    if not routes:
        problems.append("no fallback route configured")
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            problems.append(f"blank or non-string route: {route!r}")
    return {"configured_routes": routes, "problems": problems, "valid": not problems}
