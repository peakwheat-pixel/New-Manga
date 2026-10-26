"""Detection capability port (D06 §6, TASK-019).

Detect produces the initial Region geometry for a page. The port is
provider-neutral: adapters report candidate polygons with an explicit
coordinate space, and the caller — never the adapter — assigns business
RegionIDs, matching the TASK-016 conclusion that a Vision/OCR model must not
invent a business id.

No production handler is wired for this capability in TASK-019: no Detect AC
is assigned to this Task and Region-creation semantics belong to the Region
editing slice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ports.providers.errors import ProviderInputError

COORDINATE_SPACE_PAGE = "page-global"
COORDINATE_SPACE_TILE = "tile-local"
COORDINATE_SPACES = frozenset({COORDINATE_SPACE_PAGE, COORDINATE_SPACE_TILE})


def to_page_global(
    polygon: tuple[tuple[float, float], ...],
    *,
    coordinate_space: str,
    tile_origin: tuple[float, float] | None = None,
) -> tuple[tuple[float, float], ...]:
    """Translate a tile-local polygon into page coordinates (TASK-016).

    The Tile origin must be given explicitly; a missing origin or an unknown
    coordinate space fails closed instead of guessing an offset.
    """
    if not polygon:
        raise ProviderInputError("polygon must not be empty", stage="detection")
    if coordinate_space == COORDINATE_SPACE_TILE:
        if tile_origin is None:
            raise ProviderInputError(
                "tile-local polygons require an explicit tile origin",
                stage="detection",
            )
        if len(tile_origin) != 2:
            raise ProviderInputError("tile origin must be [x, y]", stage="detection")
        return tuple(
            (x + tile_origin[0], y + tile_origin[1]) for x, y in polygon
        )
    if coordinate_space != COORDINATE_SPACE_PAGE:
        raise ProviderInputError(
            f"unsupported coordinate space: {coordinate_space!r}", stage="detection"
        )
    return polygon


@dataclass(frozen=True)
class DetectionRequest:
    """One page to detect on; the image arrives as encoded bytes."""

    page_id: str
    image_bytes: bytes = field(repr=False, default=b"")
    width: int = 0
    height: int = 0
    options: tuple[tuple[str, str], ...] = ()

    def option_dict(self) -> dict[str, str]:
        return dict(self.options)


@dataclass(frozen=True)
class RegionCandidate:
    """One detected candidate; the id is assigned by the caller, not the model."""

    polygon: tuple[tuple[float, float], ...]
    reading_order: int = 0
    confidence: float | None = None
    #: Provider-assigned placeholder (e.g. ``unmapped-3``) kept for audit only.
    provider_label: str = ""

    def __post_init__(self) -> None:
        if self.polygon and len(self.polygon) < 3:
            raise ProviderInputError(
                "a polygon needs at least three points", stage="detection"
            )


@dataclass(frozen=True)
class DetectionResult:
    page_id: str
    candidates: tuple[RegionCandidate, ...]
    coordinate_space: str = COORDINATE_SPACE_PAGE
    provider_id: str = ""
    provider_type: str = ""
    model: str = ""
    options: tuple[tuple[str, str], ...] = ()
    elapsed_ms: int | None = None

    def page_global_candidates(
        self, *, tile_origin: tuple[float, float] | None = None
    ) -> tuple[RegionCandidate, ...]:
        if self.coordinate_space == COORDINATE_SPACE_PAGE:
            return self.candidates
        return tuple(
            RegionCandidate(
                polygon=to_page_global(
                    candidate.polygon,
                    coordinate_space=self.coordinate_space,
                    tile_origin=tile_origin,
                ),
                reading_order=candidate.reading_order,
                confidence=candidate.confidence,
                provider_label=candidate.provider_label,
            )
            for candidate in self.candidates
        )

    def provenance(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "model": self.model,
            "options": dict(self.options),
            "coordinate_space": self.coordinate_space,
            "candidate_count": len(self.candidates),
            "elapsed_ms": self.elapsed_ms,
        }


class DetectionProvider(Protocol):
    """One detection adapter (local detector or OpenAI-compatible Vision)."""

    provider_id: str
    provider_type: str

    def detect(self, request: DetectionRequest) -> DetectionResult: ...
