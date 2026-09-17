"""Dependency-free inpaint route implementations (raster mechanism only).

The route **declaration and fail-closed gate** (TASK-018 R-007) and the
non-target protection **rule** live in the application layer
(``application/translation/inpaint/route_catalog.py`` and ``protection.py``);
this module keeps only the bytes-level implementations and their providers, so
no application module has to import infrastructure (Standards S-1/S-2 of the
TASK-019 review).

Non-target protection is enforced after every repaint: pixels outside the
final mask must be byte-identical, otherwise
:class:`~ports.providers.errors.NonTargetWriteViolation` is raised and nothing
is committed.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from application.translation.inpaint.protection import protected_pixel_violations
from application.translation.inpaint.route_catalog import route_gate
from ports.inpaint.ports import (
    MODE_BYTES_PER_PIXEL,
    ROUTE_EDGE_BLEED,
    ROUTE_SIMPLE_FILL,
    BooleanMask,
    ImageFrame,
    InpaintRequest,
    InpaintResult,
)
from ports.providers.errors import (
    NonTargetWriteViolation,
    ProviderInputError,
    ProviderNotImplemented,
)

DEFAULT_FILL_RGB = (255, 255, 255)


# ----------------------------------------------------------------------
# raster helpers (dependency-free, bytes only)
# ----------------------------------------------------------------------


def _set_pixel(buffer: bytearray, offset: int, rgb: tuple[int, int, int]) -> None:
    buffer[offset] = rgb[0]
    buffer[offset + 1] = rgb[1]
    buffer[offset + 2] = rgb[2]


def _pixel_at(data: bytes, offset: int) -> tuple[int, int, int]:
    return (data[offset], data[offset + 1], data[offset + 2])


def simple_fill(
    image: ImageFrame,
    mask: BooleanMask,
    *,
    fill: tuple[int, int, int] = DEFAULT_FILL_RGB,
) -> ImageFrame:
    """Paint masked pixels with one solid colour; leave the rest untouched."""
    _require_same_shape(image, mask)
    bpp = MODE_BYTES_PER_PIXEL[image.mode]
    buffer = bytearray(image.data)
    for y, row in enumerate(mask.rows):
        base = y * image.width * bpp
        for x, cell in enumerate(row):
            if cell:
                _set_pixel(buffer, base + x * bpp, fill)
    return ImageFrame(image.width, image.height, image.mode, bytes(buffer))


def edge_bleed(
    image: ImageFrame,
    mask: BooleanMask,
    *,
    iterations: int = 4,
) -> ImageFrame:
    """Iteratively copy the nearest unmasked neighbour into masked pixels.

    A dependency-free *structural* baseline, never reported as a learned
    inpainting model (TASK-018 wording preserved).
    """
    if iterations < 0:
        raise ProviderInputError("iterations must be >= 0", stage="inpaint")
    _require_same_shape(image, mask)
    bpp = MODE_BYTES_PER_PIXEL[image.mode]
    width, height = image.width, image.height
    buffer = bytearray(image.data)
    remaining = [list(row) for row in mask.rows]
    for _ in range(iterations):
        if not any(any(row) for row in remaining):
            break
        snapshot = bytes(buffer)
        next_remaining = [list(row) for row in remaining]
        for y in range(height):
            for x in range(width):
                if not remaining[y][x]:
                    continue
                neighbours: list[tuple[int, int, int]] = []
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = y + dy, x + dx
                    if not (0 <= ny < height and 0 <= nx < width):
                        continue
                    if remaining[ny][nx]:
                        continue
                    neighbours.append(_pixel_at(snapshot, (ny * width + nx) * bpp))
                if neighbours:
                    next_remaining[y][x] = False
                    averaged = tuple(  # type: ignore[assignment]
                        sum(channel[i] for channel in neighbours) // len(neighbours)
                        for i in range(3)
                    )
                    _set_pixel(buffer, (y * width + x) * bpp, averaged)  # type: ignore[arg-type]
        remaining = next_remaining
    return ImageFrame(width, height, image.mode, bytes(buffer))


def require_non_target_protection(
    before: ImageFrame, after: ImageFrame, mask: BooleanMask
) -> None:
    violations = protected_pixel_violations(before, after, mask)
    if violations:
        sample = violations[:5]
        raise NonTargetWriteViolation(
            f"{len(violations)} pixel(s) changed outside the mask, e.g. {sample}",
            stage="inpaint",
        )


def _require_same_shape(image: ImageFrame, mask: BooleanMask) -> None:
    if (image.width, image.height) != (mask.width, mask.height):
        raise ProviderInputError("mask and image dimensions differ", stage="inpaint")


# ----------------------------------------------------------------------
# providers
# ----------------------------------------------------------------------


@dataclass
class SimpleFillProvider:
    """``simple-fill`` route provider (D06 §21 white/solid small regions)."""

    provider_id: str = "inpaint-simple-fill"
    provider_type: str = "local-simple-fill"
    route: str = ROUTE_SIMPLE_FILL
    requires_gpu: bool = False
    supports_cpu_fallback: bool = False
    fill: tuple[int, int, int] = DEFAULT_FILL_RGB
    options: tuple[tuple[str, str], ...] = field(default=())

    def inpaint(self, request: InpaintRequest) -> InpaintResult:
        self._require_route(request)
        result = simple_fill(request.image, request.final_mask, fill=self.fill)
        require_non_target_protection(request.image, result, request.final_mask)
        return _result(self, request, result)

    def _require_route(self, request: InpaintRequest) -> None:
        if request.route != self.route:
            raise ProviderNotImplemented(
                f"{self.provider_id} only implements route {self.route!r}",
                provider_id=self.provider_id,
                stage="inpaint",
            )


@dataclass
class EdgeBleedProvider:
    """``edge-bleed`` structural baseline provider."""

    provider_id: str = "inpaint-edge-bleed"
    provider_type: str = "local-edge-bleed"
    route: str = ROUTE_EDGE_BLEED
    requires_gpu: bool = False
    supports_cpu_fallback: bool = False
    iterations: int = 4
    options: tuple[tuple[str, str], ...] = field(default=())

    def inpaint(self, request: InpaintRequest) -> InpaintResult:
        if request.route != self.route:
            raise ProviderNotImplemented(
                f"{self.provider_id} only implements route {self.route!r}",
                provider_id=self.provider_id,
                stage="inpaint",
            )
        result = edge_bleed(request.image, request.final_mask, iterations=self.iterations)
        require_non_target_protection(request.image, result, request.final_mask)
        return _result(self, request, result)


def _result(
    provider: object, request: InpaintRequest, image: ImageFrame
) -> InpaintResult:
    return InpaintResult(
        page_id=request.page_id,
        region_id=request.region_id,
        image=image,
        route=request.route,
        provider_id=getattr(provider, "provider_id"),
        provider_type=getattr(provider, "provider_type"),
        model="",
        options=getattr(provider, "options", ()),
        device=request.device,
        mask_record=request.mask_record,
    )


def provider_for_route(route: str, **kwargs) -> object:
    """Build the provider for an implemented route or fail closed."""
    gate = route_gate(route)
    if not gate.runnable:
        raise ProviderNotImplemented(gate.reason, stage="inpaint")
    if route == ROUTE_SIMPLE_FILL:
        return SimpleFillProvider(**kwargs)
    if route == ROUTE_EDGE_BLEED:
        return EdgeBleedProvider(**kwargs)
    raise ProviderNotImplemented(f"route {route!r} has no provider", stage="inpaint")


def run_routes(
    routes: Sequence[str],
    *,
    invoke: Callable[[str], InpaintResult],
) -> InpaintResult:
    """Try routes in the configured order, recording the chain.

    Only the routes the caller explicitly lists are tried (D06 §51/§53); the
    returned provenance carries the fallback chain that actually happened.
    """
    attempts: list[str] = []
    last_error: Exception | None = None
    for route in routes:
        attempts.append(route)
        gate = route_gate(route)
        if not gate.runnable:
            last_error = ProviderNotImplemented(gate.reason, stage="inpaint")
            continue
        try:
            result = invoke(route)
        except Exception as error:  # noqa: BLE001 - re-raised after the chain
            last_error = error
            continue
        return InpaintResult(
            page_id=result.page_id,
            region_id=result.region_id,
            image=result.image,
            route=result.route,
            provider_id=result.provider_id,
            provider_type=result.provider_type,
            model=result.model,
            options=result.options,
            device=result.device,
            router_reason=result.router_reason,
            fallback_chain=tuple(attempts),
            mask_record=result.mask_record,
            elapsed_ms=result.elapsed_ms,
        )
    if last_error is None:  # pragma: no cover - routes is never empty
        raise ProviderNotImplemented("no inpaint route was requested", stage="inpaint")
    raise last_error
