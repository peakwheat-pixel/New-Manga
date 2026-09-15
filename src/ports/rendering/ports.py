"""Rendering port contracts (TASK-014).

Application use cases depend only on these protocols; the Qt/SQLite
adapters live in ``infrastructure.rendering``. DTOs are shared by both
sides, so they stay free of Qt/sqlite types (TASK-005 guards).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from application.rendering.style import TextDirection
from ports.repositories.artifacts import (
    ArtifactRecord,
    ArtifactRevisionRecord,
    ArtifactType,
)


@dataclass(frozen=True)
class LayoutRequest:
    """One layout attempt for a region's text at a concrete font size."""

    text: str
    font_family: str
    font_size: float
    direction: TextDirection  # concrete (never AUTO — resolve first)
    box_width: int
    box_height: int
    stroke_width: float = 0.0  # 0 → no stroke allowance in the box
    line_spacing: float = 1.0
    text_align: str = "start"


@dataclass(frozen=True)
class DrawItem:
    """A single positioned text run for the compositor.

    Horizontal layout: one item per line, ``x``/``y`` is the line's
    left origin / baseline. Vertical layout: one item per character
    (``per_char``), ``x`` is the column left edge and ``y`` the glyph
    baseline, columns ordered right-to-left by the engine.
    """

    text: str
    x: float
    y: float
    per_char: bool = False


@dataclass(frozen=True)
class LayoutResult:
    items: tuple[DrawItem, ...]
    extents_width: float
    extents_height: float
    fits: bool
    font_available: bool
    resolved_family: str


class TextLayoutEngine(Protocol):
    """Measure and lay out text for one (style, size, box) combination."""

    def layout(self, request: LayoutRequest) -> LayoutResult: ...


@dataclass(frozen=True)
class ResolvedFont:
    requested_family: str
    resolved_family: str
    available: bool


class FontCatalog(Protocol):
    """Resolve a requested family to an installed one (D03 §11.6 default
    font may be absent — that must be diagnosable, never fatal)."""

    def resolve(self, family: str) -> ResolvedFont: ...


@dataclass(frozen=True)
class RenderOp:
    """A region's fully resolved draw instruction for the compositor."""

    items: tuple[DrawItem, ...]
    region_x: int
    region_y: int
    region_width: int
    region_height: int
    font_family: str  # already resolved (installed) family
    font_size: float
    text_color: str
    stroke_enabled: bool
    stroke_color: str
    stroke_width: float
    direction: TextDirection
    text_align: str = "start"


class ImageCompositor(Protocol):
    """Compose rendered text onto page images (D06 §23, TASK-002 §8.2)."""

    def compose_page(self, base_png: bytes, ops: Sequence[RenderOp]) -> bytes:
        """Full-page render: every op is drawn onto the base (Clean) image."""
        ...

    def compose_region(
        self,
        base_png: bytes,
        clean_png: bytes,
        box: tuple[int, int, int, int],
        op: RenderOp,
    ) -> bytes:
        """Single-region composition (§8.2): the target box on ``base`` is
        first restored from ``clean`` (erasing the region's previous
        translation), then the op is drawn — other regions stay intact."""
        ...


@dataclass(frozen=True)
class SourceStyle:
    """D06 §8 Color/Source Style Step output for one region."""

    detected_source_font_size: float | None
    source_font_size_confidence: float
    text_color: str | None = None
    stroke_hint_color: str | None = None
    background_color: str | None = None
    direction_hint: TextDirection | None = None


class SourceStyleAnalyzer(Protocol):
    """Analyze a cropped original-image region for style hints (D06 §8)."""

    def analyze(self, crop_png: bytes) -> SourceStyle: ...


class PageArtifactLocator(Protocol):
    """Locate a page's artifact of a given type together with its current
    revision (read-only; the shared ArtifactRepositoryPort has no page
    query, and that frozen port file is outside this slice's paths)."""

    def locate_current(
        self, page_id: str, artifact_type: ArtifactType
    ) -> tuple[ArtifactRecord, ArtifactRevisionRecord] | None: ...


__all__ = [
    "ArtifactRecord",
    "ArtifactRevisionRecord",
    "ArtifactType",
    "DrawItem",
    "FontCatalog",
    "ImageCompositor",
    "LayoutRequest",
    "LayoutResult",
    "PageArtifactLocator",
    "RenderOp",
    "ResolvedFont",
    "SourceStyle",
    "SourceStyleAnalyzer",
    "TextLayoutEngine",
]
