"""Inpaint capability port (D06 §20~§22/§53, TASK-018 absorbed, TASK-019).

The port keeps the TASK-018 conclusions structural:

- a route that has no registered implementation is **not_implemented** and
  fails closed — dependency satisfaction alone never makes a route runnable
  (R-007);
- the *raw* and the *final* mask, the parameters and the protected-area check
  travel with every result, so mask records are auditable and persistable
  (AC-INPAINT-001/003);
- an inpaint writes **only** masked pixels: any change outside the mask is a
  hard failure, not a warning (non-target protection).

The port itself performs no persistence and holds no model handle: adapters
declare their device/weight requirements and the runtime resolves them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ports.providers.errors import ProviderInputError

#: Route names follow D06 §21. Only explicitly registered routes may run.
ROUTE_SIMPLE_FILL = "simple-fill"
ROUTE_EDGE_BLEED = "edge-bleed"
ROUTE_MANGA_LAMA = "manga-lama"
ROUTE_AOT_GAN = "aot-gan"
ROUTE_BRUSHNET = "brushnet"
ROUTE_FLUX_FILL = "flux-fill"

#: Routes whose only requirement is the Python runtime (TASK-018: dependency
#: free, measurable today).
DEPENDENCY_FREE_ROUTES = frozenset({ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED})

#: Learned routes: declared candidates, **no implementation in this Task**.
LEARNED_ROUTES = frozenset(
    {ROUTE_MANGA_LAMA, ROUTE_AOT_GAN, ROUTE_BRUSHNET, ROUTE_FLUX_FILL}
)

ALL_ROUTES = DEPENDENCY_FREE_ROUTES | LEARNED_ROUTES

#: Explicit route registry state (TASK-018 R-007 fail-closed gate).
IMPLEMENTED = "implemented"
NOT_IMPLEMENTED = "not_implemented"

MODE_RGB24 = "rgb24"
MODE_RGB32 = "rgb32"
MODE_RGBA32 = "rgba32"
MODE_BYTES_PER_PIXEL = {MODE_RGB24: 3, MODE_RGB32: 4, MODE_RGBA32: 4}


@dataclass(frozen=True)
class ImageFrame:
    """A decoded raster image: ``width * height * bytes_per_pixel`` bytes.

    Kept deliberately dumb so a provider can be exercised without Qt or
    numpy; the production adapter converts Qt images into this shape.
    """

    width: int
    height: int
    mode: str
    data: bytes = field(repr=False, default=b"")

    def __post_init__(self) -> None:
        if self.mode not in MODE_BYTES_PER_PIXEL:
            raise ProviderInputError(f"unsupported pixel mode: {self.mode!r}", stage="inpaint")
        if self.width <= 0 or self.height <= 0:
            raise ProviderInputError("image dimensions must be positive", stage="inpaint")
        expected = self.width * self.height * MODE_BYTES_PER_PIXEL[self.mode]
        if len(self.data) != expected:
            raise ProviderInputError(
                f"image buffer is {len(self.data)} bytes, expected {expected}",
                stage="inpaint",
            )

    @property
    def pixel_count(self) -> int:
        return self.width * self.height


@dataclass(frozen=True)
class BooleanMask:
    """A row-major boolean mask (``True`` = repaint this pixel)."""

    width: int
    height: int
    rows: tuple[tuple[bool, ...], ...]

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ProviderInputError("mask dimensions must be positive", stage="inpaint")
        if len(self.rows) != self.height:
            raise ProviderInputError("mask row count does not match height", stage="inpaint")
        for row in self.rows:
            if len(row) != self.width:
                raise ProviderInputError("mask row width mismatch", stage="inpaint")

    @property
    def area(self) -> int:
        return sum(1 for row in self.rows for cell in row if cell)

    def bbox(self) -> tuple[int, int, int, int] | None:
        """Half-open bounding box of set pixels, or None when empty."""
        xs: list[int] = []
        ys: list[int] = []
        for y, row in enumerate(self.rows):
            for x, cell in enumerate(row):
                if cell:
                    xs.append(x)
                    ys.append(y)
        if not xs:
            return None
        return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)

    def covers(self, inner: "BooleanMask") -> bool:
        if (inner.width, inner.height) != (self.width, self.height):
            return False
        return all(
            not inner.rows[y][x] or self.rows[y][x]
            for y in range(self.height)
            for x in range(self.width)
        )


@dataclass(frozen=True)
class MaskRecord:
    """The auditable mask record persisted next to every result (AC-INPAINT-001)."""

    parameters: tuple[tuple[str, str], ...]
    raw_area: int
    final_area: int
    raw_bbox: tuple[int, int, int, int] | None
    final_bbox: tuple[int, int, int, int] | None
    final_covers_raw: bool
    source: str = ""

    def as_dict(self) -> dict:
        return {
            "mask_params": dict(self.parameters),
            "raw_mask_area": self.raw_area,
            "final_mask_area": self.final_area,
            "raw_mask_bbox": list(self.raw_bbox) if self.raw_bbox else None,
            "final_mask_bbox": list(self.final_bbox) if self.final_bbox else None,
            "final_covers_raw": self.final_covers_raw,
            "mask_source": self.source,
        }


@dataclass(frozen=True)
class InpaintRequest:
    """One masked repaint on the current upstream image of a Page."""

    page_id: str
    region_id: str | None
    image: ImageFrame
    raw_mask: BooleanMask
    final_mask: BooleanMask
    route: str
    mask_record: MaskRecord
    device: str = ""
    options: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.route not in ALL_ROUTES:
            raise ProviderInputError(f"unknown inpaint route: {self.route!r}", stage="inpaint")
        if not self.final_mask.covers(self.raw_mask):
            raise ProviderInputError(
                "final mask must cover the raw mask", stage="inpaint"
            )
        if (self.image.width, self.image.height) != (
            self.final_mask.width,
            self.final_mask.height,
        ):
            raise ProviderInputError(
                "mask and image dimensions differ", stage="inpaint"
            )


@dataclass(frozen=True)
class InpaintResult:
    """One clean image plus its provenance (D06 §22.2)."""

    page_id: str
    region_id: str | None
    image: ImageFrame
    route: str
    provider_id: str = ""
    provider_type: str = ""
    model: str = ""
    options: tuple[tuple[str, str], ...] = ()
    device: str = ""
    router_reason: str = ""
    fallback_chain: tuple[str, ...] = ()
    mask_record: MaskRecord | None = None
    elapsed_ms: int | None = None

    def provenance(self) -> dict:
        record = {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "model": self.model,
            "options": dict(self.options),
            "device": self.device,
            "route": self.route,
            "router_reason": self.router_reason,
            "fallback_chain": list(self.fallback_chain),
            "elapsed_ms": self.elapsed_ms,
        }
        if self.mask_record is not None:
            record.update(self.mask_record.as_dict())
        return record


class InpaintProvider(Protocol):
    """One inpaint adapter for exactly the route it declares."""

    provider_id: str
    provider_type: str
    route: str
    requires_gpu: bool
    supports_cpu_fallback: bool

    def inpaint(self, request: InpaintRequest) -> InpaintResult: ...
